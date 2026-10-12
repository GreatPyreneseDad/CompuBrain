-- brain/sf/03_mail.sql
-- Which inbound emails the mail loop has already pulled into the repo. Run as BRAIN_OWNER.
use role brain_owner;
use warehouse brain_wh;
use schema brain.core;

create table if not exists mail_seen (
  message_id varchar primary key,
  seen_at    timestamp_ltz default current_timestamp(),
  sender     varchar,
  subject    varchar,
  files      varchar
);
