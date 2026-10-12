---
title: "Engineering On-Call Handbook"
source: eng-wiki
scope: internal
---
# Engineering On-Call Handbook

## Purpose and scope

This handbook covers how engineering on-call works for Ridgeline, including rotation rules, paging, severity levels, incident response, and handoffs. It applies to everyone on the Platform, Data Pipelines, and Integrations teams. Customer-facing support escalations follow the Support Escalation Guide, but once an escalation is classified as a production incident, this document governs.

## Rotation structure

- Each team runs a primary and a secondary on-call engineer, rotating weekly. Weeks start Monday 09:00 Mountain Time.
- The Incident Commander (IC) role is separate from on-call. Any on-call engineer can declare an incident and act as IC until a Senior Engineer or Engineering Manager takes over.
- A rotation schedule is published in the on-call calendar at least six weeks in advance. Swaps must be posted in #oncall-schedule at least 48 hours before the shift and approved by the team's Engineering Manager.
- No one should be on primary for more than two consecutive weeks. Lisbon and Denver engineers are paired across time zones so that each region has coverage during its business hours.

## Severity levels

| Level | Definition | Example | Response target |
|---|---|---|---|
| SEV1 | Ridgeline unavailable for multiple customers, or data loss or corruption | Ingest API returning 5xx for all tenants | Acknowledge within 5 minutes |
| SEV2 | Major feature degraded for a customer segment, no data loss | Route ETA calculations stale for one region | Acknowledge within 15 minutes |
| SEV3 | Minor degradation or a workaround exists | Nightly report export delayed by 2 hours | Next business day |

If you are unsure between two levels, choose the higher one. You can downgrade later.

## Paging policy

- Pages go out through PagerDuty. Only alerts tagged `actionable` page a human. Dashboards and informational alerts go to Slack.
- Primary is paged first. If no acknowledgment arrives within the response target, the page escalates to secondary, then to the Engineering Manager after an additional 10 minutes.
- Do not silence a page without a reason written in the incident channel. Silencing a page for more than 4 hours requires Engineering Manager approval.
- Repeated noisy alerts are a bug. File a ticket in the ON-CALL project within two business days, labeled `alert-noise`.

## Declaring and running an incident

1. **Declare.** Create a channel named `#inc-YYYYMMDD-short-description`, post the severity, and set the topic to the current IC's name.
2. **Assign roles.** IC coordinates. A Scribe records a timeline in the incident doc. A Comms lead drafts status page updates. Engineers doing the fix report to IC, not to each other.
3. **Stabilize first.** Roll back, fail over, or disable the affected feature before investigating root cause. Log every production change in the channel with a timestamp.
4. **Update cadence.** SEV1 updates every 30 minutes on the status page. SEV2 every 60 minutes. Post an update even if nothing has changed.
5. **Resolve.** IC declares resolution only after error rates have returned to baseline for 30 minutes. Status page is updated to resolved.
6. **Review.** SEV1 and SEV2 incidents get a written postmortem within five business days, using the template in the incident doc library. Postmortems are blameless and reviewed in the weekly Reliability meeting.

## Handoff checklist

At the end of each shift, the outgoing on-call engineer completes this checklist and posts it to the team channel:

- [ ] Open incidents listed, with current status and owner
- [ ] Alerts acknowledged in the last 7 days that did not resolve, with links
- [ ] Any production changes in flight, including planned deploys or migrations
- [ ] Known flaky alerts and whether a ticket exists
- [ ] Customer-facing commitments due in the next 48 hours
- [ ] Incoming on-call confirms receipt in the channel

A handoff is complete only when the incoming engineer replies with confirmation. Until then, the outgoing engineer stays reachable.

## Review and updates

This handbook is owned by the Platform Engineering Manager and reviewed each quarter. The next scheduled review is in July 2026. Propose changes by pull request to the `eng-handbooks` repository. Changes to severity definitions or paging thresholds also need sign-off from the Director of Engineering.
