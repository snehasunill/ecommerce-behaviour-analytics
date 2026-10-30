"""Exports real analytical results for Tableau Public; no synthetic observations."""
import duckdb
from .ingest import DB, ROOT

EXPORTS=['funnel_summary','engagement_summary','cohort_retention','daily_activity','item_metrics']

def main():
    if not DB.exists(): raise FileNotFoundError('Run ingestion and analysis first')
    con=duckdb.connect(str(DB),read_only=True)
    out=ROOT/'data'/'processed'/'tableau'
    out.mkdir(parents=True,exist_ok=True)
    try:
        for table in EXPORTS:
            target=out/(table+'.csv')
            con.execute(f"COPY (SELECT * FROM {table}) TO '{target.as_posix()}' (HEADER, DELIMITER ',')")
            print(table,con.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0], 'rows')
    finally:con.close()

if __name__=='__main__': main()
