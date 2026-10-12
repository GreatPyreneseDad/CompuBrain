# Experimental Ingest (Gen 2)

## Capabilities (extends Gen 1)

- Reads `.docx` files (Office Open XML): extracts text from headers, body, and footers
- Reads `.rtf` files: converts RTF markup to plain text with charset handling
- Both formats infer section structure via `_headings_from_plain()`: short lines without terminal punctuation become headings
- Scope tagging works identically to `.md`/`.txt` (classifier runs, no frontmatter)

## Behaviour changes from Classic

- `.docx` and `.rtf` require `--source` and `--default-scope` (no frontmatter support)
- File type detection: suffix-based (`.docx`, `.rtf` in `READERS` set)
- Title derived from filename stem (dashes/underscores → spaces → title case)
- Binary formats handled via stdlib only (no new dependencies)

## Evaluation

- Target: RTF order forms from `inbox/` chunk and tag correctly (manual inspection)
- Target: `.docx` and `.rtf` produce comparable chunk counts to equivalent `.md` (measured per document)
- Regression: existing `.md`/`.txt` behaviour unchanged (asserted by `test_chunk_docx.py` staying green)
