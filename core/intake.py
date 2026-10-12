"""New company data in, actions out.

  python -m core.intake "Order Form - Halcyon Freight Lines"       # document title, already ingested

For each role, the brain reads only the part of the new document that role may see, pulls related
knowledge through the same gate, and decides what that role now has to do. Each plan becomes a
GitHub issue. A role that can see none of the document gets no issue. Disagreements between
sources become their own issue. Every action is written to the ledger on the role's own session.
"""
from __future__ import annotations
import sys, re
from core import gate, identity, retrieve, render, ledger
from core.gh import GitHub

# The agent principals that act for each team. Tokens are demo values.
AGENTS = [("demo-intake-sales", "sales"), ("demo-intake-exec", "leadership"), ("demo-support-bot", "support")]

SYSTEM = """You are an operations agent acting for one team inside a company. A new document has just arrived. \
You are shown the part of it your team is permitted to see, and numbered sources from the company knowledge \
base, which are everything else your team is permitted to see.

Decide what your team must now do because of this document. Use only the new document and the sources.
- Every task must be concrete, owned by a role, and carry a due date worked out from dates in the document \
and time limits in the sources (state the rule you applied).
- Cite the source number for each task that comes from a company rule. Use 0 for the new document itself.
- If sources disagree with each other or with the new document on a fact, do not pick one. List it in "conflicts".
- If the new document requires nothing of your team, set "actionable" to false.

Always finish by calling the record_plan tool exactly once. Do not answer in prose."""

_VALUE = {"type": "object", "properties": {"value": {"type": "string"}, "source": {"type": "integer"}},
          "required": ["value", "source"]}
PLAN_TOOL = {
    "name": "record_plan",
    "description": "Record what this team must do because of the new document.",
    "input_schema": {"type": "object", "required": ["actionable", "kind", "subject", "title", "summary", "tasks"],
        "properties": {
            "actionable": {"type": "boolean"},
            "kind": {"type": "string", "enum": ["new_client", "policy_change", "incident", "other"]},
            "subject": {"type": "string", "description": "the customer or matter, two to four words"},
            "title": {"type": "string", "description": "issue title, under 70 characters, starting with a verb"},
            "summary": {"type": "string", "description": "two sentences: what arrived and why it matters to this team"},
            "tasks": {"type": "array", "maxItems": 7, "items": {"type": "object", "required": ["task", "owner", "due", "source"],
                "properties": {"task": {"type": "string", "description": "one or two sentences"},
                               "owner": {"type": "string"}, "due": {"type": "string"}, "source": {"type": "integer"}}}},
            "watch": {"type": "array", "maxItems": 4, "items": {"type": "string"}},
            "conflicts": {"type": "array", "items": {"type": "object", "required": ["fact", "values"],
                "properties": {"fact": {"type": "string", "description": "the disputed fact, under 60 characters"},
                               "values": {"type": "array", "items": _VALUE}}}}}}}

def new_doc_chunks(role: str, title: str) -> list:
    """The part of the new document this role can read. Runs on the role's own session."""
    return gate.query(role, """select c.id, c.document_id, c.content from chunk c
        join visible_document d on d.id = c.document_id where d.title = %s order by c.ord""", (title,))

def plan(principal, title: str, team: str):
    mine = new_doc_chunks(principal.sf_role, title)
    if not mine:
        return None, [], []
    brief = "\n\n".join(r[2] for r in mine)
    question = f"What must the {team} team do now that this has arrived? Onboarding steps, deadlines, refund window, obligations.\n{brief[:700]}"
    hits, _, _ = retrieve.retrieve(principal, question)
    hits = [h for h in hits if h.document_id != mine[0][1]]
    sources = "\n\n".join(f"[{i}] {h.title} ({h.source})\n{h.content}" for i, h in enumerate(hits, 1))
    msg = render.client().messages.create(
        model=render.ANSWER_MODEL, max_tokens=6000, system=SYSTEM,
        tools=[PLAN_TOOL],
        messages=[{"role": "user", "content":
                   f"Your team: {team}\n\nNew document [0] \"{title}\" (the part your team may see):\n{brief}\n\nSources:\n\n{sources}"}])
    out = next((b.input for b in msg.content if b.type == "tool_use"), None)
    if out is None:
        raise RuntimeError("the model did not record a plan")
    out.setdefault("watch", []); out.setdefault("conflicts", [])
    out["tokens"] = (msg.usage.input_tokens, msg.usage.output_tokens)
    return out, hits, mine

