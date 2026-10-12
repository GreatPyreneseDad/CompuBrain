"""Model and store settings. One place to change them."""
import os

INGEST_MODEL = os.environ.get("BRAIN_INGEST_MODEL", "claude-haiku-5-5")    # bulk: tagging, summaries, digests
ANSWER_MODEL = os.environ.get("BRAIN_ANSWER_MODEL", "claude-sonnet-5-5")   # /ask rendering
EMBED_DIM = 1024
DATABASE_URL = os.environ.get("DATABASE_URL", "")
SCOPES = ["public", "internal", "sales", "support", "finance", "legal", "people", "exec"]
