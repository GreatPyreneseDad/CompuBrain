"""Flow: planned tasks, unblock emails between departments, and the choke-point forecast.

Tasks and emails are written on the planning role's own session and carry its scope, so the same
gate that filters knowledge filters work: a role sees only the work planned under scopes it holds.
An email is written only from material the receiving department may see.
"""
from __future__ import annotations
import re, json, datetime, collections, threading
from core import gate, mail, render
from ingest.llm import ask_json

TEAM_SCOPE = {"sales": "sales", "exec": "exec", "support_agent": "support"}
DEPARTMENTS = ["sales", "sales_ops", "support", "customer_success", "engineering", "product",
               "finance", "legal", "leadership", "people"]
HOME = {"sales": "sales", "exec": "leadership", "support_agent": "support"}     # a planner's own department

_dept_cache, _lock = None, threading.Lock()
def departments() -> dict:
    global _dept_cache
    with _lock:
        if _dept_cache is None:
            rows = gate.query("BRAIN_ROUTER", "select id, name, contact_title, email, scopes, capacity_per_week from department")
            _dept_cache = {r[0]: {"id": r[0], "name": r[1], "contact": r[2], "email": r[3],
                                  "scopes": set(r[4].split(",")), "capacity": int(r[5])} for r in rows}
        return _dept_cache

def _date(s):
    m = re.match(r"\s*(\d{4}-\d{2}-\d{2})", str(s or ""))
    return m.group(1) if m else None

EMAIL = """You write a short work email from one department of a company to another, asking for something that \
is blocking the sender's work. Use only the request lines and the background given. Plain, specific, courteous. \
State what is needed, for which customer or matter, and the date it is needed by. At most 110 words in the body. \
The recipient may only be told what appears in the background given. If a request line contains a figure, a \
name or a fact that is not in that background, leave it out and describe the request in general terms instead. \
Open with the recipient's title; end with the sender's department as the last line. \
Return {"subject": "...", "body": "..."}."""

def store(p, title, out, hits, mine, issue_url="") -> list:
    """Store the plan's tasks; write one unblock email per department this plan waits on."""
    scope, home, depts = TEAM_SCOPE[p.role_id], HOME[p.role_id], departments()
    subject = out.get("subject") or title
    dispatched, waits = [], collections.defaultdict(list)
    for t in out.get("tasks", []):
        dept = t.get("department") if t.get("department") in depts else home
        blocker = t.get("blocked_by") if t.get("blocked_by") in depts and t.get("blocked_by") != dept else None
        due = _date(t.get("due_date")) or _date(t.get("due"))
        gate.query(p.sf_role, """insert into task (subject, document, planned_by, scope, department, task, due_date,
                                                   blocked_by, need, issue_url)
                                 values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                   (subject, title, p.handle, scope, dept, t["task"], due, blocker, t.get("need") or None, issue_url))
        if blocker:
            waits[blocker].append((t, dept, due))

    for to, items in waits.items():
        d = depts[to]
        # Only material the receiving department may see goes into the email.
        seen = [h for h in hits if h.scope in d["scopes"]]
        doc_part = [m[2] for m in mine if m[3] in d["scopes"]]
        used = {hits[t["source"] - 1].scope for t, _, _ in items
                if isinstance(t.get("source"), int) and 1 <= t["source"] <= len(hits)} | {m[3] for m in mine}
        withheld = sorted(used - d["scopes"])
        needed_by = min([due for _, _, due in items if due] or [None], default=None) if any(x[2] for x in items) else None
        asks = "\n".join(f"- {t.get('need') or t['task']}" + (f" (needed by {due})" if due else "") for t, _, due in items)
        background = "\n\n".join([f"From the new document:\n{c}" for c in doc_part[:2]] +
                                 [f"{h.title}:\n{h.content}" for h in seen[:3]]) or "(none the recipient may see)"
        note = (f"\nBefore the sign-off add one sentence: some background sits in material the recipient's department "
                f"does not hold; ask {depts[HOME[p.role_id]]['name']} for a briefing.") if withheld else ""
        try:
            m = ask_json(EMAIL + note, f"From: {depts[home]['name']}\nTo: {d['contact']}, {d['name']}\n"
                                       f"About: {subject}\n\nRequests:\n{asks}\n\nBackground the recipient may see:\n{background}",
                         max_tokens=600)
            subj, body = str(m.get("subject") or "").strip(), str(m["body"])
            subj = subj or f"Needed from {d['name']}: {subject}"
        except Exception:
            subj, body = f"Needed from {d['name']}: {subject}", f"{d['contact']},\n\n{asks}\n\n{depts[home]['name']}"
        status = mail.send(d["email"], subj, body, ["company-brain", f"to-{to}", f"from-{home}"])
        gate.query(p.sf_role, """insert into outbox (scope, sent_as, from_dept, to_dept, to_email, subject, body, about,
                                                     needed_by, withheld, status, issue_url)
                                 values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                   (scope, p.handle, home, to, d["email"], subj, body, subject, needed_by, ",".join(withheld), status, issue_url))
        dispatched.append({"to": d["name"], "email": d["email"], "subject": subj, "needed_by": needed_by,
                           "withheld": withheld, "status": status})
    return dispatched

