import pandas as pd, numpy as np, glob, hashlib
U='/root/.claude/uploads/96af3fac-5838-5648-857b-e9dc3247b73e/'
SP='/tmp/claude-0/-home-user/96af3fac-5838-5648-857b-e9dc3247b73e/scratchpad/'
WD=pd.bdate_range('2020-01-01','2026-11-04')
def sheet(path):
    raw=pd.read_csv(path,header=None,dtype=str)
    cols=['Date']+[t if isinstance(t,str) else f'_blank{i}' for i,t in enumerate(raw.iloc[1,1:])]
    df=raw.iloc[2:].copy(); df.columns=cols
    df['Date']=pd.to_datetime(df['Date'],format='%m/%d/%Y'); df=df.set_index('Date')
    df=df.apply(pd.to_numeric,errors='coerce')
    return df[[c for c in df.columns if not c.startswith('_blank')]]
f=lambda p: glob.glob(U+p+'*')[0]
files={'P1_TR':f('a4f9ff2e'),'P1_PX':f('34233501'),'P2_TR':f('1a86bf27'),'P2_RV':f('e9d9ffc3'),'X_TR':f('fb436c67'),'Y_PX':f('a50c4c29')}
S={k:sheet(v) for k,v in files.items()}
# pull3: realign FX to weekdays, BTC to weekdays
y=S['Y_PX']
btc=y['XBTUSD Curncy'].dropna(); btc=btc[btc.index.dayofweek<5].reindex(WD)
fx=y[['JPYSGD Curncy','HKDSGD Curncy']].dropna(how='all').reset_index(drop=True); assert len(fx)==len(WD)
fx.index=WD
usdsgd=S['P1_PX']['USDSGD Curncy'].reindex(WD).ffill()
jpysgd=(fx['JPYSGD Curncy']/100).reindex(WD).ffill(); hkdsgd=fx['HKDSGD Curncy'].reindex(WD).ffill()
yh=pd.read_csv(SP+'extra4_totalreturn_yahoo.csv',index_col=0,parse_dates=True).reindex(WD).ffill()
TR=pd.concat([S['P1_TR'],S['P2_TR'],S['X_TR'],yh],axis=1)
TR=TR.loc[:,~TR.columns.duplicated()].reindex(WD).ffill()
TR['BTC']=btc.ffill()
# ---- convert to SGD returns
ccy={}
for c in TR.columns:
    if c.endswith('SP Equity'): ccy[c]='SGD'
    elif c.startswith(('1330','1631')): ccy[c]='JPY'
    elif c.startswith('2823'): ccy[c]='HKD'
    else: ccy[c]='USD'
fxlevel={'SGD':pd.Series(1.0,index=WD),'USD':usdsgd,'JPY':jpysgd,'HKD':hkdsgd}
def short(c): return c.split(' ')[0]
R={}
for c in TR.columns:
    s=TR[c]; rl=s.pct_change(); rf=fxlevel[ccy[c]].pct_change()
    R[short(c)]=((1+rl)*(1+rf)-1)
R=pd.DataFrame(R)
# USD local returns (for hedging, ALLW proxy)
RU=pd.DataFrame({short(c):TR[c].pct_change() for c in TR.columns if ccy[c]=='USD'})
# hedge carry (1M fwd points per month -> daily)
pts=S['P2_RV']['USDSGD1M Curncy'].reindex(WD).ffill()
carry=(pts/10000/usdsgd)/21
rf6=(S['P2_RV']['USGG6M Index'].reindex(WD).ffill()/100)/252
rf3=(S['P2_RV']['USGG3M Index'].reindex(WD).ffill()/100)/252
fxr=usdsgd.pct_change()
# ALLW proxy before 2025-03-06 via NNLS on USD returns
from scipy.optimize import nnls
comp=['SPY','TLT','IEF','TIP','GLD','PDBC']
allw=RU['ALLW']; fit=allw.dropna().index
A=RU.loc[fit,comp].values; b=allw.loc[fit].values
wts,_=nnls(A,b); pred=RU[comp].fillna(0).values@wts
r2=1-((b-A@wts)**2).sum()/((b-b.mean())**2).sum()
allw_full=allw.copy(); allw_full[allw_full.isna()]=pd.Series(pred,index=RU.index)[allw_full.isna()]
allw_full.iloc[0]=np.nan
RU['ALLW_proxy']=allw_full
R['ALLW']=((1+allw_full)*(1+fxr)-1)
ALLW_FIT={'weights':dict(zip(comp,[round(x,3) for x in wts])),'r2':round(r2,3),'n':len(fit),'start':str(fit[0].date())}
# hedged variants and proxy composites (SGD returns)
def unh(t): return R[t]
def hed(t): return RU[t]+carry
inst=pd.DataFrame(index=WD)
for t in R.columns: inst[t]=R[t]
for t in ['DEM','LQD','HYG','EMB','BOND','AGG']: inst[t+'_H']=hed(t)
usdcash=(1+rf3)*(1+fxr)-1
inst['USDCASH']=usdcash
inst['AB_proxy']=0.5*inst['AGG']+0.3*inst['HYG']+0.2*inst['EMB']
inst['ALZ_proxy_H']=0.5*inst['LQD_H']+0.3*inst['HYG_H']+0.2*inst['EMB_H']
inst['FMA_proxy']=0.40*inst['ACWI']+0.25*inst['HYG']+0.20*inst['BNDX']+0.15*inst['USDCASH']
inst=inst.iloc[1:]
inst['BITB']=inst['BTC']
RF_SGD6M=float(S['P2_RV']['USGG6M Index'].iloc[-1])/100
def sha(path):
    return hashlib.sha256(open(path,'rb').read()).hexdigest()
FILEHASH={k:sha(v) for k,v in files.items()}
FILEHASH['extra4_yahoo']=sha(SP+'extra4_totalreturn_yahoo.csv')
if __name__=='__main__':
    print(inst.shape, inst.index[0].date(), inst.index[-1].date())
    print('ALLW fit',ALLW_FIT)
    print(inst.isna().sum()[inst.isna().sum()>2])
    v=inst.std()*np.sqrt(252)
    print(v.round(3).sort_values().to_string())
