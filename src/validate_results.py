"""Integration checks for exported experiment evidence; exits nonzero on inconsistency."""
import hashlib
import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from churn_study import clean_data,features,margin,policy_metrics,score_metrics,payoff_parameters

ROOT=Path(__file__).resolve().parents[1]

def main(output=None, skip_original_archive=False):
    output=Path(output) if output else ROOT/'results';manifest=json.loads((output/'manifest.json').read_text())
    assert manifest['status']=='complete'
    assert manifest['source_sha256']==hashlib.sha256((ROOT/'src/churn_study.py').read_bytes()).hexdigest()
    assert manifest['data_sha256']==hashlib.sha256((ROOT/'01_Data/telco_churn_raw.csv').read_bytes()).hexdigest()
    df=clean_data(pd.read_csv(ROOT/'01_Data/telco_churn_raw.csv')).set_index('customerID',drop=False)
    metrics=pd.read_csv(output/'model_metrics.csv');policies=pd.read_csv(output/'policy_metrics.csv');fairness=pd.read_csv(output/'fairness_metrics.csv')
    benefit,cost=payoff_parameters(**manifest['config']['economic'])
    bayes=cost/(benefit+cost);replayed=0;groups_checked=0
    for seed in manifest['config']['seeds']:
        directory=output/f'seed_{seed}';splits=pd.read_csv(directory/'split_ids.csv')
        assert len(splits)==len(df) and splits.customerID.is_unique
        assert set(splits.customerID)==set(df.customerID)
        for name,group in splits.groupby('partition'):
            assert np.array_equal(group.y_true.to_numpy(),df.loc[group.customerID].Churn.eq('Yes').astype(int).to_numpy())
        choice=json.loads((directory/'policy_selection.json').read_text())
        validation_metrics=metrics[(metrics.seed==seed)&(metrics.partition=='validation')&(metrics.calibration=='calibrated')&metrics.model.str.endswith('_original')]
        winner=validation_metrics.sort_values(['scenario_profit','model'],ascending=[False,True]).iloc[0].model
        assert winner==choice['selected_model']
        model_files=sorted(directory.glob('*.joblib'))
        assert len(model_files)==manifest['configurations_per_seed'], 'Regenerate all fitted models before replay validation'
        for path in model_files:
            saved=joblib.load(path)
            for part in ['validation','test']:
                pr=pd.read_csv(directory/f'{path.stem}_{part}_predictions.csv')
                assert set(pr.customerID)==set(splits.loc[splits.partition.eq(part),'customerID'])
                X=features(df.loc[pr.customerID],saved['variant'])
                assert X.columns.tolist()==saved['columns']
                z=margin(saved['model'],X,saved['family']);prob=saved['calibrator'].predict_proba(z.reshape(-1,1))[:,1]
                np.testing.assert_allclose(prob,pr.p_calibrated,atol=1e-12,rtol=1e-12)
                row=metrics[(metrics.seed==seed)&(metrics.model==path.stem)&(metrics.partition==part)&(metrics.calibration=='calibrated')].iloc[0]
                recomputed={**score_metrics(pr.y_true,prob),**policy_metrics(pr.y_true,prob>=bayes,benefit,cost)}
                for k,v in recomputed.items():np.testing.assert_allclose(row[k],v,atol=1e-9,equal_nan=True)
                replayed+=1
        pr=pd.read_csv(directory/'selected_policy_predictions.csv')
        yy=df.loc[pr.customerID].Churn.eq('Yes').astype(int).to_numpy()
        assert np.array_equal(yy,pr.y_true.to_numpy())
        assert np.array_equal(pr.gender.to_numpy(),df.loc[pr.customerID].gender.to_numpy())
        assert np.array_equal(pr.SeniorCitizen.to_numpy(),df.loc[pr.customerID].SeniorCitizen.to_numpy())
        for policy in ['contact_none','contact_all','standard_0.5','economic_bayes','validation_profit','equal_opportunity']:
            d=pr[policy].to_numpy();row=policies[(policies.seed==seed)&(policies.policy==policy)].iloc[0]
            for k,v in policy_metrics(pr.y_true,d,benefit,cost).items():np.testing.assert_allclose(row[k],v,atol=1e-9,equal_nan=True)
            for attr in ['gender','SeniorCitizen','intersection']:
                group=fairness[(fairness.seed==seed)&(fairness.policy==policy)&(fairness.attribute==attr)]
                for key in ['n','TP','FP','TN','FN']:assert int(group[key].sum())==int(row[key])
                groups_checked+=1
        expected=pr.p_calibrated.to_numpy()>=np.where(pr.SeniorCitizen.eq(1),choice['equal_opportunity']['1'],choice['equal_opportunity']['0'])
        assert np.array_equal(expected,pr.equal_opportunity.to_numpy())
        assert choice['equal_opportunity']['validation_abs_tpr_gap']<=manifest['config']['equal_opportunity_tolerance']+1e-12
    first=manifest['config']['seeds'][0];shap=json.loads((output/f'seed_{first}'/'shap_validation.json').read_text())
    assert shap['raw_additivity_max_error']<1e-7 and shap['calibrated_probability_max_error']<1e-7
    original={} if skip_original_archive else json.loads((ROOT/'archive/original_submission/manifest.json').read_text())
    for path,digest in original.items():assert hashlib.sha256((ROOT/'archive/original_submission'/path).read_bytes()).hexdigest()==digest
    check={'status':'passed','prediction_artifacts_replayed':replayed,'group_reconciliations':groups_checked,'original_artifacts_unchanged':None if skip_original_archive else len(original),'raw_shap_error':shap['raw_additivity_max_error'],'calibrated_shap_error':shap['calibrated_probability_max_error']}
    (output/'validation.json').write_text(json.dumps(check,indent=2));print(json.dumps(check,indent=2))

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',default=str(ROOT/'results'))
    parser.add_argument('--skip-original-archive', action='store_true', help='Supplement only: omit unrelated historical archive check')
    args=parser.parse_args()
    main(args.output,args.skip_original_archive)
