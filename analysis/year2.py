import pandas as pd, numpy as np
D=pd.read_pickle('year_raw.pkl')
num=lambda s: pd.to_numeric(s,errors='coerce')
# ---- daily NAV & flows (SGD)
eq=D['equity'].copy(); eq['d']=pd.to_datetime(eq.ReportDate); eq['nav']=num(eq.Total)
nav=eq.pivot_table(index='d',columns='acct',values='nav',aggfunc='sum').sort_index()
ct=D['cashtx']; dw=ct[ct.Type=='Deposits/Withdrawals'].copy()
dw['d']=pd.to_datetime(dw.ReportDate if 'ReportDate' in dw else dw['Date/Time'].str[:10]); dw['amt']=num(dw.Amount)*num(dw.FXRateToBase)
flows=dw.pivot_table(index='d',columns='acct',values='amt',aggfunc='sum').reindex(nav.index).fillna(0)
print('flows by acct (SGD):',flows.sum().round(0).to_dict(),'| total',round(flows.sum().sum()))
# in-kind internal transfers (base) by account/date
tr=D['transfers'].copy(); tr['d']=pd.to_datetime(tr.ReportDate); tr['v']=num(tr.PositionAmountInBase)
ik=tr.pivot_table(index='d',columns='acct',values='v',aggfunc='sum').reindex(nav.index).fillna(0)
print('in-kind by acct',ik.sum().round(0).to_dict(),'total',round(ik.sum().sum()))
nav['ALL']=nav[['A','B','C']].sum(axis=1)
F_all=flows.sum(axis=1)  # internal cash transfers cancel; in-kind internal cancel
def twr(navs,fl):
    r=(navs-fl)/navs.shift(1)-1
    return r.dropna()
r_all=twr(nav.ALL,F_all)
# guard against tiny-base distortions
print('combined: start',round(nav.ALL.iloc[0]),'end',round(nav.ALL.iloc[-1]))
cum=(1+r_all).cumprod(); print('combined TWR',round((cum.iloc[-1]-1)*100,2),'% | ann vol',round(r_all.std()*np.sqrt(252)*100,1),'| maxDD',round(((cum/cum.cummax()-1).min())*100,1))
pl=nav.ALL.iloc[-1]-nav.ALL.iloc[0]-F_all.sum(); print('combined P&L SGD',round(pl))
# Modified Dietz combined
days=(nav.index[-1]-nav.index[0]).days; w=((nav.index[-1]-F_all.index)/pd.Timedelta(days=days)).values if False else None
tot=(nav.index[-1]-nav.index).days/days
md=pl/(nav.ALL.iloc[0]+(F_all*tot).sum()); print('Modified Dietz combined',round(md*100,2),'% ; avg capital',round(nav.ALL.iloc[0]+(F_all*tot).sum()))
# per account MD
for a in 'ABC':
    f=flows[a]+ik[a]; p=nav[a].iloc[-1]-nav[a].iloc[0]-f.sum(); base=nav[a].iloc[0]+(f*tot).sum()
    print(a,'P&L',round(p),'avg capital',round(base),'MD',round(p/base*100,1),'%')
nav.to_pickle('nav.pkl'); pd.to_pickle(dict(F_all=F_all,flows=flows,ik=ik,r_all=r_all),'flows.pkl')
# monthly NAV table
print(nav.resample('ME').last().round(0).to_string())
