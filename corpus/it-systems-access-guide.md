---
title: "IT Systems and Access Guide"
source: it-wiki
scope: internal
---
# IT Systems and Access Guide

This guide covers how to request access to company systems, the device standards we expect, the software installation policy, what happens at offboarding, and how to reach IT for help. It applies to all employees and contractors in Denver, Lisbon, and remote locations. Questions about this document go to the IT Operations queue (see Getting Help below).

## Requesting access

Access to Ridgeline production, customer data stores, and the finance tools is granted by role, not by individual request. Your manager chooses the role; IT provisions it.

1. Open a ticket in the IT Access queue in Jira Service Management. Use the "New system access" form.
2. Name the system, the role, and the business reason. Example: "Ridgeline staging, read-write, needed for the Q3 connector release."
3. Your manager approves in the ticket. Approval by the system owner is also required for anything in the restricted tier (production databases, customer PII exports, billing admin).
4. IT provisions the access within two business days for standard tier and five business days for restricted tier.
5. Access is recorded in the access register, which the Security team reviews each quarter.

Do not ask for access through Slack or by email. Requests made outside the ticket queue are not tracked and will be closed.

Shared credentials are not permitted. Service accounts are created by Platform Engineering only and are rotated every 90 days.

## Device standards

Company laptops must meet the following minimums:

- Current supported OS: macOS 14 or later, or Windows 11 (version 23H2 or later).
- Full-disk encryption enabled (FileVault or BitLocker). IT verifies this through the device management agent.
- Screen lock after 10 minutes of inactivity, or less.
- The managed endpoint agent installed and reporting. Do not disable it.
- Hardware refresh every 4 years, or sooner if the device fails the standards check twice in one quarter.

Personal devices may be used for Slack and email only, through the managed mobile profile. They may not hold customer data or source code.

## Software installation policy

Software falls into three categories:

- **Approved:** listed in the Software Catalog. Install from Self Service without a ticket.
- **Request required:** not in the catalog. Submit a "Software request" ticket with the vendor name, the business need, and whether it will touch customer data. Security review takes up to five business days.
- **Prohibited:** unlicensed software, peer-to-peer file sharing tools, remote-access tools not on the approved list (the approved list currently includes ScreenConnect for support staff only), and browser extensions that request access to all sites unless reviewed.

Do not install software with administrator rights bypassed. If you need admin rights for a specific task, request time-limited elevation through the Privileged Access form; approval is by the IT Security lead and the elevation expires after eight hours.

## Offboarding

HR initiates offboarding in Workday on the employee's last working day. IT acts on that record. The steps are:

1. **Day of separation, before the end of the day:** IT disables Google Workspace and Okta sign-in. Email is converted to a shared mailbox owned by the manager for 90 days.
2. **Within 4 hours:** all active sessions are revoked and the VPN and endpoint certificates are removed.
3. **Within 2 business days:** the manager confirms in the offboarding ticket which shared channels, repositories, and files need reassignment.
4. **Within 5 business days:** the laptop is collected or a prepaid shipping label is sent. Devices are wiped on receipt and returned to inventory.
5. **Within 30 days:** the access register is updated and any service credentials the person owned are rotated.

Contractors follow the same steps, with the contract end date used in place of the HR record.

## Getting help

| Need | Route | Response target |
|---|---|---|
| Password reset, MFA issues, locked account | IT Help portal, or call the Denver service desk at extension 4400 | 30 minutes, business hours |
| Device problems, software install | IT Help portal, category "Endpoint" | Same business day |
| Access requests | IT Access queue (see Requesting access) | As stated above |
| Suspected phishing or a security incident | Report in Slack #security-report or call 24/7 on-call at extension 4911 | Immediate triage |
| Lisbon on-site support | Ticket with location set to Lisbon | Next business day |

Do not email individual IT staff for requests. Tickets are the record, and work that is not in the queue cannot be scheduled.
