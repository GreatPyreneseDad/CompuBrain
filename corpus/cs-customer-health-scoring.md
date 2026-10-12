---
title: "Customer Health Scoring"
source: cs-wiki
scope: internal
---
# Customer Health Scoring

## Purpose

This document describes how the customer health score is calculated for each Ridgeline account, what goes into it, and what each band triggers. Customer Success Managers (CSMs) own the score. Support Operations maintains the support inputs, and the Data Platform team maintains the freshness inputs. The score is recalculated nightly and shown on the account page in the CS console. Version 2.1 takes effect 2026-03-02 and replaces the version 2.0 weights.

## Components and weights

The score is a weighted sum of four components, each normalized to 0-100 before weighting.

| Component | Weight | Measured as |
|---|---|---|
| Usage | 40% | Share of licensed seats active in the last 14 days, compared with the account's 90-day baseline |
| Sponsor engagement | 25% | Logins, report views, and meeting attendance by the named executive sponsor in the last 30 days |
| Support load | 20% | Open ticket count and severity-weighted ticket age, inverted so more load scores lower |
| Data freshness | 15% | Percentage of connected data sources that have synced successfully in the last 24 hours |

Usage uses seat activity rather than raw session counts, so one heavy user does not mask a dormant team. An account with fewer than five licensed seats is scored on sponsor engagement and freshness only, with the weights rescaled to 62.5% and 37.5%.

## Scoring detail

- **Usage:** 100 if 80% or more of seats are active against baseline. Scale linearly down to 0 at 30%.
- **Sponsor engagement:** 100 if the sponsor has logged in at least four times in 30 days. 50 if at least once. 0 if no activity and no meeting in 60 days.
- **Support load:** Start at 100. Subtract 10 per open P2 ticket and 25 per open P1 ticket, to a floor of 0. Subtract a further 15 if any ticket is older than 10 business days.
- **Data freshness:** Direct percentage, so 95% of sources syncing gives 95.

## Bands and triggers

**Green (75-100).** No action beyond the standard quarterly business review. The CSM logs the score in the monthly portfolio review.

**Yellow (50-74).** The CSM reviews the component breakdown within two business days and records a primary driver in the account notes. If the driver is data freshness, the CSM opens a ticket with Data Platform. If it is support load, the CSM asks Support Operations for a triage review.

**Orange (30-49).** The CSM must contact the sponsor within five business days and schedule a working session within 15 business days. The Account Executive is notified so the renewal forecast can be updated. The account appears on the weekly at-risk list.

**Red (below 30).** The CSM Lead and the Account Executive are notified the same day. A written recovery plan with named owners and dates is due within five business days, and the plan is reviewed at the next weekly at-risk meeting. The account is flagged in the renewal forecast as at risk.

## Overrides

A CSM may override the band by one level, up or down, with a written reason in the account notes. Overrides above one level require the CS Director's approval and are reviewed in the monthly portfolio meeting. Overrides are tracked so we can see whether they improve forecast accuracy.

## Review cadence

Weights and thresholds are reviewed quarterly by the CS Operations lead. The next review is scheduled for 2026-06-15. Changes to weights require a version bump and a note in the CS console changelog. Historical scores are not recalculated when weights change.
