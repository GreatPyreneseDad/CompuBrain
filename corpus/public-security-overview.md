---
title: "Security and Compliance Overview"
source: website
scope: public
---
# Security and Compliance Overview

This document summarises the security and compliance programme for Ridgeline, the analytics platform Kestrel Ridge provides to freight fleets, brokers, and third-party logistics providers. It is intended for customers, prospective customers, and their security reviewers. It describes controls at a summary level. Detailed evidence is available under NDA on request.

Last reviewed: 14 January 2026. Owner: Information Security function.

## Certifications and Independent Assurance

- **SOC 2 Type II**: Our most recent report covers the period 1 July 2025 to 31 December 2025 and covers the Security, Availability, and Confidentiality trust services criteria. The bridge letter for January to March 2026 is available to customers on request.
- **ISO/IEC 27001:2022**: Certified for the Ridgeline production environment and the Denver and Lisbon offices. The certificate is renewed annually after surveillance audits.
- **Penetration testing**: An independent firm tests Ridgeline web and API surfaces twice a year. Summary findings and remediation status are shared with customers under NDA. Critical and high findings are fixed or mitigated within 14 and 30 days respectively.

## Encryption

- All data in transit uses TLS 1.2 or higher. TLS 1.0 and 1.1 are disabled at the edge.
- Customer data at rest is encrypted with AES-256. Keys are managed in a cloud key management service with automatic rotation every 365 days.
- Database backups are encrypted with keys separate from the production keys.
- Customer-managed keys are available on the Enterprise plan for customers who require control of their own key material.

## Access Control

- Access to production systems requires single sign-on with multi-factor authentication. Hardware security keys are required for engineers with production access.
- Production access follows least privilege. Access is granted per role and reviewed quarterly by the Security Engineering lead and the relevant service owner.
- Engineers do not have standing access to customer data. Access is granted just-in-time through an approval workflow, logged, and expires after four hours.
- Customers control access within their own Ridgeline tenant. Role-based permissions, SAML 2.0 single sign-on, and SCIM provisioning are supported. Audit logs of user and administrative actions are retained for 13 months.

## Data Residency

Customer data is stored in one of three regions, selected at contract signature:

- **United States** (primary: US East, failover: US West)
- **European Union** (primary: Frankfurt, failover: Dublin)
- **Canada** (primary: Montréal, failover: Toronto)

Data does not leave the selected region for storage or processing. Support personnel in other locations may view data only through the approved access workflow described above. Residency cannot be changed after onboarding without a documented migration, which requires written agreement from both parties.

## Data Retention and Deletion

Telemetry and operational data are retained for the period set in the customer agreement, with a default of 24 months. On contract termination, customer data is deleted from production within 30 days and from backups within 90 days. Deletion certificates are issued on request.

## Responsible Disclosure

We welcome reports of security vulnerabilities in Ridgeline and our public websites. Please send reports to **security@kestrelridge.example**, with PGP encryption if the report contains sensitive detail. Our public key is published at kestrelridge.example/.well-known/security.txt.

Please do not access data that is not your own, degrade service, or perform social engineering against staff. We will acknowledge reports within two business days, keep you informed of progress, and credit researchers who wish to be named once a fix is released.
