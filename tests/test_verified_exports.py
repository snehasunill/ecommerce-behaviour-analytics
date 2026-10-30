"""Validate shipped Tableau aggregates against independent source-data audit."""
import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data' / 'processed' / 'tableau'
VERIFIED = json.loads((ROOT / 'data' / 'processed' / 'independently_verified.json').read_text())

def test_funnel_counts_and_rates():
    row = pd.read_csv(OUT / 'funnel_summary.csv').iloc[0]
    f = VERIFIED['funnel']
    for key in ['viewed', 'carted', 'purchased']:
        assert int(row[key]) == f[key]
    assert round(100*(int(row.carted)-int(row.purchased))/int(row.carted),2) == f['cart_dropoff_pct']

def test_daily_event_count_reconciles_to_raw():
    daily = pd.read_csv(OUT/'daily_activity.csv')
    assert int(daily.event_count.sum()) == VERIFIED['quality']['rows']
    per_event = daily.groupby('event')['event_count'].sum().to_dict()
    assert per_event == VERIFIED['quality']['event_types']

def test_engagement_reconciles():
    summary = pd.read_csv(OUT/'engagement_summary.csv')
    groups = VERIFIED['statistics']['groups']
    for label, name in [('1 active day','single_day'),('2+ active days','repeat_days')]:
        row = summary.loc[summary.engagement_group==label].iloc[0]
        assert int(row.visitors)==groups[name]['visitors']
        assert int(row.buyers)==groups[name]['buyers']
        assert abs(row.purchase_pct-100*groups[name]['conversion_rate']) < 0.0005

def test_exact_day_cohorts_and_eligibility():
    cohort = pd.read_csv(OUT/'cohort_retention.csv')
    for day in [1,7,30]:
        d=cohort.loc[cohort.day_n==day]
        ref=VERIFIED['retention'][f'D{day}']
        assert int(d.eligible_visitors.sum())==ref['eligible']
        assert int(d.returned_visitors.sum())==ref['returned']
        assert (d.returned_visitors <= d.eligible_visitors).all()

def test_item_minimum_support():
    items=pd.read_csv(OUT/'item_metrics.csv')
    assert len(items)==VERIFIED['quality']['item_min_100_views_count']
    assert (items.views>=100).all()
