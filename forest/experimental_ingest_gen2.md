# EXPERIMENTAL Ingest (gen 2)

## Capabilities
All CLASSIC capabilities, plus:
- Ingest .docx files (Word 2007+ Open XML format)
- Extract plain text from .docx: body, headers, footers
- Map Word XML elements: `<w:t>` → text, `<w:tab/>` → `\t`, `<w:br/>` → `\n`, `<w:p>` → `\n\n`
- Title from filename stem (titlecased, hyphens/underscores → spaces) for .docx
- No frontmatter support for .docx (requires `--source` and `--default-scope`)

## Behaviour Changes
- Extensions: `.md`, `.txt`, `.docx`
- Directories: recursively glob `*.md`, `*.txt`, `*.docx`
- .docx files:
  - Unzipped in memory (stdlib zipfile)
  - Parsed with xml.etree.ElementTree (no third-party deps)
  - Text fed to existing chunk.split() pipeline
  - Always marked pretagged=False (classifier runs unless scopes explicit in chunks)
- .md/.txt behaviour unchanged (CLASSIC preserved)

## Evaluation Metrics
- .docx files successfully ingested: count (target: >0 from samples/)
- .docx extraction failures: count (target: 0 for valid files)
- Chunks from .docx: mean per document
- Text fidelity: manual spot-check that paragraphs, tabs, breaks preserved
- Existing .md/.txt tests: all green (no regressions)

## Integration Points
- `ingest/chunk.py`: load() now branches on `.docx` suffix
- `ingest/run.py`, `ingest/run_sf.py`: glob pattern includes `.docx`
- `ingest/docx.py`: new module, extract_text() function
- Tests: `ingest/test_docx.py` (unit), `ingest/test_chunk_docx.py` (integration)

## Risks
- .doc (binary) files will fail with zipfile.BadZipFile (not supported, .docx only)
- Malformed .docx (missing document.xml) raises KeyError (caught by ingest runner, prints FAIL)
- Large .docx files load entirely into memory (acceptable for document ingest workload)
