"""T3 -> T2 -> T1 descent under the gate.

Digests and summaries choose the documents that matter; chunks from those documents are preferred.
Every query here runs on the asker's own session, so each grain is already filtered by scope.
"""
from __future__ import annotations
from dataclasses import dataclass
from core import gate
from ingest import embed
from ingest.llm import ask as llm

@dataclass
class Hit:
    chunk_id: str
    document_id: str
    title: str
    source: str
    scope: str
    content: str
    score: float

EXPAND = ("Rewrite the question as a search query for a company knowledge base: the key terms, with "
          "abbreviations spelled out and two or three close synonyms. One line, no punctuation, no answer.")

def qvec(question: str) -> str:
    text = question
    if embed.provider() == "local":            # lexical vectors need the vocabulary spelled out
        try:
            text = question + " " + llm(EXPAND, question[:600], max_tokens=300)
        except Exception:
            pass                                # expansion is a boost, never a requirement
    v = embed.embed([text], "query")[0]
    return "[" + ",".join(f"{x:.6f}" for x in v) + "]::vector(float, 1024)"

def retrieve(principal, question: str, q: str | None = None):
    q = q or qvec(question)
    role, profile = principal.sf_role, principal.profile
    digests = gate.query(role, f"""
        select topic, scope, content, document_ids, vector_cosine_similarity(embedding, {q}) s
        from digest order by s desc limit 12""")
    summaries = gate.query(role, f"""
        select s.document_id, d.title, s.scope, s.content, vector_cosine_similarity(s.embedding, {q}) sim
        from summary s join visible_document d on d.id = s.document_id order by sim desc limit 8""")
    # Documents the upper tiers point at: the top digests' members, then the top summaries.
    picked = []
    # The asker holds one digest per scope for a topic; the best-matching topic is read across all of them.
    topic = digests[0][0] if digests else None
    on_topic = [r for r in digests if r[0] == topic]
    for i in [r[0] for r in summaries[:4]] + [i for r in on_topic for i in r[3].split(",") if i]:
        if i not in picked:
            picked.append(i)
    picked = picked[:14]
    cols = f"""c.id, c.document_id, d.title, d.source, c.scope, c.content,
               vector_cosine_similarity(c.embedding, {q}) sim
        from chunk c join visible_document d on d.id = c.document_id"""
    rows = gate.query(role, f"select {cols} order by sim desc limit 40")
    if picked:                                   # the best chunk of each picked document is always read
        marks = ",".join(["%s"] * len(picked))
        best = gate.query(role, f"""select {cols} where c.document_id in ({marks})
            qualify row_number() over (partition by c.document_id order by sim desc) = 1""", tuple(picked))
    else:
        best = []
    prefer = set(profile.get("prefer_sources", []))
    def hit(r):
        return Hit(r[0], r[1], r[2], r[3], r[4], r[5],
                   float(r[6]) + (0.05 if r[1] in picked else 0) + (0.02 if r[3] in prefer else 0))
    k = 14 if profile.get("grain") == "chunk" else 8
    out = {h.chunk_id: h for h in sorted((hit(r) for r in best), key=lambda h: -h.score)[:k]}
    per_doc = {}
    for h in out.values():
        per_doc[h.document_id] = 1
    for h in sorted((hit(r) for r in rows), key=lambda h: -h.score):
        if len(out) >= k:
            break
        if h.chunk_id in out or per_doc.get(h.document_id, 0) >= 3:      # no document crowds the context
            continue
        out[h.chunk_id] = h
        per_doc[h.document_id] = per_doc.get(h.document_id, 0) + 1
    hits = sorted(out.values(), key=lambda h: -h.score)[:k]
    return hits, summaries[:4], digests[:2]

def denied_scopes(principal, q: str, k: int = 8) -> list:
    """Scopes the asker lacks that hold near matches, best first. Names and scores only: the router
    reads scope and vector of each chunk, never content."""
    rows = gate.query("BRAIN_ROUTER", f"""
        select scope, max(sim) from (
          select scope, vector_cosine_similarity(embedding, {q}) sim from scope_probe order by sim desc limit {int(k)})
        group by scope order by 2 desc""")
    return [(s, float(sim)) for s, sim in rows if s not in principal.scopes]
