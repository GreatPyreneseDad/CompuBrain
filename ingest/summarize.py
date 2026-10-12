"""T2 summaries and T3 digests. Each is built from one scope's material only, so it inherits that scope."""
from __future__ import annotations
import re
from ingest.llm import ask, ask_json

TOPICS = ["refunds", "pricing", "contracts", "compensation", "hiring", "performance", "benefits",
          "revenue", "budget", "forecasting", "security", "incidents", "support-process",
          "product", "architecture", "onboarding", "sales-process", "strategy", "board", "legal-disputes"]

SUMMARY_SYSTEM = f"""You summarize part of a company document for a retrieval index. Write a summary of at most \
120 words that keeps the specific facts someone would search for: numbers, time limits, named roles and people, \
decisions, and who is responsible for what. No preamble.

Also assign 1 to 3 topics. Prefer these: {", ".join(TOPICS)}. If none fits, invent a short lowercase \
hyphenated topic.

Return {{"summary": "...", "topics": ["..."]}}."""

DIGEST_SYSTEM = """You write a topic digest for a retrieval index from summaries of several company documents. \
At most 180 words. State what each document establishes on this topic and name the document for each claim, \
like (Sales Playbook). If two documents disagree on a fact, say so plainly and give both values with their \
documents; never average or pick one. Leave out material unrelated to the topic. No preamble."""

def summarize(title: str, scope: str, chunks: list) -> tuple:
    body = "\n\n".join(c.content for c in chunks)
    res = ask_json(SUMMARY_SYSTEM, f"Document: {title}\n\n{body}", max_tokens=1000)
    topics = [re.sub(r"[^a-z0-9]+", "-", str(t).lower()).strip("-") for t in res.get("topics", [])][:3]
    return str(res["summary"]).strip(), [t for t in topics if t] or ["general"]

def digest(topic: str, items: list) -> str:
    """items: [(title, summary)] all from one scope."""
    if len(items) == 1:
        return f"({items[0][0]}) {items[0][1]}"
    body = "\n\n".join(f"<document title=\"{t}\">\n{s}\n</document>" for t, s in items)
    return ask(DIGEST_SYSTEM, f"Topic: {topic}\n\n{body}", max_tokens=1000)
