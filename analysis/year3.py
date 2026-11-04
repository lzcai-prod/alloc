import pandas as pd, numpy as np, pickle
from options_load import *
D=pd.read_pickle('year_raw.pkl'); num=lambda s: pd.to_numeric(s,errors='coerce')
nav=pd.read_pickle('nav.pkl'); FL=pd.read_pickle('flows.pkl'); r_all=FL['r_all']
s,e=pd.Timestamp('2025-11-04'),pd.Timestamp('2026-11-03')
p=D['pnl'].copy()
for c in p.columns:
    if c not in ('ClientAccountID','AccountAlias','Model','CurrencyPrimary','FromDate','ToDate','acct'): p[c]=num(p[c])
p=p.set_index('acct')
t=D['trades'].copy(); t['fx']=num(t.FXRateToBase); t['real']=num(t.FifoPnlRealized)*t.fx; t['mon']=num(t.TradeMoney).abs()*t.fx
acc={}
for a in 'ABC':
    ta=t[t.acct==a]; q=p.loc[a]
    pl=q.EndingValue-q.StartingValue-q.DepositsWithdrawals-q.AssetTransfers
    acc[a]=dict(start=q.StartingValue,end=q.EndingValue,deposits=q.DepositsWithdrawals,inkind=q.AssetTransfers,pl=pl,twr=q.TWR,mtm=q.Mtm,div=q.Dividends,wht=q.WithholdingTax,interest=q.Interest,comm=q.Commissions,
      taxes=q.TransactionTax+q.SalesTax,turn=ta.mon.sum(),avgnav=nav[a].mean(),ntr=int(len(ta[ta.AssetClass.isin(['STK','OPT'])])),
      real_stk=ta[ta.AssetClass=='STK'].real.sum(),real_opt=ta[ta.AssetClass=='OPT'].real.sum(),nsym=ta[ta.AssetClass=='STK'].Symbol.nunique())
A=pd.DataFrame(acc).T
tot=A[['start','end','deposits','pl','mtm','div','wht','interest','comm','taxes','turn','real_stk','real_opt']].sum()
print(A.round(1).T.to_string()); print('TOTAL',tot.round(0).to_dict())
# ---- combined cumulative vs benchmarks
cum=(1+r_all).cumprod(); idx=cum.index
def cumb(series): x=(1+series.loc[s:e]).cumprod(); return x
bench={'SPY':inst['SPY'],'QQQ':inst['QQQ'],'ALLW':inst['ALLW'],'60/40 (ACWI/AGG)':0.6*inst['ACWI']+0.4*inst['AGG']}
fin={k:float((1+v.loc[s:e]).prod()-1) for k,v in bench.items()}; fin['IBKR combined (TWR)']=float(cum.iloc[-1]-1)
print(fin)
# ---- core (A+C+UOB) with today's weights: ex-ante vol, last 12m vs ALLW (backcast)
ib_by_acct=pd.read_csv(SP+'ibkr_positions_2026-11-03.csv'); ib_by_acct['symbol']=ib_by_acct.symbol.astype(str)
ib_by_acct['inst']=ib_by_acct.symbol.map(lambda x:{'1330.T':'1330','1631.T':'1631'}.get(x,x))
def vec(d): 
    x=pd.Series(0.0,index=ALL)
    for k,v in d.items(): x[k]+=v
    return x
xB=vec(ib_by_acct[ib_by_acct.acct=='B'].groupby('inst').value_sgd.sum())
xAC=vec(ib_by_acct[ib_by_acct.acct.isin(['A','C'])].groupby('inst').value_sgd.sum())
xU=vec(uob_exp)
cash=pd.read_csv(SP+'ibkr_cash_2026-11-03.csv').groupby('acct').value_sgd.sum()
NAVB=float(xB.sum()+cash['B']); NAVcore=float(xAC.sum()+cash['A']+cash['C']+UOB_NAV)
xcore=xAC+xU
vol=lambda x: float(np.sqrt(x.values@COV.values@x.values))
print('G (account B) NAV',round(NAVB),'ex-ante vol of G',round(vol(xB)/NAVB*100,2),'% | invested',round(xB.sum()/NAVB*100),'%')
print('Core NAV',round(NAVcore),'ex-ante vol',round(vol(xcore)/NAVcore*100,2),'% | IBKR core part cash',round(cash['A']+cash['C']))
def bt(x,nav_): w=(x/nav_); w=w[w!=0]; return (inst[w.index]*w).sum(axis=1)
bc=bt(xcore,NAVcore); bu=bt(xU,UOB_NAV)
ann=lambda x:(1+x).prod()**(252/len(x))-1
print('core backcast 2020-26: cagr',round(ann(bc)*100,1),'vol',round(bc.std()*np.sqrt(252)*100,1),'| ALLW(proxy) cagr',round(ann(inst['ALLW'].dropna())*100,1),'vol',round(inst['ALLW'].std()*np.sqrt(252)*100,1))
print('last12m (backcast today weights): core',round(((1+bc.loc[s:e]).prod()-1)*100,1),'| UOB proxy',round(((1+bu.loc[s:e]).prod()-1)*100,1),'| ALLW',round(fin['ALLW']*100,1))
k=bc.std()/inst['ALLW'].std(); print('vol-matched ALLW scale',round(k,2),'-> cagr',round(ann(k*inst['ALLW'].dropna())*100,1),'last12m',round(((1+k*inst['ALLW'].loc[s:e]).prod()-1)*100,1))
# ---- G designs: vol of mixes (ex-ante, EWMA) and 2020-26 realized
def mix(d): 
    x=pd.Series(0.0,index=ALL)
    for k,v in d.items(): x[k]=v
    return x
G={'G4 growth (QQQ35 VOO25 SPMO15 XBI10 GLD10 BTC5)':{'QQQ':.35,'VOO':.25,'SPMO':.15,'XBI':.10,'GLD':.10,'BITB':.05},
   'Diversified (VOO30 EWJ10 EZU10 DEM10 GLD15 PDBC10 IEF15)':{'VOO':.3,'EWJ':.1,'EZU':.1,'DEM':.1,'GLD':.15,'PDBC':.1,'IEF':.15},
   'Equity only (VOO50 QQQ30 EWJ10 EZU10)':{'VOO':.5,'QQQ':.3,'EWJ':.1,'EZU':.1}}
GR={}
for n,d in G.items():
    x=mix(d); s_=bt(x,1.0); cum_=(1+s_).cumprod()
    GR[n]=dict(exante=vol(x),vol_lr=s_.std()*np.sqrt(252),cagr=ann(s_),dd=(cum_/cum_.cummax()-1).min(),last12=(1+s_.loc[s:e]).prod()-1)
    print(f'{n:58s} ex-ante {GR[n]["exante"]*100:5.1f}% | 2020-26 vol {GR[n]["vol_lr"]*100:5.1f}% cagr {GR[n]["cagr"]*100:5.1f}% maxDD {GR[n]["dd"]*100:6.1f}% | last12m {GR[n]["last12"]*100:5.1f}%')
pickle.dump(dict(A=A,tot=tot,fin=fin,cum=cum,bench=bench,NAVB=NAVB,NAVcore=NAVcore,vB=vol(xB)/NAVB,vcore=vol(xcore)/NAVcore,GR=GR,
 core_cagr=ann(bc),core_vol=bc.std()*np.sqrt(252),core12=(1+bc.loc[s:e]).prod()-1,uob12=(1+bu.loc[s:e]).prod()-1,allw12=fin['ALLW'],cashAC=float(cash['A']+cash['C']),cashB=float(cash['B'])),open(SP+'report/year.pkl','wb'))
