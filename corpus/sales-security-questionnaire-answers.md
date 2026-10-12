---
title: "Standard Answers to Customer Security Questionnaires"
source: sales-playbook
scope: sales
---
# Standard Answers to Customer Security Questionnaires

## Purpose and how to use this document

This document holds approved answers to the questions that come up most often in customer security reviews. Use these answers as written, or adapt the wording only to fit the question's format. Do not answer from memory or from older deals. Last reviewed: 14 January 2026. Next review: 1 July 2026.

If a question is not covered here, or the customer asks for something beyond these answers, route it to the Security Review queue (see the last section). Do not guess.

## Data residency

**Approved answer:** Ridgeline customer data is stored in one of two regions, chosen at contract signature:

- **United States:** AWS us-west-2 (Oregon).
- **European Union:** AWS eu-west-1 (Ireland).

Customer data does not move between regions unless the customer requests a migration in writing. Backups are kept in the same region as the primary copy. Support staff in Denver and Lisbon may access customer data for troubleshooting under the access controls described below, which is disclosed as remote access, not as storage.

**Do not say:** that data is "never" accessed from outside the region, or that a region is "fully isolated." Both are inaccurate for support access.

## Encryption

**Approved answer:**

- **In transit:** TLS 1.2 or higher for all external connections. TLS 1.0 and 1.1 are disabled.
- **At rest:** AES-256 for databases, object storage, and backups. Keys are managed in AWS KMS with annual rotation.
- **Customer-managed keys:** Not available on the standard plan. Ask the Solutions Engineering lead before committing to it.

## Single sign-on and access control

**Approved answer:** Ridgeline supports SAML 2.0 and OpenID Connect for single sign-on with common identity providers. SCIM 2.0 provisioning is available on the Business and Enterprise plans. Multi-factor authentication is enforced for all internal staff. Customer users can enforce MFA through their identity provider; Ridgeline does not enforce it on its own for SSO users.

Role-based access is available within the application. Ridgeline staff access to production systems requires a ticket, manager approval, and is logged and reviewed quarterly.

## Audit reports and certifications

**Approved answer:** Ridgeline's most recent SOC 2 Type II report covers the period 1 October 2024 through 30 September 2025, issued by an independent CPA firm. Reps may share the report only through the Trust Center, after the customer signs the mutual NDA. Do not email the report as an attachment.

Ridgeline does not hold ISO 27001 certification as of this review. Do not state that it is "in progress" unless Compliance has confirmed a date in writing.

Penetration test summaries are available on request from the Trust Center. Full reports are not shared.

## Subprocessors

**Approved answer:** The current subprocessor list is published on the Trust Center and includes the cloud hosting provider, the email delivery provider, the error monitoring provider, and the support ticketing provider. Customers who subscribe receive 30 days' written notice before a new subprocessor is added, and may object under the terms of the Data Processing Addendum.

Send the link rather than pasting the list. The list changes, and a pasted copy goes stale.

## Incident notification

**Approved answer:** Ridgeline notifies affected customers without undue delay and no later than 72 hours after confirming a security incident that affects their data. Notice is sent to the security contact on file, and updates follow at least daily until containment. The Data Processing Addendum controls if a customer's contract sets a different timeline. Check the signed contract before quoting any number.

**Do not say:** that Ridgeline has "never had a breach." Answer whether there has been a reportable incident only as Legal has confirmed for that customer.

## Escalation

Send anything outside these answers to the Security Review queue, owned by the Security Compliance lead, with the customer name, the question verbatim, and the deal's close date. Target response is two business days. Legal reviews any question about liability, indemnity, or contractual commitments, and only Legal can approve wording that goes beyond this document.
