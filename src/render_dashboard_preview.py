"""Static preview using real aggregated outputs; NOT a published Tableau dashboard."""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'data'/'processed'/'tableau'
f=pd.read_csv(D/'funnel_summary.csv').iloc[0]
e=pd.read_csv(D/'engagement_summary.csv')
r=pd.read_csv(D/'cohort_retention.csv')
a=pd.read_csv(D/'daily_activity.csv',parse_dates=['event_date'])
fig,ax=plt.subplots(2,2,figsize=(14,9),constrained_layout=True)
fig.suptitle('Customer Journey | Engagement & Conversion Analytics\nRetailrocket • May–September 2015 • Verified aggregate data',fontsize=17)
ax[0,0].barh(['Viewed','Carted after view','Purchased after cart'],[f.viewed,f.carted,f.purchased])
ax[0,0].invert_yaxis();ax[0,0].set_title('Ordered visitor funnel');ax[0,0].set_xlabel('Distinct visitors')
for j,v in enumerate([f.viewed,f.carted,f.purchased]):ax[0,0].text(v+f.viewed*.01,j,f'{v:,.0f}',va='center',fontsize=9)
ax[0,0].set_xlim(0,f.viewed*1.27)
ax[0,1].bar(e.engagement_group,e.purchase_pct)
ax[0,1].set_title('Purchase in following 30 days');ax[0,1].set_ylabel('Visitors purchasing (%)')
for j,v in enumerate(e.purchase_pct):ax[0,1].text(j,v+.012,f'{v:.3f}%',ha='center',fontsize=10)
ret=r.groupby('day_n')[['eligible_visitors','returned_visitors']].sum()
ax[1,0].bar([f'D{n}' for n in ret.index],100*ret.returned_visitors/ret.eligible_visitors)
ax[1,0].set_title('Exact-day observed return rates');ax[1,0].set_ylabel('Horizon-eligible visitors (%)')
weekly=a.assign(week=a.event_date.dt.to_period('W').dt.start_time).groupby(['week','event'],observed=True).event_count.sum().reset_index()
for evt, g in weekly.groupby('event',observed=True):ax[1,1].plot(g.week,g.event_count,label=evt)
ax[1,1].legend();ax[1,1].set_title('Weekly behavioural events');ax[1,1].tick_params(axis='x',rotation=35)
fig.text(.5,.005,'Observational analysis • Funnel steps may span sessions/items • Not a Tableau screenshot',ha='center',fontsize=9)
out=ROOT/'dashboard'/'analytics_preview.png';fig.savefig(out,dpi=155,bbox_inches='tight');plt.close(fig)
print(out)
if __name__=='__main__':pass
