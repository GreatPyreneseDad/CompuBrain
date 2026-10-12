# Host rules for consuming into CompuBrain

This repo is a company knowledge brain. Most consumes here add a **reader**: a way to turn one more
file type into plain text so the ingest pipeline can chunk and scope-tag it.

## Adding a reader for a file type

1. Put the extraction code in one new module, `ingest/<format>.py`, exposing one function
   `extract_text(path) -> str`. Standard library only. No new dependencies.
2. In `ingest/chunk.py`:
   - add the extension, lower case with the dot, to the `READERS` set;
   - in `load()`, add a branch for that extension next to the `.docx` branch and shaped like it:
     call `extract_text`, pass the text through `_headings_from_plain`, require `source` and
     `default_scope`, derive the title from the file name, set `pretagged=False`.
3. Do not edit `ingest/run.py`, `ingest/run_sf.py`, `core/`, `api/`, `sf/` or `ui/`. They pick up
   new readers from `READERS` on their own.
4. Tests go in `ingest/test_<format>.py` and build their sample input in the test itself.
   Do not add sample files, and never add a placeholder standing in for a binary file.
5. Put the upstream licence in `ingest/LICENSE-<project>`.

## Never

- Never weaken or bypass anything under `sf/`, `core/gate.py` or the scope tagging in `ingest/tag.py`.
- Never read environment variables or make network calls from a reader.
