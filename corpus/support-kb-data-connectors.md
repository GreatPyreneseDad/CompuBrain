---
title: "Support KB - Data Connectors and Sync Schedules"
source: support-kb
scope: public
---
# Data Connectors and Sync Schedules

This article lists the data connectors Ridgeline supports, how often each one syncs, how far back we can backfill history, and what to do when a sync fails. Applies to Ridgeline version 6.x and later. Last reviewed March 2026.

## Supported connector types

Ridgeline connects to three categories of source system:

- **Telematics platforms.** Vehicle position, engine hours, fault codes, and driver-status events. Pulled through the platform's API using a key you generate in your telematics account.
- **Transportation management systems (TMS).** Loads, stops, dispatch assignments, and invoice status. Connected through the TMS vendor's export or API integration.
- **Electronic logging device (ELD) providers.** Hours-of-service logs, duty status changes, and driver certifications. Connected through the ELD provider's data feed.

The full, current list of named integrations is in **Settings > Integrations > Available connectors**. If your system is not listed, contact your account manager. Custom file imports (CSV or SFTP drop) are available on request for systems without a supported connector.

## Sync frequency

Default sync intervals, per connector category:

| Category | Default interval | Minimum interval |
|---|---|---|
| Telematics | Every 15 minutes | Every 5 minutes |
| TMS | Every 60 minutes | Every 15 minutes |
| ELD | Every 60 minutes | Every 30 minutes |
| SFTP / CSV import | Once per day, 02:00 UTC | Once per hour |

Intervals are set per connection in **Settings > Integrations > [connection] > Schedule**. Shorter intervals increase load on your source system and may hit that vendor's API rate limits. If a connector is hitting rate limits, Ridgeline will lengthen the interval automatically for that connection and show a notice on the integration status page.

## Backfill limits

When you first connect a source, or when you add a new vehicle or load type, Ridgeline backfills historical data.

- **Standard backfill:** up to 90 days of history.
- **Extended backfill:** up to 365 days, available on request. Extended backfills are scheduled by Support and typically complete within 48 hours.
- **Backfills run in the background** and do not block live sync. Dashboards show a progress bar on the connection page.

Data older than the backfill window cannot be pulled retroactively from Ridgeline. If you need it, export from the source system and use a CSV import.

## What to do when a sync fails

1. **Check the integration status page.** Each connection shows its last successful sync time, the last error, and the error code.
2. **Match the error to a cause:**
   - `AUTH_EXPIRED`: the API key or OAuth token has expired. Reauthorize the connection in Settings.
   - `RATE_LIMITED`: the source system throttled us. Wait one cycle; if it recurs, lengthen the interval.
   - `SCHEMA_MISMATCH`: the source changed a field name or format. Open a support ticket with the error ID.
   - `SOURCE_UNREACHABLE`: the source API or SFTP host did not respond. Check the vendor's status page first.
3. **Retry manually** using **Sync now** on the connection page once the cause is resolved.
4. **Open a ticket** if the error persists after two manual retries. Include the connection name, error code, and the time of the most recent failure, in UTC.

Ridgeline retries failed syncs automatically at the next scheduled interval. Three consecutive failures mark the connection as **Degraded**, and an email goes to the account's integration admins.

## Data gaps after an outage

If a source was unavailable, Ridgeline fills the gap on the next successful sync, up to the last 72 hours, without manual action. For outages longer than 72 hours, request a targeted backfill from Support with the start and end dates.

## Related articles

- Reauthorizing an integration
- Reading the integration status page
- CSV and SFTP import format specifications
