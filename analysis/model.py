import pandas as pd, numpy as np
from data import *
from sklearn.covariance import LedoitWolf
P=pd.read_csv(SP+'ibkr_positions_2026-11-03.csv'); CASH=pd.read_csv(SP+'ibkr_cash_2026-11-03.csv'); UOB=pd.read_csv(SP+'uob_holdings_2026-10-31.csv')
P['symbol']=P.symbol.astype(str)
sym={'2823':'2823','1330.T':'1330','1631.T':'1631'}
P['inst']=P.symbol.map(lambda s: sym.get(s,s))
P['inst']=P.inst.replace({'BITB':'BITB'})
BUCKET={'VOO':'US_EQ','QQQ':'US_EQ','SPMO':'US_EQ','SPY':'US_EQ','XBI':'US_THEME','XLP':'US_THEME',
'EWJ':'INTL_DM','EZU':'INTL_DM','EWU':'INTL_DM','LVHI':'INTL_DM','1330':'INTL_DM','1631':'INTL_DM','ACWI':'INTL_DM',
'2823':'EM_EQ','DEM':'EM_EQ','DEM_H':'EM_EQ','D05':'SG_EQ','ES3':'SG_EQ','VNQ':'REAL_ESTATE',
'PDBC':'COMMOD','CPER':'COMMOD','USO':'COMMOD','DBA':'COMMOD','GLD':'GOLD','BITB':'CRYPTO','ALLW':'ALLW',
'VCIT':'CREDIT','LQD_H':'CREDIT','HYG':'CREDIT','HYG_H':'CREDIT','EMB':'CREDIT','EMB_H':'CREDIT',
'AGG':'CORE_BONDS','BOND_H':'CORE_BONDS','A35':'CORE_BONDS','BNDX':'CORE_BONDS','IEF':'CORE_BONDS','USDCASH':None}
BUCKETS=['US_EQ','US_THEME','INTL_DM','EM_EQ','SG_EQ','REAL_ESTATE','COMMOD','GOLD','CRYPTO','ALLW','CREDIT','CORE_BONDS']
LEGS={ # UOB fund -> {instrument: weight}
'AB American Income A USD':{'AGG':.5,'HYG':.3,'EMB':.2},
'Allianz Global Diversified Credit AMgi H2-SGD':{'LQD_H':.5,'HYG_H':.3,'EMB_H':.2},
'Fidelity America A-USD':{'SPY':1},
'Fidelity Global Multi Asset Income A-MINCOME(G)-USD':{'ACWI':.40,'HYG':.25,'BNDX':.20,'USDCASH':.15},
'JPM Emerging Markets Dividend A (mth) SGD Hedged':{'DEM_H':1},
'JPM Emerging Markets Dividend A (mth) USD':{'DEM':1},
'PIMCO Total Return Bond E SGD Hedged Acc':{'BOND_H':1},
'Schroder Asian Investment Grade Credit A':{'VCIT':1},
'Schroder Singapore Trust A SGD Dist':{'ES3':1},
'United Singapore Bond Fund SGD':{'A35':1}}
ibkr_exp=P.groupby('inst').value_sgd.sum()
_u={}
for _,r in UOB.iterrows():
    for k,w in LEGS[r.fund].items(): _u[k]=_u.get(k,0)+r.value_sgd*w
uob_exp=pd.Series(_u,dtype=float)
CASH_SGD=float(CASH.value_sgd.sum())
IBKR_NAV=float(ibkr_exp.sum()+CASH_SGD)
UOB_NAV=float(UOB.value_sgd.sum()); BOOK=IBKR_NAV+UOB_NAV
# ---- covariance
LOOK_W=4*52
def make_cov(cols, lam=0.97, rng_end=None):
    d=inst[cols]
    w=(1+d).resample('W-FRI').prod()-1
    w=w.iloc[-LOOK_W:]
    z=(w-w.mean())/w.std()
    lw=LedoitWolf().fit(z.values); S=lw.covariance_; sd=np.sqrt(np.diag(S)); corr=S/np.outer(sd,sd)
    # EWMA daily vol
    r=d.iloc[-756:]; wt=lam**np.arange(len(r))[::-1]; wt/=wt.sum()
    ew=np.sqrt(((r**2).mul(wt,axis=0)).sum()*252)  # zero-mean EWMA
    cov=corr*np.outer(ew.values,ew.values)
    return pd.DataFrame(cov,index=cols,columns=cols), pd.Series(ew.values,index=cols), pd.DataFrame(corr,index=cols,columns=cols), lw.shrinkage_
ALL=sorted(set(ibkr_exp.index)|set(uob_exp.index)|{'IEF'})
COV,EWVOL,CORR,SHR=make_cov(ALL)
def exposure(ibkr_series, uob_series=uob_exp):
    x=pd.Series(0.0,index=ALL)
    for s in (ibkr_series,uob_series):
        for k,v in s.items(): x[k]+=v
    return x
def risk(x,cov=COV):
    xv=x.values; var=xv@cov.values@xv
    mrc=(cov.values@xv)*xv/var
    rc=pd.Series(mrc,index=x.index)
    return np.sqrt(var)/x.sum() if False else np.sqrt(var), rc
def bucket_rc(x):
    s,rc=risk(x); b=pd.Series({i:BUCKET[i] for i in x.index})
    return s, rc.groupby(b).sum()
if __name__=='__main__':
    print('IBKR NAV',round(IBKR_NAV),'UOB',round(UOB_NAV),'BOOK',round(BOOK),'shrink',round(SHR,3))
    x0=exposure(ibkr_exp)  # cash excluded (zero-risk SGD)
    s,rcb=bucket_rc(x0)
    print('current book vol (SGD, % of book):',round(s/BOOK*100,2))
    ex=pd.DataFrame({'ibkr':ibkr_exp.groupby(lambda i:BUCKET[i]).sum(),'uob':uob_exp.groupby(lambda i:BUCKET[i]).sum()}).fillna(0)
    ex['book%']=(ex.ibkr+ex.uob)/BOOK*100; ex['RC%']=rcb*100
    print(ex.reindex(BUCKETS).round(1))
    print('uob usdcash exposure', uob_exp.get('USDCASH'))
