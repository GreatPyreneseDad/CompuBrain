"""Text in, 1024-dim vectors out. One function so the provider is swappable.

Provider is picked from the environment:
  VOYAGE_API_KEY  -> voyage-3
  OPENAI_API_KEY  -> text-embedding-3-small with dimensions=1024
  neither         -> local hashed bag-of-words. Lexical only: good enough to exercise the
                     pipeline and the gate, not good enough for the demo. Prints a warning.
Force one with BRAIN_EMBED=voyage|openai|local.
"""
from __future__ import annotations
import os, sys, re, json, math, hashlib, urllib.request
from config import EMBED_DIM

def provider() -> str:
    forced = os.environ.get("BRAIN_EMBED")
    if forced:
        return forced
    if os.environ.get("VOYAGE_API_KEY"):
        return "voyage"
    if os.environ.get("OPENAI_API_KEY"):
        return "openai"
    return "local"

def embed(texts: list, kind: str = "document") -> list:
    """kind is 'document' at ingest and 'query' at ask time."""
    p = provider()
    if p == "local":
        _warn()
        return [_local(t) for t in texts]
    out = []
    for i in range(0, len(texts), 64):
        batch = texts[i:i + 64]
        out.extend(_voyage(batch, kind) if p == "voyage" else _openai(batch))
    return out

def _post(url, key, payload):
    req = urllib.request.Request(url, json.dumps(payload).encode(),
                                 {"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)

def _voyage(batch, kind):
    res = _post("https://api.voyageai.com/v1/embeddings", os.environ["VOYAGE_API_KEY"],
                {"model": "voyage-3", "input": batch, "input_type": kind})
    return [d["embedding"] for d in sorted(res["data"], key=lambda d: d["index"])]

def _openai(batch):
    res = _post("https://api.openai.com/v1/embeddings", os.environ["OPENAI_API_KEY"],
                {"model": "text-embedding-3-small", "input": batch, "dimensions": EMBED_DIM})
    return [d["embedding"] for d in sorted(res["data"], key=lambda d: d["index"])]

_warned = False
def _warn():
    global _warned
    if not _warned:
        print("embed: no VOYAGE_API_KEY or OPENAI_API_KEY; using local lexical vectors (dev only)", file=sys.stderr)
        _warned = True

_STOP = set("a an and are as at be by for from has have in is it its of on or that the this to was were will with".split())

def _local(text: str) -> list:
    words = [w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in _STOP]
    words = [w[:-1] if w.endswith("s") and len(w) > 3 else w for w in words]
    vec = [0.0] * EMBED_DIM
    for tok in words + [a + "_" + b for a, b in zip(words, words[1:])]:
        h = int.from_bytes(hashlib.md5(tok.encode()).digest()[:8], "big")
        vec[h % EMBED_DIM] += 1.0 if (h >> 40) & 1 else -1.0
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]
