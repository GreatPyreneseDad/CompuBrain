"""Mail transport for unblock emails, through AgentMail. Off unless configured.

With AGENTMAIL_API_KEY set, the brain sends from its own inbox (BRAIN_MAIL_FROM) to a department's
inbox, and only when that inbox is one of the brain's own AgentMail addresses. Departments without
a real inbox stay queued: the email is written and shown, never sent to a made-up address.
"""
from __future__ import annotations
import os, json, urllib.request, urllib.error

API = "https://api.agentmail.to/v0"
FROM = os.environ.get("BRAIN_MAIL_FROM", "compubrain-brain@agentmail.to")

def configured() -> bool:
    return bool(os.environ.get("AGENTMAIL_API_KEY"))

def deliverable(to_email: str) -> bool:
    return to_email.startswith("compubrain-") and to_email.endswith("@agentmail.to")

def send(to_email: str, subject: str, body: str, labels: list | None = None) -> str:
    """Returns the status to store: queued (not sent), sent, or failed."""
    if not configured() or not deliverable(to_email) or os.environ.get("BRAIN_NO_SEND") == "1":
        return "queued"
    payload = {"to": to_email, "subject": subject, "text": body, "labels": labels or ["company-brain"]}
    req = urllib.request.Request(f"{API}/inboxes/{urllib.request.quote(FROM)}/messages/send",
                                 json.dumps(payload).encode(), method="POST",
                                 headers={"Authorization": f"Bearer {os.environ['AGENTMAIL_API_KEY']}",
                                          "Content-Type": "application/json", "User-Agent": "company-brain"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return "sent" if r.status == 200 else "failed"
    except Exception:
        return "failed"
