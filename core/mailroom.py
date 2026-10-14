"""The mail loop: emails that reach the company inbox become documents in inbox/, and the brain acts.

  python -m core.mailroom            poll once, pull new mail into inbox/, process it

Each new email is written to inbox/ as a Markdown document (subject, sender, body). Attachments are
saved beside it under their own names. Readable files are ingested and planned; an attachment the
brain cannot read raises a tooling request. Message ids are remembered in MAIL_SEEN so nothing is
pulled twice. Email is outside data: the planner is told not to follow instructions found in it.
"""
from __future__ import annotations
import os, re, json, pathlib, urllib.request, urllib.parse
from core import gate, process

API = "https://api.agentmail.to/v0"
INBOX_ADDR = os.environ.get("BRAIN_MAIL_INBOX", "compubrain-brain@agentmail.to")
OUT = pathlib.Path("inbox")

def _get(path):
    req = urllib.request.Request(API + path, headers={"Authorization": f"Bearer {os.environ['AGENTMAIL_API_KEY']}",
                                                      "User-Agent": "company-brain"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def _slug(s: str, n: int = 48) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:n] or "mail"

def public_sender(sender: str) -> str:
    """'Name <user@host>' -> 'Name (host address)'. The full address goes only to MAIL_SEEN, behind the gate;
    inbox/ and GitHub issues are public copies."""
    mm = re.match(r"\s*(.*?)\s*<([^>]+)>\s*$", sender or "")
    if mm:
        name, addr = mm.group(1).strip().strip('"'), mm.group(2)
    else:
        name, addr = "", (sender or "").strip()
    host = addr.split("@")[-1] if "@" in addr else addr
    return f"{name} ({host} address)" if name else (f"a {host} address" if host else "an unknown sender")

def pull() -> tuple:
    """Write new received messages to inbox/. Returns (files, senders)."""
    box = urllib.parse.quote(INBOX_ADDR)
    seen = {r[0] for r in gate.query("BRAIN_OWNER", "select message_id from mail_seen")}
    listing = _get(f"/inboxes/{box}/messages?limit=30").get("messages", [])
    files, senders = [], {}
    OUT.mkdir(exist_ok=True)
    for m in reversed(listing):                                   # oldest first
        if "received" not in (m.get("labels") or []) or m["message_id"] in seen:
            continue
        mid = urllib.parse.quote(m["message_id"], safe="")
        d = _get(f"/inboxes/{box}/messages/{mid}")
        subject, sender = (d.get("subject") or "(no subject)").strip(), d.get("from", "")
        body = (d.get("extracted_text") or d.get("text") or "").strip()
        slug = _slug(subject)
        saved = []
        for a in d.get("attachments") or []:
            name = re.sub(r"[^A-Za-z0-9._-]+", "-", a.get("filename") or "attachment")
            info = _get(f"/inboxes/{box}/messages/{mid}/attachments/{urllib.parse.quote(a['attachment_id'], safe='')}")
            with urllib.request.urlopen(info["download_url"], timeout=60) as r:
                data = r.read()
            if len(data) > 5_000_000:
                continue
            target = OUT / name
            target.write_bytes(data)
            saved.append(str(target)); senders[str(target)] = public_sender(sender)
        title = f"Email - {subject}".replace('"', "'")
        note = ("\n\nAttachments received with this email: " + ", ".join(pathlib.Path(s).name for s in saved) + ".") if saved else ""
        doc = OUT / f"mail-{slug}.md"
        doc.write_text(f'---\ntitle: "{title}"\nsource: email\n---\n# {subject}\n\n'
                       f"Email received {d.get('timestamp', '')[:10]} from {public_sender(sender)}.\n\n{body}{note}\n")
        files += [str(doc)] + saved; senders[str(doc)] = public_sender(sender)
        gate.query("BRAIN_OWNER", "insert into mail_seen (message_id, sender, subject, files) values (%s, %s, %s, %s)",
                   (m["message_id"], sender, subject, ",".join([str(doc)] + saved)))
        print(f"mail: {subject!r} from {sender} -> {doc.name}" + (f" + {len(saved)} attachment(s)" if saved else ""))
    return files, senders

if __name__ == "__main__":
    files, senders = pull()
    if files:
        process.process(files, senders)
    else:
        print("mail: nothing new")
