-- brain/db/schema.sql
-- Company Brain: identity-gated knowledge store.
-- Target: Postgres 15+ with pgvector (Supabase). Run as the database owner.
--
-- Enforcement model
--   1. The API connects as owner, then per request, inside a transaction:
--        SET LOCAL ROLE brain_app;
--        SELECT set_config('app.principal_id', '<uuid>', true);
--   2. RLS derives scopes from the principal inside the database.
--      The app never supplies scopes, so it cannot widen them by accident.
--   3. Ingest and the admin ledger view run as owner (bypasses RLS on purpose).

create schema if not exists extensions;
create extension if not exists vector with schema extensions;
create schema if not exists brain;
set search_path = brain, extensions, public;

-- ───────────────────────── identity ─────────────────────────

create table brain.scope (
  id text primary key
);

create table brain.role (
  id      text primary key,
  profile jsonb not null          -- grain, max_words, format, define_terms, surface_conflicts, prefer_sources
);

create table brain.role_scope (
  role_id text not null references brain.role(id) on delete cascade,
  scope   text not null references brain.scope(id),
  primary key (role_id, scope)
);

create table brain.principal (
  id         uuid primary key default gen_random_uuid(),
  handle     text not null unique,
  kind       text not null check (kind in ('human', 'agent')),
  role_id    text not null references brain.role(id),
  token_hash text not null unique  -- sha256 hex of the bearer token
);

-- ───────────────────────── knowledge, three grains ─────────────────────────

-- Document: metadata only. Visible if the asker can see at least one chunk.
create table brain.document (
  id            uuid primary key default gen_random_uuid(),
  title         text not null,
  source        text not null,                      -- handbook, finance-wiki, board-minutes, ...
  default_scope text not null references brain.scope(id),
  scopes        text[] not null default '{}',       -- distinct scopes of its chunks, set by ingest
  created_at    timestamptz not null default now(),
  unique (source, title)                            -- re-ingest replaces
);

-- T1: raw chunks. One scope each. This is where a mixed document gets split.
create table brain.chunk (
  id          uuid primary key default gen_random_uuid(),
  document_id uuid not null references brain.document(id) on delete cascade,
  ord         int  not null,
  scope       text not null references brain.scope(id),
  content     text not null,
  tokens      int  not null default 0,
  embedding   vector(1024),                         -- 1024 dims: voyage-3, or OpenAI 3-small with dimensions=1024
  unique (document_id, ord)
);

-- T2: document summaries. One per (document, scope), built only from that scope's chunks.
-- An asker reads the summaries for the scopes they hold; nothing is over-restricted, nothing mixes.
create table brain.summary (
  document_id uuid not null references brain.document(id) on delete cascade,
  scope       text not null references brain.scope(id),
  topics      text[] not null default '{}',
  content     text not null,
  embedding   vector(1024),
  primary key (document_id, scope)
);

-- T3: topic digests across documents. One per (topic, scope), built only from that scope's summaries.
create table brain.digest (
  id           uuid primary key default gen_random_uuid(),
  topic        text not null,
  scope        text not null references brain.scope(id),
  document_ids uuid[] not null,
  content      text not null,
  embedding    vector(1024),
  unique (topic, scope)
);

create index chunk_doc_idx   on brain.chunk (document_id);
create index chunk_scope_idx on brain.chunk (scope);
-- No vector indexes on purpose. Under a scope filter an HNSW index post-filters and can
-- return fewer than k rows; exact scan is correct and fast up to tens of thousands of rows.
-- Add hnsw (embedding vector_cosine_ops) with iterative scan when the corpus outgrows that.

-- ───────────────────────── ledger ─────────────────────────

create table brain.ledger (
  id             bigint generated always as identity primary key,
  at             timestamptz not null default now(),
  principal_id   uuid not null references brain.principal(id),
  role_id        text not null,
  scopes         text[] not null,
  question       text not null,
  outcome        text not null check (outcome in ('answered', 'refused', 'empty')),
  denied_scopes  text[] not null default '{}',     -- scopes that had relevant hits the asker could not see
  document_ids   uuid[] not null default '{}',
  chunk_ids      uuid[] not null default '{}',
  tokens_in      int not null default 0,
  tokens_out     int not null default 0,
  answer         text
);

create function brain.ledger_immutable() returns trigger
language plpgsql as $$
begin
  raise exception 'ledger is append-only';
end $$;

create trigger ledger_no_update before update or delete on brain.ledger
  for each row execute function brain.ledger_immutable();
create trigger ledger_no_truncate before truncate on brain.ledger
  for each statement execute function brain.ledger_immutable();

-- ───────────────────────── gate functions ─────────────────────────

-- Scopes of the current request's principal. Empty if none is set.
create function brain.app_scopes() returns text[]
language sql stable security definer
set search_path = brain, extensions, public as $$
  select coalesce(array_agg(rs.scope), '{}')
  from brain.principal p
  join brain.role_scope rs on rs.role_id = p.role_id
  where p.id = nullif(current_setting('app.principal_id', true), '')::uuid
