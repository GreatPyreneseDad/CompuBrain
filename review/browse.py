"""One browser both reviewers drive, through the same actions on the same 0-1000 grid (Argon's native convention).

Only the site under review is reachable: any request to another host is aborted, so a reviewer cannot wander off and
the page cannot call out. Every action returns a fresh screenshot and the URL.
"""
from __future__ import annotations
import base64, time
from urllib.parse import urljoin, urlparse
from playwright.sync_api import sync_playwright

GRID = 1000
VIEWPORTS = {"desktop": (1280, 800), "phone": (390, 844)}


class Browser:
    def __init__(self, base: str, viewport: str = "desktop"):
        self.base, self.host = base, urlparse(base).netloc
        self.w, self.h = VIEWPORTS[viewport]
        self._pw = sync_playwright().start()
        self._b = self._pw.chromium.launch()
        self._ctx = self._b.new_context(viewport={"width": self.w, "height": self.h}, device_scale_factor=1,
                                        is_mobile=viewport == "phone", has_touch=viewport == "phone")
        self._ctx.route("**/*", lambda r: r.continue_() if urlparse(r.request.url).netloc == self.host else r.abort())
        self.page = self._ctx.new_page()
        self.console = []
        self.page.on("console", lambda m: self.console.append(f"{m.type}: {m.text}") if m.type in ("error", "warning") else None)
        self.page.on("pageerror", lambda e: self.console.append(f"pageerror: {e}"))
        self.trail = []

    def close(self):
        try:
            self._b.close(); self._pw.stop()
        except Exception:
            pass

    # -- observation
    def screenshot(self) -> str:
        time.sleep(0.3)
        return base64.b64encode(self.page.screenshot(type="png")).decode()

    @property
    def url(self) -> str:
        return self.page.url

    def text(self, limit: int = 4000) -> str:
        try:
            return self.page.locator("body").aria_snapshot()[:limit]
        except Exception:
            return (self.page.inner_text("body") or "")[:limit]

    def _px(self, x, y):
        return int(float(x) / GRID * self.w), int(float(y) / GRID * self.h)

    # -- actions (names and arguments follow Gemini computer use)
    def act(self, name: str, a: dict) -> str:
        self.trail.append({"action": name, "args": {k: v for k, v in a.items() if k != "safety_decision"}, "url": self.url})
        p = self.page
        try:
            if name in ("open_web_browser",):
                pass
            elif name == "navigate":
                u = urljoin(self.base + "/help/", a.get("url", "/help/"))
                if urlparse(u).netloc != self.host:
                    return f"blocked: only {self.base}/help/ is in scope"
                p.goto(u, wait_until="load")
            elif name == "click_at":
                p.mouse.click(*self._px(a["x"], a["y"]))
            elif name == "hover_at":
                p.mouse.move(*self._px(a["x"], a["y"]))
            elif name == "type_text_at":
                p.mouse.click(*self._px(a["x"], a["y"]))
                if a.get("clear_before_typing", True):
                    p.keyboard.press("Control+A"); p.keyboard.press("Backspace")
                p.keyboard.type(str(a.get("text", "")))
                if a.get("press_enter", True):
                    p.keyboard.press("Enter")
            elif name == "key_combination":
                p.keyboard.press(str(a.get("keys", "")).replace("+", "+"))
            elif name == "scroll_document":
                d = a.get("direction", "down"); p.mouse.wheel(0, -600 if d == "up" else 600) if d in ("up", "down") else p.mouse.wheel(-600 if d == "left" else 600, 0)
            elif name == "scroll_at":
                p.mouse.move(*self._px(a["x"], a["y"])); m = float(a.get("magnitude", 800)) / GRID * self.h
                d = a.get("direction", "down"); p.mouse.wheel(0, -m if d == "up" else m) if d in ("up", "down") else p.mouse.wheel(-m if d == "left" else m, 0)
            elif name == "go_back":
                p.go_back(wait_until="load")
            elif name == "go_forward":
                p.go_forward(wait_until="load")
            elif name in ("wait_5_seconds",):
                time.sleep(5)
            elif name == "search":
                p.goto(self.base + "/help/", wait_until="load")
            elif name == "drag_and_drop":
                p.mouse.move(*self._px(a["x"], a["y"])); p.mouse.down(); p.mouse.move(*self._px(a["destination_x"], a["destination_y"])); p.mouse.up()
            else:
                return f"unsupported action {name}"
            try:
                p.wait_for_load_state("load", timeout=5000)
            except Exception:
                pass
            return "ok"
        except Exception as e:
            return f"error: {str(e)[:200]}"
