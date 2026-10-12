"""Generate the filler documents of the synthetic corpus with the ingest model.

The eight demo-critical documents (handbook, sales playbook, legal memo, finance wiki
rev-rec, board minutes, comp bands, two support KB refund articles) are written by hand
and are NOT touched here: the planted facts and the 30-vs-45-day conflict live in them.

  python -m ingest.make_corpus            # writes missing files into corpus/
  python -m ingest.make_corpus --force    # regenerates every filler
"""
from __future__ import annotations
import sys, pathlib, concurrent.futures as cf
from ingest.llm import ask

CORPUS = pathlib.Path(__file__).resolve().parent.parent / "corpus"

COMPANY = ("Kestrel Ridge is a fictional B2B software company of about 310 people (Denver, Lisbon, remote). "
           "Its product is Ridgeline, an analytics platform for freight and logistics operators. "
           "Customers are trucking fleets, freight brokers, and third-party logistics providers.")

# slug, title, source, scope, brief
FILLERS = [
 ("sales-pricing-guide", "Pricing and Packaging Guide", "sales-playbook", "sales",
  "List prices for three tiers (Team, Business, Enterprise), per-seat and per-connected-fleet pricing, what each tier includes, how to quote add-ons."),
 ("sales-competitive-battlecard", "Competitive Battlecard", "sales-playbook", "sales",
  "How Ridgeline compares with three fictional competitors (FleetLens, Haulmetric, Cargoscope): where we win, where we lose, landmines to set, objections and responses."),
 ("sales-territory-plan-fy2027", "Territory Plan FY2027", "sales-playbook", "sales",
  "Regional territory split for North America and EMEA, named-account rules, how inbound leads are routed, rules of engagement between account executives."),
 ("sales-onboarding-first-30-days", "Sales Onboarding: First 30 Days", "sales-playbook", "sales",
  "Week-by-week plan for a new account executive: systems access, shadowing calls, product certification, first pipeline review. Defines common sales acronyms used at the company."),
 ("sales-security-questionnaire-answers", "Standard Answers to Customer Security Questionnaires", "sales-playbook", "sales",
  "Approved answers on data residency, encryption, SSO, audit reports, subprocessors, and incident notification, for reps filling out customer security reviews."),
 ("support-kb-getting-started", "Support KB - Getting Started with Ridgeline", "support-kb", "public",
  "Customer-facing: creating a workspace, inviting users, connecting the first telematics data source, building the first dashboard."),
 ("support-kb-sso-setup", "Support KB - Setting Up Single Sign-On", "support-kb", "public",
  "Customer-facing: SAML SSO setup steps for two common identity providers, attribute mapping, testing, common errors and fixes."),
 ("support-kb-data-connectors", "Support KB - Data Connectors and Sync Schedules", "support-kb", "public",
  "Customer-facing: supported telematics, TMS and ELD connectors, sync frequency, backfill limits, what to do when a sync fails."),
 ("support-kb-billing-faq", "Support KB - Billing FAQ", "support-kb", "public",
  "Customer-facing: invoices, payment methods, changing seat counts mid-term, tax documents, updating billing contacts. Do not state any refund window; point to the separate refund policy article."),
 ("support-kb-status-and-sla", "Support KB - Service Levels and Status Page", "support-kb", "public",
  "Customer-facing: uptime commitment of 99.9 percent, support response targets by severity, how service credits are requested, where the status page is."),
 ("support-escalation-runbook", "Support Escalation Runbook", "support-kb", "support",
  "Internal to support: severity definitions, when to page the on-call engineer, escalation ladder by role (no personal names), customer communication cadence during an incident."),
 ("support-macros-common-issues", "Support Macros for Common Issues", "support-kb", "support",
  "Internal to support: canned responses and diagnostic steps for login problems, stale dashboards, connector authentication failures, export timeouts."),
 ("support-quality-rubric", "Support Quality Rubric", "support-kb", "support",
  "Internal to support: how tickets are scored for accuracy, tone, and resolution; targets for first response and time to resolution; how reviews are sampled."),
 ("finance-wiki-expense-policy", "Finance Wiki - Expense and Procurement Policy", "finance-wiki", "internal",
  "Company-wide: purchase approval thresholds, vendor onboarding steps, corporate card rules, how to submit expenses, month-end cutoff dates."),
 ("finance-wiki-fy2027-budget", "Finance Wiki - FY2027 Operating Budget", "finance-wiki", "finance",
  "Confidential: budget by department, headcount plan by quarter, planned burn, key assumptions on bookings growth and gross margin, contingency triggers."),
 ("finance-wiki-forecast-method", "Finance Wiki - Bookings and Cash Forecast Method", "finance-wiki", "finance",
  "Confidential: how the weekly bookings forecast is built from pipeline stages and weights, cash collection assumptions, who reviews it and when."),
 ("finance-wiki-month-end-close", "Finance Wiki - Month-End Close Calendar", "finance-wiki", "finance",
  "Confidential: day-by-day close calendar, owners by role, reconciliations required, review and sign-off steps, common causes of late close."),
 ("finance-wiki-unit-economics", "Finance Wiki - Unit Economics and Margin", "finance-wiki", "finance",
  "Confidential: gross margin by tier, hosting cost per connected fleet, customer acquisition cost and payback period, how these are computed."),
 ("legal-contracting-guide", "Legal - Contracting Guide for Non-Lawyers", "legal-memo", "internal",
  "Company-wide: when a contract needs Legal review, who can sign what, how to request an NDA, standard turnaround times, what never to agree to without Legal."),
 ("legal-memo-data-processing", "Legal Memo - Data Processing Addendum Positions", "legal-memo", "legal",
  "Privileged: the company's fallback positions when customers negotiate the data processing addendum: liability caps, audit rights, subprocessor notice, breach notification timing."),
 ("legal-memo-open-disputes", "Legal Memo - Open Customer Disputes", "legal-memo", "legal",
  "Privileged: status of three open disputes with fictional customers (a service-credit claim, a non-payment, an early-termination claim), exposure estimates, recommended posture."),
 ("legal-memo-ip-and-open-source", "Legal Memo - Open Source Licence Compliance", "legal-memo", "legal",
  "Privileged: findings from a licence audit of product dependencies, two copyleft components that need remediation, recommended policy for engineers."),
 ("people-hiring-process", "Hiring Process Guide", "people-ops", "internal",
  "Company-wide: opening a requisition, interview loop structure, scorecards, debrief, offer approval steps by role. No salary figures."),
 ("people-performance-calibration-notes", "Performance Calibration Notes - August 2026", "people-ops", "people",
  "Confidential: outcome of the August calibration: rating distribution by function, promotion counts by level, three anonymized difficult cases and how they were resolved."),
 ("people-benefits-guide", "Benefits Guide", "people-ops", "internal",
  "Company-wide: health cover, retirement matching, parental leave, learning budget, wellness stipend, how to enrol and when."),
 ("people-attrition-report-q3", "Attrition and Engagement Report - Q3 2026", "people-ops", "people",
  "Confidential: voluntary and involuntary attrition by function, exit interview themes, engagement survey scores, flight-risk analysis by team (no named individuals)."),
 ("exec-strategy-memo-fy2027", "Executive Strategy Memo FY2027", "board-minutes", "exec",
  "Executive team only: three strategic bets for FY2027 (moving up-market, a predictive maintenance module, EMEA expansion), what gets cut to fund them, risks."),
 ("exec-acquisition-evaluation", "Acquisition Evaluation - Route Optimization Target", "board-minutes", "exec",
  "Executive team only: evaluation of acquiring a fictional small route-optimization company called Wayfold: strategic fit, price range under discussion, integration risks, open diligence questions."),
 ("board-minutes-2026-q2", "Board Minutes - Q2 2026", "board-minutes", "exec",
  "Minutes of the Q2 2026 board meeting: financial review with ARR and retention figures, product roadmap update, discussion of sales leadership hiring, resolutions. Do not mention refunds."),
 ("eng-postmortem-ingest-outage", "Postmortem - Telematics Ingest Outage, July 2026", "postmortem", "internal",
  "Blameless postmortem: a 3 hour 40 minute outage of the telematics ingest pipeline caused by a queue misconfiguration during a deploy. Timeline, impact, root cause, what went well, action items."),
 ("eng-postmortem-dashboard-latency", "Postmortem - Dashboard Latency Regression, September 2026", "postmortem", "internal",
  "Blameless postmortem: dashboards loading in 20+ seconds for two days after a query-planner change. Timeline, detection gap, root cause, remediation, action items."),
 ("eng-oncall-handbook", "Engineering On-Call Handbook", "eng-wiki", "internal",
  "Company-internal: on-call rotation rules, paging policy, severity levels, handoff checklist, how to declare and run an incident."),
 ("eng-architecture-overview", "Ridgeline Architecture Overview", "eng-wiki", "internal",
  "Company-internal: high-level architecture: ingest pipeline, stream processing, warehouse, query layer, dashboard service, tenancy model, main dependencies."),
 ("product-roadmap-h1-2027", "Product Roadmap H1 2027", "product-wiki", "internal",
  "Company-internal: themes and committed items for H1 2027, what moved out and why, dependencies between teams, how customer requests are weighed."),
 ("product-release-notes-2026-09", "Release Notes - September 2026", "product-wiki", "public",
  "Public release notes: new features, improvements, and fixes shipped in September 2026 for Ridgeline."),
 ("marketing-messaging-guide", "Messaging and Positioning Guide", "marketing", "internal",
  "Company-internal: positioning statement, three value pillars, proof points, words we use and avoid, boilerplate descriptions of 25, 50 and 100 words."),
 ("public-security-overview", "Security and Compliance Overview", "website", "public",
  "Public: summary of the security programme: certifications, encryption, access control, data residency options, responsible disclosure contact."),
 ("public-company-overview", "About Kestrel Ridge", "website", "public",
  "Public: company story, what Ridgeline does, who it serves, offices, values."),
 ("it-systems-access-guide", "IT Systems and Access Guide", "it-wiki", "internal",
  "Company-internal: how to request access to systems, device standards, software installation policy, offboarding steps, IT help contact routes."),
 ("cs-customer-health-scoring", "Customer Health Scoring", "cs-wiki", "internal",
  "Company-internal: how the customer health score is calculated from usage, support load, sponsor engagement and data freshness; what each band triggers."),
]

