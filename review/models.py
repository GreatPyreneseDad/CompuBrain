"""The two reviewers. Argon drives the browser through Gemini's native computer-use tool; Grok drives the same browser
through function tools and sees a screenshot after every action. Each also judges the other's findings.

Both speak plain HTTPS with the standard library. Keys: GEMINI_API_KEY, XAI_API_KEY. Models: ARGON_MODEL
(default gemini-4-argon), GROK_MODEL (default grok-4.7). REVIEW_FAKE=1 swaps both for a scripted stand-in that
drives the browser through a fixed path and reports one issue: plumbing tests only, never a review.
"""
from __future__ import annotations
import json, os, re, time, urllib.error, urllib.request

MAX_STEPS = int(os.environ.get("REVIEW_MAX_STEPS", "25"))

REPORT = """When you have finished the task (or given up), stop acting and reply with ONLY one JSON object:
{"completed": true|false, "summary": "<one or two sentences: what you did and whether a customer could do it>",
 "issues": [{"page": "<URL path>", "severity": "high|medium|low", "category": "broken|confusing|accessibility|visual|content",
             "observation": "<what you saw, specific>", "suggestion": "<the change that would fix it, specific>"}]}
Report only problems you actually saw in this session. high = a customer cannot finish the task; medium = they can,
with real friction or a clear defect; low = polish. No issues is a fine answer."""

CONFIRM = """Another reviewer tested the same help center and reported the issues below. You have screenshots of every
page at desktop and phone width. For each issue, judge whether the screenshots (and your own experience of this site,
if you tested it) support it. Reply with ONLY a JSON array, one entry per issue, in order:
[{"id": "<issue id>", "agree": true|false, "reason": "<one sentence>"}]
Agree only if you can see the problem or have seen it yourself. Taste alone is not a defect."""


def first_json(text: str):
    text = re.sub(r"```(?:json)?", "", text or "")
    for opener, closer in (("{", "}"), ("[", "]")):
        start = text.find(opener)
        while start >= 0:
            depth = 0
            for i in range(start, len(text)):
                if text[i] == opener: depth += 1
                elif text[i] == closer:
                    depth -= 1
                    if depth == 0:
                        try:
                            return json.loads(text[start:i + 1])
                        except json.JSONDecodeError:
                            break
            start = text.find(opener, start + 1)
    return None


def post(url: str, body: dict, headers: dict, tries: int = 4) -> dict:
    data = json.dumps(body).encode()
    for t in range(tries):
        req = urllib.request.Request(url, data=data, headers={"content-type": "application/json", **headers})
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="replace")[:400]
            if e.code in (429, 500, 502, 503, 504) and t < tries - 1:
                time.sleep(5 * (t + 1)); continue
            raise RuntimeError(f"{url.split('?')[0]} {e.code}: {msg}")
        except urllib.error.URLError:
            if t < tries - 1:
                time.sleep(5 * (t + 1)); continue
            raise


# ------------------------------------------------------------------ Argon --

class Argon:
    name = "argon"

    def __init__(self):
        self.key = os.environ["GEMINI_API_KEY"]; self.model = os.environ.get("ARGON_MODEL", "gemini-4-argon")
        self.label = f"argon/{self.model}"

    def _call(self, contents, tools=True):
        body = {"contents": contents, "generationConfig": {"temperature": 0.2}}
        if tools:
            body["tools"] = [{"computerUse": {"environment": "ENVIRONMENT_BROWSER"}}]
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        r = post(url, body, {"x-goog-api-key": self.key})
        cand = (r.get("candidates") or [{}])[0]
        return cand.get("content") or {"role": "model", "parts": []}

    def review(self, browser, task: str) -> dict:
        shot = browser.screenshot()
        contents = [{"role": "user", "parts": [{"text": f"{task}\n\nThe help center is open at {browser.url}. Stay on this site.\n\n{REPORT}"},
                                               {"inlineData": {"mimeType": "image/png", "data": shot}}]}]
        for _ in range(MAX_STEPS):
            msg = self._call(contents); contents.append(msg)
            calls = [p["functionCall"] for p in msg.get("parts", []) if "functionCall" in p]
            if not calls:
                text = "".join(p.get("text", "") for p in msg.get("parts", []))
                return first_json(text) or {"completed": False, "summary": "no JSON report", "issues": [], "raw": text[:2000]}
            parts = []
            for c in calls:
                args = c.get("args") or {}
                result = browser.act(c["name"], args)
                resp = {"url": browser.url}
                if result != "ok":
                    resp["error"] = result
                if args.get("safety_decision"):
                    resp["safety_acknowledgement"] = "true"
                parts.append({"functionResponse": {"name": c["name"], "response": resp}})
            parts.append({"inlineData": {"mimeType": "image/png", "data": browser.screenshot()}})
            contents.append({"role": "user", "parts": parts})
        contents.append({"role": "user", "parts": [{"text": "Step limit reached. Stop now and give the JSON report."}]})
        msg = self._call(contents, tools=False)
        return first_json("".join(p.get("text", "") for p in msg.get("parts", []))) or {"completed": False, "summary": "step limit, no report", "issues": []}

    def confirm(self, issues: list, shots: dict) -> list:
        parts = [{"text": CONFIRM + "\n\nIssues:\n" + json.dumps(issues, indent=1)}]
        for name, b64 in shots.items():
            parts += [{"text": f"screenshot: {name}"}, {"inlineData": {"mimeType": "image/png", "data": b64}}]
        msg = self._call([{"role": "user", "parts": parts}], tools=False)
        return first_json("".join(p.get("text", "") for p in msg.get("parts", []))) or []


