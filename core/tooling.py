"""When the brain meets a file it has no reader for, it asks for the tool.

It opens a tooling issue saying what arrived and who is blocked, writes the `/cerata consume`
command, and starts the CERATA workflow with that command. CERATA builds the reader and opens a
pull request; a person reviews and merges it. core.process then goes back for the file.

The prey for each file type comes from the short list below. The brain does not search for
libraries on its own.
"""
from __future__ import annotations
import os, pathlib
from core import gate
from core.gh import GitHub

# file type -> (open-source prey, what to take from it)
KNOWN_PREY = {
    ".rtf":  ("joshy/striprtf", "RTF to plain text"),
    ".pdf":  ("py-pdf/pypdf", "plain-text extraction from a PDF"),
    ".xlsx": ("dilshod/xlsx2csv", "reading worksheet cells from an .xlsx file as rows of text"),
}

def title_for(ext: str) -> str:
    return f"[tooling] The brain cannot read {ext} files"

def command_for(ext: str):
    if ext not in KNOWN_PREY:
        return None
    prey, what = KNOWN_PREY[ext]
    return (f"consume {prey} -- add a reader for {ext} files to ingest: {what}. "
            f"Follow .cerata/guide.md: one module ingest/{ext.lstrip('.')}.py with extract_text(path), "
            f"register '{ext}' in ingest.chunk.READERS and route it in ingest.chunk.load like .docx.")

def request(path: str, sender: str = "") -> str:
    """Open (or find) the tooling issue for this file type and start CERATA. Returns the issue URL."""
    gh, p = GitHub(), pathlib.Path(path)
    ext = p.suffix.lower()
    cmd = command_for(ext)
    body = [f"A file arrived that the brain has no reader for: `{p.name}`" + (f", sent by {sender}" if sender else "") + ".",
            "", "**Blocked:** the teams this document concerns cannot get their tasks, unblock requests or forecast "
            "update until it can be read. The file is kept in `inbox/` and will be processed as soon as a reader exists.", ""]
    if cmd:
        prey = KNOWN_PREY[ext][0]
        body += [f"**Requested tool:** a `{ext}` reader, to be metabolized from [`{prey}`](https://github.com/{prey}).",
                 "", "The brain has started CERATA with this command:", "", "```", f"/cerata {cmd}", "```", "",
                 "- [ ] CERATA opens a pull request with the reader and its tests",
                 "- [ ] A person reviews and merges it",
                 f"- [ ] The brain processes `{p.name}` and closes this issue"]
    else:
        body += [f"**No known reader for `{ext}`.** A person should name one: comment `/cerata hunt owner/repo` "
                 "with a candidate, then `/cerata consume` it."]
    body += ["", "---", "Opened by the Company Brain. It picks the candidate from a fixed list; it does not merge its own tools."]
    existing = gh.find_open_issue(title_for(ext))
    url = gh.open_issue(title_for(ext), "\n".join(body), ["brain", "tooling", f"tooling:{ext.lstrip('.')}"])
    if existing:
        gh.comment(existing["number"], f"Another `{ext}` file is waiting: `{p.name}`.")
        return url
    started = False
    if cmd and not gh.dry_run:
        try:
            gh._call("POST", f"/repos/{gh.repo}/actions/workflows/cerata.yml/dispatches",
                     {"ref": os.environ.get("GITHUB_REF_NAME", "main"), "inputs": {"command": cmd}})
            started = True
        except Exception as e:
            print(f"tooling: could not start CERATA: {e}")
    number = url.rstrip("/").split("/")[-1]
    if number.isdigit() and cmd:
        gh.comment(int(number), f"/cerata {cmd}\n\n<sub>{'CERATA started by workflow dispatch with this command.' if started else 'CERATA was not started automatically; an owner can post this command to start it.'}</sub>")
    try:        # the wait shows up in the flow forecast: sales is blocked on a tool, engineering owns the gap
        gate.query("BRAIN_SALES", """insert into task (subject, document, planned_by, scope, department, task, blocked_by, need, issue_url)
                                     values (%s, %s, 'svc-intake-sales', 'sales', 'sales', %s, 'engineering', %s, %s)""",
                   (p.stem.replace("-", " ").title(), p.name, f"Process {p.name}: the brain cannot read {ext} files yet",
                    f"A {ext} reader for the brain (requested from CERATA, awaiting review and merge)", "" if url == "dry-run" else url))
    except Exception as e:
        print(f"tooling: wait not recorded: {e}")
    print(f"tooling: {p.name} -> {url}" + (" (CERATA started)" if started else ""))
    return url

def resolve(ext: str, files: list) -> None:
    """A reader now exists: note it on the open tooling issue for this file type and close it."""
    gh = GitHub()
    issue = gh.find_open_issue(title_for(ext))
    if issue is None:
        return
    gh.comment(issue["number"], f"The `{ext}` reader is merged. Processed: " + ", ".join(f"`{f}`" for f in files) + ". Closing.")
    gh._call("PATCH", f"/repos/{gh.repo}/issues/{issue['number']}", {"state": "closed", "state_reason": "completed"})
    try:
        gate.query("BRAIN_OWNER", "delete from task where blocked_by = 'engineering' and task like %s", (f"%cannot read {ext} files yet",))
    except Exception:
        pass
