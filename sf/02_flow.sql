-- brain/sf/02_flow.sql
-- Flow: departments, planned tasks, and the unblock outbox. Run as BRAIN_OWNER after 01_schema.sql.
--   python -m sf.apply sf/02_flow.sql
-- TASK and OUTBOX carry a scope and sit behind the same SCOPE_GATE policy as knowledge:
-- a role sees only the work planned under scopes it holds.

use role brain_owner;
use warehouse brain_wh;
use schema brain.core;

-- Who to write to, what they may be told, and how much they can take on. Capacity is illustrative.
create or replace table department (
  id                varchar primary key,
  name              varchar not null,
  contact_title     varchar not null,
  email             varchar not null,
  scopes            varchar not null,         -- comma-separated: what an email to this department may draw on
  capacity_per_week int not null
);

insert into department (id, name, contact_title, email, scopes, capacity_per_week) values
  ('sales',            'Sales',            'Regional Director',            'sales-leads@kestrelridge.example',  'public,internal,sales', 6),
  ('sales_ops',        'Sales Operations', 'VP of Sales Operations',       'sales-ops@kestrelridge.example',    'public,internal,sales', 4),
  ('support',          'Support',          'Support Lead',                 'support-leads@kestrelridge.example','public,internal,support', 6),
  ('customer_success', 'Customer Success', 'Head of Customer Success',     'cs-leads@kestrelridge.example',     'public,internal', 5),
  ('engineering',      'Engineering',      'VP of Engineering',            'eng-leads@kestrelridge.example',    'public,internal', 3),
  ('product',          'Product',          'VP of Product',                'product-leads@kestrelridge.example','public,internal', 3),
  ('finance',          'Finance',          'Controller',                   'finance@kestrelridge.example',      'public,internal,finance', 4),
  ('legal',            'Legal',            'General Counsel',              'legal@kestrelridge.example',        'public,internal,legal', 2),
  ('leadership',       'Leadership',       'Chief of Staff',               'exec-office@kestrelridge.example',  'public,internal,sales,finance,legal,exec', 3),
  ('people',           'People Ops',       'Head of People',               'people-ops@kestrelridge.example',   'public,internal,people', 3);

create or replace table task (
  id          varchar default uuid_string() primary key,
  created_at  timestamp_ltz default current_timestamp(),
  subject     varchar not null,               -- the customer or matter
  document    varchar not null,               -- title of the document that caused it
  planned_by  varchar not null,               -- principal handle that planned it
  scope       varchar not null,               -- scope the plan was made under
  department  varchar not null,               -- owning department
  task        varchar not null,
  due_date    date,
  blocked_by  varchar,                        -- department this task waits on, if any
  need        varchar,                        -- what is needed from them
  issue_url   varchar
) with row access policy scope_gate on (scope);

create or replace table outbox (
  id          varchar default uuid_string() primary key,
  created_at  timestamp_ltz default current_timestamp(),
  scope       varchar not null,               -- scope of the plan that raised it
  sent_as     varchar not null,               -- principal handle
  from_dept   varchar not null,
  to_dept     varchar not null,
  to_email    varchar not null,
  subject     varchar not null,
  body        varchar not null,
  about       varchar not null,               -- customer or matter
  needed_by   date,
  withheld    varchar default '',             -- scopes the sender drew on that the recipient does not hold
  status      varchar default 'queued',       -- queued | sent | failed
  issue_url   varchar
) with row access policy scope_gate on (scope);

grant select on table department to role brain_router;
grant select on table department to role brain_sales;
grant select on table department to role brain_exec;
grant select on table department to role brain_support_agent;
grant select, insert on table task   to role brain_sales;
grant select, insert on table task   to role brain_exec;
grant select, insert on table task   to role brain_support_agent;
grant select, insert on table outbox to role brain_sales;
grant select, insert on table outbox to role brain_exec;
grant select, insert on table outbox to role brain_support_agent;
