---
title: "Release Notes - September 2026"
source: product-wiki
scope: public
---
# Release Notes: September 2026

Ridgeline shipped version 6.8 on September 9, 2026, with a follow-up patch, 6.8.1, on September 22. This document lists new features, improvements, and fixes for the month. Changes roll out to all workspaces over two weeks, so you may not see every item on the same day.

## New Features

**Lane-level fuel variance report.** Fleet operators can now compare planned and actual fuel consumption by lane, by driver, and by vehicle class. The report covers the trailing 90 days and exports to CSV. Filters are saved per user.

**Detention time alerts.** Dispatchers can set a threshold, from 30 minutes to 4 hours, after which Ridgeline flags a stop where a driver has been waiting. Alerts appear in the dispatch board and can be sent by email or to a webhook. Brokers can enable the same alerts for carrier partners.

**Carrier scorecards for brokers.** Brokers can view on-time pickup rate, on-time delivery rate, and claim frequency for each carrier in their network. Scorecards use the last 180 days of load data. Carriers can see their own scorecard but not those of other carriers.

**Bulk load import from spreadsheet.** Users can upload up to 2,000 loads per file using the standard Ridgeline template. Each row is validated before import. Rows with errors are listed in a downloadable file with the reason for each failure.

## Improvements

- Dispatch board loads up to 40% faster for accounts with more than 500 active loads, based on internal testing in August.
- Map view now clusters vehicles when more than 150 are visible in one area.
- Invoice PDFs include the carrier's MC number and the shipper reference field.
- Role permissions for "Dispatcher" and "Dispatch Lead" are now separated. Dispatch Leads can reassign loads across regions. Dispatchers are limited to their assigned region.
- Audit log entries now show the IP address and client type for each change.

## Fixes

- Fixed a bug where ETA recalculation stopped after a driver went more than 30 minutes without a location ping. ETA now updates on the next ping.
- Fixed duplicate load numbers appearing when two users created loads within the same second.
- Fixed CSV exports that dropped the final row when the file exceeded 10,000 rows.
- Fixed time zone display on proof-of-delivery documents for loads crossing a daylight saving boundary.
- Fixed an issue where accessorial charges entered in a foreign currency were rounded before conversion. Rounding now happens after conversion.

## Known Issues

- Detention alerts may fire up to five minutes late for stops in areas with weak cellular coverage. The team is evaluating a fix for 6.9.
- The bulk import validator does not yet check trailer length against equipment type. Users should review those fields before submitting large files.

## Upgrade and Deprecation Notes

The legacy `/v1/loads/status` API endpoint will be retired on December 31, 2026. Integrations should move to `/v2/loads/status`, which returns the same fields plus a `last_updated_utc` timestamp. The v2 endpoint has been available since June 2026. Migration guidance is in the developer portal under "Load Status Migration."

No changes to existing user data or permissions were required for 6.8. Workspace admins may want to review the new Dispatch Lead role and assign it where appropriate.

## Questions and Feedback

For product questions, contact your account manager or open a ticket through the Ridgeline help center. Feature requests are reviewed weekly by the product team. Release notes for the next version will be published in October 2026.
