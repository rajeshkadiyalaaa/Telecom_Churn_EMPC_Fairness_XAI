"""Reproducible churn experiments. All policy selection uses validation data only."""
from __future__ import annotations
import argparse
import hashlib
import importlib.metadata
import json
import platform
import time
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from scipy.special import expit, logit
from scipy.stats import beta
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss, log_loss, confusion_matrix
from imblearn.over_sampling import RandomOverSampler
from catboost import CatBoostClassifier, Pool

ROOT = Path(__file__).resolve().parents[1]

def clean_data(raw):
    df = raw.copy()
    if df.customerID.duplicated().any() or df.Churn.isna().any() or not set(df.Churn).issubset({'Yes','No'}):
        raise ValueError('Invalid IDs or target labels')
    tc = pd.to_numeric(df.TotalCharges, errors='coerce')
    missing = tc.isna()
    eligible = df.TotalCharges.astype(str).str.strip().eq('') & df.tenure.eq(0)
    if (missing & ~eligible).any():
        raise ValueError('Unexpected missing/non-numeric charges; manual data review required')
    df['TotalCharges'] = tc.fillna(0.0)
    df['TotalCharges_missing'] = missing.astype(int)
    if df.isna().any().any():
        raise ValueError('Unexpected missing fields')
    return df

def features(df, variant='original'):
    X = df.drop(columns=['customerID','Churn']).copy()
    if variant == 'unaware':
        X = X.drop(columns=['SeniorCitizen','gender'])
    if variant == 'engineered':
        protection = (X[['OnlineSecurity','OnlineBackup','DeviceProtection','TechSupport']]=='Yes').sum(axis=1)
        streaming = (X[['StreamingTV','StreamingMovies']]=='Yes').sum(axis=1)
        services = protection + streaming + X.PhoneService.eq('Yes') + X.MultipleLines.eq('Yes') + X.InternetService.ne('No')
        X['CurrentRate_CumulativeDifference'] = X.MonthlyCharges*X.tenure-X.TotalCharges
        X['Protection_to_Streaming_Ratio'] = (protection+1)/(streaming+1)
        X['Avg_Price_Per_Service'] = X.MonthlyCharges/services.clip(lower=1)
        X['Contract_Tenure_Product'] = X.tenure*X.Contract.map({'Month-to-month':1/12,'One year':1.,'Two year':2.})
        X['Early_Lifecycle'] = (X.tenure<=5).astype(int)
        X['Fiber_ElectronicCheck_Monthly'] = (X.InternetService.eq('Fiber optic') & X.PaymentMethod.eq('Electronic check') & X.Contract.eq('Month-to-month')).astype(int)
    assert 'customerID' not in X and 'Churn' not in X and 'Churn_Binary' not in X
    return X

def split_indices(y, seed, config):
    dev, test = train_test_split(np.arange(len(y)),test_size=config['test_fraction'],random_state=seed,stratify=y)
    rest, val = train_test_split(dev,test_size=config['validation_fraction_of_development'],random_state=seed+1,stratify=y[dev])
    fit, cal = train_test_split(rest,test_size=config['calibration_fraction_of_remaining'],random_state=seed+2,stratify=y[rest])
    splits = {'fit':fit,'calibration':cal,'validation':val,'test':test}
    assert sum(map(len,splits.values()))==len(y)
    assert len(set(np.concatenate(list(splits.values()))))==len(y)
    return splits

def payoff_parameters(clv=200.,offer_cost=10.,contact_cost=1.,acceptance=.3):
    if not (clv>offer_cost>=0 and contact_cost>=0 and 0<=acceptance<=1):
        raise ValueError('Invalid economics')
    return acceptance*(clv-offer_cost)-contact_cost, offer_cost+contact_cost

def policy_metrics(y, decision, benefit=56., cost=11.):
    y = np.asarray(y); decision = np.asarray(decision,dtype=bool)
    tn,fp,fn,tp = confusion_matrix(y,decision,labels=[0,1]).ravel()
    return {'n':len(y),'TP':int(tp),'FP':int(fp),'TN':int(tn),'FN':int(fn),
            'selection_rate':float(decision.mean()),'recall':float(tp/(tp+fn)) if tp+fn else np.nan,
            'fpr':float(fp/(fp+tn)) if fp+tn else np.nan,
            'precision':float(tp/(tp+fp)) if tp+fp else np.nan,
            'accuracy':float((tp+tn)/len(y)), 'f1':float(2*tp/(2*tp+fp+fn)) if 2*tp+fp+fn else 0.,
            'scenario_profit':float(benefit*tp-cost*fp),
            'profit_per_customer':float((benefit*tp-cost*fp)/len(y))}

