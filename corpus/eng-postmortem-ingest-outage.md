---
title: "Postmortem - Telematics Ingest Outage, July 2026"
source: postmortem
scope: internal
---
# Postmortem: Telematics Ingest Outage, July 2026

## Summary

On Tuesday 14 July 2026, the telematics ingest pipeline stopped processing device pings for 3 hours 40 minutes, from 13:12 to 16:52 UTC. The cause was a queue configuration change shipped in a routine deploy of the ingest service. The change set consumer prefetch and in-flight limits to values copied from a low-volume reporting queue. Throughput fell from roughly 3,000 messages per second to about 40, the backlog grew faster than consumers could drain it, and no one was paged until 30 minutes after the first symptom. This review is blameless. It focuses on how the system and process allowed the change to reach production and stay there.

## Impact

- **Data delay:** Pings from about 11,400 active vehicles were delayed. Most were recovered from the backlog after the fix, with full processing completed by 18:10 UTC.
- **Data loss:** About 2,180 device units exceeded their on-device buffer during the window. Roughly 0.4% of pings from those units were not recovered. Affected fleets were notified with the list of vehicle IDs and time gaps.
- **Customer-facing:** Ridgeline dashboards showed stale location and fuel data. Three fleet customers opened support tickets. Two brokers asked for root cause; this document is the answer to that request.
- **Internal:** Two engineers were pulled off planned work for the rest of the day. The on-call rotation was reviewed the following week.

## Timeline (UTC)

- **13:12** Deploy of ingest service v4.18 begins. Config template change included queue settings for `telematics-ingest-q`.
- **13:19** Deploy completes on all consumer nodes. Consumer lag begins to climb.
- **13:31** Backlog-age alert fires at the 30-minute threshold. Alert routed to the secondary queue, not acknowledged for 9 minutes.
- **13:40** On-call acknowledges, sees backlog growing, begins checking recent deploys.
- **13:52** Incident declared (Sev 2). Incident commander role assigned to the on-call platform engineer.
- **14:15** Consumer metrics show prefetch and in-flight values of 1. Config diff matches the reporting-queue template.
- **14:20** Decision to roll back. Rollback starts, but the rollback pipeline requires a manual approval step that takes 25 minutes.
- **15:05** Rollback completes on all consumer nodes. Throughput recovers to 1,100 messages per second.
- **15:40** Throughput reaches full rate, but the backlog is still 2.1 million messages.
- **16:52** Backlog drained, pipeline declared healthy.
- **18:10** Full reprocessing complete. Incident closed.

## Root cause

The ingest service's deploy template was generated from a shared queue template used for several services. The template defaulted `consumer.prefetch` and `consumer.max_inflight` to 1, which was appropriate for the reporting queue. The telematics ingest queue needs values of 500 and 64. A values override existed for this queue but was not applied when the template was regenerated during the v4.18 change.

Pre-deploy checks validated that the config file parsed and matched the schema. They did not check that numeric values fell within expected ranges for the target queue, and they did not run a throughput check in staging under production-like load. Staging runs at about 5% of production volume, so the low throughput did not show up there.

## What went well

- The on-call engineer correlated the backlog growth with the deploy within 20 minutes of acknowledgment.
- Incident roles were assigned quickly once the incident was declared.
- Affected customers were notified with specific vehicle and time-range data, not general status updates.
- The reprocessing job was idempotent, so no duplicate records were written during recovery.

## Action items

| # | Action | Owner (role) | Due |
|---|---|---|---|
| 1 | Add per-queue value overrides to the shared template so generated configs cannot silently inherit reporting-queue defaults | Platform Engineering Lead | 31 July 2026 |
| 2 | Add range checks for prefetch, in-flight, and partition settings to pre-deploy validation | Platform Engineer | 14 August 2026 |
| 3 | Lower the backlog-age alert threshold to 5 minutes for ingest queues and route it to the primary on-call rotation | SRE Lead | 24 July 2026 |
| 4 | Add a throughput canary to the deploy pipeline that halts rollout if consumer rate drops more than 50% in the first 5 minutes | Deploy Tooling Engineer | 28 August 2026 |
| 5 | Evalu
