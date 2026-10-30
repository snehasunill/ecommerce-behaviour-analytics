"""Deterministic validation: fixture is used only for tests, never portfolio findings."""
import pytest

duckdb=pytest.importorskip('duckdb')
from src.analysis import run_sql, statistical_results
from src.validate import validate

@pytest.fixture
def db():
    con=duckdb.connect(':memory:')
    con.execute('''CREATE TABLE events(timestamp_ms BIGINT,visitorid BIGINT,event VARCHAR,itemid BIGINT,transactionid BIGINT,event_ts TIMESTAMP)''')
    def add(day,visitor,event,item=1,tx=None,ms=0):
        # 2024-01-01 + day days and millisecond increment
        epoch=1704067200000+day*86400000+ms
        con.execute('INSERT INTO events VALUES (?,?,?,?,?,epoch_ms(?))',[epoch,visitor,event,item,tx,epoch])
    add(0,1,'view'); add(1,1,'addtocart'); add(2,1,'transaction',tx=3)
    add(0,2,'view'); add(1,2,'addtocart')
    add(0,3,'transaction',tx=4) # purchase without observed cart or view
    add(0,4,'view'); add(0,4,'addtocart',ms=0) # equal timestamp: not ordered
    add(0,5,'view'); add(3,5,'view'); add(10,5,'transaction',tx=5)
    add(39,6,'view') # ineligible for 37-day follow-up, given max day 39
    add(0,7,'view'); add(7,7,'view'); add(30,7,'view')
    yield con
    con.close()

def test_funnel_requires_order(db):
    run_sql(db,['02_conversion_funnel.sql'])
    row=db.execute('SELECT viewed,carted,purchased,cart_dropoff_pct FROM funnel_summary').fetchone()
    assert row==(6,2,1,50.0)
    assert db.execute('SELECT cart_ms FROM funnel_visitors WHERE visitorid=4').fetchone()[0] is None

def test_cohort_exact_day_and_censoring(db):
    run_sql(db,['04_cohort_retention.sql'])
    # user 7 active on D7; user 6 first observed on day 39 and excluded from D1/7/30.
    assert db.execute("SELECT COUNT(*) FROM cohort_retention WHERE eligible_visitors=0").fetchone()[0]==0
    row=db.execute('SELECT eligible_visitors,returned_visitors FROM cohort_retention WHERE day_n=7').fetchone()
    assert row == (6,1)

def test_engagement_disjoint_windows(db):
    run_sql(db,['03_engagement.sql'])
    assert db.execute('SELECT COUNT(*) FROM engagement_visitors').fetchone()[0]==6
    # Visitor 1 purchased on exposure day 2, so NOT counted as next-30-day buyer.
    assert db.execute('SELECT purchase_next_30d FROM engagement_visitors WHERE visitorid=1').fetchone()[0]==0
    # Visitor 5 purchased on day 10, after pre-window.
    assert db.execute('SELECT purchase_next_30d FROM engagement_visitors WHERE visitorid=5').fetchone()[0]==1

def test_data_quality(db):
    result=validate(db)
    assert result['rows']==15
    assert result['invalid_events']==0

def test_zero_denominator():
    con=duckdb.connect(':memory:')
    con.execute('CREATE TABLE funnel_visitors(visitorid INT, view_ms BIGINT,cart_ms BIGINT,purchase_ms BIGINT)')
    # Assert DuckDB TRY safe division behavior using NULLIF.
    assert con.execute('SELECT 1.0/NULLIF(0,0)').fetchone()[0] is None
    con.close()


def test_property_mapping_point_in_time_and_conflicts(db):
    run_sql(db,['05_product_analysis.sql'])
    # Optional category mapper expects a high-support item table; lower threshold here.
    db.execute('CREATE OR REPLACE TABLE item_metrics AS SELECT DISTINCT itemid FROM events')
    db.execute('CREATE TABLE item_properties(itemid BIGINT,timestamp_ms BIGINT,property VARCHAR,value VARCHAR)')
    base=1704067200000
    db.executemany('INSERT INTO item_properties VALUES (?,?,?,?)',[
        (1,base-100,'categoryid','10'),
        (1,base+86400000,'categoryid','11'),
        (1,base+86400000,'categoryid','12'),
        (1,base+2*86400000,'categoryid','13'),
    ])
    from src.ingest import ROOT
    db.execute((ROOT/'sql'/'06_optional_category_mapping.sql').read_text())
    assert db.execute("SELECT DISTINCT categoryid FROM item_categories_pit WHERE timestamp_ms=?",[base]).fetchall()==[(10,)]
    assert db.execute("SELECT COUNT(*) FROM item_categories_pit WHERE timestamp_ms=? AND mapping_status='ambiguous'",[base+86400000]).fetchone()[0]>=1
    assert db.execute("SELECT DISTINCT categoryid FROM item_categories_pit WHERE timestamp_ms=?",[base+2*86400000]).fetchall()==[(13,)]
