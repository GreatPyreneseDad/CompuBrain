---
title: "Ridgeline Architecture Overview"
source: eng-wiki
scope: internal
---
# Ridgeline Architecture Overview

This document describes how Ridgeline is put together at a high level: how data enters the system, how it is processed and stored, how it is queried, and how tenants are kept apart. It is for internal engineering, support, and sales engineering use. It does not cover deployment runbooks or on-call procedures, which live in the platform wiki. Last reviewed 2026-03-12 by the Platform Engineering lead.

## Overview

Ridgeline ingests operational data from freight and logistics customers (telematics, electronic logging device feeds, dispatch exports, load boards, and fuel card transactions), normalizes it into a common schema, and serves analytics on lanes, drivers, equipment, and margins. Most of the system runs in AWS us-west-2. Customer-facing traffic terminates at a single regional edge, and all services run in Kubernetes.

The main flow is: ingest, then stream processing, then warehouse, then query layer, then dashboard service. Each stage has its own failure domain and its own on-call owner.

## Ingest Pipeline

Ingest accepts data in three ways: authenticated HTTPS push (JSON or NDJSON, up to 5 MB per request), SFTP drops for customers whose systems cannot push, and vendor pull connectors that poll partner APIs on a schedule. All three paths write raw payloads to an object store bucket per tenant before anything else happens. Raw payloads are kept for 400 days so we can replay them after a schema fix.

Ingest does minimal validation: authentication, tenant resolution, size limits, and a parse check. Records that fail parsing go to a dead-letter prefix with the reason code, and the customer's integration status page shows the count. Ingest does not transform business data.

## Stream Processing

Parsed records are published to Kafka topics partitioned by tenant and source type. A Flink job layer handles normalization into the canonical schema (unit conversion, timezone resolution to UTC with the carrier's home terminal zone, deduplication by source event ID within a 72-hour window), and enrichment against reference tables such as lane geometry and equipment profiles.

Peak throughput in February 2026 was about 38,000 events per second across all tenants, with a design ceiling of 100,000. Consumer lag is an alert: if any normalization job lags more than 10 minutes for 15 minutes, the platform on-call is paged.

## Warehouse and Query Layer

Normalized events land in ClickHouse, partitioned by tenant and day, with a 13-month hot retention and older data moved to Parquet in object storage. Relational metadata (tenants, users, saved reports, permissions) lives in PostgreSQL. We do not join across these two stores in the request path.

The query layer is a service that accepts structured query requests from the dashboard and public API, validates them against a metric catalog, and compiles them to ClickHouse SQL. Every compiled query includes a tenant filter injected by the query layer, not by the caller. Query timeout is 20 seconds; longer queries return a partial-result error and are logged for review.

## Dashboard Service

The dashboard is a single-page web application backed by a thin service that handles saved dashboards, scheduled exports, and report sharing. It calls the query layer and does not talk to ClickHouse directly. Scheduled exports run as jobs and write CSV or PDF files to a signed-URL bucket that expires after 72 hours.

## Tenancy Model

Ridgeline uses a pooled model. Most tenants share ClickHouse and Kafka clusters, with tenant_id on every row and every message. Isolation is enforced at three layers: the ingest path resolves tenant from the API credential and never from the payload; the query layer injects the tenant filter; and ClickHouse row policies provide a backstop. Two of our largest customers run on dedicated ClickHouse shards because of volume, and that is a contractual exception documented in their order forms.

Cross-tenant benchmarking features use aggregated, anonymized rollups built by a separate job. Raw cross-tenant access is not possible through any service.

## Main Dependencies

- AWS: EKS, S3, RDS for PostgreSQL, MSK for Kafka, and IAM.
- ClickHouse (self-managed on EC2 within our VPC) for analytics storage.
- Apache Flink for stream processing.
- Auth provider for SSO and SAML with customer identity providers.
- Twilio and PagerDuty for customer notifications and on-call paging.

Changes to any of these dependencies go through the Architecture Review group before rollout.
