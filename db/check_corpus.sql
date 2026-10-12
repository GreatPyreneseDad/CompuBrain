-- brain/db/check_corpus.sql
-- After ingesting corpus/, shows what each demo asker can see. Run as owner; read-only.
set search_path = brain, extensions, public;
\pset footer off
\echo == rows per scope (owner view) ==
select scope, count(*) chunks, (select count(*) from summary s where s.scope = c.scope) summaries,
       (select count(*) from digest d where d.scope = c.scope) digests
from chunk c group by scope order by scope;

begin;
create temp table t_ids on commit drop as select handle, id from principal;
create temp table t_out (asker text, chunks int, summaries int, digests int, documents int,
  sees_30_day bool, sees_approver bool, sees_45_day bool, sees_q3_exceptions bool, sees_comp bool) on commit drop;
grant select on t_ids to brain_app; grant insert on t_out to brain_app;
set local role brain_app;
do $$
declare h text;
begin
  foreach h in array array['maya', 'dana', 'svc-support-bot'] loop
    perform set_config('app.principal_id', (select id::text from t_ids where handle = h), true);
    insert into t_out select h,
      (select count(*) from brain.chunk), (select count(*) from brain.summary),
      (select count(*) from brain.digest), (select count(*) from brain.document),
      exists (select 1 from brain.chunk where content ~* 'within 30 days|window .* is 30 days|30 days of'),
      exists (select 1 from brain.chunk where content ilike '%Priya Raman%')
        or exists (select 1 from brain.summary where content ilike '%Priya%')
        or exists (select 1 from brain.digest where content ilike '%Priya%'),
      exists (select 1 from brain.chunk where content ilike '%45 days%refund%' or content ilike '%refund window of 45%')
        or exists (select 1 from brain.digest where content ilike '%45%' and topic = 'refunds'),
      exists (select 1 from brain.chunk where content ilike '%Meridian Health%')
        or exists (select 1 from brain.summary where content ilike '%Meridian%')
        or exists (select 1 from brain.digest where content ilike '%Meridian%'),
      exists (select 1 from brain.chunk where content ~ '145,000 to 178,000|190,000 to 240,000')
        or exists (select 1 from brain.summary where content ~ '145,000|190,000 to 240,000')
        or exists (select 1 from brain.digest where content ~ '145,000|190,000 to 240,000');
  end loop;
end $$;
reset role;
\echo == what each asker can reach, across all three grains ==
select * from t_out;
rollback;
