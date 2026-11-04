"""The help center contract: a customer-facing site built from what a customer may see, and nothing else.

    python -m helpcenter.build --out <dir>

writes a static site to <dir>: an index, one page per document the BRAIN_CUSTOMER role can see, and an "ask us"
box on every page that posts the visitor's question to the brain's /ask route. The API serves <dir> at /help/.

Where the content comes from is the whole point. A page may hold only what core.gate.query("BRAIN_CUSTOMER", sql)
returns: the database's row access policy decides what a customer sees, chunk by chunk, so a public article's
internal section never reaches the site. Reading corpus/ files from disk, or asking as any other role, bypasses
the gate. The referee runs the build in a copy of the repo where core.gate is a SQLite gate that holds exactly the
rows Snowflake would give BRAIN_CUSTOMER (tables chunk, summary, digest, document_scope and the view
visible_document, same columns as sf/01_schema.sql; %s parameters), refuses every other role, and where corpus/
carries canary strings in places only a bypass could reach.

  1  the build runs and writes index.html
  2  every visible document has its own page, linked from the index: title as its h1, chunks in ord order
  3  it asks only as BRAIN_CUSTOMER, only through core.gate
  4  nothing outside the customer's view reaches any output file (planted canaries, restricted titles, scope markers)
  5  content is escaped: a chunk holding markup shows as text, never as markup
  6  every page is a complete document (doctype, lang, charset, viewport, unique title, one h1) and every link and
     asset is relative and resolves inside the site (it is served under /help/)
  7  self-contained: no external scripts, styles, fonts or images
  8  the ask box: on every page, a form posting {"question": ...} as JSON to /ask with "Authorization: Bearer <token>"
     (HELPCENTER_TOKEN at build time, default "helpcenter-public"); the answer is written with textContent, and no
     script uses innerHTML, outerHTML, insertAdjacentHTML or document.write
  9  the build is deterministic: building twice gives the same files, byte for byte
 10  helpcenter/ modules use the standard library (plus core and helpcenter) only, and make no network calls

Builders work under helpcenter/ only and must not change goals/.  Run one check:  python3 goals/helpcenter/referee.py --only <n>
"""
import ast, hashlib, html, json, os, re, shutil, sqlite3, subprocess, sys, tempfile
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
W = Path(tempfile.mkdtemp(prefix="helpcenter-"))
TOKEN = "hc-test-token-42"
RESULTS = []

CANARIES = ["CANARY-REFUND-INTERNAL-5521", "CANARY-EXEC-3317", "CANARY-TITLE-8890"]
RESTRICTED_TITLES = ["Compensation Bands 2026", "Board Minutes", "Acquisition Evaluation", "Project Nightjar"]

# what Snowflake's policy hands BRAIN_CUSTOMER: public rows only. Chunks are inserted out of order on purpose.
DOCS = [  # id, title, source
    ("d-start", "Getting Started with Halcyon", "support-kb"),
    ("d-refund", "Refund Policy", "support-kb"),
    ("d-sso", "Single Sign-On Setup", "support-kb"),
    ("d-status", "Status and SLA", "support-kb"),
]
CHUNKS = [  # document_id, ord, content
    ("d-status", 2, "Credits are applied to the next invoice automatically."),
    ("d-start", 0, "Welcome to Halcyon. Create a workspace from the dashboard to begin."),
    ("d-status", 0, "Halcyon targets 99.9 percent monthly uptime for paid plans."),
    ("d-refund", 0, "Annual plans can be refunded in full within 30 days of purchase."),
    ("d-sso", 0, 'Paste your identity provider\'s metadata URL. Note: <script>alert("hc")</script> & \'quotes\' stay text.'),
    ("d-start", 1, "Invite your team under Settings, then Members."),
    ("d-status", 1, "If we miss the target you receive a service credit."),
]
HOSTILE = '<script>alert("hc")</script>'


def check(n, title):
    def wrap(fn):
        RESULTS.append((n, title, fn)); return fn
    return wrap


