# Classic Ingest (Gen 1)

## Capabilities

- Reads `.md` and `.txt` files with optional YAML frontmatter
- Chunks on Markdown headings (max 300 words per chunk)
- Supports explicit scope markers: `<!-- scope: <scope> -->`
- Auto-tags chunks without explicit scope via LLM classifier
- Generates summaries and digests per document
- Computes embeddings for vector retrieval (Voyage, OpenAI, or lexical fallback)

## Behaviour

- Frontmatter `scope:` field pre-tags entire document (skips classifier)
- Heading hierarchy becomes chunk breadcrumb trail: `[Section > Subsection]`
- Long sections split on paragraph boundaries
- Upload-only: no crawlers, no network calls during chunk processing

## Evaluation

- Metrics: chunk count, scope distribution, embedding dimensions (measured)
- Quality: manual review of chunking and scope assignment (no automated metric)
