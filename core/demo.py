"""The four demo beats, asserted.   python -m core.demo"""
from __future__ import annotations
import sys, json
from core.ask import ask, DEMO_TOKENS

Q = "What's our refund policy on enterprise contracts, and who approves exceptions?"
COMP = "What are the comp bands for an L4 engineer?"
failed = 0

def check(label, cond):
    global failed
    failed += 0 if cond else 1
    print(("ok   " if cond else "FAIL ") + label)

def text(r):
    return r["answer"] if isinstance(r["answer"], str) else json.dumps(r["answer"])

def titles(r):
    return {s["title"] for s in r["sources"]}

r = ask(DEMO_TOKENS["maya"], Q); t = text(r); print(f"\n[maya, {r['seconds']}s] {t}\n")
check("maya: answered", r["outcome"] == "answered")
check("maya: 30-day window", "30" in t)
check("maya: names the approver", "Priya Raman" in t)
check("maya: cites handbook and sales playbook", {"Employee Handbook", "Sales Playbook"} <= titles(r))
check("maya: no 45-day memo, no board minutes", "45" not in t and "Meridian" not in t)
check("maya: within length", len(t.split()) <= 150)

r = ask(DEMO_TOKENS["dana"], Q); t = text(r); print(f"\n[dana, {r['seconds']}s] {t}\n")
check("dana: answered", r["outcome"] == "answered")
check("dana: flags 30 vs 45", "30" in t and "45" in t and len(r["conflicts"]) >= 1)
check("dana: revenue-recognition note", "Finance Wiki - Revenue Recognition for Enterprise Contracts" in titles(r))
check("dana: two Q3 exceptions from board minutes", "Meridian" in t and "Castellan" in t
      and "Board Minutes - Q3 2026" in titles(r))
check("dana: cites playbook and legal memo", {"Sales Playbook", "Legal Memo - Refund Terms in the Enterprise MSA"} <= titles(r))

r = ask(DEMO_TOKENS["svc-support-bot"], Q); t = text(r); print(f"\n[bot, {r['seconds']}s] {t}\n")
check("bot: answered as a JSON object", r["outcome"] == "answered" and isinstance(r["answer"], dict))
check("bot: customer-facing policy present", "30 days" in t)
check("bot: approver not leaked", "Priya" not in t and "Raman" not in t)
check("bot: only public and support sources", {s["scope"] for s in r["sources"]} <= {"public", "support"})

r = ask(DEMO_TOKENS["maya"], COMP); t = text(r); print(f"\n[maya comp, {r['seconds']}s] {t}\n")
check("comp: refused", r["outcome"] == "refused")
check("comp: routed", "outside your scope" in t and "People Ops" in t)
check("comp: no figures, no sources", "145" not in t and not r["sources"])
check("comp: denied scope recorded", "people" in r["denied_scopes"])

print(f"\n{'ALL BEATS PASS' if not failed else str(failed) + ' FAILED'}")
sys.exit(1 if failed else 0)
