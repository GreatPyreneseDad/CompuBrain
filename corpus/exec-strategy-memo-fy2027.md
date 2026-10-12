---
title: "Executive Strategy Memo FY2027"
source: board-minutes
scope: exec
---
# Executive Strategy Memo FY2027

## Purpose and decision requested

This memo sets out three strategic bets for FY2027, what we propose to cut to fund them, and the main risks. It is for the executive team only. We need approval of the bets and the funding changes at the 14 May 2026 leadership review. Anything not approved there goes back into the FY2027 plan as an open item.

## Context

FY2026 closed with 214 paying fleet and broker accounts and roughly $38M in ARR. Net revenue retention is 109%, but new logo growth has slowed for two quarters. Win/loss data from Q1 2026 shows we lose most often to two causes: buyers at larger carriers want SSO, audit logs, and role-based access that we only partly support, and smaller fleets churn when they cannot see equipment health alongside dispatch data. Both problems are visible in the account data. We are not guessing.

## Bet 1: Move up-market

We will target fleets over 500 power units and 3PLs with more than $200M in annual freight volume. This requires enterprise security features (SAML SSO, granular roles, audit export), a dedicated enterprise support tier, and two named solutions engineers for accounts above $150K ACV.

Target: 18 enterprise accounts signed by end of FY2027, average ACV of $140K, for about $2.5M in new ARR.

Owner: VP Product, with the Head of Sales as co-owner for pipeline.

## Bet 2: Predictive maintenance module

We will ship a predictive maintenance module that uses telematics and fault-code history to flag components likely to fail within 14 days. The current data pipeline already ingests most of the required signals from our three largest telematics partners. The gap is the model and the alerting workflow.

Target: general availability by 30 September 2026, attached to at least 40% of accounts within two quarters of launch. We will price it as an add-on at roughly 20% of base subscription. Owner: Director of Data Science, reporting to VP Product.

## Bet 3: EMEA expansion

We will enter the UK, Netherlands, and Germany using the Lisbon team as the base for pre-sales and support. Two EU-based account executives and one solutions engineer will be hired in Q3 2026. Hosting for EU customers moves to an EU region by 31 July 2026, which is a prerequisite and is already scoped.

Target: 12 EMEA customers and $1.1M ARR by end of FY2027. We are not planning a local entity beyond what Lisbon already supports; we will revisit that in Q1 2027 if we pass 8 customers.

Owner: Chief Revenue Officer.

## What gets cut to fund them

The three bets total about $6.4M in incremental spend for FY2027. We propose to fund it as follows:

- **Legacy integrations (-$1.2M):** Retire four low-usage integrations with fewer than 10 active accounts each. Affected customers get a migration path by 30 June 2026.
- **Custom reporting builder (-$0.9M):** Freeze the roadmap and maintain the current version only. Most usage is served by standard dashboards.
- **Marketing programs in APAC (-$0.7M):** Pause paid acquisition in APAC; keep the two existing partner relationships.
- **Hiring freeze on G&A roles (-$1.0M):** Hold open G&A requisitions until Q4 2026, except finance and security.
- **Vendor consolidation (-$0.6M):** Consolidate analytics tooling from three vendors to one.

Net new investment after these cuts is about $2.0M. The remainder comes from forecasted expansion revenue, which is already in the plan.

## Key risks

- **Enterprise deals slip.** Long security reviews could push revenue into FY2028. Mitigation: start SOC 2 Type II renewal evidence collection in April.
- **Model accuracy disappoints.** If the predictive module cannot reach 70% precision on 14-day failures in the pilot, we ship it as a reporting feature rather than an alert product. Pilot results are due 15 July 2026.
- **EMEA hosting delay.** Missing 31 July pushes EU launch by a quarter. We accept that risk; we will not sign EU customers before the region is live.
- **Cut customers push back.** Four integration retirements may trigger escalations from two or three accounts. Account teams have the migration plan before the notice goes out.
- **Execution load.** Three bets at once stretches product and engineering. We cap active epics at nine and review in the monthly exec meeting.

## Decisions and next steps

1. Approve the three bets and the funding changes at the 14 May 2026 review.
2. VP Product to deliver the enterprise security scope and sequencing by 29 May 2026.
3. Chief Revenue Officer to open EMEA hiring requisitions by 1 June 2026.
4. Director of Data Science to confirm pilot customers for the predictive module by 15 June 2026.