# ------------------------------------------------------------------ world --

FAKE_GATE = '''"""Referee stand-in for core.gate: the rows Snowflake's row access policy would give BRAIN_CUSTOMER, in SQLite."""
import json, os, sqlite3
ASKER_ROLES = {"BRAIN_SALES", "BRAIN_EXEC", "BRAIN_SUPPORT_AGENT", "BRAIN_CUSTOMER"}

def query(role, sql, params=None):
    with open(os.environ["HC_GATE_LOG"], "a") as f:
        f.write(json.dumps({"role": role, "sql": sql}) + "\\n")
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


def make_db(path):
    con = sqlite3.connect(path)
    con.executescript("""
      create table _document_base (id text primary key, title text, source text, default_scope text, created_at text);
      create table document_scope (document_id text, scope text);
      create table chunk (id text primary key, document_id text, ord int, scope text, content text, tokens int, embedding text);
      create table summary (document_id text, scope text, topics text, content text, embedding text);
      create table digest (id text, topic text, scope text, document_ids text, content text, embedding text);
      create view visible_document as select d.* from _document_base d
        where exists (select 1 from document_scope ds where ds.document_id = d.id);
    """)
    for i, (did, title, src) in enumerate(DOCS):
        con.execute("insert into _document_base values (?,?,?,?,?)", (did, title, src, "public", f"2026-10-0{i + 1} 09:00:00"))
        con.execute("insert into document_scope values (?, 'public')", (did,))
    for i, (did, ord_, content) in enumerate(CHUNKS):
        con.execute("insert into chunk values (?,?,?,?,?,?,?)", (f"c{i}", did, ord_, "public", content, len(content.split()), None))
    con.execute("insert into summary values ('d-start','public','onboarding','How to create a workspace and invite your team.',null)")
    con.execute("insert into digest values ('g1','onboarding','public','d-start','Getting set up: workspaces and members.',null)")
    con.commit(); con.close()


def plant(copy):
    """Canaries only a gate bypass could reach: an internal section in a public article, a restricted document."""
    c = copy / "corpus"; c.mkdir(exist_ok=True)
    (c / "support-kb-refund-policy.md").write_text(
        "---\ntitle: \"Refund Policy\"\nsource: support-kb\nscope: public\n---\n# Refund Policy\n\n"
        "Annual plans can be refunded in full within 30 days of purchase.\n\n"
        "## Exceptions we do not publish\n<!-- scope: internal -->\n"
        "Enterprise accounts over the threshold get discretionary refunds. CANARY-REFUND-INTERNAL-5521\n")
    (c / "zz-project-nightjar.md").write_text(
        "---\ntitle: \"Project Nightjar Acquisition CANARY-TITLE-8890\"\nsource: board-minutes\nscope: exec\n---\n"
        "# Project Nightjar Acquisition CANARY-TITLE-8890\n\nThe board approved the offer. CANARY-EXEC-3317\n")


def files_of(root):
    r = subprocess.run(["git", "ls-files", "-co", "--exclude-standard"], cwd=root, capture_output=True, text=True)
    return [f for f in r.stdout.splitlines() if f and not f.startswith("helpcenter/dist/") and (root / f).is_file()]


def build_once(tag):
    copy = W / f"repo-{tag}"
    for f in files_of(ROOT):
        (copy / f).parent.mkdir(parents=True, exist_ok=True); shutil.copy2(ROOT / f, copy / f)
    (copy / "core" / "gate.py").write_text(FAKE_GATE)
    plant(copy)
    db, log, out = W / f"gate-{tag}.db", W / f"gate-{tag}.log", W / f"out-{tag}"
    make_db(db); log.write_text("")
    env = {k: v for k, v in os.environ.items() if not k.startswith(("SNOWFLAKE", "ANTHROPIC", "OPENAI", "VOYAGE"))}
    env.update({"HC_GATE_DB": str(db), "HC_GATE_LOG": str(log), "HELPCENTER_TOKEN": TOKEN, "PYTHONPATH": str(copy),
                "PYTHONHASHSEED": "random" if tag == "a" else "12345"})
    r = subprocess.run([sys.executable, "-m", "helpcenter.build", "--out", str(out)], cwd=copy, env=env,
                       capture_output=True, text=True, timeout=300)
    return {"rc": r.returncode, "err": (r.stdout + r.stderr)[-600:], "out": out, "log": log, "copy": copy}


_B = {}
def built(tag="a"):
    if tag not in _B:
        _B[tag] = build_once(tag)
    b = _B[tag]
    assert b["rc"] == 0, f"python -m helpcenter.build failed: {b['err']}"
    assert (b["out"] / "index.html").is_file(), "the build wrote no index.html"
    return b


def html_files(out):
    return sorted(p for p in out.rglob("*.html"))


def all_text_files(out):
    return [p for p in out.rglob("*") if p.is_file() and p.suffix.lower() in (".html", ".htm", ".css", ".js", ".json", ".txt", ".xml", ".svg", ".map", "")]


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags, self.h1, self.title, self.text, self.refs, self.forms, self.inputs, self.buttons, self.scripts = [], [], "", [], [], 0, 0, 0, []
        self.lang = self.charset = self.viewport = False
        self._in = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs); self.tags.append(tag); self._in.append(tag)
        if tag == "html" and a.get("lang"): self.lang = True
        if tag == "meta" and (a.get("charset") or "charset" in (a.get("content") or "").lower()): self.charset = True
        if tag == "meta" and a.get("name", "").lower() == "viewport": self.viewport = True
        if tag == "h1": self.h1.append("")
        if tag == "form": self.forms += 1
        if tag in ("input", "textarea") and (tag == "textarea" or a.get("type", "text") in ("text", "search")): self.inputs += 1
        if tag == "button" or (tag == "input" and a.get("type") == "submit"): self.buttons += 1
        for k in ("href", "src"):
            if a.get(k) is not None: self.refs.append((tag, k, a[k]))
        if tag == "link" and a.get("href"): pass
    def handle_endtag(self, tag):
        if self._in and self._in[-1] == tag: self._in.pop()
    def handle_data(self, d):
        if "title" in self._in: self.title += d
        if "h1" in self._in and self.h1: self.h1[-1] += d
        if "script" in self._in: self.scripts.append(d)
        elif "style" not in self._in: self.text.append(d)


def parse(p):
    pg = Page(); src = p.read_text(encoding="utf-8", errors="replace"); pg.feed(src); pg.src = src
    return pg


def page_for(out, title):
    for p in html_files(out):
        pg = parse(p)
        if any(h.strip() == title for h in pg.h1):
            return p, pg
    return None, None


def site_js(out):
    """Every script the site runs: inline blocks and local .js files."""
    js = [p.read_text(encoding="utf-8", errors="replace") for p in out.rglob("*.js")]
    for p in html_files(out):
        js += parse(p).scripts
    return "\n".join(js)


def resolve(base_file, out, ref):
    ref = ref.split("#")[0].split("?")[0]
    if not ref:
        return base_file
    return (base_file.parent / ref).resolve()


# ----------------------------------------------------------------- checks --

@check(1, "the build runs and writes index.html")
def c1():
    built()


@check(2, "every visible document has its own page, linked from the index, title as h1, chunks in order")
def c2():
    out = built()["out"]
    idx = parse(out / "index.html")
    linked = {resolve(out / "index.html", out, r) for t, k, r in idx.refs if t == "a" and k == "href"}
    for did, title, _ in DOCS:
        p, pg = page_for(out, title)
        assert p is not None, f"no page has <h1>{title}</h1>"
        assert p.resolve() in linked, f"the index does not link to the page for {title!r}"
        body = html.unescape(" ".join(pg.text))
        mine = [c for c in sorted(CHUNKS, key=lambda c: c[1]) if c[0] == did]
        pos = []
        for _, _, content in mine:
            plain = re.sub(r"\s+", " ", content)
            i = re.sub(r"\s+", " ", body).find(plain)
            assert i >= 0, f"{title}: chunk text missing: {plain[:50]!r}"
            pos.append(i)
        assert pos == sorted(pos), f"{title}: chunks are not in ord order"


@check(3, "it asks only as BRAIN_CUSTOMER, only through core.gate")
def c3():
    b = built()
    calls = [json.loads(l) for l in b["log"].read_text().splitlines() if l.strip()]
    assert calls, "the build never called core.gate.query: its content came from somewhere else"
    roles = sorted({c["role"] for c in calls})
    assert roles == ["BRAIN_CUSTOMER"], f"the build asked as {roles}; a customer-facing page asks as BRAIN_CUSTOMER only"


@check(4, "nothing outside the customer's view reaches any output file")
def c4():
    out = built()["out"]
    for p in all_text_files(out):
        t = p.read_text(encoding="utf-8", errors="replace")
        for c in CANARIES:
            assert c not in t, f"{p.relative_to(out)} holds {c}: content reached the site around the gate (corpus/ read from disk?)"
        for title in RESTRICTED_TITLES:
            assert title not in t, f"{p.relative_to(out)} names a restricted document ({title!r})"
        assert "scope: internal" not in t and "<!-- scope:" not in t, f"{p.relative_to(out)} carries a scope marker from a source file"


@check(5, "content is escaped: markup in a chunk shows as text")
def c5():
    out = built()["out"]
    for p in all_text_files(out):
        assert HOSTILE not in p.read_text(encoding="utf-8", errors="replace"), f"{p.relative_to(out)} carries a chunk's <script> as live markup"
    p, pg = page_for(out, "Single Sign-On Setup")
    assert p is not None, "no page for Single Sign-On Setup"
    assert HOSTILE in html.unescape(" ".join(pg.text)), "the SSO page does not show the chunk's markup as text"


@check(6, "complete documents; every link and asset relative and resolving inside the site")
def c6():
    out = built()["out"]
    titles = {}
    for p in html_files(out):
        pg = parse(p); rel = p.relative_to(out)
        assert pg.src.lstrip().lower().startswith("<!doctype html>"), f"{rel}: no <!doctype html>"
        assert pg.lang, f"{rel}: <html> has no lang"
        assert pg.charset, f"{rel}: no charset meta"
        assert pg.viewport, f"{rel}: no viewport meta (phones)"
        assert pg.title.strip(), f"{rel}: empty <title>"
        assert pg.title.strip() not in titles, f"{rel} and {titles.get(pg.title.strip())} share the title {pg.title.strip()!r}"
        titles[pg.title.strip()] = rel
        assert len(pg.h1) == 1, f"{rel}: {len(pg.h1)} <h1> elements, want one"
        for tag, k, ref in pg.refs:
            if re.match(r"^(mailto:|tel:|#|data:)", ref) or re.match(r"^[a-z][a-z0-9+.-]*://", ref, re.I) or ref.startswith("//"):
                continue                                                    # external refs are check 7's business
            assert not ref.startswith("/"), f"{rel}: {tag} {k}={ref!r} is root-absolute; the site is served under /help/"
            target = resolve(p, out, ref)
            if target.is_dir():
                target = target / "index.html"
            assert target.is_file() and out.resolve() in target.parents, f"{rel}: {tag} {k}={ref!r} does not resolve inside the site"


@check(7, "self-contained: no external scripts, styles, fonts or images")
def c7():
    out = built()["out"]
    for p in all_text_files(out):
        t = p.read_text(encoding="utf-8", errors="replace"); rel = p.relative_to(out)
        for m in re.finditer(r"""(?:src|href)\s*=\s*["']?\s*((?:https?:)?//[^"'\s>]+)""", t, re.I):
            tag = t[max(0, t.rfind("<", 0, m.start())):m.start()].lower()
            assert tag.startswith("<a"), f"{rel}: loads {m.group(1)} from another host"
        assert not re.search(r"""@import\s+(?:url\()?\s*["']?(?:https?:)?//""", t, re.I), f"{rel}: @import from another host"
        assert not re.search(r"""url\(\s*["']?(?:https?:)?//""", t, re.I), f"{rel}: url() from another host"


@check(8, "the ask box: on every page, posts the question to /ask with the help center token, answer as text")
def c8():
    out = built()["out"]
    for p in html_files(out):
        pg = parse(p); rel = p.relative_to(out)
        assert pg.forms >= 1 and pg.inputs >= 1 and pg.buttons >= 1, f"{rel}: no ask form (form, text input, submit button)"
    js = site_js(out)
    assert re.search(r"""fetch\s*\(\s*[`"']/ask[`"']""", js), "no script calls fetch('/ask', ...)"
    assert re.search(r"""method\s*:\s*[`"']POST[`"']""", js, re.I), "the ask call is not a POST"
    assert re.search(r"""[`"']?Authorization[`"']?\s*:\s*[`"']Bearer\s""", js) or re.search(r"""[`"']Bearer\s*[`"']\s*\+""", js) or "Bearer ${" in js, \
        "the ask call sends no Authorization: Bearer header"
    assert TOKEN in js, "the token is not the HELPCENTER_TOKEN given at build time"
    assert "helpcenter-public" not in js, "the default token was used although HELPCENTER_TOKEN was set"
    assert re.search(r"""JSON\.stringify\s*\(\s*\{\s*question\b""", js), "the body is not JSON {question: ...}"
    assert "textContent" in js, "the answer is not written with textContent"
    for bad in ("innerHTML", "outerHTML", "insertAdjacentHTML", "document.write"):
        assert bad not in js, f"a script uses {bad}: an answer could become markup"


@check(9, "the build is deterministic")
def c9():
    a, b = built("a")["out"], built("b")["out"]
    def digest(root):
        return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.rglob("*")) if p.is_file()}
    da, db = digest(a), digest(b)
    assert set(da) == set(db), f"different files: {sorted(set(da) ^ set(db))[:5]}"
    diff = [k for k in da if da[k] != db[k]]
    assert not diff, f"files differ between two builds: {diff[:5]}"


@check(10, "helpcenter/ modules: standard library (plus core, helpcenter) only, no network")
def c10():
    mods = [p for p in (ROOT / "helpcenter").rglob("*.py") if not p.name.startswith("test_")] if (ROOT / "helpcenter").is_dir() else []
    assert mods, "there is no helpcenter/ package"
    std = set(sys.stdlib_module_names) | {"__future__", "core", "helpcenter"}
    net = {"socket", "ssl", "urllib", "http", "ftplib", "smtplib", "poplib", "imaplib", "asyncio", "subprocess", "webbrowser"}
    for f in mods:
        tree = ast.parse(f.read_text())
        for node in ast.walk(tree):
            names = [a.name for a in node.names] if isinstance(node, ast.Import) else \
                    [node.module or ""] if isinstance(node, ast.ImportFrom) and node.level == 0 else []
            for n in names:
                top = n.split(".")[0]
                assert top in std, f"{f.relative_to(ROOT)} imports {n}, not the standard library"
                assert top not in net, f"{f.relative_to(ROOT)} imports {n}: the build makes no network calls"
                assert n not in ("core.retrieve", "core.ask", "core.identity", "sf", "sf.conn"), f"{f.relative_to(ROOT)} imports {n}: go through core.gate only"


def main():
    only = int(sys.argv[sys.argv.index("--only") + 1]) if "--only" in sys.argv else None
    p = f = 0
    for n, title, fn in sorted(RESULTS):
        if only is not None and n != only:
            continue
        try:
            fn(); p += 1; print(f"PASS {n} {title}")
        except Exception as e:
            f += 1; print(f"FAIL {n} {title}: {type(e).__name__}: {str(e)[:300]}")
    print(f"SUMMARY passed={p} failed={f}")
    shutil.rmtree(W, ignore_errors=True)
    sys.exit(1 if f else 0)


if __name__ == "__main__":
    main()
