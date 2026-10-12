"""Gate test on Snowflake. Run after 01_schema.sql and `python -m ingest.run_sf corpus/`.

  python -m sf.test_gate

Becomes each asker role in turn and asserts what it can and cannot reach, at all three grains.
Exits non-zero on the first failure.
"""
import sys
from snowflake.connector.errors import ProgrammingError
from sf.conn import connect, as_role

EXPECT = {
    "BRAIN_SALES":         {"scopes": {"public", "internal", "sales"},
                            "approver": True,  "memo45": False, "q3": False},
    "BRAIN_EXEC":          {"scopes": {"public", "internal", "sales", "finance", "legal", "exec"},
                            "approver": True,  "memo45": True,  "q3": True},
    "BRAIN_SUPPORT_AGENT": {"scopes": {"public", "support"},
                            "approver": False, "memo45": False, "q3": False},
}
GRAINS = ["chunk", "summary", "digest"]
passed = 0

def ok(label, cond, detail=""):
    global passed
    if not cond:
        print(f"FAIL {label} {detail}"); sys.exit(1)
    passed += 1
    print(f"ok   {label}")

def one(cur, sql, params=None):
    cur.execute(sql, params)
    return cur.fetchone()[0]

def denied(cur, sql):
    try:
        cur.execute(sql)
    except ProgrammingError:
        return True
    return False

def anywhere(cur, pattern):
    return any(one(cur, f"select count(*) from {g} where content ilike %s", (pattern,)) > 0 for g in GRAINS)

with connect("BRAIN_OWNER") as conn:
    cur = conn.cursor()
    total = one(cur, "select count(*) from chunk")
    ok("owner sees the whole corpus", total > 0, f"({total} chunks)")
    ok("every chunk is embedded", one(cur, "select count(*) from chunk where embedding is null") == 0)

    for role, want in EXPECT.items():
        as_role(cur, role)
        ok(f"{role}: session holds only this role",
           one(cur, "select current_role()") == role and one(cur, "select current_secondary_roles()").count("BRAIN") == 0)
        for g in GRAINS + ["document_scope"]:
            cur.execute(f"select distinct scope from {g}")
            got = {r[0] for r in cur.fetchall()}
            ok(f"{role}: {g} scopes", got and got <= want["scopes"], f"got {sorted(got)}")
        ok(f"{role}: sees fewer chunks than the owner", one(cur, "select count(*) from chunk") < total)
        ok(f"{role}: 30-day window reachable", anywhere(cur, "%30 days%"))
        ok(f"{role}: approver name {'reachable' if want['approver'] else 'unreachable'}",
           anywhere(cur, "%Priya%") == want["approver"])
        ok(f"{role}: 45-day memo {'reachable' if want['memo45'] else 'unreachable'}",
           anywhere(cur, "%45 days%") == want["memo45"])
        ok(f"{role}: Q3 exceptions {'reachable' if want['q3'] else 'unreachable'}",
           anywhere(cur, "%Meridian Health%") == want["q3"])
        ok(f"{role}: comp bands unreachable", not anywhere(cur, "%145,000 to 178,000%"))
        ok(f"{role}: comp document title hidden",
           one(cur, "select count(*) from visible_document where title ilike 'Compensation Bands%'") == 0)
        for t in ["principal", "brain_role", "role_scope", "document", "scope_probe", "ledger"]:
            ok(f"{role}: cannot read {t}", denied(cur, f"select count(*) from {t}"))
        ok(f"{role}: cannot write chunk",
           denied(cur, "insert into chunk (document_id, ord, scope, content) values ('x', 0, 'public', 'x')"))
        ok(f"{role}: cannot rewrite ledger", denied(cur, "update ledger set question = 'edited'")
           and denied(cur, "delete from ledger"))
        cur.execute("insert into ledger (principal_id, role_id, scopes, question, outcome) "
                    "values ('gate-test', %s, '', 'gate test', 'empty')", (role,))
        ok(f"{role}: can append to ledger", True)

    as_role(cur, "BRAIN_ROUTER")
    ok("router resolves a token",
       one(cur, "select r.sf_role from principal p join brain_role r on r.id = p.role_id "
                "where p.token_hash = sha2('demo-maya', 256)") == "BRAIN_SALES")
    ok("router sees scope vectors for every scope", one(cur, "select count(distinct scope) from scope_probe") == 8)
    ok("router cannot read chunk content", denied(cur, "select count(*) from chunk"))

    as_role(cur, "BRAIN_OWNER")
    ok("ledger stamped with the asker's Snowflake role",
       one(cur, "select count(distinct sf_role) from ledger where principal_id = 'gate-test'") == 3)
    cur.execute("delete from ledger where principal_id = 'gate-test'")

print(f"\n{passed} assertions passed")
