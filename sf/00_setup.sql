-- brain/sf/00_setup.sql
-- Run once, in a Snowsight worksheet, as ACCOUNTADMIN. Needs Enterprise Edition or higher
-- (row access policies are not available on Standard).
-- Creates: a warehouse, the BRAIN database, the roles, and a key-pair service user.
-- Everything after this file runs as the service user; nothing else needs ACCOUNTADMIN.

use role accountadmin;

create warehouse if not exists brain_wh warehouse_size = xsmall auto_suspend = 60 auto_resume = true;
create database if not exists brain;

-- Roles. One per kind of asker, plus the owner (ingest, admin) and the router (identity + refusal routing).
create role if not exists brain_owner;
create role if not exists brain_router;
create role if not exists brain_sales;
create role if not exists brain_exec;
create role if not exists brain_support_agent;

grant ownership on database brain to role brain_owner;
grant usage on warehouse brain_wh to role brain_owner;
grant usage on warehouse brain_wh to role brain_router;
grant usage on warehouse brain_wh to role brain_sales;
grant usage on warehouse brain_wh to role brain_exec;
grant usage on warehouse brain_wh to role brain_support_agent;

-- Cortex embedding functions.
grant database role snowflake.cortex_user to role brain_owner;
grant database role snowflake.cortex_user to role brain_router;
grant database role snowflake.cortex_user to role brain_sales;
grant database role snowflake.cortex_user to role brain_exec;
grant database role snowflake.cortex_user to role brain_support_agent;

-- The service user the API connects as. Key-pair only, no password.
create user if not exists brain_svc
  type = service
  default_role = brain_owner
  default_warehouse = brain_wh
  default_secondary_roles = ()            -- the asker role must be the only role in the session
  rsa_public_key = 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAz2LiU+ovEgcJmHi1gger9dDnVCyET6ZOQk/GjA5YPwJJYCCner9O7npeHrL/qtjShMJC8VYZGt3bf276g3FrmpE5z3d28Rldn6EI56l9hpJVC5wHnnOpZsv8qp+opSwFVIvqAKlqyB0aBiaXU5c1V5GpZhQGHJjr605JJ3O/CFvIa+cSy9ukKlesYo6raNekCoxbcAbw3AcUJFE4H+z3J9CY+fSoOezSCtO4DzUdIoJPVA3Oz7sQUHS6yOU5tMeTML/fXSaNTs8hbLhbk7YCLTPSmes5R8snq8a93SCBDtCOZlU/X5iBUhQ7pZS6h6jhAwvHm8NL7EqqOmAnmKAF5wIDAQAB';

grant role brain_owner         to user brain_svc;
grant role brain_router        to user brain_svc;
grant role brain_sales         to user brain_svc;
grant role brain_exec          to user brain_svc;
grant role brain_support_agent to user brain_svc;

-- So you can see the objects yourself in Snowsight.
grant role brain_owner to role sysadmin;

-- Only if the embedding model is not served in your region (01_schema.sql fails on EMBED_TEXT_1024):
-- alter account set cortex_enabled_cross_region = 'ANY_REGION';

-- The value to send back: your account identifier.
select current_organization_name() || '-' || current_account_name() as account_identifier;
