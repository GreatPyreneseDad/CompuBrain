---
title: "Product Roadmap H1 2027"
source: product-wiki
scope: internal
---
# Product Roadmap H1 2027

## Purpose and scope

This document covers what Product and Engineering have committed to for Ridgeline in January through June 2027, what was pulled out of the plan, and how customer requests are weighed against it. It is for internal use. Customer-facing timing should come from the Account Management team after this plan is locked on December 12, 2026.

Commitments are items with an owner, a staffed team, and a target quarter. Anything else is an intention and is labeled as such.

## Themes for H1 2027

Three themes organize the half:

1. **Settlement-grade data for brokers.** Brokers need freight invoices, carrier payments, and accessorial charges to reconcile against each other without manual exports. This is the largest theme and takes roughly 45% of planned engineering capacity.
2. **Fleet telemetry at scale.** Ingest and query performance for fleets above 2,000 active vehicles. Current p95 query latency on the largest tenant is 8.4 seconds for a 30-day fleet utilization report. The target is under 2 seconds.
3. **Admin and audit controls.** Role-scoped dashboards, export logging, and retention settings. Driven mostly by enterprise security reviews, which have become a blocking item in about one in four renewals.

## Committed items

- **Invoice-to-payment matching v2** (Broker Data team, target end of Feb 2027). Automated match on carrier invoice number, PO, and amount tolerance, with a review queue for exceptions.
- **Telemetry query tier** (Platform team, target end of Mar 2027). Separate read path for reports over 90 days. Owner: Platform Engineering Lead.
- **Export audit log** (Security & Admin team, target mid-Apr 2027). Every CSV or API bulk export logged with user, scope, and row count.
- **Role-scoped dashboards** (Analytics UX team, target end of May 2027). Dispatch, safety, and finance views with field-level permissions.

Each committed item has a named Engineering owner and a Product Manager. Changes to target quarter require sign-off from the VP of Product and the Engineering Director.

## Moved out of H1 and why

Four items were planned for late 2026 or H1 2027 and have been removed from this half:

- **Real-time geofence alerts.** Dropped to H2. The streaming pipeline it depends on is not ready, and two design partners said batch alerts at five-minute intervals are acceptable for now.
- **Multi-currency invoicing.** Dropped indefinitely. Only 3 of 310 active accounts (about 1%) bill outside USD, and the finance integration cost was estimated at six engineer-months.
- **Native ELD vendor connectors beyond the top three.** Reduced to maintenance. Connector support tickets consume about 30% of the Integrations team's time, and adding connectors increases that load linearly.
- **Driver-facing mobile app.** Moved to a research spike in Q1 only. Not a committed item.

## Cross-team dependencies

- Invoice matching v2 depends on the Data Platform team finishing the schema migration for carrier payments, currently due February 6, 2027. If that slips, matching moves to March and the Q2 export work shifts with it.
- The telemetry query tier needs a Security review of the new read path before any customer data is routed through it. Security has committed to a review window in March.
- Role-scoped dashboards depend on the Admin and audit controls being merged first, because permission checks are shared.
- Account Management needs the final list by December 12, 2026, to brief customers. Changes after that date are communicated in the quarterly update, not individually.

## How customer requests are weighed

Requests enter through the product feedback form and are tagged by Customer Success. They are scored on four factors: the number of accounts asking, the ARR of those accounts, whether the request is tied to a renewal or a churn risk, and the engineering cost estimate from the owning team. Requests that touch a committed theme get a bonus weight, but they do not automatically displace committed items.

A single large account can move a request up the list only if it also clears a renewal or security blocker. Feature requests from one account alone go to the backlog review, which meets monthly in the Product Council.

## Review cadence

The roadmap is reviewed at the end of each month. Changes to committed items are logged in the planning doc with the date and reason. The first mid-half review is March 27, 2027.
