"""File in, chunks out. Splits on Markdown headings; a long section splits again on paragraphs.

A section can carry its own scope with a marker line directly under its heading:
    ## Compensation bands
    <!-- scope: people -->
The marker covers that section only. Everything else takes the document's default scope.

EXPERIMENTAL: .docx files are supported. Text is extracted via ingest.docx.extract_text() and
then processed like plain text.
"""
from __future__ import annotations
import re, pathlib
from dataclasses import dataclass

MAX_WORDS = 300
MARKER = re.compile(r"^\s*<!--\s*scope:\s*([a-z]+)\s*-->\s*$", re.M)
HEADING = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")

@dataclass
class Chunk:
    ord: int
    content: str
    scope: str | None = None      # explicit marker, else None until tag.py fills it
    explicit: bool = False

@dataclass
class Doc:
    title: str
    source: str
    default_scope: str
    pretagged: bool               # frontmatter carried a scope: trust it, skip the classifier
    chunks: list

def load(path, source=None, default_scope=None) -> Doc:
    """Load and chunk a document from .md, .txt, or .docx.
    
    CLASSIC: .md and .txt only
    EXPERIMENTAL: also .docx (extracts text, no frontmatter support)
    """
    path = pathlib.Path(path)
    
    # EXPERIMENTAL: handle .docx
    if path.suffix == '.docx':
        from ingest.docx import extract_text
        text = _headings_from_plain(extract_text(path))
        if not source or not default_scope:
            raise ValueError(f"{path.name}: .docx files require --source and --default-scope")
        return Doc(
            title=path.stem.replace("-", " ").replace("_", " ").title(),
            source=source,
            default_scope=default_scope,
            pretagged=False,
            chunks=split(text)
        )
    
    # CLASSIC: .md and .txt with optional frontmatter
    text = path.read_text(encoding="utf-8", errors="replace")
    meta = {}
    if text.startswith("---"):
        import yaml  # lazy import: not needed for .docx path
        _, front, text = text.split("---", 2)
        meta = yaml.safe_load(front) or {}
    scope = meta.get("scope") or default_scope
    if not scope:
        raise ValueError(f"{path.name}: no scope in frontmatter and no --default-scope given")
    return Doc(title=str(meta.get("title") or path.stem.replace("-", " ").title()),
               source=str(meta.get("source") or source or "upload"),
               default_scope=scope, pretagged="scope" in meta, chunks=split(text))

def _headings_from_plain(text: str) -> str:
    """Word text has no Markdown. Treat a short line with no closing punctuation, followed by a
    paragraph, as a section heading, so a Word document splits (and is scope-tagged) by section."""
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    out = []
    for i, p in enumerate(paras):
        is_heading = (len(p) <= 70 and "\n" not in p and not p.endswith((".", ":", ";", ",", "?", "!"))
                      and i + 1 < len(paras))
        out.append(("# " if i == 0 else "## ") + p if is_heading else p)
    return "\n\n".join(out)

def split(text: str) -> list:
    sections, path, body = [], [], []          # path = heading trail, body = lines of current section

    def flush():
        raw = "\n".join(body).strip()
        if raw:
            sections.append((" > ".join(path), raw))
        body.clear()

    for line in text.splitlines():
        m = HEADING.match(line)
        if m:
            flush()
            level = len(m.group(1))
            del path[level - 1:]
            path.extend([""] * (level - 1 - len(path)))
            path.append(m.group(2))
        else:
            body.append(line)
    flush()

    chunks = []
    for trail, raw in sections:
        trail = " > ".join(p for p in trail.split(" > ") if p)
        marker = MARKER.search(raw)
        raw = MARKER.sub("", raw).strip()
        if not raw:
            continue
        for piece in _pack(raw):
            content = f"[{trail}]\n{piece}" if trail else piece
            chunks.append(Chunk(len(chunks), content, marker.group(1) if marker else None, bool(marker)))
    return chunks

def _pack(raw: str) -> list:
    """Greedy-pack paragraphs up to MAX_WORDS. A single oversized paragraph stays whole."""
    out, cur, n = [], [], 0
    for para in re.split(r"\n\s*\n", raw):
        w = len(para.split())
        if cur and n + w > MAX_WORDS:
            out.append("\n\n".join(cur)); cur, n = [], 0
        cur.append(para.strip()); n += w
    if cur:
        out.append("\n\n".join(cur))
    return out