$$;

-- Bearer token → principal, role, profile, scopes. The only way the app reads identity.
create function brain.resolve_token(token text)
returns table (principal_id uuid, handle text, kind text, role_id text, profile jsonb, scopes text[])
language sql stable security definer
set search_path = brain, extensions, public as $$
  select p.id, p.handle, p.kind, p.role_id, r.profile,
         coalesce((select array_agg(rs.scope order by rs.scope)
                   from brain.role_scope rs where rs.role_id = p.role_id), '{}')
  from brain.principal p
  join brain.role r on r.id = p.role_id
  where p.token_hash = encode(sha256(convert_to(token, 'UTF8')), 'hex')
$$;

-- Refusal routing. Looks across ALL chunks for the query's nearest neighbours and
-- returns only scope names and counts for scopes the asker lacks. No content, no ids.
-- Lets the app say "that's outside your scope (people)" without the model seeing a row.
create function brain.denied_scope_hits(q vector(1024), max_dist float default 0.35, k int default 20)
returns table (scope text, hits bigint)
language sql stable security definer
set search_path = brain, extensions, public as $$
  select n.scope, count(*)
  from (
    select c.scope, c.embedding <=> q as dist
    from brain.chunk c
    order by c.embedding <=> q
    limit k
  ) n
  where n.dist < max_dist
    and not (n.scope = any (brain.app_scopes()))
  group by n.scope
$$;

-- ───────────────────────── row-level security ─────────────────────────

do $$ begin
  if not exists (select 1 from pg_roles where rolname = 'brain_app') then
    create role brain_app nologin;
  end if;
end $$;
grant brain_app to current_user;

alter table brain.scope      enable row level security;
alter table brain.role       enable row level security;
alter table brain.role_scope enable row level security;
alter table brain.principal  enable row level security;
alter table brain.document   enable row level security;
alter table brain.chunk      enable row level security;
alter table brain.summary    enable row level security;
alter table brain.digest     enable row level security;
alter table brain.ledger     enable row level security;

create policy chunk_gate on brain.chunk for select to brain_app
  using (scope = any (brain.app_scopes()));

create policy document_gate on brain.document for select to brain_app
  using (scopes && brain.app_scopes());

create policy summary_gate on brain.summary for select to brain_app
  using (scope = any (brain.app_scopes()));

create policy digest_gate on brain.digest for select to brain_app
  using (scope = any (brain.app_scopes()));

create policy ledger_append on brain.ledger for insert to brain_app
  with check (principal_id = nullif(current_setting('app.principal_id', true), '')::uuid);

-- brain_app: read knowledge through the gate, append to the ledger, nothing else.
-- No grants on principal, role, role_scope: identity is reached only via the functions.
grant usage on schema brain to brain_app;
grant usage on schema extensions to brain_app;   -- for the <=> operator
grant select on brain.document, brain.chunk, brain.summary, brain.digest to brain_app;
grant insert on brain.ledger to brain_app;

revoke execute on all functions in schema brain from public;
grant execute on function brain.app_scopes()                         to brain_app;
grant execute on function brain.resolve_token(text)                  to brain_app;
grant execute on function brain.denied_scope_hits(vector, float, int) to brain_app;

-- ───────────────────────── seed: scopes, roles, demo principals ─────────────────────────

insert into brain.scope (id) values
  ('public'), ('internal'), ('sales'), ('support'),
  ('finance'), ('legal'), ('people'), ('exec');

insert into brain.role (id, profile) values
  ('sales', '{"grain":"summary","max_words":120,"format":"prose","define_terms":true,
              "surface_conflicts":false,"prefer_sources":["handbook","sales-playbook"]}'),
  ('exec',  '{"grain":"chunk","max_words":300,"format":"prose","define_terms":false,
              "surface_conflicts":true,"prefer_sources":["board-minutes","finance-wiki","legal-memo"]}'),
  ('support_agent', '{"grain":"chunk","max_words":150,"format":"json","define_terms":false,
              "surface_conflicts":false,"prefer_sources":["support-kb"]}');

insert into brain.role_scope (role_id, scope) values
  ('sales', 'public'), ('sales', 'internal'), ('sales', 'sales'),
  -- exec holds 'sales' too: the CFO beat cites the sales playbook against the legal memo.
  ('exec', 'public'), ('exec', 'internal'), ('exec', 'sales'),
  ('exec', 'finance'), ('exec', 'legal'), ('exec', 'exec'),
  ('support_agent', 'public'), ('support_agent', 'support');

-- Demo tokens. Local test values only; rotate or drop before anything real.
insert into brain.principal (handle, kind, role_id, token_hash) values
  ('maya',            'human', 'sales',         encode(sha256(convert_to('demo-maya', 'UTF8')), 'hex')),
  ('dana',            'human', 'exec',          encode(sha256(convert_to('demo-dana', 'UTF8')), 'hex')),
  ('svc-support-bot', 'agent', 'support_agent', encode(sha256(convert_to('demo-support-bot', 'UTF8')), 'hex'));