def score_metrics(y,p):
    return {'roc_auc':float(roc_auc_score(y,p)), 'average_precision':float(average_precision_score(y,p)),
            'brier':float(brier_score_loss(y,p)),'log_loss':float(log_loss(y,p,labels=[0,1]))}

def threshold_curve(y,p):
    """All realizable >= score cutoffs, including no contact; ties stay together."""
    y=np.asarray(y); p=np.asarray(p)
    order=np.argsort(-p,kind='stable'); s=p[order]; labels=y[order]
    ends=np.r_[np.flatnonzero(s[:-1]!=s[1:]),len(s)-1]
    tp=np.r_[0,np.cumsum(labels)[ends]].astype(int)
    selected=np.r_[0,ends+1]
    return np.r_[np.nextafter(s[0],np.inf),s[ends]],tp,selected-tp

def select_profit_threshold(y,p,benefit=56.,cost=11.):
    thresholds,tp,fp=threshold_curve(y,p)
    # Ties prefer fewer offers because no-contact/high thresholds appear first.
    return float(thresholds[np.argmax(benefit*tp-cost*fp)])

def empirical_empc(y,p,clv=200.,offer_cost=10.,contact_cost=1.,nodes=128):
    """Descriptive oracle score metric, NOT a deployable policy selected on test labels."""
    _,tp,fp=threshold_curve(y,p)
    x,w=np.polynomial.legendre.leggauss(nodes); g=(x+1)/2; weights=w/2*beta.pdf(g,6,14)
    benefits=g*(clv-offer_cost)-contact_cost
    profits=benefits[:,None]*tp-(offer_cost+contact_cost)*fp
    return float(weights@profits.max(axis=1)/len(y))

def select_equal_opportunity(y,p,group,tolerance=.05,benefit=56.,cost=11.):
    curves=[]
    for value in [0,1]:
        m=np.asarray(group)==value
        if np.sum(np.asarray(y)[m])==0: raise ValueError('No positive labels in fairness group')
        t,tp,fp=threshold_curve(np.asarray(y)[m],np.asarray(p)[m])
        curves.append((t,tp,fp,tp/np.sum(np.asarray(y)[m])))
    a,b=curves
    gap=np.abs(a[3][:,None]-b[3][None,:])
    profit=(benefit*a[1]-cost*a[2])[:,None]+(benefit*b[1]-cost*b[2])[None,:]
    profit=np.where(gap<=tolerance+1e-12,profit,-np.inf)
    i,j=np.unravel_index(np.argmax(profit),profit.shape)
    return {'0':float(a[0][i]),'1':float(b[0][j]),'validation_abs_tpr_gap':float(gap[i,j]),'validation_profit':float(profit[i,j])}

def fairness_rows(df,y,d,policy,seed,benefit=56.,cost=11.):
    rows=[]
    for attribute in ['SeniorCitizen','gender','intersection']:
        groups = df.SeniorCitizen.astype(str)+'|'+df.gender if attribute=='intersection' else df[attribute].astype(str)
        for value in sorted(groups.unique()):
            mask=groups.eq(value).to_numpy()
            m=policy_metrics(np.asarray(y)[mask],np.asarray(d)[mask],benefit,cost)
            rows.append({'seed':seed,'policy':policy,'attribute':attribute,'group':value,**m})
    return rows

def tpr_gap(y,d,g):
    rates=[np.mean(np.asarray(d)[(np.asarray(g)==v)&(np.asarray(y)==1)]) for v in [0,1]]
    return float(rates[1]-rates[0])

