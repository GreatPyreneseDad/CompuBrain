"""token -> principal -> scopes -> tiered retrieval under the gate -> render by profile -> ledger.

  python -m core.ask --as maya "What's our refund policy on enterprise contracts, and who approves exceptions?"
"""
from __future__ import annotations
import sys, json, time, argparse
from core import identity, retrieve, render, ledger

ROUTING = {
    "people":  "Comp questions go to your manager or People Ops.",
    "finance": "Ask the Finance team.",
    "legal":   "Ask the Office of General Counsel.",
    "exec":    "Ask your department head.",
    "sales":   "Ask the account team.",
    "support": "Ask the Support team.",
    "internal": "This is internal to employees.",
}
DEMO_TOKENS = {"maya": "demo-maya", "dana": "demo-dana", "svc-support-bot": "demo-support-bot"}

def ask(token: str, question: str) -> dict:
    t0 = time.time()
    p = identity.resolve(token)
    if p is None:
        return {"outcome": "unauthorized", "answer": "Unknown token."}
    q = retrieve.qvec(question)
    hits, summaries, digests = retrieve.retrieve(p, question, q)
    denied = retrieve.denied_scopes(p, q)
    out = render.render(p, question, hits, summaries, digests) if hits else {"answerable": False}
    cited = [hits[n - 1] for n in out.get("citations", [])]

    if out.get("answerable"):
        outcome, answer = "answered", out["answer"]
    elif denied:
        outcome, cited = "refused", []
        answer = f"That's outside your scope. {ROUTING.get(denied[0][0], '')}".strip()
    else:
        outcome, cited, answer = "empty", [], "I don't have anything on that."

    denied_names = [s for s, _ in denied]
    ledger.write(p, question, outcome, denied_names, cited, answer, out.get("tokens_in", 0), out.get("tokens_out", 0))
    sources, seen = [], set()
    for n in out.get("citations", []) if outcome == "answered" else []:
        h = hits[n - 1]
        sources.append({"n": n, "title": h.title, "source": h.source, "scope": h.scope})
    return {"asker": p.handle, "kind": p.kind, "role": p.role_id, "scopes": list(p.scopes),
            "outcome": outcome, "answer": answer, "sources": sources,
            "conflicts": out.get("conflicts", []) if outcome == "answered" else [],
            "denied_scopes": denied_names, "chunks_retrieved": len(hits),
            "seconds": round(time.time() - t0, 1)}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--as", dest="who", default="maya", choices=sorted(DEMO_TOKENS))
    ap.add_argument("question")
    a = ap.parse_args()
    print(json.dumps(ask(DEMO_TOKENS[a.who], a.question), indent=2))

if __name__ == "__main__":
    main()
