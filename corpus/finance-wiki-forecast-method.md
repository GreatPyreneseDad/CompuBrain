---
title: "Finance Wiki - Bookings and Cash Forecast Method"
source: finance-wiki
scope: finance
---
# Finance Wiki - Bookings and Cash Forecast Method

**Confidential: Finance only. Do not forward outside the finance distribution list.**

## Purpose and scope

This page describes how Finance builds the weekly bookings forecast and the 13-week cash forecast for Kestrel Ridge. It covers how CRM pipeline stages become weighted bookings, the collection assumptions applied to billed invoices, and who reviews each output and when. It does not cover revenue recognition, which is governed by the accounting policy page.

Version 3.2 applies from the week of 2 March 2026. Earlier versions are archived in the finance drive.

## Pipeline stages and weights

Opportunities in the CRM move through six stages. Each stage carries a fixed probability weight, set by the FP&A Lead and reviewed each quarter against trailing win rates.

| Stage | Definition | Weight |
|---|---|---|
| 1. Qualified | Discovery complete, budget owner identified | 10% |
| 2. Demo | Technical demo delivered to operations | 20% |
| 3. Proposal | Written proposal and pricing sent | 40% |
| 4. Negotiation | Legal or procurement review underway | 65% |
| 5. Verbal | Customer has confirmed intent in writing | 85% |
| 6. Signed | Order form executed | 100% |

Weighted bookings equal contract value multiplied by stage weight. Multi-year deals are counted at first-year committed value only. Usage-based amounts are excluded until the customer has a trailing 90-day run rate in Ridgeline.

Opportunities with no activity for 45 days drop to a 5% weight automatically. Sales Operations maintains that rule in the CRM.

## Building the weekly bookings forecast

Each Monday, Sales Operations freezes the pipeline export at 06:00 Mountain. FP&A runs the weighting script against that snapshot and produces three numbers:

1. Committed bookings: Signed deals with start dates in the forecast quarter.
2. Weighted pipeline: All open opportunities, weighted by stage.
3. Expected bookings: Committed plus weighted pipeline, less a 7% historical slippage haircut.

The slippage haircut is based on the trailing eight-quarter average of deals that moved out of the quarter they were forecast in. Do not override it without a memo to the CFO Office.

## Cash collection assumptions

Cash forecasting starts from open AR, not from bookings. Collections are modeled by customer segment:

- Freight brokers and 3PLs: average 38 days to pay, 2% of invoices written off or disputed in a given quarter.
- Trucking fleets on annual prepay: collected at signature, 30-day lag on any monthly add-ons.
- Enterprise accounts on net-60 terms: modeled at 52 days based on the last four quarters.

New bookings enter the cash forecast only after the first invoice is issued. Signature alone does not create a cash assumption. Payment-term changes approved by Sales require a Finance sign-off before the terms are reflected in the model.

## Review cadence and owners

| Output | Prepared by | Reviewed by | Timing |
|---|---|---|---|
| Weekly bookings forecast | FP&A Analyst | FP&A Lead | Monday by 12:00 |
| Weekly bookings review | FP&A Lead | VP Finance | Tuesday 09:30 |
| 13-week cash forecast | Treasury Analyst | Controller | Thursday by 15:00 |
| Monthly forecast to leadership | VP Finance | CFO | Second business day of each month |

Variances above 10% against the prior week's expected bookings must be explained in writing in the review notes.

## Known limits

- Stage weights are judgment-based and lag changes in sales motion by about one quarter.
- The collection model assumes no major customer insolvency. Concentration risk above 8% of AR for any single customer is flagged separately in the Treasury risk tab.
- Usage-based revenue is not in the forecast until the 90-day run rate exists, so forecasts understate some expansion.

Questions about this page go to the FP&A Lead. Do not share the stage weights or collection assumptions with Sales or customers.
