"""Extract plain text from .html files with the standard library's html.parser.

Headings and paragraphs become separate blocks of text, entities are decoded, and the content of
script and style elements is dropped. Blocks are separated by blank lines so that chunk.py's
heading detection can section the page the way it does for .docx and .rtf.

No third-party code is ported here. Standard library only, no environment or network access.
"""
from __future__ import annotations

EXTENSIONS = (".html",)
from html.parser import HTMLParser
from pathlib import Path

# Elements whose content is not page text.
_SKIP = frozenset(("script", "style", "template", "noscript"))

# Elements that end the current paragraph, on open and on close.
_BLOCKS = frozenset((
    "address", "article", "aside", "blockquote", "body", "br", "caption", "dd", "details", "div", "dl",
    "dt", "fieldset", "figcaption", "figure", "footer", "form", "h1", "h2", "h3", "h4", "h5", "h6",
    "head", "header", "hr", "html", "li", "main", "nav", "ol", "p", "pre", "section", "summary",
    "table", "tbody", "td", "tfoot", "th", "thead", "title", "tr", "ul",
))


class _TextParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)   # &amp;, &#36;, &eacute; ... arrive decoded in handle_data
        self.blocks: list[str] = []
        self._parts: list[str] = []
        self._skip = 0

    def _flush(self) -> None:
        text = " ".join("".join(self._parts).split())
        self._parts.clear()
        if text:
            self.blocks.append(text)

    def handle_starttag(self, tag, attrs):
        if tag in _SKIP:
            self._skip += 1
        elif tag in _BLOCKS:
            self._flush()

    def handle_endtag(self, tag):
        if tag in _SKIP:
            if self._skip:
                self._skip -= 1
        elif tag in _BLOCKS:
            self._flush()

    def handle_data(self, data):
        if not self._skip:
            self._parts.append(data)


def extract_text(html_path: str | Path) -> str:
    """Extract the visible text of an .html file, one paragraph per block, separated by blank lines."""
    raw = Path(html_path).read_bytes()
    try:
        html = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        html = raw.decode("cp1252", errors="replace")
    parser = _TextParser()
    parser.feed(html)
    parser.close()
    parser._flush()
    return "\n\n".join(parser.blocks).strip()
