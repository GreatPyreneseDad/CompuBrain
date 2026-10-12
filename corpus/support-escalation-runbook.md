---
title: "Support Escalation Runbook"
source: support-kb
scope: support
---
# Support Escalation Runbook

## Purpose and scope

This runbook is for Support staff handling Ridgeline customer tickets: fleet operators, freight brokers, and 3PL accounts. It defines severity levels, when to page the on-call engineer, who owns each step of an escalation, and how often we update customers during an incident. Engineering has its own incident process, which starts once this runbook hands off to them. Revision date: 2026-03-02. Owner: Support Operations Lead.

## Severity definitions

Assign severity at ticket creation based on customer impact. Re-rate whenever impact changes.

- **SEV1:** Ridgeline is unavailable or returning wrong data for a production customer, or dispatch/ETA data is missing for active loads. Affects multiple accounts or one account with more than 50 active vehicles.
- **SEV2:** A core feature is degraded (reports fail to load, exports time out, alerts delayed more than 30 minutes) for one or more accounts, with a workaround available.
- **SEV3:** A single user cannot complete a task, or a non-critical feature is broken, with no operational impact on loads or dispatch.
- **SEV4:** Questions, feature requests, cosmetic issues, and documentation gaps.

If you are unsure between two levels, choose the higher one and note your reasoning in the ticket. Downgrading is a Tier 2 decision; upgrading is always allowed.

## When to page the on-call engineer

Page on-call through the PagerDuty service "Ridgeline Production" for any of the following:

- Any SEV1, immediately, regardless of time of day.
- Any SEV2 that has lasted more than 60 minutes without a known cause.
- Two or more separate customers reporting the same symptom within 30 minutes.
- Suspected data integrity problems (mismatched load counts, duplicate telemetry, timestamps off by a timezone offset).
- Status page is showing green but customers confirm an outage.

Do not page for SEV3 or SEV4. Create a Jira ticket in the RIDGE project and tag it for the next business-day triage.

When paging, include: account name, affected feature, first-seen time in UTC, number of affected users or vehicles, and whether a workaround exists. Pages without these fields are returned to you for completion.

## Escalation ladder

| Level | Role | Responsible for | Respond within |
|---|---|---|---|
| L1 | Support Specialist | Intake, severity assignment, known-issue check | 15 minutes (business hours), 30 minutes (off hours) |
| L2 | Support Engineer (Tier 2) | Reproduction, account-level diagnosis, workaround | 30 minutes |
| L3 | Support Operations Lead | Customer-facing incident comms, cross-team coordination | 30 minutes for SEV1/SEV2 |
| On-call | Platform on-call engineer | Production diagnosis and fix | 10 minutes for SEV1, 30 minutes for SEV2 |
| Escalation | Director of Customer Operations | Executive customer contact, SEV1 decisions on scope | Within 1 hour for SEV1 |

L1 moves to L2 when reproduction is needed or the issue is not in the known-issues list. L2 pages on-call directly when a page criterion is met. L3 takes over comms for any SEV1 and any SEV2 lasting more than two hours.

## Customer communication cadence

Once a SEV1 or SEV2 is confirmed, the owner (L3 for SEV1, L2 for SEV2 unless L3 is engaged) sends the first update within 20 minutes of acknowledgment. Use the status page and direct email to named account admins.

- **SEV1:** Updates every 30 minutes until resolution, even if the update is "no change, investigating."
- **SEV2:** Updates every 60 minutes.
- **Resolution:** Send a closing message within 30 minutes of the fix being confirmed, with a summary of cause, duration, and any follow-up actions. Do not mark the status page resolved until on-call confirms.

Every update states what we know, what we are doing, and when the next update will come. Do not speculate on root cause in customer messages until engineering has confirmed it.

## Handoff and documentation

Record every escalation in the ticket with timestamps for each level change. When handing to on-call or L3, post a summary in the incident channel using the template: impact, scope, timeline, workaround, and open questions. Support does not close a SEV1 or SEV2 ticket until the post-incident review is scheduled, which must occur within three business days.
