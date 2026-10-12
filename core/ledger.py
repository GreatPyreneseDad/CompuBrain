"""Append-only record of who asked what and what they saw. Written on the asker's own session;
asker roles hold INSERT on the ledger and nothing else."""
from __future__ import annotations
import json
from core import gate

def write(principal, question, outcome, denied, cited, answer, tokens_in=0, tokens_out=0):
    gate.query(principal.sf_role, """
        insert into ledger (principal_id, role_id, scopes, question, outcome, denied_scopes,
                            document_ids, chunk_ids, tokens_in, tokens_out, answer)
        values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (principal.id, principal.role_id, ",".join(principal.scopes), question, outcome,
         ",".join(denied), ",".join(sorted({h.document_id for h in cited})),
         ",".join(h.chunk_id for h in cited), tokens_in, tokens_out,
         answer if isinstance(answer, str) else json.dumps(answer)))

def read(limit: int = 50) -> list:
    rows = gate.query("BRAIN_OWNER", """
        select l.asked_at, p.handle, l.role_id, l.sf_role, l.scopes, l.question, l.outcome,
               l.denied_scopes, l.document_ids, l.tokens_in, l.tokens_out, l.answer
        from ledger l left join principal p on p.id = l.principal_id
        order by l.asked_at desc limit %s""", (limit,))
    keys = ["at", "asker", "role", "sf_role", "scopes", "question", "outcome",
            "denied_scopes", "document_ids", "tokens_in", "tokens_out", "answer"]
    return [dict(zip(keys, [str(r[0])] + list(r[1:]))) for r in rows]
