-- brain/sf/01_schema.sql
-- Run as BRAIN_OWNER (the service user's default role) after 00_setup.sql.
--
-- Enforcement model
--   Every stored row, at all three grains, carries one scope.
--   One row access policy, SCOPE_GATE, is attached to every knowledge table. It admits a row when
--   the session's primary role is mapped to that row's scope in ROLE_SCOPE.
--   A row access policy binds everyone, the table owner included, so BRAIN_OWNER is in the map
--   with every scope (ingest must see what it writes) and an unmapped role sees nothing.
--   Per request the API does USE ROLE <the asker's role> and then runs plain SQL. It never
--   passes scopes, so it cannot widen them by accident.

use role brain_owner;
use warehouse brain_wh;
create schema if not exists brain.core;
use schema brain.core;

-- ───────────────────────── identity ─────────────────────────

create or replace table scope (id varchar primary key);

create or replace table brain_role (
  id      varchar primary key,
  sf_role varchar not null unique,        -- the Snowflake role this brain role runs as
  profile variant not null                -- grain, max_words, format, define_terms, surface_conflicts, prefer_sources
);

create or replace table role_scope (
  sf_role varchar not null,
  scope   varchar not null,
  primary key (sf_role, scope)
);

create or replace table principal (
  id         varchar default uuid_string() primary key,
  handle     varchar not null unique,
  kind       varchar not null,            -- human | agent
  role_id    varchar not null,
  token_hash varchar not null unique      -- sha256 hex of the bearer token
);

-- ───────────────────────── the gate ─────────────────────────

create or replace row access policy scope_gate as (row_scope varchar) returns boolean ->
  exists (select 1 from brain.core.role_scope rs
          where rs.sf_role = current_role() and rs.scope = row_scope);

-- ───────────────────────── knowledge, three grains ─────────────────────────

create or replace table document (
  id            varchar primary key,
  title         varchar not null,
  source        varchar not null,
  default_scope varchar not null,
  created_at    timestamp_ltz default current_timestamp()
);

-- Which scopes a document has chunks in. Gated; it is how an asker reaches document metadata.
create or replace table document_scope (
  document_id varchar not null,
  scope       varchar not null,
  primary key (document_id, scope)
) with row access policy scope_gate on (scope);

-- T1
create or replace table chunk (
  id          varchar default uuid_string() primary key,
  document_id varchar not null,
  ord         int not null,
  scope       varchar not null,
  content     varchar not null,
  tokens      int default 0,
  embedding   vector(float, 1024)
) with row access policy scope_gate on (scope);

-- T2: one per (document, scope), built only from that scope's chunks.
create or replace table summary (
  document_id varchar not null,
  scope       varchar not null,
  topics      varchar not null default '',     -- comma-separated
  content     varchar not null,
  embedding   vector(float, 1024),
  primary key (document_id, scope)
) with row access policy scope_gate on (scope);

-- T3: one per (topic, scope), built only from that scope's summaries.
create or replace table digest (
  id           varchar default uuid_string() primary key,
  topic        varchar not null,
  scope        varchar not null,
  document_ids varchar not null default '',    -- comma-separated
  content      varchar not null,
  embedding    vector(float, 1024)
) with row access policy scope_gate on (scope);

-- Document metadata an asker may see: documents with at least one chunk in a scope they hold.
-- The base table is not granted to asker roles; titles of fully restricted documents stay hidden.
create or replace secure view visible_document as
  select d.* from document d
  where exists (select 1 from document_scope ds where ds.document_id = d.id);

-- Refusal routing for the router role only: scope and vector of every chunk, no content.
-- The router is mapped to every scope, so this view sees all rows. It lets the API name the
-- scopes an asker lacks that hold near matches, without any asker role touching those rows.
create or replace secure view scope_probe as
  select scope, embedding from chunk;

-- ───────────────────────── ledger ─────────────────────────

create or replace table ledger (
  id            varchar default uuid_string(),
  asked_at      timestamp_ltz default current_timestamp(),
  sf_role       varchar default current_role(),     -- recorded by the database, not the app
  principal_id  varchar not null,
  role_id       varchar not null,
  scopes        varchar not null,
  question      varchar not null,
  outcome       varchar not null,                    -- answered | refused | empty
  denied_scopes varchar default '',
  document_ids  varchar default '',
  chunk_ids     varchar default '',
  tokens_in     int default 0,
  tokens_out    int default 0,
  answer        varchar
);

-- ───────────────────────── grants ─────────────────────────
-- Asker roles: read knowledge through the gate, append to the ledger. Nothing else.
-- No grant on PRINCIPAL, BRAIN_ROLE, ROLE_SCOPE, DOCUMENT, SCOPE_PROBE, and no SELECT/UPDATE/DELETE on LEDGER.

grant usage on database brain to role brain_router;
grant usage on schema brain.core to role brain_router;
grant select on table principal to role brain_router;
grant select on table brain_role to role brain_router;
grant select on table role_scope to role brain_router;
grant select on view scope_probe to role brain_router;

grant usage on database brain to role brain_sales;
grant usage on schema brain.core to role brain_sales;
grant select on table chunk to role brain_sales;
grant select on table summary to role brain_sales;
grant select on table digest to role brain_sales;
grant select on table document_scope to role brain_sales;
grant select on view visible_document to role brain_sales;
grant insert on table ledger to role brain_sales;

grant usage on database brain to role brain_exec;
grant usage on schema brain.core to role brain_exec;
grant select on table chunk to role brain_exec;
grant select on table summary to role brain_exec;
grant select on table digest to role brain_exec;
grant select on table document_scope to role brain_exec;
grant select on view visible_document to role brain_exec;
grant insert on table ledger to role brain_exec;

grant usage on database brain to role brain_support_agent;
grant usage on schema brain.core to role brain_support_agent;
grant select on table chunk to role brain_support_agent;
grant select on table summary to role brain_support_agent;
grant select on table digest to role brain_support_agent;
grant select on table document_scope to role brain_support_agent;
grant select on view visible_document to role brain_support_agent;
grant insert on table ledger to role brain_support_agent;

-- ───────────────────────── seed ─────────────────────────

insert into scope (id) values
  ('public'), ('internal'), ('sales'), ('support'), ('finance'), ('legal'), ('people'), ('exec');

insert into brain_role (id, sf_role, profile)
  select 'sales', 'BRAIN_SALES', parse_json('{"grain":"summary","max_words":120,"format":"prose","define_terms":true,"surface_conflicts":false,"prefer_sources":["handbook","sales-playbook"]}')
  union all
  select 'exec', 'BRAIN_EXEC', parse_json('{"grain":"chunk","max_words":300,"format":"prose","define_terms":false,"surface_conflicts":true,"prefer_sources":["board-minutes","finance-wiki","legal-memo"]}')
  union all
  select 'support_agent', 'BRAIN_SUPPORT_AGENT', parse_json('{"grain":"chunk","max_words":150,"format":"json","define_terms":false,"surface_conflicts":false,"prefer_sources":["support-kb"]}');

insert into role_scope (sf_role, scope) values
  ('BRAIN_SALES', 'public'), ('BRAIN_SALES', 'internal'), ('BRAIN_SALES', 'sales'),
  -- exec holds sales too: the CFO beat cites the sales playbook against the legal memo.
  ('BRAIN_EXEC', 'public'), ('BRAIN_EXEC', 'internal'), ('BRAIN_EXEC', 'sales'),
  ('BRAIN_EXEC', 'finance'), ('BRAIN_EXEC', 'legal'), ('BRAIN_EXEC', 'exec'),
  ('BRAIN_SUPPORT_AGENT', 'public'), ('BRAIN_SUPPORT_AGENT', 'support');

-- Owner (ingest) and router (refusal routing) see every scope.
insert into role_scope (sf_role, scope) select 'BRAIN_OWNER', id from scope;
insert into role_scope (sf_role, scope) select 'BRAIN_ROUTER', id from scope;

-- Demo tokens. Test values only.
insert into principal (handle, kind, role_id, token_hash)
  select 'maya', 'human', 'sales', sha2('demo-maya', 256)
  union all select 'dana', 'human', 'exec', sha2('demo-dana', 256)
  union all select 'svc-support-bot', 'agent', 'support_agent', sha2('demo-support-bot', 256);

-- Smoke test for the embedding model. If this fails on region, see the note in 00_setup.sql.
select vector_l2_distance(
  snowflake.cortex.embed_text_1024('voyage-multilingual-2', 'refund policy'),
  snowflake.cortex.embed_text_1024('voyage-multilingual-2', 'refund policy')) as should_be_zero;
