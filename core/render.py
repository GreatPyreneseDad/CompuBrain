"""Profile-shaped answer. The model sees only what the gate returned."""
from __future__ import annotations
import json, re
import anthropic
from config import ANSWER_MODEL

_client = None
def client():
    global _client
    _client = _client or anthropic.Anthropic(max_retries=4)
    return _client

SYSTEM = """You answer questions for one person or agent inside a company, from the numbered sources given \
and nothing else. The sources are everything this asker is permitted to see.

Rules
- Use only the sources. No outside knowledge, no guessing at what other documents might say.
- Cite every factual sentence with its source numbers, like [2] or [1][4].
- If the sources disagree on a fact, do not pick one and do not average. State each value with its source. \
List each such disagreement in "conflicts".
- If the sources do not answer the question, set "answerable" to false and leave "answer" empty. A source that \
only says where to ask is not an answer.
- If the sources answer part of the question, answer that part and say plainly which part they do not cover.

Shape for this asker
{shape}

Reply with one JSON object and nothing else:
{{"answerable": true | false,
  "answer": {answer_type},
  "citations": [source numbers actually used],
  "conflicts": [{{"fact": "...", "values": [{{"value": "...", "source": n}}]}}]}}"""

def _shape(profile: dict) -> tuple:
    lines = [f"- Hard limit: {profile.get('max_words', 150)} words. Count them. Cut the least important fact rather than run over."]
    if profile.get("define_terms"):
        lines.append("- The reader is new. Plain words; spell out any term or acronym the first time.")
    else:
        lines.append("- The reader knows the business. No definitions, no preamble.")
    if profile.get("surface_conflicts"):
        lines.append("- Lead with the answer in two sentences. Then every disagreement between sources, with both "
                     "citations. Then one or two sentences from each other source document that bears on the "
                     "question: its financial treatment, recent decisions or cases, open reviews. Breadth across "
                     "documents matters more than depth in one; do not restate procedure the reader already knows.")
    else:
        lines.append("- Give the answer and who to go to. Mention a disagreement only if it is in the sources.")
    if profile.get("format") == "json":
        lines.append("- The reader is an automated agent that relays text to a customer. \"answer\" is an object: "
                     "{\"customer_text\": text safe to send to the customer verbatim, \"next_step\": what the agent "
                     "should do, \"unknown\": things asked that the sources do not contain}. No [n] markers inside the object; "
                     "list the sources in \"citations\" only. Never name an internal "
                     "person unless a source names them.")
        return "\n".join(lines), "{...the object described above...}"
    lines.append("- Prose. No headings.")
    return "\n".join(lines), '"the answer text with [n] citations"'

def render(principal, question: str, hits: list, summaries: list, digests: list) -> dict:
    shape, answer_type = _shape(principal.profile)
    parts = [f"[{i}] {h.title} ({h.source})\n{h.content}" for i, h in enumerate(hits, 1)]
    if principal.profile.get("grain") == "summary" and summaries:
        parts.append("Background summaries (cite the numbered sources above, not these):\n" +
                     "\n".join(f"- {s[1]}: {s[3]}" for s in summaries))
    msg = client().messages.create(
        model=ANSWER_MODEL, max_tokens=2500,
        system=SYSTEM.format(shape=shape, answer_type=answer_type),
        messages=[{"role": "user", "content": "Sources:\n\n" + "\n\n".join(parts) + f"\n\nQuestion: {question}"}])
    text = "".join(b.text for b in msg.content if b.type == "text")
    m = re.search(r"\{.*\}", text, re.S)
    try:
        out = json.loads(m.group(0))
    except Exception:
        out = {"answerable": bool(text.strip()), "answer": text.strip(), "citations": [], "conflicts": []}
    out["citations"] = [n for n in out.get("citations", []) if isinstance(n, int) and 1 <= n <= len(hits)]
    out.setdefault("conflicts", [])
    out["tokens_in"], out["tokens_out"] = msg.usage.input_tokens, msg.usage.output_tokens
    return out
