"""Run audited SQL analytics and statistical inference on the observed dataset."""
import json
import math
from pathlib import Path
import duckdb
import numpy as np
import pandas as pd
from scipy.stats import norm
from statsmodels.stats.proportion import proportion_confint, confint_proportions_2indep
from statsmodels.stats.power import NormalIndPower
import statsmodels.api as sm
from .ingest import ROOT, DB
from .validate import validate

OUT=ROOT/'data'/'processed'

def run_sql(con, files=None):
    files=files or ['02_conversion_funnel.sql','03_engagement.sql','04_cohort_retention.sql','05_product_analysis.sql']
    for filename in files:
        sql=(ROOT/'sql'/filename).read_text()
        con.execute(sql)

def statistical_results(con):
    df=con.execute('SELECT first_week_active_days,first_week_events,first_week_carts,purchase_next_30d FROM engagement_visitors').df()
    result={'design':'First seven days of observed activity are predictors; purchase in following 30 days is outcome; minimum 37-day follow-up.'}
    groups={}
    for k, frame in [('single_day',df[df.first_week_active_days==1]), ('repeat_days',df[df.first_week_active_days>=2])]:
        n=len(frame); bought=int(frame.purchase_next_30d.sum()); low,high=proportion_confint(bought,n,alpha=.05,method='wilson') if n else (None,None)
        groups[k]={'visitors':n,'buyers':bought,'conversion_rate':bought/n if n else None,'wilson_95_ci':[low,high]}
    result['groups']=groups
    if all(groups[k]['visitors'] for k in groups):
        a,b=groups['repeat_days'],groups['single_day']
        result['repeat_minus_single_percentage_points']=100*(a['conversion_rate']-b['conversion_rate'])
        low,high=confint_proportions_2indep(a['buyers'],a['visitors'],b['buyers'],b['visitors'],method='newcomb',compare='diff')
        result['difference_95_ci_percentage_points']=[100*low,100*high]
    if df.purchase_next_30d.nunique()==2:
        design=pd.DataFrame({'repeat_days':(df.first_week_active_days>=2).astype(int),
                             'log1p_events':np.log1p(df.first_week_events),
                             'any_cart':(df.first_week_carts>0).astype(int)})
        try:
            fit=sm.Logit(df.purchase_next_30d,sm.add_constant(design)).fit(disp=False,maxiter=100)
            conf=fit.conf_int()
            result['logistic_regression']={name:{'odds_ratio':float(np.exp(fit.params[name])),
                'odds_ratio_95_ci':[float(np.exp(conf.loc[name,0])),float(np.exp(conf.loc[name,1]))],
                'p_value':float(fit.pvalues[name])} for name in fit.params.index}
            result['logistic_regression_notes']='Observational associations, not causal effects; predictors measure activity in the first observed week only.'
        except (ValueError, np.linalg.LinAlgError, RuntimeError) as exc:
            result['logistic_regression_error']=str(exc)
    return result

def experiment_design(con):
    # Prospective randomized cart UX experiment; uses observed ordered-funnel rate as planning proxy only.
    rate=con.execute('SELECT cart_to_purchase_pct FROM funnel_summary').fetchone()[0]
    p=(rate or 0)/100
    mde_abs=.02  # pre-specified illustrative 2 percentage-point absolute lift
    if p<=0 or p+mde_abs>=1:
        return {'baseline_proxy':p,'warning':'Cannot compute power with observed baseline proxy'}
    test=NormalIndPower()
    from statsmodels.stats.proportion import proportion_effectsize
    effect=abs(proportion_effectsize(p,p+mde_abs))
    n=math.ceil(test.solve_power(effect_size=effect,alpha=.05,power=.8,ratio=1,alternative='two-sided'))
    return {'baseline_proxy':p,'absolute_mde_percentage_points':2.0,'alpha':.05,'power':.8,
            'required_users_per_arm':n,'randomization_unit':'eligible visitor',
            'primary_metric':'visitor-level cart-to-purchase conversion within a prespecified 7-day window',
            'notes':'Hypothetical experiment only. Historical ordered-funnel conversion is a rough planning proxy, not an experimental baseline. Recalculate with eligibility/window-aligned data. No test was run.'}

def main():
    if not DB.exists():
        raise FileNotFoundError('Database missing. Run: python -m src.ingest')
    OUT.mkdir(parents=True,exist_ok=True)
    con=duckdb.connect(str(DB))
    try:
        quality=validate(con)
        (OUT/'quality_report.json').write_text(json.dumps(quality,indent=2,default=str))
        run_sql(con)
        stats=statistical_results(con)
        experiment=experiment_design(con)
        (OUT/'statistics.json').write_text(json.dumps(stats,indent=2,default=str))
        (OUT/'experiment_power.json').write_text(json.dumps(experiment,indent=2,default=str))
        summary=con.execute('SELECT * FROM funnel_summary').df().to_dict(orient='records')[0]
        print('QUALITY:',json.dumps(quality,default=str))
        print('FUNNEL:',json.dumps(summary,default=str))
        print('STATISTICS:',json.dumps(stats,default=str))
        print('EXPERIMENT:',json.dumps(experiment,default=str))
    finally: con.close()

if __name__=='__main__': main()
