"""Hard-fail validation for gross source defects; log repeated-event counts as diagnostics."""
import json
from pathlib import Path
import duckdb
from .ingest import DB, ROOT


def validate(con):
    r={}
    r['rows']=con.execute('SELECT COUNT(*) FROM events').fetchone()[0]
    r['event_types']=dict(con.execute('SELECT event,COUNT(*) FROM events GROUP BY 1').fetchall())
    r['distinct_visitors']=con.execute('SELECT COUNT(DISTINCT visitorid) FROM events').fetchone()[0]
    r['time_range']=list(map(str,con.execute('SELECT MIN(event_ts), MAX(event_ts) FROM events').fetchone()))
    r['null_keys']=con.execute('SELECT COUNT(*) FROM events WHERE visitorid IS NULL OR itemid IS NULL').fetchone()[0]
    r['invalid_events']=con.execute("SELECT COUNT(*) FROM events WHERE event NOT IN ('view','addtocart','transaction') OR event IS NULL").fetchone()[0]
    r['missing_transaction_ids']=con.execute("SELECT COUNT(*) FROM events WHERE event='transaction' AND transactionid IS NULL").fetchone()[0]
    r['unexpected_transaction_ids']=con.execute("SELECT COUNT(*) FROM events WHERE event<>'transaction' AND transactionid IS NOT NULL").fetchone()[0]
    r['exact_duplicate_rows']=con.execute('''SELECT COALESCE(SUM(n-1),0) FROM
       (SELECT COUNT(*) n FROM events GROUP BY timestamp_ms,visitorid,event,itemid,transactionid HAVING COUNT(*)>1)''').fetchone()[0]
    r['nonpositive_timestamps']=con.execute('SELECT COUNT(*) FROM events WHERE timestamp_ms<=0 OR event_ts IS NULL').fetchone()[0]
    r['item_property_available']=con.execute("SELECT COUNT(*)>0 FROM information_schema.tables WHERE table_name='item_properties'").fetchone()[0]
    if r['item_property_available']:
        r['property_item_match_pct']=con.execute('''SELECT ROUND(100.0*COUNT(DISTINCT e.itemid) FILTER (WHERE p.itemid IS NOT NULL)/NULLIF(COUNT(DISTINCT e.itemid),0),2)
          FROM events e LEFT JOIN (SELECT DISTINCT itemid FROM item_properties) p USING(itemid)''').fetchone()[0]
    fatal=['null_keys','invalid_events','missing_transaction_ids','unexpected_transaction_ids','nonpositive_timestamps']
    assert r['rows']>0, 'Empty event table'
    assert not any(r[k] for k in fatal), f"Data validation failed: {[(k,r[k]) for k in fatal if r[k]]}"
    return r


def main():
    con=duckdb.connect(str(DB),read_only=True)
    try: result=validate(con)
    finally: con.close()
    p=ROOT/'data'/'processed'/'quality_report.json'
    p.write_text(json.dumps(result,indent=2,default=str))
    print(json.dumps(result,indent=2,default=str))

if __name__=='__main__': main()
