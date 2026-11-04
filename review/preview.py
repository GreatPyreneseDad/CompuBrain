"""Preview world for reviewing the help center without Snowflake.

The real site is built as BRAIN_CUSTOMER against Snowflake. Reviewers need the real articles, so this builds a SQLite
gate holding what that role would see: every chunk of corpus/ whose scope is public (frontmatter scope, overridden per
section by a <!-- scope: --> marker, exactly as ingest tags it), and nothing else. The build runs in a copy of the
repo whose core.gate answers from that database and refuses every other role, the same arrangement the referee uses.
"""
from __future__ import annotations
import os, shutil, sqlite3, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

GATE = '''"""Preview stand-in for core.gate: the public rows only, in SQLite."""
import os, sqlite3
ASKER_ROLES = {"BRAIN_CUSTOMER"}
def query(role, sql, params=None):
    if role != "BRAIN_CUSTOMER":
        raise PermissionError(f"the help center asks as BRAIN_CUSTOMER, not {role}")
    con = sqlite3.connect(f"file:{os.environ['HC_GATE_DB']}?mode=ro", uri=True)
    try:
        cur = con.execute(sql.replace("%s", "?"), tuple(params or ()))
        return cur.fetchall() if cur.description else []
    finally:
        con.close()
def warm():
    pass
'''


def public_rows(corpus: Path):
    sys.path.insert(0, str(ROOT))
    from ingest import chunk
    docs, chunks = [], []
    for f in sorted(corpus.glob("*.md")):
        try:
            d = chunk.load(f)
        except Exception:
            continue
        mine = [c for c in d.chunks if (c.scope or d.default_scope) == "public"]
        if not mine:
            continue
        did = f.stem
        docs.append((did, d.title, d.source, d.default_scope))
        for c in mine:
            chunks.append((f"{did}-{c.ord}", did, c.ord, "public", c.content))
    return docs, chunks


def make_db(path: Path, corpus: Path) -> int:
    docs, chunks = public_rows(corpus)
    if path.exists():
        path.unlink()
    con = sqlite3.connect(path)
    con.executescript("""
      create table _document_base (id text primary key, title text, source text, default_scope text, created_at text);
      create table document_scope (document_id text, scope text);
      create table chunk (id text primary key, document_id text, ord int, scope text, content text, tokens int, embedding text);
      create table summary (document_id text, scope text, topics text, content text, embedding text);
      create table digest (id text, topic text, scope text, document_ids text, content text, embedding text);
      create view visible_document as select d.* from _document_base d
        where exists (select 1 from document_scope ds where ds.document_id = d.id);""")
    for did, title, src, scope in docs:
        con.execute("insert into _document_base values (?,?,?,?, '2026-10-01 09:00:00')", (did, title, src, scope))
        con.execute("insert into document_scope values (?, 'public')", (did,))
    for row in chunks:
        con.execute("insert into chunk values (?,?,?,?,?,0,null)", (*row,))
    con.commit(); con.close()
    return len(docs)


def build(out: Path, work: Path, token: str = "helpcenter-public") -> Path:
    """Build the site from the public preview rows. Returns the database path (the preview /ask reads it too)."""
    copy = work / "repo"
    if copy.exists():
        shutil.rmtree(copy)
    files = subprocess.run(["git", "ls-files", "-co", "--exclude-standard"], cwd=ROOT, capture_output=True, text=True).stdout.split()
    for f in files:
        if f.startswith("helpcenter/dist/") or not (ROOT / f).is_file():
            continue
        (copy / f).parent.mkdir(parents=True, exist_ok=True); shutil.copy2(ROOT / f, copy / f)
    (copy / "core" / "gate.py").write_text(GATE)
    db = work / "preview.db"
    n = make_db(db, ROOT / "corpus")
    env = {**os.environ, "HC_GATE_DB": str(db), "HELPCENTER_TOKEN": token, "PYTHONPATH": str(copy)}
    r = subprocess.run([sys.executable, "-m", "helpcenter.build", "--out", str(out)], cwd=copy, env=env, capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        raise RuntimeError(f"helpcenter.build failed: {(r.stdout + r.stderr)[-800:]}")
    print(f"preview: built {out} from {n} public documents")
    return db
