"""Whole-book sensitivity to SPY (SGD) and historical drawdown ratios. Needs model.py (current exposures, proxies)."""
from options_load import *
ib=pd.read_csv(SP+'ibkr_positions_2026-11-03.csv'); ib['symbol']=ib.symbol.astype(str); ib['inst']=ib.symbol.map(lambda x:{'1330.T':'1330','1631.T':'1631'}.get(x,x))
x=pd.Series(0.0,index=ALL)
for k,v in ib.groupby('inst').value_sgd.sum().items(): x[k]+=v
for k,v in uob_exp.items(): x[k]+=v
w=x/BOOK; port=(inst[w[w!=0].index]*w[w!=0]).sum(axis=1); spy=inst['SPY']
beta=lambda y,m: np.cov(y,m)[0,1]/np.var(m,ddof=1)
pw=(1+port).resample('W-FRI').prod()-1; sw=(1+spy).resample('W-FRI').prod()-1
print('weekly beta',round(beta(pw,sw),2),'| downside beta',round(beta(pw[sw<-0.01],sw[sw<-0.01]),2),'| corr',round(np.corrcoef(pw,sw)[0,1],2))
for nm,a,b in [('Covid','2020-02-19','2020-03-23'),('2022H1','2022-01-03','2022-06-16'),('Apr2025','2025-02-19','2025-04-08'),('Mar2026','2026-03-02','2026-03-23')]:
    p=(1+port.loc[a:b]).prod()-1; s_=(1+spy.loc[a:b]).prod()-1; print(nm,round(p*100,1),round(s_*100,1),round(p/s_,2))
