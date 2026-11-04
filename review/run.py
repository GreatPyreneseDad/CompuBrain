"""Review the help center as customers would, with two models that can see and use the pages, and file what they
both find as a proposal on the network.

    python -m review.run [--dry] [--force] [--work <dir>]

1. The help center goal's referee must be green on this checkout (--force skips): reviewing a half-built site
   only files noise.
2. Build the site from the public rows of corpus/ (review/preview.py) and serve it on localhost with a preview /ask.
3. Argon and Grok each do the same customer tasks in a real browser (desktop and phone) and report issues.
4. Each judges the other's issues against screenshots of every page. An issue is agreed when the other reviewer
   confirms it. Agreed issues of medium or high severity are the result.
5. Unless --dry, or review work is already in flight on the network (an unlaid review proposal, or an open bounty
   under helpcenter/), the result is filed as one proposal, signed by this repo's reviewer pair. The panel turns it
   into bounties with acceptance tests, the same as any proposal.

Writes <work>/report.json, <work>/report.md and <work>/shots/*.png either way.
"""
from __future__ import annotations
import argparse, base64, datetime, json, os, subprocess, sys, tempfile, urllib.request
from pathlib import Path

from review import preview, serve
from review.browse import Browser
from review.models import reviewers

ROOT = Path(__file__).resolve().parents[1]
REPO = os.environ.get("REVIEW_REPO_URL", "https://github.com/GreatPyreneseDad/CompuBrain.git")
PICKS = "https://nnnlitdzggyyboyqismx.supabase.co/functions/v1/picks"
SEVERE = {"high", "medium"}

TASKS = [
    ("desktop", "You are a new Ridgeline customer (Ridgeline is made by Kestrel Ridge). Using this help center, find out how to invite your team to your workspace."),
    ("desktop", "You bought an annual plan three weeks ago and want your money back. Find out whether you can get a refund, "
                "first by browsing, then by asking your question in the ask box on the page."),
    ("phone", "You are on your phone. Find the instructions for setting up single sign-on, and check the pages are comfortable to read and use at this size."),
    ("desktop", "Use this help center the way a customer would: browse, follow links, use the ask box with a question of "
                "your own, try the keyboard (Tab) to move around. Note anything broken, confusing, inaccessible or poorly presented."),
]


NOTE = ("\n\nNote: in this preview the ask box is answered by a simple stand-in (answers start with [preview answer]); the live "
        "site answers with the company's AI under the same access rules. Judge whether the ask box works and how it presents "
        "answers, loading and errors, not how good the stand-in's answer is.")


def log(*a):
    print("review:", *a, flush=True)


def get_json(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"user-agent": "compubrain-review"}), timeout=60) as r:
        return json.loads(r.read())


def referee_green() -> bool:
    r = subprocess.run(["bash", "goals/helpcenter/acceptance.sh"], cwd=ROOT, capture_output=True, text=True, timeout=900)
    log((r.stdout.strip().splitlines() or ["(no output)"])[-1])
    return r.returncode == 0


def page_shots(base: str, site: Path, shots_dir: Path) -> dict:
    shots = {}
    pages = sorted(p.relative_to(site).as_posix() for p in site.rglob("*.html"))[:12]
    for vp in ("desktop", "phone"):
        b = Browser(base, vp)
        try:
            for rel in pages:
                b.act("navigate", {"url": rel})
                png = b.page.screenshot(type="png", full_page=True)
                name = f"{vp}-{rel.replace('/', '_')}"
                (shots_dir / f"{name}.png").write_bytes(png)
                shots[name] = base64.b64encode(png).decode()
        finally:
            b.close()
    return shots


def in_flight() -> str:
    try:
        props = get_json(f"{PICKS}?proposals")
        for p in props:
            if p.get("by", "").endswith("/reviewer") and "compubrain" in p.get("repo_url", "").lower() \
                    and p.get("status") in ("filed", "accepted") and not int(p.get("bounties") or 0):
                return f"review proposal {p['id'][:8]} not laid out yet"
        for r in get_json(f"{PICKS}?json"):
            loc = (r.get("f") or {}).get("location") or {}
            if "compubrain" in str(loc.get("repo", "")).lower() and str(loc.get("path", "")).startswith("helpcenter") and not r.get("judged"):
                return f"bounty {r['id'][:8]} under helpcenter/ still open"
    except Exception as e:
        return f"could not read the board ({e}); not filing blind"
    return ""


