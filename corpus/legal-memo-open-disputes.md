---
title: "Legal Memo - Open Customer Disputes"
source: legal-memo
scope: legal
---
# Legal Memo: Open Customer Disputes

**Privileged and Confidential. Prepared at the request of counsel in anticipation of litigation. Do not forward outside the legal team.**

**Date:** 2026-04-10
**Audience:** Legal
**Matters covered:** Three open customer disputes involving Ridgeline subscriptions

## Purpose and Scope

This memo summarizes the status of three open disputes, estimates our exposure on each, and recommends a posture. Figures come from billing records, support tickets, and the executed order forms. Amounts are as of 2026-04-08. Customer names are fictional for this memo.

## Matter 1: Harlan Freight Group (Service Credit Claim)

Harlan claims a service credit for the March 2026 platform incident, which degraded data ingestion for 19 hours on 2026-03-14 and 2026-03-15. Harlan's order form commits to 99.5% monthly availability, with credits on a stepped schedule. Our status page and monitoring logs show availability for March at 98.9%, which is a breach of the commitment.

Harlan's claim is $38,400, calculated as the maximum credit tier applied to the full monthly fee plus a claimed fee for manual reporting. Our reading of the schedule supports a credit of $19,200. The manual reporting fee has no contractual basis. Harlan has not threatened litigation, but its account lead has linked the claim to a renewal discussion.

## Matter 2: Pinecrest Logistics (Non-Payment)

Pinecrest has $112,600 in invoices outstanding, with the oldest over 120 days past due. Pinecrest disputes the integration setup fees on the 2025 order, asserting that the onboarding work was not completed as scoped. Our project records show the scoped deliverables were marked complete in August 2025, and Pinecrest signed the acceptance form. Pinecrest did not raise the dispute until February 2026.

Pinecrest's counsel sent a letter on 2026-03-02 reserving rights but has not filed. We have sent two demand letters, and the second drew a response that did not contest the principal amount.

## Matter 3: Ostrander Fleet Services (Early Termination)

Ostrander gave notice on 2026-03-20 that it would terminate for convenience, citing repeated latency complaints. The order form has no termination-for-convenience right. It permits termination for uncured material breach after a 30-day notice and cure period. Ostrander's notice did not invoke that process, and the 30-day period has not started.

Remaining committed fees through the end of the 36-month term are $286,000. Ostrander has stopped paying the platform fee for April 2026 but is still using the service.

## Exposure Summary

| Matter | Amount Claimed | Likely Exposure | Range |
|---|---|---|---|
| Harlan (service credit) | $38,400 | $19,200 | $19,200 to $38,400 |
| Pinecrest (non-payment) | $112,600 | $95,000 | $60,000 to $112,600 |
| Ostrander (termination) | $286,000 | $90,000 | $0 to $286,000 |

The Ostrander range depends heavily on whether a material breach is established. Our latency data supports a cure argument but not a clean one, given two incidents in Q1.

## Recommended Posture

**Harlan:** Accept the contractual credit of $19,200 in writing, state that the manual reporting fee is not part of the order form, and link the resolution to no change in renewal terms. Do not characterize the March incident as a breach beyond the SLA definition.

**Pinecrest:** Continue demand. Send a final notice with a 14-day deadline, citing the signed acceptance form. If unpaid, refer to outside collections counsel and evaluate filing for the principal amount. Preserve all project records.

**Ostrander:** Respond in writing that no termination right exists under the order form and that the 30-day cure process has not been invoked. Ask Ostrander to identify any claimed uncured breach. Hold settlement discussions until Engineering completes the latency root-cause report, expected 2026-05-01.

## Open Items

- Pull the signed Pinecrest acceptance form and the August 2025 completion record for the file.
- Confirm the Harlan credit calculation with Finance before the written response goes out.
- Litigation hold notices issued to Support, Success, and Engineering on Ostrander and Pinecrest. Confirm acknowledgments by 2026-04-17.
- Revisit this memo after the 2026-05-01 root-cause report.
