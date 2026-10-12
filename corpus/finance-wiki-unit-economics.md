---
title: "Finance Wiki - Unit Economics and Margin"
source: finance-wiki
scope: finance
---
# Finance Wiki: Unit Economics and Margin

**Confidential. Finance and named leadership only. Do not forward outside the finance team.**

Owner: Finance Analytics (FP&A). Last reviewed: 2026-03-31.

## Purpose and scope

This page defines how Kestrel Ridge calculates gross margin by pricing tier, hosting cost per connected fleet, and customer acquisition cost (CAC) with payback period. It covers Ridgeline subscription revenue only. Professional services and hardware pass-through revenue are excluded. Figures are for Q1 2026 unless noted.

## Definitions

- **Connected fleet:** a customer tenant with at least one telematics feed active during the calendar month. A tenant with no active feed is not counted, even if the subscription is billed.
- **Tier:** Starter (up to 50 connected vehicles), Growth (up to 250), Enterprise (contracted, 251 or more).
- **COGS (cost of revenue):** hosting and data storage, third-party telematics and map data fees, payment processing, and the share of Support and Customer Success payroll that handles production issues. R&D, sales, and general G&A are not in COGS.
- **Gross margin:** (subscription revenue minus COGS) divided by subscription revenue.
- **Fully loaded S&M:** all sales and marketing payroll, commissions, paid acquisition, events, and tooling, for the period.

## Gross margin by tier

Q1 2026 results:

| Tier | Share of MRR | Gross margin |
|---|---|---|
| Starter | 22% | 71% |
| Growth | 49% | 78% |
| Enterprise | 29% | 81% |
| Blended | 100% | 77% |

Starter runs lower because support load per dollar is higher and data fees are a larger share of price. Enterprise margin benefits from annual prepayment, which lowers payment processing cost. Commissions are not in COGS, so they do not affect these figures.

## Hosting cost per connected fleet

Hosting cost per connected fleet is total production hosting spend (compute, storage, egress, managed database) divided by the count of connected fleets in the same month. Shared staging and development environments are excluded.

Q1 2026 monthly averages:

- Starter: $168
- Growth: $690
- Enterprise: $2,940
- Blended: $412

Blended cost rose 6% from Q4 2025, mostly from egress on Enterprise telemetry exports. Finance Analytics reviews this line monthly with the Platform Infrastructure lead.

## Customer acquisition cost and payback

**CAC** = fully loaded S&M for the quarter divided by new logos closed in the quarter. Logos that churn within 30 days are removed from the count.

Q1 2026 blended CAC: $18,400.

**Payback period (months)** = CAC divided by (new logo MRR multiplied by gross margin for that tier).

Worked example, Growth tier: CAC $21,000, average new MRR $4,800, gross margin 78%. Monthly gross profit per new logo is $3,744. Payback is $21,000 / $3,744 = 5.6 months.

Blended Q1 2026 payback: 9.4 months.

## Data sources and refresh

- Revenue: billing ledger, reconciled to the general ledger at month close.
- Hosting: cloud provider invoices, tagged by environment. Untagged spend is assigned to production and flagged.
- Connected fleet counts: Platform telemetry job, run on the first business day of each month.
- S&M: payroll system and AP ledger, with commissions from the Sales Ops export.

Figures are refreshed at month close. Restated figures are noted in the change log at the bottom of this page.

## Open items

- Decide whether Enterprise onboarding credits count against new MRR in payback. Current treatment: they do not.
- Confirm allocation share of Support payroll to COGS for the Lisbon team. Current estimate is 60%, pending time-tracking data.
