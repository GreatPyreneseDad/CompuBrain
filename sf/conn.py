"""Snowflake connection for the brain. Key-pair auth as the BRAIN_SVC service user.

Environment:
  SNOWFLAKE_ACCOUNT           e.g. MYORG-MYACCOUNT
  SNOWFLAKE_PRIVATE_KEY_FILE  path to brain_svc_key.p8
  SNOWFLAKE_USER              default BRAIN_SVC
"""
from __future__ import annotations
import os
import snowflake.connector

EMBED_MODEL = os.environ.get("BRAIN_SF_EMBED_MODEL", "voyage-multilingual-2")
EMBED = f"snowflake.cortex.embed_text_1024('{EMBED_MODEL}', {{}})"      # EMBED.format('content') or .format('%s')

def connect(role: str = "BRAIN_OWNER"):
    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ.get("SNOWFLAKE_USER", "BRAIN_SVC"),
        private_key_file=os.environ["SNOWFLAKE_PRIVATE_KEY_FILE"],
        role=role, warehouse="BRAIN_WH", database="BRAIN", schema="CORE",
        session_parameters={"QUERY_TAG": "company-brain"})

def as_role(cur, role: str):
    """Become one asker. Secondary roles off, so the session holds this role's grants and no others."""
    cur.execute(f"use role {role}")
    cur.execute("use secondary roles none")
