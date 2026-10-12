# CLASSIC Ingest (gen 1)

## Capabilities
- Ingest .md and .txt files from disk
- Parse YAML frontmatter for title, source, scope metadata
- Chunk on Markdown headings, split long sections on paragraphs (MAX_WORDS=300)
- Scope markers: `<!-- scope: <name> -->` under headings
- Classify untagged documents with LLM if no frontmatter scope
- Summarize per scope, generate digests per topic+scope
- Embed chunks, summaries, digests (Voyage, OpenAI, or local fallback)
- Store to Postgres or Snowflake
- Parallel processing (8 workers default)

## Behaviour
- Extensions: `.md`, `.txt` only
- Directories: recursively glob `*.md` and `*.txt`
- Frontmatter required for source/scope unless `--source` and `--default-scope` provided
- Re-ingesting same (source, title) replaces document atomically
- One failed file does not halt batch (prints FAIL, continues)

## Evaluation
- Files ingested: count
- Chunks per document: mean, max
- Scopes per document: set
- Failures: count, reasons
- Digests generated: count (topic, scope) pairs
