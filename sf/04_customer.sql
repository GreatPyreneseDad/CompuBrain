-- brain/sf/04_customer.sql — run as BRAIN_OWNER after 04_customer_admin.sql:  python -m sf.apply sf/04_customer.sql
use role brain_owner;
use schema brain.core;

grant usage on database brain to role brain_customer;
grant usage on schema brain.core to role brain_customer;
grant select on table chunk to role brain_customer;
grant select on table summary to role brain_customer;
grant select on table digest to role brain_customer;
grant select on table document_scope to role brain_customer;
grant select on view visible_document to role brain_customer;
grant insert on table ledger to role brain_customer;

-- Short, plain answers from the knowledge base articles; never internal terms or conflicts.
insert into brain_role (id, sf_role, profile)
  select 'customer', 'BRAIN_CUSTOMER', parse_json('{"grain":"chunk","max_words":120,"format":"prose","define_terms":true,"surface_conflicts":false,"prefer_sources":["support-kb","public-site"]}');

-- Public only. This one row is the whole customer boundary.
insert into role_scope (sf_role, scope) values ('BRAIN_CUSTOMER', 'public');

-- The help center's token. It ships inside the page, so treat it as public: it can only ever reach public rows.
insert into principal (handle, kind, role_id, token_hash)
  select 'web-helpcenter', 'agent', 'customer', sha2('helpcenter-public', 256);