SYSTEM = (f"You write realistic internal and external documents for a fictional company. {COMPANY}\n\n"
          "Write the document in Markdown. Start with a single '# ' title line, then 5 to 8 '## ' sections. "
          "Aim for 450 to 700 words. Be concrete: specific numbers, role titles, steps, dates in 2026. "
          "Write like a real working document, plainly, without marketing gloss. "
          "Invent people only as role titles, not personal names, unless the brief names someone. "
          "Hard limits: do not state any refund window or refund approver; do not state salary or compensation "
          "figures unless the brief asks for them; do not include frontmatter or code fences around the document.")

def generate(item):
    slug, title, source, scope, brief = item
    body = ask(SYSTEM, f"Document title: {title}\nAudience scope: {scope}\nBrief: {brief}", max_tokens=4000)
    if body.startswith("```"):
        body = body.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    front = f'---\ntitle: "{title}"\nsource: {source}\nscope: {scope}\n---\n'
    (CORPUS / f"{slug}.md").write_text(front + body + "\n")
    return slug, len(body.split())

def main():
    force = "--force" in sys.argv
    todo = [f for f in FILLERS if force or not (CORPUS / f"{f[0]}.md").exists()]
    with cf.ThreadPoolExecutor(8) as pool:
        for slug, words in pool.map(generate, todo):
            print(f"{slug}: {words} words")
    print(f"{len(list(CORPUS.glob('*.md')))} documents in corpus/")

if __name__ == "__main__":
    main()
