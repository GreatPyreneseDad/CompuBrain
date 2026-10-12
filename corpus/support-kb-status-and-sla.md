---
title: "Support KB - Service Levels and Status Page"
source: support-kb
scope: public
---
# Support KB: Service Levels and Status Page

*Public article. Last updated March 2, 2026.*

## Uptime commitment

Kestrel Ridge commits to 99.9% monthly availability for the Ridgeline production environment. Availability is measured per calendar month across the web application, the API, and scheduled data delivery jobs.

The following are excluded from availability calculations:

- Scheduled maintenance windows, which run Sunday 02:00 to 04:00 Mountain Time and are announced at least five business days in advance on the status page.
- Outages caused by a customer's own network, credentials, or integrations.
- Force majeure events affecting our hosting providers' core regions, to the extent they are beyond our reasonable control.

Downtime that is not excluded counts toward the monthly figure, measured in minutes. At 99.9%, the allowable unplanned downtime in a 30-day month is about 43 minutes.

## Support response targets

Every support ticket is assigned one of four severity levels. Response targets are measured from the time the ticket is received through the support portal or by email.

| Severity | Definition | First response target | Coverage |
|---|---|---|---|
| Sev 1 | Ridgeline is unavailable for all users, or data loss is occurring | 30 minutes | 24x7 |
| Sev 2 | A major feature is unusable, with no workaround | 2 business hours | Business hours |
| Sev 3 | A feature is degraded, with a workaround available | 1 business day | Business hours |
| Sev 4 | General questions, feature requests, or cosmetic issues | 2 business days | Business hours |

Business hours are 08:00 to 18:00 Mountain Time and 09:00 to 17:00 Lisbon time, Monday through Friday, excluding Kestrel Ridge holidays published on the status page.

A first response is a human reply that acknowledges the issue and assigns a severity. It is not a resolution. If you believe a ticket has been mis-classified, reply to the ticket and state the business impact. We will re-evaluate.

## Requesting a service credit

If monthly availability falls below 99.9%, you may be eligible for a service credit against your next invoice. The credit schedule is:

- Availability below 99.9% and at least 99.0%: 10% of that month's subscription fees.
- Availability below 99.0%: 25% of that month's subscription fees.

To request a credit:

1. Open a ticket in the support portal and select the category "Service credit request."
2. Include your account ID, the affected calendar month, and a short description of the impact on your operations.
3. Attach any status page incident links or your own logs that show the outage.

Support reviews each request against recorded availability for the month. Credits are applied to the next invoice and do not convert to cash. Credit amounts are capped as described in your order form. If your order form has different credit terms, the order form governs.

## Status page

Live system status, current incidents, scheduled maintenance, and post-incident reports are published at **status.kestrelridge.com**. You can subscribe to email or SMS alerts from that page for all incidents or for specific components, such as the API or data delivery.

During a Sev 1 incident, we update the status page at least every 30 minutes until service is restored. A post-incident report is published within five business days for any incident that counted toward monthly downtime.

The status page is the authoritative source for availability figures used in service credit reviews.

## Contacting support

- Support portal: support.kestrelridge.com
- Email: support@kestrelridge.com
- Sev 1 issues: use the portal's "Urgent" option, which pages the on-call engineer directly.

When reporting an issue, include the time it started, your time zone, affected users or fleet IDs, and any error messages. This shortens time to first response and diagnosis.
