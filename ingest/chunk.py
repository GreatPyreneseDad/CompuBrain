"""File in, chunks out. Splits on Markdown headings; a long section splits again on paragraphs.

A section can carry its own scope with a marker line directly under its heading:
    ## Compensation bands
    <!-- scope: people -->
The marker covers that section only. Everything else takes the document's default scope.

Other file types are plug-in readers: a module ingest/<format>.py that declares the extensions it reads,
    EXTENSIONS = (".docx",)
and exposes extract_text(path) -> str. load() finds it by that declaration, so adding a reader is one new file
and no edit here. .docx and .rtf are readers of this kind.
"""
from __future__ import annotations
import ast, importlib, re, pathlib
from dataclasses import dataclass

MAX_WORDS = 300

PLAIN = {".md", ".txt"}

def _discover() -> dict:
    """extension → reader module name, read statically from each ingest/*.py's top-level EXTENSIONS.
    Nothing is imported here: a reader loads only when a file of its type does."""
    found = {}
    for f in sorted(pathlib.Path(__file__).parent.glob("*.py")):
        if f.name.startswith(("test_", "_")) or f.stem == "chunk":
            continue
        try:
            tree = ast.parse(f.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            continue
        for node in tree.body:
            if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "EXTENSIONS" for t in node.targets):
                try:
                    exts = ast.literal_eval(node.value)
                except ValueError:
                    continue
                for e in ([exts] if isinstance(exts, str) else exts):
                    if isinstance(e, str) and e.startswith(".") and e.lower() not in PLAIN:
                        found.setdefault(e.lower(), f.stem)
    return found

_PLUGINS = _discover()

# File types the brain can read: plain text plus every plug-in reader. Callers test `suffix.lower() in READERS`.
# Anything else raises UnsupportedFormat, which is how the brain learns it is missing a tool.
READERS = PLAIN | set(_PLUGINS)

class UnsupportedFormat(ValueError):
    pass
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
    """Load and chunk a document: .md/.txt (with optional frontmatter) or any plug-in reader's type."""
    path = pathlib.Path(path)
    if path.suffix.lower() not in READERS:
        raise UnsupportedFormat(f"{path.name}: no reader for {path.suffix or 'this file type'}")

    ext = path.suffix.lower()          # routing is case-insensitive: REPORT.DOCX is a .docx
    if ext in _PLUGINS:
        reader = importlib.import_module(f"ingest.{_PLUGINS[ext]}")
        if not source or not default_scope:
            raise ValueError(f"{path.name}: {ext} files require --source and --default-scope")
        text = _headings_from_plain(reader.extract_text(path))
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
        import yaml  # lazy import: not needed for .docx/.rtf path
        _, front, text = text.split("---", 2)
        meta = yaml.safe_load(front) or {}
    scope = meta.get("scope") or default_scope
    if not scope:
        raise ValueError(f"{path.name}: no scope in frontmatter and no --default-scope given")
    return Doc(title=str(meta.get("title") or path.stem.replace("-", " ").title()),
               source=str(meta.get("source") or source or "upload"),
               default_scope=scope, pretagged="scope" in meta, chunks=split(text))

def _headings_from_plain(text: str) -> str:
    """Plain text from Word or RTF has no Markdown. Treat a short line with no closing punctuation,
    followed by body text, as a section heading, so the document splits (and is scope-tagged) by
    section. The body may follow after a blank line or on the very next line."""
    def looks_like_heading(line: str) -> bool:
        return 0 < len(line) <= 70 and not line.endswith((".", ":", ";", ",", "?", "!"))
    def has_own_body(p: str) -> bool:
        head, _, rest = p.partition("\n")
        return bool(rest.strip()) and looks_like_heading(head.strip())
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    out, first, bodyless = [], True, False       # bodyless: the last heading emitted still waits for its body
    for i, p in enumerate(paras):
        head, _, rest = p.partition("\n")
        if has_own_body(p):                                              # heading with its body right under it
            out.append(("# " if first else "## ") + head.strip()); out.append(rest.strip())
            bodyless = False
        elif ("\n" not in p and looks_like_heading(p) and not bodyless
              and i + 1 < len(paras) and not has_own_body(paras[i + 1])):
            out.append(("# " if first else "## ") + p)                   # next paragraph will be its body
            bodyless = True
        else:
            out.append(p)                                                # body text, never dropped
            bodyless = False
        first = False
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
