"""Run a SQL file statement by statement as BRAIN_OWNER.   python -m sf.apply sf/01_schema.sql"""
import sys, pathlib
from sf.conn import connect

def main():
    sql = pathlib.Path(sys.argv[1]).read_text()
    with connect() as conn:
        for cur in conn.execute_string(sql, remove_comments=True):
            row = cur.fetchone()
            print(f"ok   {' '.join(cur.query.split())[:70]}  ->  {str(row[0])[:60] if row else ''}")

if __name__ == "__main__":
    main()
