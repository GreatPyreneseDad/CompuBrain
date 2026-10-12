"""token -> principal -> role -> {scopes, profile}. Read through the router role, cached."""
from __future__ import annotations
import json, hashlib, threading
from dataclasses import dataclass
from core import gate

@dataclass(frozen=True)
class Principal:
    id: str
    handle: str
    kind: str            # human | agent
    role_id: str
    sf_role: str         # the Snowflake role this principal's questions run as
    scopes: tuple
    profile: dict

_cache, _lock = {}, threading.Lock()

def resolve(token: str) -> Principal | None:
    h = hashlib.sha256(token.encode()).hexdigest()
    with _lock:
        if h in _cache:
            return _cache[h]
    rows = gate.query("BRAIN_ROUTER", """
        select p.id, p.handle, p.kind, p.role_id, r.sf_role, r.profile,
               (select listagg(rs.scope, ',') within group (order by rs.scope)
                from role_scope rs where rs.sf_role = r.sf_role)
        from principal p join brain_role r on r.id = p.role_id
        where p.token_hash = %s""", (h,))
    if not rows:
        return None
    pid, handle, kind, role_id, sf_role, profile, scopes = rows[0]
    p = Principal(pid, handle, kind, role_id, sf_role, tuple((scopes or "").split(",")), json.loads(profile))
    with _lock:
        _cache[h] = p
    return p
