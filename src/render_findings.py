"""Generate a factual results snapshot from pipeline outputs (no generated claims)."""
import json
from pathlib import Path
import duckdb
from .ingest import ROOT, DB

def main():
    p=ROOT/'data'/'processed'
    stats=json.loads((p/'statistics.json').read_text())
    power=json.loads((p/'experiment_power.json').read_text())
    con=duckdb.connect(str(DB),read_only=True)
    try:
        f=con.execute('SELECT * FROM funnel_summary').df().iloc[0].to_dict()
        counts=con.execute('SELECT COUNT(*) AS n,COUNT(DISTINCT visitorid) AS u FROM events').fetchone()
        retention=con.execute('SELECT day_n, SUM(returned_visitors),SUM(eligible_visitors) FROM cohort_retention GROUP BY 1 ORDER BY 1').fetchall()
        items=con.execute('SELECT COUNT(*) FROM item_metrics').fetchone()[0]
    finally:con.close()
    groups=stats['groups']
    gap=stats.get('repeat_minus_single_percentage_points')
    lines=[
        '# Verified observed findings — Retailrocket',
        '',
        f'- Dataset: **{counts[0]:,} recorded events** across **{counts[1]:,} observed visitors**.',
        f'- Ordered visitor funnel: **{f["viewed"]:,.0f} views → {f["carted"]:,.0f} carts → {f["purchased"]:,.0f} purchases** (distinct visitors, strictly ordered milestones).',
        f'- Of visitors reaching the qualifying cart stage, **{f["cart_dropoff_pct"]:.2f}%** did not have a later observed qualifying purchase; this is not verified checkout abandonment.',
        f'- View-to-purchase progression: **{f["view_to_purchase_pct"]:.2f}%** of visitors with a view.',
    ]
    if gap is not None:
        lines += [f'- Within the follow-up-eligible landmark sample, future 30-day purchase rates differed by **{gap:+.3f} percentage points** between repeat-day and single-day first-week engagement groups (association, not causation).',
                  f'- Repeat group: {groups["repeat_days"]["buyers"]:,}/{groups["repeat_days"]["visitors"]:,}; single-day group: {groups["single_day"]["buyers"]:,}/{groups["single_day"]["visitors"]:,}.']
    for day,returned,eligible in retention:
        lines.append(f'- D{day} exact-day observed return: **{100*returned/eligible:.2f}%** ({returned:,}/{eligible:,} eligible cohort members).' if eligible else f'- D{day}: no eligible cohorts.')
    lines += [f'- Items with at least 100 observed view events: **{items:,}**.',
              '', '## Resume bullet candidates — verify these descriptions before using',
              f'- Analyzed **{counts[0]:,} e-commerce behavioral events** with DuckDB SQL, constructing an ordered visitor funnel that quantified **{f["cart_dropoff_pct"]:.2f}%** observed cart-stage non-progression.',
              ('- Compared future purchase rates across first-week engagement groups with 95%% confidence intervals and logistic regression, measuring an observed **%+.3f-percentage-point** difference while separating predictors from subsequent outcomes.' % gap) if gap is not None else '- Investigated early engagement and future purchase with a disjoint observation/outcome window, Wilson confidence intervals, and logistic regression.',
              f'- Produced **5 Tableau-ready analytical datasets** spanning funnel, engagement, cohort return, temporal trends, and item performance; evaluated **{items:,}** adequately supported items and documented a checkout A/B test proposal (not conducted).',
              '', 'Dashboard status: CSV exports generated; Tableau visualization still requires manual authoring/publication.',
              'No experiment was run, and no actual improvement in conversion is claimed.',
              '']
    path=ROOT/'reports'/'verified_findings.md'
    path.write_text('\n'.join(lines))
    print('Wrote',path)

if __name__=='__main__':main()
