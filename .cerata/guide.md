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

## The help center (`helpcenter/`)

The customer-facing site. `python -m helpcenter.build --out <dir>` writes it as static files; the API serves
`helpcenter/dist` at `/help/`. The contract is `goals/helpcenter/referee.py`.

- Content comes from `core.gate.query("BRAIN_CUSTOMER", sql)` and nothing else. That role is mapped to the public
  scope only, and the row access policy filters chunk by chunk: a public article can hold an internal section the
  database never returns. **Never read `corpus/`** or any file to get content, never ask as another role, and never
  import `core.retrieve`, `core.ask`, `core.identity` or `sf`.
- Tables you can read: `visible_document` (id, title, source, default_scope, created_at), `chunk` (document_id, ord,
  scope, content), `summary`, `digest`, `document_scope` (columns as in `sf/01_schema.sql`). Plain SQL, `%s` parameters.
- Escape everything that came from the database. Write answers with `textContent`; never `innerHTML`, `outerHTML`,
  `insertAdjacentHTML` or `document.write`.
- Relative links only (the site lives under `/help/`), no external scripts, styles, fonts or images, and the
  same input must give the same bytes (no timestamps, no unordered iteration).
- The ask box posts `{"question": ...}` as JSON to `/ask` with `Authorization: Bearer <token>`, the token being
  `HELPCENTER_TOKEN` at build time (default `helpcenter-public`). It is public by design: it can only reach public rows.
- Standard library only.
