"""Minimal GitHub REST client for the brain's actions. Dry-run when no token is set."""
from __future__ import annotations
import os, json, urllib.request, urllib.error, urllib.parse

API = os.environ.get("GITHUB_API_URL", "https://api.github.com")

class GitHub:
    def __init__(self, token: str | None = None, repo: str | None = None):
        self.token = token or os.environ.get("GITHUB_TOKEN", "")
        self.repo = repo or os.environ.get("GITHUB_REPOSITORY", "")
        self.dry_run = not (self.token and self.repo)

    def _call(self, method, path, body=None):
        req = urllib.request.Request(API + path, json.dumps(body).encode() if body is not None else None, method=method)
        for k, v in {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28",
                     "User-Agent": "company-brain", "Authorization": f"Bearer {self.token}",
                     "Content-Type": "application/json"}.items():
            req.add_header(k, v)
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                raw = r.read()
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"GitHub {method} {path}: {e.code} {e.read().decode(errors='replace')[:300]}") from None

    def find_open_issue(self, title: str):
        if self.dry_run:
            return None
        issues = self._call("GET", f"/repos/{self.repo}/issues?state=open&labels=brain&per_page=100")
        return next((i for i in issues if i.get("title") == title and "pull_request" not in i), None)

    def open_issue(self, title: str, body: str, labels: list) -> str:
        if self.dry_run:
            print(f"\n----- DRY RUN: would open issue -----\nTITLE: {title}\nLABELS: {', '.join(labels)}\n\n{body}\n")
            return "dry-run"
        existing = self.find_open_issue(title)
        if existing:                      # re-running intake on the same document must not duplicate
            return existing["html_url"]
        return self._call("POST", f"/repos/{self.repo}/issues", {"title": title, "body": body, "labels": labels})["html_url"]

    def comment(self, number: int, body: str) -> str:
        if self.dry_run:
            print(f"\n----- DRY RUN: would comment on #{number} -----\n{body}\n")
            return "dry-run"
        return self._call("POST", f"/repos/{self.repo}/issues/{number}/comments", {"body": body})["html_url"]
