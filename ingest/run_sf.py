"""Ingest into Snowflake. Same pipeline as ingest.run; the store and the embeddings are Snowflake's.

  python -m ingest.run_sf corpus/
  python -m ingest.run_sf handout/ --source handout --default-scope internal
  python -m ingest.run_sf --digests-only

EXPERIMENTAL: .docx files are supported alongside .md and .txt.

Chunking, tagging and summaries run here against the Anthropic API. Embeddings come from
ingest.embed, or from Cortex with BRAIN_SF_EMBED=cortex (paid accounts only). Connects as BRAIN_OWNER, which the scope map lets
see every scope. Re-ingesting a document (same source and title) replaces it.
"""
from __future__ import annotations
import os, argparse, pathlib, uuid, collections, concurrent.futures as cf
from ingest import summarize, embed
from ingest.run import prepare
from sf.conn import connect, EMBED

def store(cur, doc):
    scopes = sorted({c.scope for c in doc.chunks})
    cur.execute("select id from document where source = %s and title = %s", (doc.source, doc.title))
    for (old,) in cur.fetchall():
        for t in ("chunk", "summary", "document_scope"):
            cur.execute(f"delete from {t} where document_id = %s", (old,))
        cur.execute("delete from document where id = %s", (old,))
    doc_id = str(uuid.uuid4())
    cur.execute("insert into document (id, title, source, default_scope) values (%s, %s, %s, %s)",
                (doc_id, doc.title, doc.source, doc.default_scope))
    cur.executemany("insert into document_scope (document_id, scope) values (%s, %s)", [(doc_id, s) for s in scopes])
    cur.executemany("insert into chunk (document_id, ord, scope, content, tokens) values (%s, %s, %s, %s, %s)",
                    [(doc_id, c.ord, c.scope, c.content, len(c.content) // 4) for c in doc.chunks])
    cur.executemany("insert into summary (document_id, scope, topics, content) values (%s, %s, %s, %s)",
                    [(doc_id, s, ",".join(topics), text) for s, (text, topics) in sorted(doc.summaries.items())])
    return scopes

def embed_pending(cur):
    """Fill every missing vector. Summaries and digests are embedded with their title or topic.

    BRAIN_SF_EMBED=cortex computes vectors inside Snowflake (not available on trial accounts).
    Otherwise vectors come from ingest.embed (Voyage, OpenAI, or the dev-only local fallback) and
    are loaded through a temp table, because VECTOR values cannot be bound as parameters.
    """
    jobs = [
        ("chunk", "id", "''",
         "select id, '', content from chunk where embedding is null"),
        ("summary", "document_id", "scope",
         "select s.document_id, s.scope, d.title || '. ' || s.content from summary s "
         "join document d on d.id = s.document_id where s.embedding is null"),
        ("digest", "id", "''",
         "select id, '', topic || '. ' || content from digest where embedding is null"),
    ]
    if os.environ.get("BRAIN_SF_EMBED") == "cortex":
        for table, _, _, select in jobs:
            text = select.split(",", 2)[2].split(" from ")[0]
            if table == "summary":
                cur.execute(f"update summary set embedding = {EMBED.format('document.title || $$. $$ || summary.content')} "
                            "from document where document.id = summary.document_id and summary.embedding is null")
            else:
                cur.execute(f"update {table} set embedding = {EMBED.format(text)} where embedding is null")
        return
    for table, k1, k2, select in jobs:
        cur.execute(select)
        rows = cur.fetchall()
        if not rows:
            continue
        vecs = embed.embed([r[2] for r in rows])
        cur.execute("create or replace temporary table _vec (k1 varchar, k2 varchar, v varchar)")
        cur.executemany("insert into _vec (k1, k2, v) values (%s, %s, %s)",
                        [(r[0], r[1], "[" + ",".join(f"{x:.6f}" for x in v) + "]") for r, v in zip(rows, vecs)])
        cur.execute(f"update {table} set embedding = parse_json(_vec.v)::vector(float, 1024) from _vec "
                    f"where {table}.{k1} = _vec.k1 and {k2} = _vec.k2")
        print(f"embedded {len(rows)} {table} rows ({embed.provider()})")

def rebuild_digests(cur, workers):
    cur.execute("select s.scope, trim(t.value::varchar), d.id, d.title, s.content "
                "from summary s join document d on d.id = s.document_id, "
                "lateral split_to_table(s.topics, ',') t order by 2, 1, 4")
    groups = collections.defaultdict(list)
    for scope, topic, doc_id, title, content in cur.fetchall():
        if topic:
            groups[(topic, scope)].append((doc_id, title, content))
    keys = sorted(groups)
    with cf.ThreadPoolExecutor(workers) as pool:
        texts = list(pool.map(lambda k: summarize.digest(k[0], [(t, s) for _, t, s in groups[k]]), keys))
    cur.execute("delete from digest")
    cur.executemany("insert into digest (topic, scope, document_ids, content) values (%s, %s, %s, %s)",
                    [(k[0], k[1], ",".join(g[0] for g in groups[k]), text) for k, text in zip(keys, texts)])
    return len(keys)

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--source"); ap.add_argument("--default-scope")
    ap.add_argument("--classify", action="store_true")
    ap.add_argument("--digests-only", action="store_true")
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()

    files = []
    for p in map(pathlib.Path, args.paths):
        # EXPERIMENTAL: include .docx
        files += sorted(f for f in p.rglob("*") if f.suffix in (".md", ".txt", ".docx")) if p.is_dir() else [p]

    with connect("BRAIN_OWNER") as conn:
        cur = conn.cursor()
        if not args.digests_only:
            failed = 0
            with cf.ThreadPoolExecutor(args.workers) as pool:
                futures = {pool.submit(prepare, f, args): f for f in files}
                for fut in cf.as_completed(futures):
                    f = futures[fut]
                    try:
                        doc = fut.result()
                        if doc is None:
                            print(f"skip  {f.name}: empty"); continue
                        cur.execute("begin")
                        scopes = store(cur, doc)
                        cur.execute("commit")
                        print(f"ok    {f.name}: {len(doc.chunks)} chunks, scopes {','.join(scopes)}")
                    except Exception as e:
                        cur.execute("rollback")
                        failed += 1
                        print(f"FAIL  {f.name}: {e}")
            if failed:
                print(f"{failed} of {len(files)} files failed")
        print(f"digests: {rebuild_digests(cur, args.workers)}")
        embed_pending(cur)
        print("embeddings: done")

if __name__ == "__main__":
    main()