def build_model(X,family,regime,seed,cfg):
    weight='balanced' if regime=='weighted' else None
    if family=='catboost':
        return CatBoostClassifier(iterations=cfg['catboost_iterations'],depth=5,learning_rate=.05,
            loss_function='Logloss',auto_class_weights='Balanced' if weight else None,
            random_seed=seed,verbose=False,allow_writing_files=False,thread_count=cfg['threads'],
            cat_features=X.select_dtypes(exclude='number').columns.tolist())
    numeric=X.select_dtypes('number').columns.tolist(); categorical=X.select_dtypes(exclude='number').columns.tolist()
    pre=ColumnTransformer([('num',StandardScaler(),numeric),('cat',OneHotEncoder(handle_unknown='ignore',drop='first'),categorical)])
    clf=LogisticRegression(max_iter=2000,class_weight=weight,random_state=seed) if family=='logistic' else RandomForestClassifier(n_estimators=cfg['random_forest_trees'],min_samples_leaf=5,max_features='sqrt',class_weight=weight,random_state=seed,n_jobs=cfg['threads'])
    return make_pipeline(pre,clf)

def margin(model,X,family):
    if family=='catboost': return np.asarray(model.predict(X,prediction_type='RawFormulaVal'))
    return logit(np.clip(model.predict_proba(X)[:,1],1e-7,1-1e-7))

def fit_configuration(X,y,splits,family,regime,seed,cfg):
    model=build_model(X,family,regime,seed,cfg)
    fit=splits['fit']; xf=X.iloc[fit]; yf=y[fit]
    if regime=='oversampled': xf,yf=RandomOverSampler(random_state=seed).fit_resample(xf,yf)
    model.fit(xf,yf)
    cal=splits['calibration']
    # Regularized Platt-style logistic calibration; fit on disjoint original-prevalence data.
    calibrator=LogisticRegression(C=1e6,max_iter=2000).fit(margin(model,X.iloc[cal],family).reshape(-1,1),y[cal])
    predictions={}
    for part in ['validation','test']:
        z=margin(model,X.iloc[splits[part]],family)
        predictions[part]={'raw':expit(z),'calibrated':calibrator.predict_proba(z.reshape(-1,1))[:,1]}
    return model,calibrator,predictions

def bootstrap_policies(y,policies,senior,gender,n_boot,seed,benefit=56.,cost=11.):
    rng=np.random.default_rng(seed); strata=pd.Series(y.astype(str)+'|'+senior.astype(str)+'|'+gender.astype(str))
    pools=[np.flatnonzero(strata.eq(s)) for s in strata.unique()]
    draws={name:[] for name in policies}; differences=[]
    for _ in range(n_boot):
        idx=np.concatenate([rng.choice(pool,len(pool),replace=True) for pool in pools])
        for name,d in policies.items():
            m=policy_metrics(y[idx],d[idx],benefit,cost);draws[name].append([m['scenario_profit'],tpr_gap(y[idx],d[idx],senior[idx])])
        differences.append(draws['equal_opportunity'][-1][0]-draws['validation_profit'][-1][0])
    out=[]
    for name,values in draws.items():
        arr=np.asarray(values)
        for k,metric in enumerate(['scenario_profit','senior_tpr_gap']):
            lo,hi=np.quantile(arr[:,k],[.025,.975]);out.append({'seed':seed,'policy':name,'metric':metric,'lower':lo,'upper':hi})
    lo,hi=np.quantile(differences,[.025,.975]);out.append({'seed':seed,'policy':'equal_opportunity_minus_validation_profit','metric':'paired_profit_difference','lower':lo,'upper':hi})
    return out

