---
title: "Support Macros for Common Issues"
source: support-kb
scope: support
---
# Support Macros for Common Issues

## Purpose and scope

This document holds the canned responses and first-pass diagnostic steps for the four issues Tier 1 sees most often: login failures, stale dashboards, connector authentication failures, and export timeouts. Use the macros as starting points. Edit the wording to fit the customer, and always confirm the diagnostic result before you send a fix. If a macro doesn't match what you see, stop and escalate to Tier 2 using the process in the last section.

Macros are maintained in the Support Knowledge Base under the `Macros / Ridgeline` folder. Do not copy them into personal notes, since they change when the product changes.

## Login problems

**Diagnostic steps**

1. Check the account in the Admin Console. Confirm the status is Active and note whether the user is locked. Accounts lock after 5 failed password attempts within 15 minutes and unlock automatically after 30 minutes.
2. Confirm which sign-in method the customer's organization uses. If SSO is enforced, password resets will not help, and the user must sign in through their identity provider.
3. Check the sign-in log for the user's email over the last 24 hours. Look for `INVALID_CREDENTIALS`, `SSO_ASSERTION_EXPIRED`, or `ACCOUNT_LOCKED`.

**Macro: LOGIN-01 (locked account)**

> Hi [Name], your Ridgeline account was locked after several failed sign-in attempts. It will unlock automatically 30 minutes after the last attempt. If you need access sooner, reply and we can unlock it on our side. Once you're in, we recommend resetting your password from the sign-in page.

**Macro: LOGIN-02 (SSO user trying a password)**

> Hi [Name], your organization requires sign-in through your company's identity provider, so Ridgeline passwords aren't used for your account. Please sign in using the "Continue with SSO" button. If that fails, contact your IT administrator, who can check the identity provider connection.

## Stale dashboards

Dashboards refresh every 15 minutes. A dashboard is considered stale when its last successful data load is more than 60 minutes old.

**Diagnostic steps**

1. Open the dashboard's data status panel and note the "last loaded" timestamp.
2. Check the Pipeline Status page for incidents affecting ingestion in the last 4 hours.
3. Confirm the underlying connector is still healthy (see the next section). Most stale dashboards trace back to a connector, not the dashboard.
4. Ask the customer to hard-refresh the browser before anything else. Cached views account for a small share of reports.

**Macro: DASH-01 (stale data, no incident)**

> Hi [Name], the dashboard was last updated at [timestamp]. We've checked the data pipeline and it's processing normally. The most likely cause is the connector feeding this dashboard. Could you tell us which data source the dashboard uses? We'll take it from there.

## Connector authentication failures

Connectors fail when the stored credentials expire or are revoked. OAuth tokens for most telematics providers expire after 90 days, and a password change at the source system breaks the connector immediately.

**Diagnostic steps**

1. Open the connector in the Admin Console and read the status. `AUTH_FAILED` means the credentials were rejected. `RATE_LIMITED` is a different problem and should not be handled as an auth failure.
2. Check when the credentials were last issued. If the date is near 90 days, token expiry is the likely cause.
3. Ask the customer whether anyone changed the service account password or deactivated the integration user in the source system.
4. Do not ask the customer to paste credentials into a support ticket. Have them re-authorize from the connector settings page.

**Macro: CONN-01 (re-authorization required)**

> Hi [Name], the [Provider] connector stopped syncing because its access credentials are no longer valid. This usually happens when the token expires or the password changes in [Provider]. To fix it, go to Settings > Connectors > [Provider] and select Re-authorize. You'll need an account with admin rights in [Provider]. Data will backfill automatically once the connection is restored, usually within two hours.

## Export timeouts

Exports time out at 120 seconds of processing. Large date ranges across many vehicles are the usual cause.

**Diagnostic steps**

1. Note the date range, the number of units or drivers included, and the export format. CSV exports above 500,000 rows often time out.
2. Ask the customer to split the export into monthly ranges and retry.
3. If the export fails on a small range, check for a data quality issue, such as a malformed timestamp batch from a connector. Escalate if found.

**Macro: EXP-01 (split export)**

> Hi [Name], the export timed out because the date range and fleet size exceeded the single-export limit. Please try again with one calendar month at a time. If you need a full-period file, we can generate it as a set of monthly files. Let us know if you'd like us to set that up.

## Escalation and logging

Escalate to Tier 2 in the #support-tier2 channel when a diagnostic step fails, when more than three customers report the same symptom within a day, or when the customer's sign-in log shows activity you cannot explain. Include the account ID, the timestamp of the last successful action, the macro you tried, and the diagnostic result. Do not promise a fix time unless Tier 2 has confirmed one.

## Maintenance

The support operations lead reviews these macros on the first Monday of each quarter. The next review is Monday, April 6, 2026. Report wording that confuses customers, or steps that no longer match the Admin Console, in the knowledge base comments on the affected macro.
