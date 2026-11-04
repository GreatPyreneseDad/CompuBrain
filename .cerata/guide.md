# Host rules for consuming into CompuBrain

This repo is a company knowledge brain. Most consumes here add a **reader**: a way to turn one more
file type into plain text so the ingest pipeline can chunk and scope-tag it.

## Adding a reader for a file type

1. Put the extraction code in one new module under `ingest/`, exposing one function
   `extract_text(path) -> str` and declaring, at top level, the extensions it reads:
   `EXTENSIONS = (".xlsx",)` (lower case, with the dot). Standard library only. No new dependencies.
   Name the module after the format but not after a standard-library module (`xlsx.py`, `pptx.py`,
   `htmlpage.py`, `csvfile.py`, `eml.py` — not `html.py`, `csv.py` or `email.py`).
2. Do **not** edit `ingest/chunk.py`. It finds readers by their `EXTENSIONS` declaration (a static scan,
   nothing imported until a file of that type loads), adds them to `READERS`, routes extensions
   case-insensitively, requires `source` and `default_scope`, passes the text through
   `_headings_from_plain`, and sets `pretagged=False`. Each reader is one file, so parallel builders
   never touch the same line. `ingest/docx.py` is the example.
3. Do not edit `ingest/run.py`, `ingest/run_sf.py`, `core/`, `api/`, `sf/` or `ui/`. They pick up
   new readers from `READERS` on their own.
4. Tests go in `ingest/test_<format>.py` and build their sample input in the test itself.
   Do not add sample files, and never add a placeholder standing in for a binary file.
5. Put the upstream licence in `ingest/LICENSE-<project>`.

## Never

- Never weaken or bypass anything under `sf/`, `core/gate.py` or the scope tagging in `ingest/tag.py`.
- Never read environment variables or make network calls from a reader.
