"""One call into the ingest model. Thinking is off: these are bulk extraction jobs."""
from __future__ import annotations
import json, re, functools
import anthropic
from config import INGEST_MODEL

@functools.lru_cache(1)
def client():
    return anthropic.Anthropic(max_retries=6)

def ask(system: str, user: str, max_tokens: int = 2000) -> str:
    msg = client().messages.create(
        model=INGEST_MODEL, max_tokens=max_tokens, system=system,
        thinking={"type": "disabled"},
        messages=[{"role": "user", "content": user}])
    if msg.stop_reason == "max_tokens":
        raise RuntimeError("ingest model hit max_tokens; raise the limit for this call")
    return "".join(b.text for b in msg.content if b.type == "text").strip()

def ask_json(system: str, user: str, max_tokens: int = 2000):
    """Ask for JSON and parse it. Tolerates a code fence or prose around the object."""
    text = ask(system + "\n\nReply with JSON only, no prose and no code fence.", user, max_tokens)
    m = re.search(r"[\[{].*[\]}]", text, re.S)
    if not m:
        raise ValueError(f"no JSON in model reply: {text[:200]}")
    return json.loads(m.group(0))
