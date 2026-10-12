"""Scope tagging. A chunk's scope comes from, in order:
  1. an explicit section marker in the document;
  2. the classifier, for documents that arrived without a scope in frontmatter (or with --classify);
  3. the document default.
The classifier can only tighten: it moves a chunk (or a whole document) into people, finance, legal, or exec,
or leaves it.
It cannot move anything toward public. A false deny is a shrug; a false allow is the failure.
"""
from __future__ import annotations
from config import SCOPES
from ingest.llm import ask_json

RESTRICTED = ["people", "finance", "legal", "exec"]

SYSTEM = """You tag passages of company documents for access control. For each passage decide whether it \
contains material that must be restricted to one of these groups:

people  - pay, salary bands, equity grants, performance ratings, promotion decisions, HR cases, attrition analysis
finance - non-public financial results, budgets, forecasts, margins, accounting treatment, reserves
legal   - privileged legal advice, dispute status, negotiating positions, legal exposure
exec    - board matters, acquisitions, strategy not yet announced, decisions about named customers made at executive level

Answer "keep" when the passage is ordinary for a document of its kind. Only restrict when the passage itself \
contains restricted material; a mention that a restricted topic exists is not enough. When unsure between keep \
and a restricted group, choose the restricted group.

Also judge the document as a whole. Some documents are restricted in their entirety whatever a single passage \
looks like: board and committee minutes and board papers are exec; legal memos and advice are legal; payroll, \
compensation and review records are people; budgets, forecasts and close workpapers are finance. Otherwise "keep".

Return {"document": "keep" | "people" | "finance" | "legal" | "exec",
        "tags": ["keep" | "people" | "finance" | "legal" | "exec", ...]}
with exactly one tag per passage, in order."""

def tag(doc, classify: bool | None = None) -> None:
    """Fill chunk.scope in place."""
    if doc.default_scope not in SCOPES:
        raise ValueError(f"{doc.title}: unknown scope {doc.default_scope!r}")
    for c in doc.chunks:
        if c.explicit and c.scope not in SCOPES:
            raise ValueError(f"{doc.title}: unknown scope marker {c.scope!r}")
    use_classifier = (not doc.pretagged) if classify is None else classify
    todo = [c for c in doc.chunks if not c.explicit]
    if use_classifier and todo and doc.default_scope not in RESTRICTED:
        tags = _classify(doc, todo)
        for c, t in zip(todo, tags):
            c.scope = t if t in RESTRICTED else doc.default_scope
    else:
        for c in todo:
            c.scope = doc.default_scope

def _classify(doc, chunks) -> list:
    out = []
    for i in range(0, len(chunks), 20):
        batch = chunks[i:i + 20]
        body = "\n\n".join(f"<passage n=\"{j + 1}\">\n{c.content}\n</passage>" for j, c in enumerate(batch))
        res = ask_json(SYSTEM, f"Document: {doc.title} (source: {doc.source}, default: {doc.default_scope})\n\n{body}")
        tags = res.get("tags", [])
        if len(tags) != len(batch):
            raise ValueError(f"{doc.title}: classifier returned {len(tags)} tags for {len(batch)} passages")
        floor = res.get("document", "keep")            # whole-document restriction covers untagged passages
        out.extend(t if t in RESTRICTED else floor for t in tags)
    return out
