"""The gate. One Snowflake session per role, each holding that role and no other.

A question runs on the session of the asker's role. The row access policy in the database decides
what that session can read. Nothing here passes a scope, so nothing here can widen one.
"""
from __future__ import annotations
import threading
from sf.conn import connect

ASKER_ROLES = {"BRAIN_SALES", "BRAIN_EXEC", "BRAIN_SUPPORT_AGENT"}
_sessions, _locks, _guard = {}, {}, threading.Lock()

def _session(role: str):
    with _guard:
        if role not in _sessions:
            conn = connect(role)
            conn.cursor().execute("use secondary roles none")
            _sessions[role], _locks[role] = conn, threading.Lock()
        return _sessions[role], _locks[role]

def query(role: str, sql: str, params=None) -> list:
    conn, lock = _session(role)
    with lock:
        cur = conn.cursor()
        cur.execute(sql, params)
        return cur.fetchall() if cur.description else []

def warm():
    for role in sorted(ASKER_ROLES | {"BRAIN_ROUTER"}):
        query(role, "select 1")
