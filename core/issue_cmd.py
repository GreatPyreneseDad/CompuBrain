"""`/brain ask as:<asker> <question>` in an issue comment -> the answer as a reply, through the gate.

Run by .github/workflows/brain-ask.yml. Reads the triggering event from GITHUB_EVENT_PATH.
In this demo any collaborator may ask as any demo asker; a deployment maps the GitHub login to
one principal instead.
"""
from __future__ import annotations
import os, re, json
from core.ask import ask, DEMO_TOKENS
from core.gh import GitHub

ALLOWED = {"OWNER", "MEMBER", "COLLABORATOR"}
USAGE = ("Usage: `/brain ask as:maya <question>` · askers: " + ", ".join(f"`{h}`" for h in sorted(DEMO_TOKENS)))

def format_reply(r: dict) -> str:
    if r["outcome"] != "answered":
        body = f"**{r['outcome'].upper()}** · {r['answer']}"
    elif isinstance(r["answer"], dict):
        body = "```json\n" + json.dumps(r["answer"], indent=2) + "\n```"
    else:
        body = r["answer"]
    lines = [f"**Asked as `{r['asker']}`** ({r['role']}; scopes: {', '.join(r['scopes'])})", "", body]
    for c in r.get("conflicts", []):
        vals = " vs ".join(sorted({v["value"] for v in c["values"]}))
        lines += ["", f"> **Sources disagree: {c['fact']}.** {vals}"]
    seen = []
    for s in r.get("sources", []):
        if s["title"] not in [t for _, t, _ in seen]:
            seen.append((s["n"], s["title"], s["scope"]))
    if seen:
        lines += ["", "<sub>Sources: " + " · ".join(f"[{n}] {t} (`{sc}`)" for n, t, sc in seen) + "</sub>"]
    if r.get("denied_scopes"):
        lines += ["", f"<sub>Related material exists in scopes this asker does not hold: {', '.join(r['denied_scopes'])}. "
                      "The model never saw it.</sub>"]
    return "\n".join(lines)

def main():
    event = json.load(open(os.environ["GITHUB_EVENT_PATH"]))
    comment, number = event["comment"], event["issue"]["number"]
    gh = GitHub()
    if comment.get("author_association") not in ALLOWED:
        return
    m = re.search(r"/brain\s+ask\s+as:(\S+)\s+(.+)", comment["body"], re.S)
    if not m or m.group(1) not in DEMO_TOKENS:
        gh.comment(number, USAGE); return
    gh.comment(number, format_reply(ask(DEMO_TOKENS[m.group(1)], m.group(2).strip())))

if __name__ == "__main__":
    main()
