---
title: "Finance Wiki - Month-End Close Calendar"
source: finance-wiki
scope: finance
---
# Finance Wiki - Month-End Close Calendar

**Confidential. Internal use by Finance only.**

## Purpose and scope

This page sets the day-by-day schedule for the monthly close, names the role that owns each step, lists the reconciliations required, and records the sign-off path. It covers the general ledger close for Kestrel Ridge entities in the US (Denver) and Portugal (Lisbon). It does not cover quarterly or annual close, which follow the separate Year-End Close runbook.

BD means business day in the entity calendar. BD+1 for March 2026 close is Wednesday 1 April 2026.

## Close calendar

| Day | Step | Owner role |
|---|---|---|
| BD-2 | Send cutoff notice to AP, Billing, and Payroll. Confirm usage-data feed schedule with Data Engineering. | Accounting Manager |
| BD+1 | Subledger cutoff at 18:00 Mountain. Lock AR and AP for prior period. | AP Lead, AR Lead |
| BD+2 | Post accruals (unbilled services, payroll, vendor invoices not yet received). Pull Ridgeline usage extract for revenue. | GL Accountant, Revenue Analyst |
| BD+3 | Complete bank and card reconciliations for all accounts. | Cash Accountant |
| BD+4 | Intercompany matching between Denver and Lisbon. Resolve differences over 500 EUR or USD equivalent. | Intercompany Accountant |
| BD+5 | Post revenue recognition entries. Roll forward deferred revenue. | Revenue Analyst |
| BD+6 | Preliminary P&L flux review against prior month and budget. | FP&A Analyst |
| BD+7 | Complete account reconciliations and sign off preparer and reviewer fields. Post final adjusting entries. | Account Owners, Accounting Manager |
| BD+8 | Lock trial balance. Issue close package to Controller. | Controller |

## Owners by role

- **Controller**: owns the calendar, approves the locked trial balance, and signs the close package.
- **Accounting Manager**: runs the daily check-in, tracks open items, and reviews all reconciliations before they go to the Controller.
- **Account Owners**: each GL account has a named owner in the reconciliation tracker. The owner prepares the reconciliation by BD+7.
- **Data Engineering liaison**: confirms that the Ridgeline usage extract ran and that row counts match the prior-month baseline.

## Required reconciliations

Each of the following must be prepared, dated, and reviewed before BD+8:

1. Cash: all operating, payroll, and card accounts, both entities.
2. Accounts receivable: subledger to GL, with aging over 60 days noted.
3. Accounts payable: subledger to GL, plus an accrual listing.
4. Deferred revenue: rollforward from contract schedule to GL balance.
5. Prepaid expenses and amortization schedules.
6. Intercompany balances: Denver and Lisbon, matched to zero or documented.
7. Fixed assets and capitalized software: additions, disposals, and depreciation.
8. Payroll liabilities and accruals.

A reconciliation with an unexplained difference over 1,000 USD is not signed off. It goes to the Controller with the open item listed.

## Review and sign-off

1. The preparer signs the reconciliation with a date and the source file name.
2. The Accounting Manager reviews within one business day and signs as reviewer.
3. Any manual journal entry over 25,000 USD needs a second approver from the approval matrix before posting.
4. The Controller signs the trial balance at BD+8. Changes after lock require a written reopen request and Controller approval, and are logged in the close tracker.

## Common causes of late close

- Usage data arrives late from Data Engineering or contains duplicate rows. Check the feed status at BD-2.
- Vendor invoices arrive after the subledger cutoff. Accrue based on purchase orders where possible.
- Intercompany differences from timing or FX rates. Agree the rate source before BD+4.
- Reconciliations started on BD+6 instead of earlier. Owners should begin prep during the month.
- Manual journal entries without support. Missing support delays review.
- Owner absence without a named backup. Each account needs a backup listed in the tracker.

If a step is at risk of missing its day, notify the Accounting Manager the same day. Do not wait for the next check-in.
