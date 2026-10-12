---
title: "Support KB - Getting Started with Ridgeline"
source: support-kb
scope: public
---
# Support KB: Getting Started with Ridgeline

This article walks you through the four steps most new Ridgeline accounts complete first: creating a workspace, inviting users, connecting your first telematics data source, and building a dashboard. Plan on about 45 to 60 minutes if your telematics provider credentials are ready.

## Before you start

You need:

- An administrator login for your Ridgeline account. Your Kestrel Ridge onboarding contact will issue this when your contract is activated.
- Admin access to at least one telematics provider (for example, your ELD or GPS vendor's fleet portal), so you can generate an API key or authorize a data share.
- A list of the people who will use Ridgeline, with work email addresses.

Ridgeline supports Chrome, Edge, and Safari, current and one version back. Pop-up blockers can interrupt the telematics authorization step, so allow pop-ups from `app.ridgeline.kestrelridge.com` before you begin.

## Create your workspace

A workspace is the top-level container for your fleet data, users, and dashboards. Most customers use one workspace per legal entity.

1. Sign in and select **Create workspace** from the account menu.
2. Enter the workspace name as your team will recognize it, for example "Northline Freight – Western Region."
3. Select your time zone. Dashboards and daily rollups use this setting, so set it to the zone where your dispatch team operates.
4. Select your primary units: miles or kilometers, and gallons or liters.
5. Select **Save**. The workspace is created with you as its only administrator.

You can change the name and time zone later. Changing units will not convert historical data, so set it correctly now.

## Invite users

Ridgeline uses three roles:

- **Administrator:** manages users, data connections, and billing contacts.
- **Analyst:** builds and edits dashboards and reports.
- **Viewer:** reads dashboards and exports data but cannot change them.

To invite users:

1. Go to **Settings > Users > Invite**.
2. Enter one or more work email addresses, separated by commas.
3. Choose a role for each group of users.
4. Select **Send invitations**.

Invitations expire after 7 days. If someone does not receive one, check their spam folder first, then resend from the Users list. Personal email domains (such as gmail.com) are blocked by default; ask an administrator to allow a specific domain under **Settings > Security** if you need an exception.

## Connect your first telematics source

Ridgeline pulls position, hours-of-service, fuel, and fault data from your telematics provider. Each provider connection is set up once per workspace.

1. Go to **Settings > Data sources > Add source**.
2. Select your provider from the list. If yours is not listed, choose **Generic CSV upload** for a one-time import or contact support about a custom integration.
3. Follow the authorization prompt. You will be redirected to your provider's portal to approve a read-only data share. For providers that use API keys, paste the key and the account ID.
4. Choose which vehicles or groups to include. You can start with a single group of 10 to 20 vehicles to confirm data looks right.
5. Select **Start sync**.

The first sync typically takes 15 to 30 minutes for up to 500 vehicles, and up to 24 hours of history is loaded. Full historical backfill can take longer. The **Sync status** column shows progress. A source is ready when its status reads **Healthy** and the last-updated time is within the past hour.

## Build your first dashboard

1. Go to **Dashboards > New dashboard** and choose **Start from template**.
2. Select **Fleet overview**. This template includes utilization, idle time, fuel economy by vehicle, and open fault codes.
3. Choose a date range. For a first check, select the last seven days.
4. Confirm that the vehicle count in the header matches what you expect. A mismatch usually means a group was not included in step 4 of the previous section.
5. Select **Save**, then **Share** to give Viewers access.

To add a widget, select **Add widget**, choose a metric, and pick a grouping such as vehicle, driver, or depot. Widgets can be resized and reordered by dragging. Analysts can schedule a dashboard to email a PDF every weekday at a set time under **Schedule**.

## Troubleshooting and getting help

- **Sync status shows "Authorization expired":** Re-authorize the source under **Settings > Data sources**. Provider tokens typically expire every 90 days.
- **Vehicle counts look low:** Check that the vehicles are assigned to a group included in the source configuration.
- **Timestamps look wrong:** Confirm the workspace time zone in **Settings > General**.

For anything not covered here, select **Help > Contact support** in the app. Include your workspace name, the data source affected, and a screenshot. Support is available Monday through Friday, 6:00 a.m. to 6:00 p.m. Mountain Time, with after-hours coverage for Severity 1 issues.
