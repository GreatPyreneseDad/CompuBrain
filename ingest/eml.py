"""Extract plain text from .eml email messages.

The text starts with the subject on its own line (chunk.py turns it into a section heading), then the From, To and
Date lines, then the body. The body is the text/plain part when there is one; an HTML-only message is converted
to text. Attachments are never read, so no MIME headers, boundaries or encoded bytes reach the output.
Standard library only (email and html.parser).
"""
from __future__ import annotations

EXTENSIONS = (".eml",)
import re
from email import policy
from email.parser import BytesParser
from html.parser import HTMLParser
from pathlib import Path

_SKIP = {"script", "style", "head"}
_BREAK = {"br", "li", "tr"}
_BLOCK = {"p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "table", "ul", "ol", "blockquote", "pre"}


class _HTMLText(HTMLParser):
    """HTML to text: tags dropped, entities decoded, script/style/head skipped, block tags become line breaks."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in _SKIP:
            self._skip += 1
        elif tag in _BREAK:
            self.parts.append("\n")
        elif tag in _BLOCK:
            self.parts.append("\n\n")

    def handle_startendtag(self, tag, attrs):
        if tag in _BREAK:
            self.parts.append("\n")
        elif tag in _BLOCK:
            self.parts.append("\n\n")

    def handle_endtag(self, tag):
        if tag in _SKIP:
            self._skip = max(0, self._skip - 1)
        elif tag in _BLOCK:
            self.parts.append("\n\n")

    def handle_data(self, data):
        if not self._skip:
            self.parts.append(re.sub(r"\s+", " ", data))


def _tidy(text: str) -> str:
    """Strip each line, collapse runs of spaces, and keep at most one blank line between paragraphs."""
    lines = [" ".join(line.split()) if line.strip() else "" for line in text.replace("\r\n", "\n").split("\n")]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def _html_to_text(html: str) -> str:
    parser = _HTMLText()
    parser.feed(html)
    parser.close()
    return _tidy("".join(parser.parts))


def _part_text(part) -> str:
    try:
        return part.get_content()
    except (LookupError, UnicodeDecodeError):
        payload = part.get_payload(decode=True) or b""
        return payload.decode("utf-8", errors="replace")


def _body(msg) -> str:
    part = msg.get_body(preferencelist=("plain", "html"))
    if part is None:
        return ""
    text = _part_text(part)
    if part.get_content_subtype() == "html":
        return _html_to_text(text)
    return _tidy(text)


def _header(msg, name: str) -> str:
    value = msg[name]
    return " ".join(str(value).split()) if value is not None else ""


def extract_text(eml_path: str | Path) -> str:
    """Extract subject, sender, recipients, date and plain-text body from an .eml file."""
    with open(eml_path, "rb") as f:
        msg = BytesParser(policy=policy.default).parse(f)
    lines = [_header(msg, "Subject") or "(no subject)"]
    for label in ("From", "To", "Date"):
        value = _header(msg, label)
        if value:
            lines.append(f"{label}: {value}")
    head = "\n".join(lines)
    body = _body(msg)
    return head + "\n\n" + body if body else head
