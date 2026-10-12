-- brain/db/test_gate.sql
-- Gate test. Run as owner against a scratch database after schema.sql:
--   psql -v ON_ERROR_STOP=1 -f schema.sql -f test_gate.sql
-- Rolls back everything it inserts. Any failed assertion aborts with an error.
begin;
set search_path = brain, extensions, public;

create function pg_temp.vec(i int) returns vector language sql as $$
  select (array(select case when g = i then 1.0 else 0.0 end from generate_series(1,1024) g))::vector(1024)
$$;

-- Two documents: a handbook mixing internal + people (comp table), and a public support article.
insert into document (id, title, source, default_scope, scopes) values
  ('00000000-0000-0000-0000-000000000001', 'Handbook', 'handbook', 'internal', '{internal,people,sales}'),
  ('00000000-0000-0000-0000-000000000002', 'Refund FAQ', 'support-kb', 'public', '{public}');
insert into chunk (document_id, ord, scope, content, embedding) values
  ('00000000-0000-0000-0000-000000000001', 0, 'internal', 'Refund window is 30 days.', pg_temp.vec(1)),
  ('00000000-0000-0000-0000-000000000001', 1, 'sales',    'Exceptions approved by VP Sales.', pg_temp.vec(2)),
  ('00000000-0000-0000-0000-000000000001', 2, 'people',   'Comp band L4: confidential.', pg_temp.vec(3)),
  ('00000000-0000-0000-0000-000000000002', 0, 'public',   'Customers may request a refund within 30 days.', pg_temp.vec(4));
insert into summary (document_id, scope, content) values
  ('00000000-0000-0000-0000-000000000001', 'internal', 'Handbook: refund window.'),
  ('00000000-0000-0000-0000-000000000001', 'sales',    'Handbook: exception approver.'),
  ('00000000-0000-0000-0000-000000000001', 'people',   'Handbook: comp bands.'),
  ('00000000-0000-0000-0000-000000000002', 'public',   'Refund FAQ summary.');
insert into digest (topic, scope, document_ids, content) values
  ('refunds', 'public',   '{}', 'Refund digest, public.'),
  ('refunds', 'internal', '{}', 'Refund digest, internal.'),
  ('refunds', 'sales',    '{}', 'Refund digest, sales.'),
  ('compensation', 'people', '{}', 'Comp digest.');

create temp table t_ids on commit drop as select handle, id from principal;
grant select on t_ids to brain_app;

create function pg_temp.expect(label text, got text, want text) returns void language plpgsql as $$
begin
  if got is distinct from want then raise exception 'FAIL %: got %, want %', label, got, want; end if;
  raise notice 'ok   %', label;
end $$;

set local role brain_app;

-- 1. No principal set: nothing visible.
select pg_temp.expect('no principal sees no chunks', (select count(*)::text from chunk), '0');
select pg_temp.expect('no principal sees no digests', (select count(*)::text from digest), '0');

-- 2. Maya (sales).
select set_config('app.principal_id', (select id::text from t_ids where handle = 'maya'), true);
select pg_temp.expect('maya chunk scopes', (select string_agg(scope, ',' order by scope) from chunk), 'internal,public,sales');
select pg_temp.expect('maya cannot read comp chunk', (select count(*)::text from chunk where content ilike '%comp%'), '0');
select pg_temp.expect('maya summaries', (select string_agg(scope, ',' order by scope) from summary), 'internal,public,sales');
select pg_temp.expect('maya digests', (select string_agg(topic || '/' || scope, ',' order by scope) from digest), 'refunds/internal,refunds/public,refunds/sales');
select pg_temp.expect('maya still sees handbook metadata', (select count(*)::text from document), '2');
select pg_temp.expect('maya denied-scope routing on comp query',
  (select string_agg(scope || ':' || hits, ',') from denied_scope_hits(pg_temp.vec(3))), 'people:1');
select pg_temp.expect('maya no denial on refund query',
  (select count(*)::text from denied_scope_hits(pg_temp.vec(1))), '0');

-- 3. Support bot: public + support only. Approver chunk (sales) invisible.
select set_config('app.principal_id', (select id::text from t_ids where handle = 'svc-support-bot'), true);
select pg_temp.expect('bot chunk scopes', (select string_agg(scope, ',' order by scope) from chunk), 'public');
select pg_temp.expect('bot cannot read approver', (select count(*)::text from chunk where content ilike '%approved%'), '0');
select pg_temp.expect('bot summaries', (select string_agg(content, ',') from summary), 'Refund FAQ summary.');
select pg_temp.expect('bot documents', (select string_agg(title, ',') from document), 'Refund FAQ');

-- 4. Dana (exec): no people scope either.
select set_config('app.principal_id', (select id::text from t_ids where handle = 'dana'), true);
select pg_temp.expect('dana cannot read comp chunk', (select count(*)::text from chunk where scope = 'people'), '0');

-- 5. Identity tables are unreachable; token resolution works.
do $$ begin
  begin perform 1 from brain.principal; raise exception 'FAIL principal readable';
  exception when insufficient_privilege then raise notice 'ok   principal table not readable'; end;
  begin insert into brain.chunk (document_id, ord, scope, content)
        values ('00000000-0000-0000-0000-000000000002', 9, 'public', 'x'); raise exception 'FAIL chunk writable';
  exception when insufficient_privilege then raise notice 'ok   chunk not writable'; end;
end $$;
select pg_temp.expect('resolve_token', (select handle || '/' || role_id || '/' || array_to_string(scopes, ',')
  from resolve_token('demo-maya')), 'maya/sales/internal,public,sales');
select pg_temp.expect('bad token resolves to nothing', (select count(*)::text from resolve_token('nope')), '0');

-- 6. Ledger: own rows only, no read, no rewrite.
insert into ledger (principal_id, role_id, scopes, question, outcome)
  select id, 'exec', '{}', 'q', 'answered' from t_ids where handle = 'dana';
do $$ begin
  begin insert into brain.ledger (principal_id, role_id, scopes, question, outcome)
        select id, 'sales', '{}', 'forged', 'answered' from t_ids where handle = 'maya';
        raise exception 'FAIL forged ledger row accepted';
  exception when insufficient_privilege then raise notice 'ok   cannot log as another principal'; end;
  begin perform 1 from brain.ledger; raise exception 'FAIL ledger readable';
  exception when insufficient_privilege then raise notice 'ok   ledger not readable by app'; end;
end $$;

reset role;
do $$ begin
  begin update brain.ledger set question = 'edited'; raise exception 'FAIL ledger updated';
  exception when raise_exception then
    if sqlerrm like 'FAIL%' then raise; end if; raise notice 'ok   owner cannot update ledger'; end;
  begin delete from brain.ledger; raise exception 'FAIL ledger deleted';
  exception when raise_exception then
    if sqlerrm like 'FAIL%' then raise; end if; raise notice 'ok   owner cannot delete ledger'; end;
end $$;

rollback;