# ------------------------------------------------------------------- Grok --

GROK_TOOLS = [{"type": "function", "function": {"name": n, "description": d, "parameters": {"type": "object", "properties": p, "required": list(p)}}}
              for n, d, p in [
    ("click_at", "Click at a point. x and y are on a 0-1000 grid over the screenshot.", {"x": {"type": "number"}, "y": {"type": "number"}}),
    ("type_text_at", "Click a field at (x, y) on the 0-1000 grid, replace its text, optionally press Enter.",
     {"x": {"type": "number"}, "y": {"type": "number"}, "text": {"type": "string"}, "press_enter": {"type": "boolean"}}),
    ("scroll_document", "Scroll the page.", {"direction": {"type": "string", "enum": ["up", "down"]}}),
    ("navigate", "Open a path on this help center, e.g. /help/ or /help/refund-policy.html.", {"url": {"type": "string"}}),
    ("go_back", "Browser back.", {}),
    ("key_combination", "Press keys, e.g. Tab or Shift+Tab or Enter.", {"keys": {"type": "string"}}),
]]


class Grok:
    name = "grok"

    def __init__(self):
        self.key = os.environ["XAI_API_KEY"]; self.model = os.environ.get("GROK_MODEL", "grok-4.7")
        self.label = f"grok/{self.model}"

    def _call(self, messages, tools=True):
        body = {"model": self.model, "messages": messages, "temperature": 0.2}
        if tools:
            body["tools"] = GROK_TOOLS
        r = post("https://api.x.ai/v1/chat/completions", body, {"authorization": f"Bearer {self.key}"})
        return r["choices"][0]["message"]

    @staticmethod
    def _seen(browser, note=""):
        return {"role": "user", "content": [
            {"type": "text", "text": f"{note}Current URL: {browser.url}\nAccessible text of the page:\n{browser.text(2500)}"},
            {"type": "image_url", "image_url": {"url": "data:image/png;base64," + browser.screenshot(), "detail": "high"}}]}

    def review(self, browser, task: str) -> dict:
        messages = [{"role": "system", "content": "You test websites as a customer would, using the browser tools. " + REPORT},
                    {"role": "user", "content": f"{task}\n\nThe help center is open. Stay on this site."}, self._seen(browser)]
        for _ in range(MAX_STEPS):
            msg = self._call(messages)
            messages.append({k: v for k, v in msg.items() if k in ("role", "content", "tool_calls")})
            calls = msg.get("tool_calls") or []
            if not calls:
                return first_json(msg.get("content") or "") or {"completed": False, "summary": "no JSON report", "issues": [], "raw": (msg.get("content") or "")[:2000]}
            for c in calls:
                try:
                    args = json.loads(c["function"].get("arguments") or "{}")
                except json.JSONDecodeError:
                    args = {}
                result = browser.act(c["function"]["name"], args)
                messages.append({"role": "tool", "tool_call_id": c["id"], "content": json.dumps({"result": result, "url": browser.url})})
            messages.append(self._seen(browser, "After your action. "))
        messages.append({"role": "user", "content": "Step limit reached. Stop now and give the JSON report."})
        return first_json(self._call(messages, tools=False).get("content") or "") or {"completed": False, "summary": "step limit, no report", "issues": []}

    def confirm(self, issues: list, shots: dict) -> list:
        content = [{"type": "text", "text": CONFIRM + "\n\nIssues:\n" + json.dumps(issues, indent=1)}]
        for name, b64 in shots.items():
            content += [{"type": "text", "text": f"screenshot: {name}"}, {"type": "image_url", "image_url": {"url": "data:image/png;base64," + b64}}]
        return first_json(self._call([{"role": "user", "content": content}], tools=False).get("content") or "") or []


# ------------------------------------------------------------------- fake --

class Fake:
    """Plumbing only: walks a fixed path, reports one low-severity issue, agrees with everything."""
    def __init__(self, name):
        self.name, self.label = name, f"{name}/fake"

    def review(self, browser, task: str) -> dict:
        browser.act("navigate", {"url": "/help/"}); browser.act("scroll_document", {"direction": "down"})
        browser.act("type_text_at", {"x": 300, "y": 900, "text": "How do I get a refund?", "press_enter": True})
        return {"completed": True, "summary": f"{self.name} fake walk", "issues": [
            {"page": "/help/", "severity": "medium", "category": "content", "observation": f"{self.name} fake observation",
             "suggestion": f"{self.name} fake suggestion"}]}

    def confirm(self, issues, shots):
        return [{"id": i["id"], "agree": True, "reason": "fake"} for i in issues]


def reviewers():
    if os.environ.get("REVIEW_FAKE") == "1":
        return [Fake("argon"), Fake("grok")]
    return [Argon(), Grok()]