def explain_catboost(model,calibrator,X,ids,y,output):
    """Native TreeSHAP on raw margin, then exact affine logit calibration transform."""
    values=model.get_feature_importance(Pool(X,cat_features=model.get_cat_feature_indices()),type='ShapValues',thread_count=4)
    z=np.asarray(model.predict(X,prediction_type='RawFormulaVal'))
    raw_error=float(np.max(np.abs(values.sum(axis=1)-z)))
    slope=float(calibrator.coef_[0,0]); intercept=float(calibrator.intercept_[0])
    contributions=values[:,:-1]*slope; base=values[:,-1]*slope+intercept
    calibrated=calibrator.predict_proba(z.reshape(-1,1))[:,1]
    calibrated_error=float(np.max(np.abs(expit(base+contributions.sum(axis=1))-calibrated)))
    assert raw_error<1e-7 and calibrated_error<1e-7
    importance=pd.DataFrame({'feature':X.columns,'mean_abs_calibrated_logit_shap':np.mean(np.abs(contributions),axis=0)}).sort_values('mean_abs_calibrated_logit_shap',ascending=False)
    importance.to_csv(output/'shap_global.csv',index=False)
    # Real customers selected by risk quartiles, without inspecting their outcomes.
    order=np.argsort(calibrated); chosen=order[[0,len(order)//3,2*len(order)//3,len(order)-1]]
    rows=[]
    for i in chosen:
        for j,col in enumerate(X.columns):
            rows.append({'customerID':ids[i],'y_true':int(y[i]),'feature':col,'feature_value':str(X.iloc[i][col]),'shap_calibrated_logit':contributions[i,j],'base_calibrated_logit':base[i],'probability':calibrated[i]})
    pd.DataFrame(rows).to_csv(output/'shap_local.csv',index=False)
    np.savez_compressed(output/'shap_values.npz',contributions=contributions,base=base,customerID=np.asarray(ids,dtype=str),feature_names=np.asarray(X.columns,dtype=str))
    info={'explained_model':'catboost_baseline_original; fixed explanatory comparator, not necessarily selected winner','method':'CatBoost native path-dependent TreeSHAP, affine transform to calibrated logits','background':'training tree path statistics; not test prevalence','raw_additivity_max_error':raw_error,'calibrated_probability_max_error':calibrated_error,'calibration_slope':slope,'calibration_intercept':intercept,'n':len(X)}
    (output/'shap_validation.json').write_text(json.dumps(info,indent=2))

def run(config_path,output):
    cfg=json.loads(Path(config_path).read_text());output=Path(output);output.mkdir(parents=True,exist_ok=True)
    raw=pd.read_csv(ROOT/'01_Data/telco_churn_raw.csv');df=clean_data(raw);y=df.Churn.eq('Yes').astype(int).to_numpy()
    manifest={'status':'running','config':cfg,'python':platform.python_version(),'versions':{p:importlib.metadata.version(p) for p in ['numpy','pandas','scipy','scikit-learn','imbalanced-learn','catboost','joblib']},'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'data_sha256':hashlib.sha256((ROOT/'01_Data/telco_churn_raw.csv').read_bytes()).hexdigest(),'limitations':'Public dataset previously inspected; retrospective benchmark, not prospective confirmation or causal retention experiment.'}
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2))
    configs=[(f,r,'original') for f in ['logistic','random_forest','catboost'] for r in ['baseline','weighted','oversampled']]+[('catboost','baseline',v) for v in ['engineered','unaware']]
    metrics=[];policies_all=[];fairness=[];intervals=[];sensitivity=[];thresholds_all=[]
    benefit,cost=payoff_parameters(**cfg['economic']);bayes=cost/(benefit+cost)
    for seed in cfg['seeds']:
        directory=output/f'seed_{seed}';directory.mkdir(exist_ok=True)
        splits=split_indices(y,seed,cfg)
        split_table=pd.concat([pd.DataFrame({'customerID':df.iloc[idx].customerID,'partition':part,'y_true':y[idx]}) for part,idx in splits.items()])
        split_table.to_csv(directory/'split_ids.csv',index=False)
        candidates={};validation=[]
        for family,regime,variant in configs:
            name=f'{family}_{regime}_{variant}';start=time.monotonic();X=features(df,variant)
            model,cal,preds=fit_configuration(X,y,splits,family,regime,seed,cfg)
            candidates[name]=(model,cal,preds)
            joblib.dump({'model':model,'calibrator':cal,'family':family,'variant':variant,'columns':X.columns.tolist()},directory/f'{name}.joblib')
            for part in ['validation','test']:
                idx=splits[part]
                pd.DataFrame({'customerID':df.iloc[idx].customerID,'y_true':y[idx],'p_raw':preds[part]['raw'],'p_calibrated':preds[part]['calibrated']}).to_csv(directory/f'{name}_{part}_predictions.csv',index=False)
                for calibration,p in preds[part].items():
                    metrics.append({'seed':seed,'model':name,'partition':part,'calibration':calibration,**score_metrics(y[idx],p),**policy_metrics(y[idx],p>=bayes,benefit,cost),'empirical_empc_oracle':empirical_empc(y[idx],p)})
            valprofit=policy_metrics(y[splits['validation']],preds['validation']['calibrated']>=bayes,benefit,cost)['scenario_profit']
            if variant=='original':validation.append((valprofit,name))
            print(f'seed={seed} {name}: validation scenario profit={valprofit:.0f}; {time.monotonic()-start:.1f}s',flush=True)
        # Deterministic tie-break by model name; no test result is used.
        selected=sorted(validation,key=lambda v:(-v[0],v[1]))[0][1]
        _,_,preds=candidates[selected];vi=splits['validation'];ti=splits['test']
        pv=preds['validation']['calibrated'];pt=preds['test']['calibrated']
        threshold=select_profit_threshold(y[vi],pv,benefit,cost)
        eo=select_equal_opportunity(y[vi],pv,df.iloc[vi].SeniorCitizen.to_numpy(),cfg['equal_opportunity_tolerance'],benefit,cost)
        groups=df.iloc[ti].SeniorCitizen.to_numpy()
        policies={'contact_none':np.zeros(len(ti),dtype=bool),'contact_all':np.ones(len(ti),dtype=bool),'standard_0.5':pt>=.5,'economic_bayes':pt>=bayes,'validation_profit':pt>=threshold,'equal_opportunity':pt>=np.where(groups==1,eo['1'],eo['0'])}
        choice={'seed':seed,'selected_model':selected,'selection':'maximum validation calibrated profit at assumed Bayes threshold','validation_profit_threshold':threshold,'economic_bayes_threshold':bayes,'equal_opportunity':eo}
        thresholds_all.append(choice);(directory/'policy_selection.json').write_text(json.dumps(choice,indent=2))
        table=df.iloc[ti][['customerID','SeniorCitizen','gender']].copy();table['y_true']=y[ti];table['p_calibrated']=pt
        for name,d in policies.items():
            table[name]=d.astype(int)
            policies_all.append({'seed':seed,'model':selected,'policy':name,**policy_metrics(y[ti],d,benefit,cost),'senior_tpr_gap':tpr_gap(y[ti],d,groups)})
            fairness.extend(fairness_rows(df.iloc[ti],y[ti],d,name,seed,benefit,cost))
        table.to_csv(directory/'selected_policy_predictions.csv',index=False)
        intervals.extend(bootstrap_policies(y[ti],policies,groups,df.iloc[ti].gender.to_numpy(),cfg['bootstrap_replicates'],seed,benefit,cost))
        for clv in [100.,200.,400.]:
            for acceptance in [.1,.3,.5]:
                b,c=payoff_parameters(clv=clv,acceptance=acceptance)
                st=select_profit_threshold(y[vi],pv,b,c)
                se=select_equal_opportunity(y[vi],pv,df.iloc[vi].SeniorCitizen.to_numpy(),cfg['equal_opportunity_tolerance'],b,c)
                for name,d in {'validation_profit':pt>=st,'equal_opportunity':pt>=np.where(groups==1,se['1'],se['0'])}.items():
                    sensitivity.append({'seed':seed,'clv':clv,'acceptance':acceptance,'offer_cost':10.,'contact_cost':1.,'policy':name,**policy_metrics(y[ti],d,b,c),'senior_tpr_gap':tpr_gap(y[ti],d,groups)})
        if seed==cfg['seeds'][0]:
            model,cal,_=candidates['catboost_baseline_original']
            explain_catboost(model,cal,features(df).iloc[ti],df.iloc[ti].customerID.to_numpy(),y[ti],directory)
        # Release all fitted estimators before proceeding to the next repeat.
        del candidates
    for name,rows in [('model_metrics',metrics),('policy_metrics',policies_all),('fairness_metrics',fairness),('bootstrap_intervals',intervals),('economic_sensitivity',sensitivity)]:
        pd.DataFrame(rows).to_csv(output/f'{name}.csv',index=False)
    (output/'policy_selections.json').write_text(json.dumps(thresholds_all,indent=2))
    pd.DataFrame({'feature':features(df,'engineered').select_dtypes('number').columns,'correlation_with_churn':[features(df,'engineered')[c].corr(pd.Series(y)) for c in features(df,'engineered').select_dtypes('number').columns]}).to_csv(output/'feature_correlations.csv',index=False)
    manifest['status']='complete';manifest['configurations_per_seed']=len(configs)
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2))
    print('Completed all experiments.',flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--config',default=str(ROOT/'config/study.json'));parser.add_argument('--output',default=str(ROOT/'results'))
    args=parser.parse_args();run(args.config,args.output)
