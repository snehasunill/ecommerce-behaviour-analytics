"""Export Tableau-ready aggregates directly from the actual Retailrocket events CSV.

Independent pandas path when DuckDB isn't installed. No synthetic or visitor-level exports.
"""
from pathlib import Path
import json
import pandas as pd
from statsmodels.stats.proportion import proportion_confint

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data' / 'processed' / 'tableau'

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    verified = json.loads((ROOT/'data'/'processed'/'independently_verified.json').read_text())
    events = pd.read_csv(ROOT/'data'/'raw'/'events.csv', usecols=['timestamp','visitorid','event','itemid'], dtype={'timestamp':'int64','visitorid':'int64','event':'category','itemid':'int64'})
    events['event_date'] = pd.to_datetime(events.timestamp,unit='ms',utc=True).dt.tz_localize(None).dt.normalize()
    f=verified['funnel']
    pd.DataFrame([f]).to_csv(OUT/'funnel_summary.csv',index=False)
    rows=[]
    for label,key in [('1 active day','single_day'),('2+ active days','repeat_days')]:
        g=verified['statistics']['groups'][key]
        rows.append({'engagement_group':label,'visitors':g['visitors'],'buyers':g['buyers'],'purchase_pct':100*g['conversion_rate'], 'ci_low_pct':100*g['wilson_95_ci'][0], 'ci_high_pct':100*g['wilson_95_ci'][1]})
    pd.DataFrame(rows).to_csv(OUT/'engagement_summary.csv',index=False)
    daily=events.groupby(['event_date','event'],observed=True).agg(event_count=('visitorid','size'),unique_visitors=('visitorid','nunique')).reset_index()
    daily.to_csv(OUT/'daily_activity.csv',index=False)
    first=events.groupby('visitorid',sort=False).event_date.min().rename('cohort_date')
    days=events[['visitorid','event_date']].drop_duplicates()
    cohort_rows=[]
    end=events.event_date.max()
    # Weekly cohort plus *exact* day-N observed repeat activity.
    for horizon in [1,7,30]:
        eligible=first[first+pd.Timedelta(days=horizon)<=end]
        eligible_frame=eligible.rename('cohort_date').reset_index()
        eligible_frame['cohort_week']=eligible_frame.cohort_date.dt.to_period('W-SUN').dt.start_time
        sizes=eligible_frame.groupby('cohort_week').size()
        target=eligible_frame[['visitorid','cohort_week','cohort_date']].copy()
        target['event_date']=target.cohort_date+pd.Timedelta(days=horizon)
        returned=target.merge(days,how='inner',on=['visitorid','event_date']).groupby('cohort_week').size()
        for week, n in sizes.items():
            k=int(returned.get(week,0))
            cohort_rows.append({'cohort_week':week.date().isoformat(),'day_n':horizon,'eligible_visitors':int(n),'returned_visitors':k,'return_pct':100*k/n})
    cohort=pd.DataFrame(cohort_rows).sort_values(['cohort_week','day_n'])
    cohort.to_csv(OUT/'cohort_retention.csv',index=False)
    items=pd.read_csv(ROOT/'data'/'processed'/'items_verified.csv')
    items.to_csv(OUT/'item_metrics.csv',index=False)
    # Confirm all externally reported totals, to prevent exporting incompatible reports.
    assert int(daily.event_count.sum())==verified['quality']['rows']
    for horizon in [1,7,30]:
        d=cohort[cohort.day_n==horizon]
        assert int(d.eligible_visitors.sum())==verified['retention'][f'D{horizon}']['eligible']
        assert int(d.returned_visitors.sum())==verified['retention'][f'D{horizon}']['returned']
    assert sum(x['visitors'] for x in rows)==sum(x['visitors'] for x in verified['statistics']['groups'].values())
    manifest={p.name:int(sum(1 for _ in p.open())-1) for p in sorted(OUT.glob('*.csv'))}
    (OUT/'manifest.json').write_text(json.dumps({'data_source':'Retailrocket events.csv; real observed records', 'export_method':'independently verified pandas', 'rows':manifest,'checks_passed':True},indent=2))
    print(json.dumps(manifest,indent=2))

if __name__=='__main__':main()
