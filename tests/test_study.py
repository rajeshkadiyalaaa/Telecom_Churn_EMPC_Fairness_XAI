import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
import pandas as pd
from churn_study import clean_data,features,split_indices,payoff_parameters,threshold_curve,select_profit_threshold,select_equal_opportunity,empirical_empc,policy_metrics

class StudyTests(unittest.TestCase):
    def test_profit_and_ties(self):
        y=np.array([1,0,1,0]);p=np.array([.8,.8,.2,.1])
        t,tp,fp=threshold_curve(y,p)
        for threshold,a,b in zip(t,tp,fp):
            m=policy_metrics(y,p>=threshold)
            self.assertEqual((a,b),(m['TP'],m['FP']))
        optimum=select_profit_threshold(y,p)
        self.assertEqual(policy_metrics(y,p>=optimum)['scenario_profit'],max(56*tp-11*fp))
    def test_no_contact_and_empc(self):
        self.assertEqual(empirical_empc(np.zeros(4),np.array([.1,.2,.3,.4])),0.)
        # Perfect ranking permits contacting exactly the two positives whenever benefit is positive.
        from scipy.integrate import quad
        from scipy.stats import beta
        expected=quad(lambda g:max(190*g-1,0)*.5*beta.pdf(g,6,14),0,1)[0]
        observed=empirical_empc(np.array([1,1,0,0]),np.array([.9,.8,.2,.1]))
        self.assertAlmostEqual(expected,observed,places=5)
    def test_group_threshold_selection(self):
        y=np.array([1,1,0,0,1,1,0,0]);g=np.array([0]*4+[1]*4);p=np.array([.9,.4,.3,.1,.8,.2,.6,.1])
        chosen=select_equal_opportunity(y,p,g,tolerance=0.)
        d=p>=np.where(g==0,chosen['0'],chosen['1'])
        self.assertEqual(d[(g==0)&(y==1)].mean(),d[(g==1)&(y==1)].mean())
        brute=[]
        for a in threshold_curve(y[g==0],p[g==0])[0]:
            for b in threshold_curve(y[g==1],p[g==1])[0]:
                dd=p>=np.where(g==0,a,b)
                if dd[(g==0)&(y==1)].mean()==dd[(g==1)&(y==1)].mean():brute.append(policy_metrics(y,dd)['scenario_profit'])
        self.assertEqual(policy_metrics(y,d)['scenario_profit'],max(brute))
    def test_data_and_split(self):
        root=Path(__file__).resolve().parents[1]
        raw=pd.read_csv(root/'01_Data/telco_churn_raw.csv');df=clean_data(raw)
        self.assertEqual(df.TotalCharges_missing.sum(),11)
        self.assertNotIn('Churn',features(df))
        bad=raw.copy();bad.loc[0,'TotalCharges']='invalid'
        with self.assertRaises(ValueError):clean_data(bad)
        cfg={'test_fraction':.2,'validation_fraction_of_development':.25,'calibration_fraction_of_remaining':.25}
        split=split_indices(df.Churn.eq('Yes').astype(int).to_numpy(),42,cfg)
        self.assertEqual(len(set(np.concatenate(list(split.values())))),len(df))
        self.assertEqual(sum(map(len,split.values())),len(df))
    def test_assumed_payoff(self):
        self.assertEqual(payoff_parameters(),(56.,11.))
        self.assertAlmostEqual(11/67,.16417910447761194)

if __name__=='__main__':unittest.main()
