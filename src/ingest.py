"""Ingest original Retailrocket CSVs without changing source records."""
from pathlib import Path
import duckdb

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / 'data' / 'processed' / 'retailrocket.duckdb'
RAW = ROOT / 'data' / 'raw'


def ingest(raw=RAW, db=DB):
    raw, db = Path(raw), Path(db)
    required = ['events.csv']
    missing = [f for f in required if not (raw / f).exists()]
    if missing:
        raise FileNotFoundError(f"Missing {missing}; download Retailrocket from https://www.kaggle.com/datasets/retailrocket/ecommerce-dataset and extract into {raw}")
    db.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(db))
    try:
        con.execute('''CREATE OR REPLACE TABLE events AS
            SELECT CAST(timestamp AS BIGINT) AS timestamp_ms,
                   CAST(visitorid AS BIGINT) AS visitorid,
                   CAST(event AS VARCHAR) AS event,
                   CAST(itemid AS BIGINT) AS itemid,
                   TRY_CAST(transactionid AS BIGINT) AS transactionid,
                   epoch_ms(CAST(timestamp AS BIGINT)) AS event_ts
            FROM read_csv(?, header=true, all_varchar=true)''', [str(raw / 'events.csv')])
        parts = [raw / p for p in ['item_properties_part1.csv','item_properties_part2.csv'] if (raw / p).exists()]
        if parts:
            readers = ' UNION ALL '.join('SELECT * FROM read_csv(?, header=true, all_varchar=true)' for _ in parts)
            con.execute(f'''CREATE OR REPLACE TABLE item_properties AS
                SELECT CAST(timestamp AS BIGINT) AS timestamp_ms,
                       CAST(itemid AS BIGINT) AS itemid,
                       property, value, epoch_ms(CAST(timestamp AS BIGINT)) AS property_ts
                FROM ({readers})''', [str(p) for p in parts])
        if (raw/'category_tree.csv').exists():
            con.execute('''CREATE OR REPLACE TABLE category_tree AS
                SELECT TRY_CAST(categoryid AS BIGINT) categoryid,
                       TRY_CAST(parentid AS BIGINT) parentid
                FROM read_csv(?, header=true, all_varchar=true)''', [str(raw/'category_tree.csv')])
        print('Imported', con.execute('SELECT COUNT(*) FROM events').fetchone()[0], 'event rows')
    finally:
        con.close()

if __name__ == '__main__':
    ingest()
