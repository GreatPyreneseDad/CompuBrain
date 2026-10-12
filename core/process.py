"""Run files from inbox/ through the brain: read what it can, ask for a tool for what it cannot.

  python -m core.process inbox/a.md inbox/b.rtf     named files
  python -m core.process --changed                   files added or changed in the last commit
  python -m core.process --catchup                   files in inbox/ that are readable now but were never ingested
"""
from __future__ import annotations
import sys, pathlib, subprocess, collections
from core import gate, intake, tooling
from ingest import chunk

INBOX = pathlib.Path("inbox")

def _skip(p: pathlib.Path) -> bool:
    return p.name.lower() == "readme.md" or p.name.startswith(".") or not p.is_file()

def process(paths: list, senders: dict | None = None) -> dict:
    readable = [p for p in map(pathlib.Path, paths) if not _skip(p) and p.suffix.lower() in chunk.READERS]
    blocked = [p for p in map(pathlib.Path, paths) if not _skip(p) and p.suffix.lower() not in chunk.READERS]
    if readable:
        subprocess.run([sys.executable, "-W", "ignore", "-m", "ingest.run_sf", *map(str, readable),
                        "--source", "inbox", "--default-scope", "internal"], check=False)
        for p in readable:
            title = intake.title_of(str(p))
            print(f"== {title}")
            intake.run(title)
    for p in blocked:
        tooling.request(str(p), (senders or {}).get(str(p), ""))
    return {"read": [str(p) for p in readable], "blocked": [str(p) for p in blocked]}

def changed() -> list:
    out = subprocess.run(["git", "diff", "--name-only", "--diff-filter=AM", "HEAD~1", "HEAD", "--", "inbox/"],
                         capture_output=True, text=True).stdout
    return [l for l in out.splitlines() if l.strip()]

def catchup() -> list:
    """Files the brain can read now but has never ingested: the ones that were waiting on a tool."""
    known = {r[0] for r in gate.query("BRAIN_OWNER", "select title from document")}
    waiting = []
    for p in sorted(INBOX.iterdir()) if INBOX.is_dir() else []:
        if _skip(p) or p.suffix.lower() not in chunk.READERS:
            continue
        try:
            if intake.title_of(str(p)) not in known:
                waiting.append(p)
        except Exception as e:
            print(f"catchup: cannot title {p.name}: {e}")
    if waiting:
        print("catchup: " + ", ".join(p.name for p in waiting))
        process([str(p) for p in waiting])
        by_ext = collections.defaultdict(list)
        for p in waiting:
            by_ext[p.suffix.lower()].append(p.name)
        for ext, names in by_ext.items():
            tooling.resolve(ext, names)
    else:
        print("catchup: nothing waiting")
    return [str(p) for p in waiting]

if __name__ == "__main__":
    args = sys.argv[1:]
    done = set()
    if "--changed" in args:
        files = changed(); print("changed:", files or "none")
        done |= set(process(files)["read"]) if files else set()
    named = [a for a in args if not a.startswith("--")]
    if named:
        process(named)
    if "--catchup" in args:
        catchup()
