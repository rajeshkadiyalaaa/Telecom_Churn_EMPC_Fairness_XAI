from pathlib import Path
import json
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/'publication'; E=ROOT/'results'; (P/'tables').mkdir(exist_ok=True); (P/'figures').mkdir(exist_ok=True)
s=json.loads((E/'policy_selections.json').read_text());pol=pd.read_csv(E/'policy_metrics.csv');ci=pd.read_csv(E/'bootstrap_intervals.csv');q=pol.pivot(index='seed',columns='policy',values='scenario_profit');eo=pol[pol.policy.eq('equal_opportunity')].set_index('seed')
t=pd.DataFrame({'model':{x['seed']:x['selected_model'] for x in s},'validation_gap':{x['seed']:100*x['equal_opportunity']['validation_abs_tpr_gap'] for x in s},'test_gap':100*eo.senior_tpr_gap.abs(),'profit':eo.scenario_profit,'difference':q.equal_opportunity-q.validation_profit}).join(ci[ci.metric.eq('paired_profit_difference')].set_index('seed')[['lower','upper']]);t.index.name='seed';t.to_csv(P/'tables/split_summary.csv');t=t.reset_index().sort_values('seed'); p=pd.read_csv(E/'policy_metrics.csv'); m=pd.read_csv(E/'model_metrics.csv'); e=pd.read_csv(E/'economic_sensitivity.csv')
plt.rcParams.update({'font.size':10,'font.family':'DejaVu Sans','ps.fonttype':42,'pdf.fonttype':42})
fig,ax=plt.subplots(figsize=(6.5,3.2)); x=range(len(t)); ax.plot(x,t.validation_gap,'o-',color='#222222',label='Validation');ax.plot(x,t.test_gap,'s--',color='#2374a6',label='Test'); ax.axhline(5,color='#777777',ls=':',label='5 pp tolerance');ax.set(xticks=list(x),xticklabels=t.seed.astype(str),xlabel='Split seed',ylabel='Absolute senior TPR gap (pp)');ax.legend(frameon=False,ncol=3,fontsize=9);fig.tight_layout()
for ext in ['png','eps']:fig.savefig(P/f'figures/figure1.{ext}',dpi=600)
plt.close(fig)
fig,ax=plt.subplots(figsize=(6.5,3.2));ax.errorbar(x,t.difference,yerr=[t.difference-t.lower,t.upper-t.difference],fmt='o',capsize=3,color='#222222');ax.axhline(0,color='#777777',ls=':');ax.set(xticks=list(x),xticklabels=t.seed.astype(str),xlabel='Split seed',ylabel='Scenario profit difference\n(currency units)');fig.tight_layout()
for ext in ['png','eps']:fig.savefig(P/f'figures/figure2.{ext}',dpi=600)
plt.close(fig)
summary=m[(m.partition=='test')&(m.calibration=='calibrated')].groupby('model')[['roc_auc','average_precision','brier','log_loss','scenario_profit','empirical_empc_oracle']].mean();summary.to_csv(P/'tables/model_summary.csv')
a=e[e.policy.eq('equal_opportunity')].copy();a['failure']=a.senior_tpr_gap.abs()>.05;a['absolute_gap_pp']=100*a.senior_tpr_gap.abs();a.groupby(['clv','acceptance']).agg(failures=('failure','sum'),mean_profit=('scenario_profit','mean'),median_gap_pp=('absolute_gap_pp','median')).to_csv(P/'tables/economics_summary.csv')
raw=m[m.partition.eq('test')].pivot(index=['seed','model'],columns='calibration',values='brier');raw['calibrated_minus_raw']=raw.calibrated-raw.raw;raw.groupby('model').mean().to_csv(P/'tables/calibration_summary.csv')
print((P/'tables/economics_summary.csv').read_text());print((P/'tables/calibration_summary.csv').read_text())
