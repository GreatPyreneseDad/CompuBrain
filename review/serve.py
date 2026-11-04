"""Serve a built help center at /help/ with a preview /ask, on localhost, for the reviewers.

/ask here is a stand-in, labeled as one: it answers from the public preview rows by word overlap, so the ask box can
be exercised end to end. The real /ask answers under the gate with the brain's model.
"""
from __future__ import annotations
import json, re, sqlite3, threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PREFIX = "[preview answer] "


STOP = set("the and for can get how what when where who why with your you our are was does did have has not this that from into about will would could should my i a an to of in on is it do".split())


def answer(db: Path, question: str) -> dict:
    """Best public chunk by IDF-weighted word overlap, titles counted. Crude on purpose: it only has to exercise the box."""
    import math
    tok = lambda t: {w for w in re.findall(r"[a-z0-9]+", t.lower()) if len(w) > 2 and w not in STOP}
    con = sqlite3.connect(db)
    rows = con.execute("select d.title, c.content from chunk c join visible_document d on d.id = c.document_id").fetchall()
    con.close()
    bags = [tok(t + " " + c) for t, c in rows]
    df = {}
    for b in bags:
        for w in b:
            df[w] = df.get(w, 0) + 1
    q = tok(question)
    score = lambda i: sum(math.log(1 + len(rows) / df[w]) * (2 if w in tok(rows[i][0]) else 1) for w in q & bags[i])
    best = max(range(len(rows)), key=score, default=None)
    if best is None or score(best) == 0:
        return {"outcome": "refused", "answer": PREFIX + "I can't find that in our help articles. Try rephrasing, or contact support."}
    title, content = rows[best]
    return {"outcome": "answered", "answer": f"{PREFIX}{' '.join(content.split()[:80])} (from: {title})"}


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, site: Path, db: Path, **k):
        self.site, self.db = site, db
        super().__init__(*a, directory=str(site), **k)

    def log_message(self, *a):
        pass

    def translate_path(self, path):
        p = path.split("?")[0].split("#")[0]
        if p == "/help":
            p = "/help/"
        if p.startswith("/help/"):
            return super().translate_path(p[len("/help"):])
        return str(self.site / "__nothing__")

    def do_GET(self):
        if self.path.split("?")[0] == "/help":
            self.send_response(301); self.send_header("Location", "/help/"); self.end_headers(); return
        super().do_GET()

    def do_POST(self):
        if self.path.split("?")[0] != "/ask":
            self.send_error(404); return
        n = int(self.headers.get("Content-Length") or 0)
        try:
            q = json.loads(self.rfile.read(n) or b"{}").get("question", "")
        except json.JSONDecodeError:
            q = ""
        auth = self.headers.get("Authorization", "")
        if not auth.lower().startswith("bearer "):
            body, code = {"detail": "Bearer token required"}, 401
        elif not q.strip():
            body, code = {"detail": "Empty question"}, 400
        else:
            body, code = answer(self.db, q), 200
        data = json.dumps(body).encode()
        self.send_response(code); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data)


def start(site: Path, db: Path, port: int = 0):
    srv = ThreadingHTTPServer(("127.0.0.1", port), partial(Handler, site=site, db=db))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}"
