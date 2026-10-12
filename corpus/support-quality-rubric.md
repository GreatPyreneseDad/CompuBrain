---
title: "Support Quality Rubric"
source: support-kb
scope: support
---
# Support Quality Rubric

## Purpose and scope

This rubric defines how Support scores Ridgeline ticket handling for accuracy, tone, and resolution. It also sets targets for first response and time to resolution, and explains how QA reviews are sampled. It applies to all Tier 1 and Tier 2 tickets from Ridgeline customers, including fleet, broker, and 3PL accounts. It does not cover Sales or Implementation tickets, which use separate checklists.

## Scoring dimensions

Each reviewed ticket is scored on three dimensions, each out of 5.

**Accuracy (weight 50%).** The answer is correct for the customer's configuration, plan, and Ridgeline version. Check the following:
- Claims about features, data sources, or report behavior match the current release notes or the internal KB.
- Troubleshooting steps match the customer's environment (for example, ELD integration vs. manual upload).
- Any commitment on timing or scope is one Support can actually make. Anything involving Engineering must be marked as pending, not promised.

**Tone (weight 20%).** The reply is clear, direct, and respectful. It does not blame the customer, does not use canned phrasing without adapting it, and avoids jargon the customer did not use first.

**Resolution (weight 30%).** The ticket reaches a state the customer confirms, or a documented next step with an owner and date. A "closed" status with no customer confirmation and no next step scores 2 at most.

A ticket score is the weighted total, reported as a percentage. A ticket scoring below 70% is flagged for coaching. A ticket with an accuracy score of 1 or 2 is flagged regardless of total.

## Response and resolution targets

Targets are measured in business hours for Denver and Lisbon combined coverage, using the support queue calendar.

| Metric | Tier 1 target | Tier 2 target |
|---|---|---|
| First response | 2 business hours | 4 business hours |
| Time to resolution (median) | 1 business day | 3 business days |
| Time to resolution (90th percentile) | 3 business days | 7 business days |

Waiting on the customer pauses the clock. Waiting on Engineering does not. Tickets marked Severity 1 (dispatch or ELD data stopped for a fleet) follow the incident runbook and are excluded from these targets.

## How reviews are sampled

QA reviews are drawn each week on Monday, covering the prior Monday through Sunday.

- Each active agent receives 6 randomly selected closed tickets per week.
- Agents in their first 30 days receive 10 per week.
- Tickets are sampled stratified by tier, so that at least 2 Tier 2 tickets appear in each agent's sample where available.
- Tickets involving a credit or a contract question are reviewed in full by the Support Operations Lead, not sampled.
- Any ticket reopened within 7 days is automatically added to the next review cycle.

The sampling script is maintained by Support Operations. Agents can request a specific ticket be reviewed, but the request does not replace the random sample.

## Calibration

Support Quality Leads meet every other Thursday, starting 2026-01-08, to score the same three tickets independently and compare results. If two reviewers' totals differ by more than 10 points on any ticket, the group discusses the gap and updates this rubric's examples section if needed. Calibration results are posted to the support channel within one business day.

## Coaching and follow-up

Flagged tickets get a coaching note from the team lead within five business days. The note names one dimension to improve and includes one concrete example from the ticket. Agents may respond in writing. Repeat flags on the same dimension across three consecutive weekly reviews trigger a joint review with the Support Manager and the agent.