def issue_body(p, out, hits, title) -> str:
    def src(n):
        if n == 0: return f"new document: {title}"
        return hits[n - 1].title if isinstance(n, int) and 1 <= n <= len(hits) else ""
    lines = [out.get("summary", ""), "", "### Tasks"]
    for t in out.get("tasks", []):
        ref = src(t.get("source"))
        lines.append(f"- [ ] **{t['task']}** · {t.get('owner', '')} · due {t.get('due', '')}" + (f" · _{ref}_" if ref else ""))
    if out.get("watch"):
        lines += ["", "### Watch"] + [f"- {w}" for w in out["watch"]]
    for c in out.get("conflicts", []):
        lines += ["", f"> **Sources disagree: {c['fact']}.** Not resolved here; see the conflict issue."]
    used = sorted({t.get("source") for t in out.get("tasks", []) if isinstance(t.get("source"), int) and t.get("source")})
    if used:
        seen = []
        for n in used:
            if n <= len(hits) and (hits[n - 1].title, hits[n - 1].scope) not in seen:
                seen.append((hits[n - 1].title, hits[n - 1].scope))
        lines += ["", "### Sources"] + [f"- {t} · `{sc}`" for t, sc in seen]
    lines += ["", "---", f"Opened by the Company Brain acting as `{p.handle}` (Snowflake role `{p.sf_role}`, "
              f"scopes: {', '.join(p.scopes)}). It read only what that role may read."]
    return "\n".join(lines)

def conflict_body(p, c, hits, title) -> str:
    def src(n):
        return f"new document: {title}" if n == 0 else (hits[n - 1].title if 1 <= n <= len(hits) else "unknown")
    rows = "\n".join(f"| {v['value']} | {src(v.get('source', -1))} |" for v in c["values"])
    return (f"The brain found sources that disagree while handling **{title}**. It has not picked one.\n\n"
            f"| Value | Document |\n| --- | --- |\n{rows}\n\n"
            f"- [ ] Decide which value is correct\n- [ ] Correct the documents that are wrong\n- [ ] Re-ingest them\n\n"
            f"---\nFound by `{p.handle}` (Snowflake role `{p.sf_role}`). Only roles holding the scopes of these "
            f"documents can see this disagreement at all.")

def run(title: str) -> list:
    gh, opened = GitHub(), []
    for token, team in AGENTS:
        p = identity.resolve(token)
        try:
            out, hits, mine = plan(p, title, team)
        except Exception as e:                       # one team's failure must not stop the others
            print(f"{p.handle}: FAILED {e}"); continue
        if out is None:
            print(f"{p.handle}: cannot see this document; no action"); continue
        if not out.get("actionable"):
            print(f"{p.handle}: nothing to do")
            ledger.write(p, f"intake: {title}", "empty", [], [], "no action", *out["tokens"]); continue
        subject = re.sub(r"[^a-z0-9]+", "-", out.get("subject", "").lower()).strip("-")[:40]
        url = gh.open_issue(f"[{team}] {out['title']}", issue_body(p, out, hits, title),
                            ["brain", f"team:{team}", out.get("kind", "other")] + ([f"subject:{subject}"] if subject else []))
        cited = [hits[t["source"] - 1] for t in out.get("tasks", [])
                 if isinstance(t.get("source"), int) and 1 <= t["source"] <= len(hits)]
        ledger.write(p, f"intake: {title}", "action", [], cited, f"opened issue: {out['title']} {url}", *out["tokens"])
        opened.append(url); print(f"{p.handle}: opened {url}")
        for c in out.get("conflicts", []):
            if len({v["value"] for v in c.get("values", [])}) < 2:
                continue
            curl = gh.open_issue(f"Sources disagree: {c['fact']}"[:120], conflict_body(p, c, hits, title), ["brain", "conflict"])
            ledger.write(p, f"intake: {title}", "action", [], [], f"opened conflict issue: {c['fact']} {curl}")
            opened.append(curl); print(f"{p.handle}: opened conflict {curl}")
    return opened

def title_of(arg: str) -> str:
    """Accept a document title or the path of an ingested file."""
    if arg.endswith((".md", ".txt", ".docx")):
        from ingest import chunk
        return chunk.load(arg, "inbox", "internal").title
    return arg

if __name__ == "__main__":
    for arg in sys.argv[1:]:
        print(f"== {title_of(arg)}")
        run(title_of(arg))
