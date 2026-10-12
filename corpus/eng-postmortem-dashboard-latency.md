---
title: "Postmortem - Dashboard Latency Regression, September 2026"
source: postmortem
scope: internal
---
# Postmortem: Dashboard Latency Regression, September 2026

## Summary

From the Sept 7 deploy until the rollback on Sept 9, Ridgeline dashboards took 20 seconds or more to load for most tenants. The cause was a change to the query planner's default configuration that disabled partition pruning on the freight event tables. No data was lost or incorrect. The problem was slowness. This postmortem is blameless and focuses on the system and the process.

## Impact

- **Duration:** about 49 hours, from the Sept 7 14:20 MT deploy to full recovery at Sept 9 13:05 MT.
- **Affected surfaces:** fleet utilization, on-time delivery, and lane profitability dashboards. Alerting, API endpoints, and exports were not affected.
- **Tenants:** 212 of 268 active tenants had dashboards above 20 seconds at p95. The most affected were tenants with more than 18 months of event history.
- **Support load:** 41 tickets, 9 of them escalations from enterprise accounts.

## Timeline (all times MT)

- **Sept 7, 14:20:** Planner configuration change ships as part of release 4.18. It enables adaptive statistics and changes the default for partition pruning on `freight_events`.
- **Sept 7, 16:00:** Query p95 on dashboard endpoints rises from about 1.4 s to 6 s. No alert fires because the alert threshold is set on API p99 and dashboard render time is not monitored.
- **Sept 8, 09:30:** First support ticket reports slow dashboards. Tier 1 support treats it as a client-side issue and asks for a browser cache clear.
- **Sept 8, 15:10:** Second and third tickets from enterprise tenants. Support opens an internal incident and pages the Platform SRE on-call.
- **Sept 8, 17:45:** Platform SRE confirms the slowdown reproduces on staging with the release 4.18 config. Query plans show full scans on `freight_events`.
- **Sept 9, 10:20:** Data Platform identifies stale partition statistics after a backfill on Sept 5 as a contributing factor.
- **Sept 9, 13:05:** Config flag reverted, statistics refreshed on affected partitions, p95 back under 2 s.

## Detection Gap

We detected this through customer tickets roughly 19 hours after the regression began. Three gaps made this possible:

1. Latency alerting covered API p99 only. Dashboard render time, which is what customers see, had no alert.
2. The synthetic check logs in and loads the home page, which is served from cache and does not exercise the planner.
3. Tier 1 support had no runbook entry for "slow dashboards" that routed to Platform SRE, so the first ticket was treated as a local problem.

## Root Cause

The release 4.18 planner change set `adaptive_stats=on` and changed the default `partition_pruning` mode from `strict` to `hint`. Under `hint` mode, the planner trusts table statistics to choose partitions. The statistics on `freight_events` were stale after the Sept 5 backfill, which added about 2.1 billion rows across 14 monthly partitions without a statistics refresh. The planner estimated the partitions were small and chose full scans. Staging tests used a 90-day dataset that did not include the backfilled range, so the regression did not appear before release.

## Remediation

- **Immediate:** reverted the planner flags to `strict` (Sept 9, 13:05). Ran `ANALYZE` on all 14 backfilled partitions.
- **Short term:** added a post-backfill step to the migration runbook that requires a statistics refresh and a query-plan check before the backfill is marked complete.
- **Validation:** replayed the top 200 dashboard queries from production against staging with full history. p95 was 1.6 s with the change disabled and 1.5 s with the change re-enabled after the statistics refresh, so the change is safe to ship again once the runbook step is in place.

## Action Items

| Action | Owner (role) | Due |
|---|---|---|
| Add dashboard render-time p95 alert, 5 s warning and 10 s page | Platform SRE lead | Sept 18, 2026 |
| Replace home-page synthetic with a dashboard query check against a full-history tenant | Platform SRE | Sept 25, 2026 |
| Add "slow dashboard" runbook entry routing to Platform SRE on-call | Support operations lead | Sept 16, 2026 |
| Require statistics refresh and plan check in backfill runbook | Data Platform lead | Sept 14, 2026 |
| Include full-history dataset in staging performance suite | QA lead | Oct 2, 2026 |
| Re-enable adaptive stats behind a canary flag, 5% of tenants | Data Platform lead | Oct 9, 2026 |
