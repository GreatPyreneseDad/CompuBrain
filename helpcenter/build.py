"""Build the help center as static files.

    python -m helpcenter.build --out <dir>

Content comes from core.gate.query("BRAIN_CUSTOMER", sql) and nothing else: the row access policy decides, chunk
by chunk, what a customer sees. No file is read for content, no other role is asked. Everything that came from the
database is escaped; the ask box writes answers with textContent.
"""
import argparse
import html
import json
import os
import re
from pathlib import Path

from core import gate

ROLE = "BRAIN_CUSTOMER"
DEFAULT_TOKEN = "helpcenter-public"
SITE_TITLE = "Help Center"

# ingest/chunk.py prefixes a chunk with its heading trail: "[Support KB: Title > Section]\n<body>"
LABEL = re.compile(r"\A\[([^\n]+)\]\n(.*)\Z", re.S)

DOCS_SQL = "select id, title from visible_document order by title, id"
CHUNKS_SQL = "select document_id, ord, content from chunk order by document_id, ord, content"

CSS = (
    "body{font-family:sans-serif;margin:0;line-height:1.5;color:#1a1a1a}"
    "main,form,.answer{max-width:46rem;margin:0 auto;padding:1rem}"
    "p{white-space:pre-wrap}"
    "form{border-top:1px solid #ccc}"
    "input[type=text]{width:70%;padding:.4rem}"
    "button{padding:.4rem .8rem}"
)

ASK_FORM = (
    '<form id="ask-form">\n'
    '<label for="ask-q">Ask us</label>\n'
    '<input type="text" id="ask-q" name="question" autocomplete="off" required>\n'
    '<button type="submit">Ask</button>\n'
    "</form>\n"
    '<div class="answer"><p id="ask-answer" aria-live="polite"></p></div>'
)

ASK_JS = """(function () {
  var form = document.getElementById("ask-form");
  if (!form) { return; }
  var input = document.getElementById("ask-q");
  var out = document.getElementById("ask-answer");
  form.addEventListener("submit", function (ev) {
    ev.preventDefault();
    var q = input.value.trim();
    if (!q) { return; }
    out.textContent = "Thinking...";
    fetch("/ask", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": __AUTH__
      },
      body: JSON.stringify({ question: q })
    }).then(function (r) {
      return r.json().then(function (d) { return { ok: r.ok, data: d }; });
    }).then(function (res) {
      var d = res.data || {};
      var text = d.answer || d.message || d.detail || d.outcome || "No answer.";
      out.textContent = typeof text === "string" ? text : JSON.stringify(text);
    }).catch(function () {
      out.textContent = "Sorry, we could not reach the help desk. Try again later.";
    });
  });
})();
"""


def esc(text):
    return html.escape(str(text), quote=True)


# inline markdown: `code` and **bold**; whichever starts first wins, so ** inside a code span stays literal
INLINE = re.compile(r"`([^`\n]+)`|\*\*(?=\S)(.+?)(?<=\S)\*\*")


def inline(text):
    """Escape text and render its inline markdown bold and code as strong and code elements."""
    out, pos = [], 0
    for m in INLINE.finditer(text):
        out.append(esc(text[pos:m.start()]))
        if m.group(1) is not None:
            out.append(f"<code>{esc(m.group(1))}</code>")
        else:
            out.append(f"<strong>{inline(m.group(2))}</strong>")
        pos = m.end()
    out.append(esc(text[pos:]))
    return "".join(out)


# a dash-prefixed line is a list item: "- text"
LIST_ITEM = re.compile(r"[ \t]*-[ \t]+(\S.*?)[ \t\r]*")


def blocks(text):
    """A chunk body as HTML: runs of '- ' lines become ul/li, the lines between them stay paragraphs."""
    out, para, items = [], [], []

    def flush_para():
        body = "\n".join(para).strip()
        if body:
            out.append(f"<p>{inline(body)}</p>")
        para.clear()

    def flush_items():
        if items:
            lis = "\n".join(f"<li>{inline(i)}</li>" for i in items)
            out.append(f"<ul>\n{lis}\n</ul>")
            items.clear()

    for line in text.split("\n"):
        m = LIST_ITEM.fullmatch(line)
        if m:
            flush_para()
            items.append(m.group(1))
        else:
            flush_items()
            para.append(line)
    flush_para()
    flush_items()
    return "\n".join(out)


def page(title, body):
    return (
        "<!doctype html>\n"
        '<html lang="en">\n<head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{esc(title)}</title>\n"
        f"<style>{CSS}</style>\n"
        "</head>\n<body>\n"
        f"<main>\n{body}\n</main>\n"
        f"{ASK_FORM}\n"
        '<script src="ask.js"></script>\n'
        "</body>\n</html>\n"
    )


def sections(chunks):
    """Chunks in order as HTML: a chunk's path label becomes an h2 (once for consecutive chunks sharing it)."""
    out, last = [], None
    for content in chunks:
        m = LABEL.match(content)
        if m:
            label, text = m.group(1).strip(), m.group(2)
            if label != last:
                out.append(f"<h2>{inline(label)}</h2>")
            last = label
        else:
            text, last = content, None
        body = blocks(text)
        if body:
            out.append(body)
    return "\n".join(out)


def slugs(docs):
    """One unique file name per document; docs arrive sorted, so the assignment is stable."""
    used, names = set(), {}
    for doc_id, title in docs:
        base = re.sub(r"[^a-z0-9]+", "-", str(title).lower()).strip("-")[:60].strip("-") or "article"
        name, n = base, 1
        while name in used:
            n += 1
            name = f"{base}-{n}"
        used.add(name)
        names[doc_id] = f"doc-{name}.html"
    return names


def fetch():
    docs = [(r[0], r[1]) for r in gate.query(ROLE, DOCS_SQL)]
    rows = {doc_id: [] for doc_id, _ in docs}
    for document_id, ord_, content in gate.query(ROLE, CHUNKS_SQL):
        if document_id in rows:
            rows[document_id].append((ord_, content))
    chunks = {doc_id: [c for _, c in sorted(r)] for doc_id, r in rows.items()}
    return docs, chunks


def build(out, token):
    docs, chunks = fetch()
    names = slugs(docs)
    out.mkdir(parents=True, exist_ok=True)
    for stale in out.glob("doc-*.html"):
        stale.unlink()

    def write(name, text):
        (out / name).write_text(text, encoding="utf-8", newline="\n")

    items = "\n".join(f'<li><a href="{esc(names[d])}">{esc(t)}</a></li>' for d, t in docs)
    listing = f"<ul>\n{items}\n</ul>" if docs else "<p>No articles yet.</p>"
    write("index.html", page(SITE_TITLE, f"<h1>{esc(SITE_TITLE)}</h1>\n{listing}"))

    for doc_id, title in docs:
        paras = sections(chunks[doc_id])
        body = f'<p><a href="index.html">All articles</a></p>\n<h1>{esc(title)}</h1>\n{paras}'
        write(names[doc_id], page(f"{title} - {SITE_TITLE}", body))

    write("ask.js", ASK_JS.replace("__AUTH__", json.dumps("Bearer " + token)))


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m helpcenter.build", description="Build the customer help center.")
    ap.add_argument("--out", default="helpcenter/dist", help="output directory (default: helpcenter/dist)")
    args = ap.parse_args(argv)
    build(Path(args.out), os.environ.get("HELPCENTER_TOKEN", DEFAULT_TOKEN))


if __name__ == "__main__":
    main()
