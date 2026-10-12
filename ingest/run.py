"""Ingest: files in -> chunks, scope tags, summaries, digests, embeddings -> Postgres.

  python -m ingest.run corpus/                                  # pre-tagged corpus
  python -m ingest.run handout/ --source handout --default-scope internal   # untagged: classifier runs
  python -m ingest.run corpus/ --classify                       # force the classifier on tagged docs too
  python -m ingest.run --digests-only                           # rebuild T3 from stored summaries

EXPERIMENTAL: .docx files are supported alongside .md and .txt.

Connects with DATABASE_URL as the database owner. Ingest is the one writer and bypasses RLS on purpose.
Re-ingesting a document (same source and title) replaces it.
"""
from __future__ import annotations
import argparse, pathlib, collections, concurrent.futures as cf
import psycopg
from config import DATABASE_URL
from ingest import chunk, tag, summarize, embed

def vec(v):
    return "[" + ",".join(f"{x:.6f}" for x in v) + "]"

def prepare(path, args):
    """Everything that needs the model for one document. Runs in a worker thread."""
    doc = chunk.load(path, args.source, args.default_scope)
    if not doc.chunks:
        return None
    tag.tag(doc, True if args.classify else None)
    by_scope = collections.defaultdict(list)
    for c in doc.chunks:
        by_scope[c.scope].append(c)
    doc.summaries = {s: summarize.summarize(doc.title, s, cs) for s, cs in by_scope.items()}
    return doc

def store(conn, doc):
    scopes = sorted({c.scope for c in doc.chunks})
    c_vecs = embed.embed([c.content for c in doc.chunks])
    s_items = sorted(doc.summaries.items())
    s_vecs = embed.embed([f"{doc.title}. {text}" for _, (text, _) in s_items])
    with conn.transaction():
        conn.execute("delete from brain.document where source = %s and title = %s", (doc.source, doc.title))
        doc_id = conn.execute(
            "insert into brain.document (title, source, default_scope, scopes) values (%s, %s, %s, %s) returning id",
            (doc.title, doc.source, doc.default_scope, scopes)).fetchone()[0]
        for c, v in zip(doc.chunks, c_vecs):
            conn.execute("insert into brain.chunk (document_id, ord, scope, content, tokens, embedding) "
                         "values (%s, %s, %s, %s, %s, %s::extensions.vector)",
                         (doc_id, c.ord, c.scope, c.content, len(c.content) // 4, vec(v)))
        for (scope, (text, topics)), v in zip(s_items, s_vecs):
            conn.execute("insert into brain.summary (document_id, scope, topics, content, embedding) "
                         "values (%s, %s, %s, %s, %s::extensions.vector)", (doc_id, scope, topics, text, vec(v)))
    return scopes

def rebuild_digests(conn, workers):
    rows = conn.execute("select s.scope, t.topic, d.id, d.title, s.content "
                        "from brain.summary s join brain.document d on d.id = s.document_id, "
                        "unnest(s.topics) as t(topic) order by t.topic, s.scope, d.title").fetchall()
    groups = collections.defaultdict(list)
    for scope, topic, doc_id, title, content in rows:
        groups[(topic, scope)].append((doc_id, title, content))
    keys = sorted(groups)
    with cf.ThreadPoolExecutor(workers) as pool:
        texts = list(pool.map(lambda k: summarize.digest(k[0], [(t, s) for _, t, s in groups[k]]), keys))
    vecs = embed.embed([f"{k[0]}. {t}" for k, t in zip(keys, texts)])
    with conn.transaction():
        conn.execute("delete from brain.digest")
        for (topic, scope), text, v in zip(keys, texts, vecs):
            conn.execute("insert into brain.digest (topic, scope, document_ids, content, embedding) "
                         "values (%s, %s, %s, %s, %s::extensions.vector)",
                         (topic, scope, [g[0] for g in groups[(topic, scope)]], text, vec(v)))
    return len(keys)

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", help="files or directories (.md, .txt, .docx)")
    ap.add_argument("--source", help="source name for files without frontmatter")
    ap.add_argument("--default-scope", help="scope for files without frontmatter")
    ap.add_argument("--classify", action="store_true", help="run the scope classifier on pre-tagged documents too")
    ap.add_argument("--digests-only", action="store_true")
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()
    if not DATABASE_URL:
        raise SystemExit("DATABASE_URL is not set")

    files = []
    for p in map(pathlib.Path, args.paths):
        # EXPERIMENTAL: include .docx
        files += sorted(f for f in p.rglob("*") if f.suffix.lower() in chunk.READERS) if p.is_dir() else [p]

    with psycopg.connect(DATABASE_URL) as conn:
        if not args.digests_only:
            with cf.ThreadPoolExecutor(args.workers) as pool:
                futures = {pool.submit(prepare, f, args): f for f in files}
                failed = 0
                for fut in cf.as_completed(futures):
                    f = futures[fut]
                    try:
                        doc = fut.result()
                        if doc is None:
                            print(f"skip  {f.name}: empty"); continue
                        scopes = store(conn, doc)
                        print(f"ok    {f.name}: {len(doc.chunks)} chunks, scopes {','.join(scopes)}")
                    except Exception as e:           # one bad file must not sink the batch
                        failed += 1
                        print(f"FAIL  {f.name}: {e}")
            if failed:
                print(f"{failed} of {len(files)} files failed")
        n = rebuild_digests(conn, args.workers)
        print(f"digests: {n}")

if __name__ == "__main__":
    main()