def gh(method, path, body=None):
    req = urllib.request.Request(f"https://api.github.com{path}", method=method, data=json.dumps(body).encode() if body else None,
                                 headers={"authorization": f"Bearer {os.environ['GITHUB_TOKEN']}", "accept": "application/vnd.github+json",
                                          "user-agent": "compubrain-review"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read() or b"{}")


def file_proposal(agreed: list, report: dict, doc: str) -> str:
    stamp = report["started"].replace(":", "").replace("-", "")[:13]
    branch, path = f"proposal/helpcenter-review-{stamp}", f"proposals/helpcenter-review-{stamp}.md"
    run = lambda *a: subprocess.run(list(a), cwd=ROOT, check=True, capture_output=True, text=True)
    run("git", "checkout", "-q", "-B", branch)
    (ROOT / path).parent.mkdir(exist_ok=True); (ROOT / path).write_text(doc)
    run("git", "add", path)
    run("git", "-c", "user.name=helpcenter review", "-c", "user.email=review@buildup.network", "commit", "-q", "-m",
        f"proposal: help center review {stamp}\n\nFiled by review/run.py from issues Argon and Grok both found.\n\nBuildup-Proposal: yes\n")
    run("git", "push", "-q", "-f", "origin", f"HEAD:refs/heads/{branch}")
    slug = REPO.split("github.com/")[1].removesuffix(".git")
    title = f"Help center review: {len(agreed)} issue{'s' if len(agreed) != 1 else ''} both reviewers found"
    pr = gh("POST", f"/repos/{slug}/pulls", {"title": f"proposal: {title}", "head": branch, "base": "main",
                                             "body": "Reference only; never merges. Filed by review/run.py: issues Argon and Grok both confirmed. "
                                                     f"Screenshots: {report.get('run_url') or 'see the workflow run'}."})
    base = subprocess.run(["git", "rev-parse", "origin/main"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    desc = f"{len(agreed)} help center issues found and cross-confirmed by Argon and Grok in a browser; details in {path}."
    js = ("import { signJws, post } from " + json.dumps(os.environ["TATEMAE_CLI"]) + "; import { readFileSync } from 'node:fs'; import { randomBytes } from 'node:crypto';"
          "const k = JSON.parse(readFileSync(process.env.TATEMAE_HOME + '/keys.json', 'utf8')); const now = Math.floor(Date.now()/1000);"
          "const a = JSON.parse(process.argv[1]);"
          "const t = signJws({ privateJwk: k.privateJwk, header: { typ: 'buildup-proposal+jwt' }, claims: { ...a, sub: k.pair_id, iat: now, exp: now + 600, jti: randomBytes(8).toString('hex') } });"
          "console.log(JSON.stringify(await post({ type: 'proposal_filed', proposal_token: t })));")
    args = json.dumps({"repo_url": REPO, "title": title, "description": desc, "pr_url": pr.get("html_url"), "base_commit": base})
    r = subprocess.run(["node", "--input-type=module", "-e", js, args], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"proposal_filed failed: {(r.stderr or r.stdout)[-300:]}")
    pid = json.loads(r.stdout.strip().splitlines()[-1]).get("proposal_event_id")
    log(f"filed {pr.get('html_url')} → proposal {pid}")
    return pid


def proposal_doc(agreed, report):
    lines = [f"# Help center review — {report['started']}", "",
             "Filed by `review/run.py`. Argon and Grok each used the help center in a real browser (desktop and phone) for the "
             "customer tasks below, then judged each other's findings against screenshots of every page. Only issues the other "
             "reviewer confirmed, at medium or high severity, are here.", "",
             f"Reviewers: {', '.join(report['reviewers'])}. Site built from the public rows of `corpus/` at `{report['commit'][:12]}`. "
             f"Screenshots: {report.get('run_url') or '(workflow artifacts)'}.", "", "## Tasks"]
    lines += [f"- ({vp}) {t}" for vp, t in TASKS]
    lines += ["", "## Issues both reviewers confirmed", ""]
    for i in agreed:
        lines += [f"### {i['id']}: {i['observation'][:90]}", f"- page: `{i['page']}` · severity: {i['severity']} · category: {i['category']}",
                  f"- found by {i['by']} ({i['viewport']}): {i['observation']}", f"- suggestion: {i['suggestion']}",
                  f"- confirmed by {i['confirmed_by']}: {i['confirm_reason']}", ""]
    lines += ["## For the panel", "",
              "Builders work under `helpcenter/` and follow `.cerata/guide.md`. Each bounty's acceptance test should be a new test "
              "module `helpcenter/test_<topic>.py` that fails now and passes when the issue is fixed, run as "
              "`python3 -m unittest helpcenter.test_<topic>` from the repo root; it can build the site the way "
              "`goals/helpcenter/referee.py` does (a stand-in `core.gate` over SQLite). Prefer one issue per bounty. "
              "`bash goals/helpcenter/acceptance.sh` must stay 10/10. Drop any issue that is taste rather than a defect."]
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dry", action="store_true"); ap.add_argument("--force", action="store_true")
    ap.add_argument("--work", default=None); a = ap.parse_args()
    work = Path(a.work or tempfile.mkdtemp(prefix="hc-review-")); shots_dir = work / "shots"; shots_dir.mkdir(parents=True, exist_ok=True)
    report = {"started": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
              "commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip(),
              "run_url": os.environ.get("REVIEW_RUN_URL"), "runs": [], "agreed": [], "filed": None}
    if not a.force and not referee_green():
        log("the help center referee is not green; nothing to review yet"); report["skipped"] = "referee not green"
        (work / "report.json").write_text(json.dumps(report, indent=1)); return 0
    site = work / "dist"
    db = preview.build(site, work)
    srv, base = serve.start(site, db)
    try:
        shots = page_shots(base, site, shots_dir)
        revs = reviewers(); report["reviewers"] = [r.label for r in revs]
        found = {r.name: [] for r in revs}
        for r in revs:
            for t, (vp, task) in enumerate(TASKS):
                b = Browser(base, vp)
                try:
                    b.act("navigate", {"url": "/help/"})
                    try:
                        out = r.review(b, task + NOTE)
                    except Exception as e:
                        out = {"completed": False, "summary": f"reviewer error: {e}", "issues": []}
                    b.page.screenshot(path=str(shots_dir / f"end-{r.name}-task{t + 1}.png"))
                finally:
                    b.close()
                run_rec = {"reviewer": r.label, "task": t + 1, "viewport": vp, "completed": out.get("completed"), "summary": out.get("summary"),
                           "steps": len(b.trail), "console": b.console[:20], "issues": out.get("issues") or []}
                report["runs"].append(run_rec)
                for k, i in enumerate(run_rec["issues"]):
                    if isinstance(i, dict) and i.get("observation"):
                        found[r.name].append({**i, "id": f"{r.name}-t{t + 1}-{k + 1}", "by": r.label, "viewport": vp, "task": t + 1,
                                              "severity": str(i.get("severity", "low")).lower()})
                log(f"{r.label} task {t + 1} ({vp}): completed={out.get('completed')} issues={len(run_rec['issues'])} steps={len(b.trail)}")
        for r in revs:
            other = [x for x in revs if x is not r][0]
            mine = found[r.name]
            if not mine:
                continue
            try:
                verdicts = {v.get("id"): v for v in other.confirm([{k: i[k] for k in ("id", "page", "severity", "category", "observation", "suggestion")} for i in mine], shots)
                            if isinstance(v, dict)}
            except Exception as e:
                log(f"{other.label} could not judge {r.label}'s issues: {e}"); verdicts = {}
            for i in mine:
                v = verdicts.get(i["id"]) or {}
                i["confirmed"], i["confirmed_by"], i["confirm_reason"] = bool(v.get("agree")), other.label, v.get("reason", "(no verdict)")
        allissues = [i for r in revs for i in found[r.name]]
        report["issues"] = allissues
        report["agreed"] = [i for i in allissues if i.get("confirmed") and i["severity"] in SEVERE]
        log(f"{len(allissues)} issues reported, {len(report['agreed'])} confirmed by the other reviewer at medium or high")
    finally:
        srv.shutdown()
    doc = proposal_doc(report["agreed"], report)
    (work / "report.md").write_text(doc)
    if report["agreed"] and not a.dry:
        why = in_flight()
        if why:
            log(f"not filing: {why}"); report["not_filed"] = why
        else:
            report["filed"] = file_proposal(report["agreed"], report, doc)
    elif not report["agreed"]:
        log("nothing both reviewers agree on: no proposal")
    (work / "report.json").write_text(json.dumps(report, indent=1))
    log(f"report: {work / 'report.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