def outbox(principal, limit: int = 40) -> list:
    rows = gate.query(principal.sf_role, """select created_at, sent_as, from_dept, to_dept, to_email, subject, body, about,
        needed_by, withheld, status, issue_url from outbox order by created_at desc limit %s""", (limit,))
    keys = ["at", "sent_as", "from", "to", "to_email", "subject", "body", "about", "needed_by", "withheld", "status", "issue_url"]
    return [dict(zip(keys, [str(r[0])] + [str(x) if isinstance(x, datetime.date) else x for x in r[1:]])) for r in rows]

def _week(d: datetime.date) -> str:
    return (d - datetime.timedelta(days=d.weekday())).isoformat()

def _matter(document: str) -> str:
    return re.sub(r"\s*\d+$", "", re.sub(r"order form\s*[-:]?\s*", "", document, flags=re.I)).strip() or document

NARRATE = """You read a workload table for the departments of one company and say where work will jam. \
Use only the numbers and tasks given. For each choke point give the department, the week, why it jams in one \
sentence, which customers are affected, and one concrete action. Then a one-sentence headline. \
Return {"headline": "...", "choke_points": [{"department": "...", "week": "YYYY-MM-DD", "why": "...", \
"affected": ["..."], "action": "..."}]} with at most 4 choke points, worst first. If nothing jams, return an empty list."""

_fc_cache = {}
def forecast(principal) -> dict:
    """Load against capacity by department and week, and who waits on whom, over the tasks this asker may see.
    A deliverable is counted once per (matter, department, due date) however many planners listed it."""
    depts = departments()
    rows = gate.query(principal.sf_role, """select document, department, due_date, blocked_by, task, need from task""")
    key = (principal.sf_role, len(rows))
    if key in _fc_cache:
        return _fc_cache[key]
    seen, load, waiting, undated = set(), collections.Counter(), collections.defaultdict(set), collections.Counter()
    examples = collections.defaultdict(list)
    for document, dept, due, blocker, task, need in rows:
        matter = _matter(document)
        k = (matter, dept, due)
        if k not in seen:
            seen.add(k)
            if due:
                load[(dept, _week(due))] += 1
                examples[(dept, _week(due))].append(f"{matter}: {task[:110]}")
            else:
                undated[dept] += 1
        if blocker:
            waiting[blocker].add((matter, dept, (need or task)[:110], due.isoformat() if due else None))
            kb = (matter, blocker, due)                 # a request to a department is work for that department
            if kb not in seen:
                seen.add(kb)
                if due:
                    load[(blocker, _week(due))] += 1
                    examples[(blocker, _week(due))].append(f"{matter} (asked by {depts[dept]['name']}): {(need or task)[:110]}")
                else:
                    undated[blocker] += 1
    weeks = sorted({w for _, w in load})[:6]
    table = []
    for d in depts.values():
        by_week = [{"week": w, "tasks": load[(d["id"], w)], "over": load[(d["id"], w)] > d["capacity"]} for w in weeks]
        inbound = sorted(waiting[d["id"]], key=lambda x: x[3] or "9999")
        total = sum(x["tasks"] for x in by_week) + undated[d["id"]]
        if total or inbound:
            table.append({"id": d["id"], "name": d["name"], "capacity": d["capacity"], "by_week": by_week,
                          "undated": undated[d["id"]], "waiting_on_them": len(inbound),
                          "waiting": [{"matter": m, "from": depts[f]["name"], "need": n, "by": by} for m, f, n, by in inbound[:6]],
                          "status": "choke" if any(x["over"] for x in by_week) or len(inbound) >= 4
                                    else "tight" if any(x["tasks"] == d["capacity"] for x in by_week) or len(inbound) >= 2 else "ok"})
    table.sort(key=lambda t: ({"choke": 0, "tight": 1, "ok": 2}[t["status"]], -t["waiting_on_them"]))
    out = {"asker": principal.handle, "scopes": list(principal.scopes), "weeks": weeks, "departments": table,
           "tasks_seen": len(rows), "headline": "", "choke_points": []}
    if table:
        brief = json.dumps([{k: t[k] for k in ("name", "capacity", "by_week", "waiting_on_them", "waiting", "status")} for t in table])
        ex = "\n".join(f"{depts[d]['name']} week of {w}: " + " | ".join(v[:4]) for (d, w), v in sorted(examples.items(), key=lambda kv: kv[0][1])[:14])
        try:
            msg = render.client().messages.create(model=render.ANSWER_MODEL, max_tokens=4000, system=NARRATE,
                messages=[{"role": "user", "content": f"Workload table:\n{brief}\n\nTasks behind the numbers:\n{ex}"}])
            text = "".join(b.text for b in msg.content if b.type == "text")
            n = json.loads(re.search(r"\{.*\}", text, re.S).group(0))
            out["headline"], out["choke_points"] = n.get("headline", ""), n.get("choke_points", [])[:4]
        except Exception as e:
            out["headline"] = ""
            out["narration_error"] = str(e)[:200]
    _fc_cache[key] = out
    return out
