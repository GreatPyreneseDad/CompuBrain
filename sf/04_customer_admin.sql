-- brain/sf/04_customer_admin.sql — the customer asker. Run in Snowsight as ACCOUNTADMIN, once, after 00_setup.sql.
-- Then: python -m sf.apply sf/04_customer.sql
--
-- BRAIN_CUSTOMER is who a customer-facing page asks as: the help center's build and its "ask us" box.
-- It is mapped to the public scope only, so the row access policy, not the page, decides what a customer can see.
create role if not exists brain_customer;
grant usage on warehouse brain_wh to role brain_customer;
grant database role snowflake.cortex_user to role brain_customer;
grant role brain_customer to user brain_svc;
grant role brain_customer to role brain_owner;      -- so BRAIN_OWNER can grant it table privileges in 04_customer.sql
