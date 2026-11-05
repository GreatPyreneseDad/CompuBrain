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
    "table{border-collapse:collapse;margin:1rem 0}"
    "th,td{border:1px solid #ccc;padding:.3rem .6rem;text-align:left;vertical-align:top}"
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


# links in plain text: a scheme URL, an email address, or a bare host with a path (kestrelridge.example/security.txt)
LINK = re.compile(
    r"""(?P<url>https?://[^\s<>"']+)"""
    r"""|(?P<mail>[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+)"""
    r"""|(?P<bare>(?<![\w@./-])(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,}/[^\s<>"']*)"""
)


def linkify(text):
    """Escape plain text and turn the emails and URLs in it into links; trailing punctuation stays outside."""
    out, pos = [], 0
    for m in LINK.finditer(text):
        token = m.group(0)
        while token and (token[-1] in ".,;:!?" or (token[-1] == ")" and token.count(")") > token.count("("))):
            token = token[:-1]
        kind = m.lastgroup
        if not token or (kind == "bare" and token.endswith("/") and "/" not in token[:-1].split("//")[-1] and False):
            continue
        href = {"url": token, "mail": "mailto:" + token, "bare": "https://" + token}[kind]
        out.append(esc(text[pos:m.start()]))
        out.append(f'<a href="{esc(href)}">{esc(token)}</a>')
        pos = m.start() + len(token)
    out.append(esc(text[pos:]))
    return "".join(out)


def inline(text):
    """Escape text and render its inline markdown bold and code as strong and code elements, and link emails and URLs."""
    out, pos = [], 0
    for m in INLINE.finditer(text):
        out.append(linkify(text[pos:m.start()]))
        if m.group(1) is not None:
            out.append(f"<code>{esc(m.group(1))}</code>")
        else:
            out.append(f"<strong>{inline(m.group(2))}</strong>")
        pos = m.end()
    out.append(linkify(text[pos:]))
    return "".join(out)


# a dash-prefixed line is a list item: "- text"
LIST_ITEM = re.compile(r"[ \t]*-[ \t]+(\S.*?)[ \t\r]*")

# a number-and-period line is a numbered step: "1. text"
ORDERED_ITEM = re.compile(r"[ \t]*(\d+)\.[ \t]+(\S.*?)[ \t\r]*")

# a pipe row is "| a | b |"; a header row followed by a separator row "|---|:---:|" starts a table
TABLE_ROW = re.compile(r"[ \t]*\|.*\|[ \t\r]*")
TABLE_SEP = re.compile(r"[ \t]*\|[ \t]*:?-+:?[ \t]*(?:\|[ \t]*:?-+:?[ \t]*)*\|?[ \t\r]*")
CELL_BREAK = re.compile(r"(?<!\\)\|")


def cells(line):
    """The cell texts of one pipe row, outer pipes dropped; a backslash-escaped pipe is a literal pipe."""
    row = line.strip()
    row = row[1:] if row.startswith("|") else row
    row = row[:-1] if row.endswith("|") and not row.endswith("\\|") else row
    return [c.replace("\\|", "|").strip() for c in CELL_BREAK.split(row)]


def table(header, rows):
    """A header row and its body rows as a table; every row is padded or cut to the header's width."""
    head = cells(header)
    width = len(head)

    def tr(tag, row, attrs=""):
        row = (row + [""] * width)[:width]
        return "<tr>" + "".join(f"<{tag}{attrs}>{inline(c)}</{tag}>" for c in row) + "</tr>"

    out = ["<table>", "<thead>", tr("th", head, ' scope="col"'), "</thead>"]
    if rows:
        out += ["<tbody>", *(tr("td", cells(r)) for r in rows), "</tbody>"]
    out.append("</table>")
    return "\n".join(out)


def blocks(text):
    """A chunk body as HTML: runs of '- ' lines become ul/li, runs of '1. ' lines ol/li (a run that starts at another
    number, such as steps resumed after a bullet list, carries it as start), pipe tables table, the rest paragraphs."""
    out, para, items = [], [], []
    list_tag = "ul"
    start = 1

    def flush_para():
        body = "\n".join(para).strip()
        if body:
            out.append(f"<p>{inline(body)}</p>")
        para.clear()

    def flush_items():
        if items:
            lis = "\n".join(f"<li>{inline(i)}</li>" for i in items)
            opening = f'<ol start="{start}">' if list_tag == "ol" and start != 1 else f"<{list_tag}>"
            out.append(f"{opening}\n{lis}\n</{list_tag}>")
            items.clear()

    lines = text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        if TABLE_ROW.fullmatch(line) and i + 1 < len(lines) and TABLE_SEP.fullmatch(lines[i + 1]):
            flush_para()
            flush_items()
            j = i + 2
            while j < len(lines) and TABLE_ROW.fullmatch(lines[j]):
                j += 1
            out.append(table(line, lines[i + 2:j]))
            i = j
            continue
        m, kind = LIST_ITEM.fullmatch(line), "ul"
        if not m:
            m, kind = ORDERED_ITEM.fullmatch(line), "ol"
        if m:
            flush_para()
            if kind != list_tag:
                flush_items()
                list_tag = kind
            if kind == "ol" and not items:
                start = int(m.group(1))
            items.append(m.group(m.lastindex))
        else:
            flush_items()
            para.append(line)
        i += 1
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
    """Chunks in order as HTML: a chunk's label becomes an h2 of its section name only (once for consecutive chunks
    sharing the label); a title-only label, with no ' > ', is the page's h1 already and gets no heading."""
    out, last = [], None
    for content in chunks:
        m = LABEL.match(content)
        if m:
            label, text = m.group(1).strip(), m.group(2)
            if label != last and " > " in label:
                out.append(f"<h2>{inline(label.split(' > ')[-1].strip())}</h2>")
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
