"""UOB period returns (Modified Dietz, chained) vs benchmarks, and proxy-basket calibration. Inputs: uob_hist.pkl (uob_hist.py) and data.py series. Output: uob_perf.pkl"""
import pickle, numpy as np, pandas as pd
from data import inst
H=pickle.load(open('uob_hist.pkl','rb')); U,N,FXU,GRAND=H['U'],H['N'],H['FXU'],H['GRAND']
dates={'2026-01':'2026-01-31','2026-03':'2026-03-31','2026-05':'2026-05-31','2026-07':'2026-07-31','2026-10':'2026-10-31'}
mid={'2026-02':'2026-02-15','2026-03':'2026-03-10','2026-04':'2026-04-15','2026-05':'2026-05-20','2026-06':'2026-06-15','2026-09':'2026-09-01'}
fl={'2026-02':14552,'2026-03':48928,'2026-04':45102,'2026-05':67246,'2026-06':35988,'2026-09':-14718}   # from uob_hist.py flows
intervals=[('2026-01','2026-03',['2026-02','2026-03']),('2026-03','2026-05',['2026-04','2026-05']),('2026-05','2026-07',['2026-06']),('2026-07','2026-10',['2026-09'])]
rows=[]; cum=1.0
for a,b,ms in intervals:
    V0,V1=GRAND[a],GRAND[b]; d0,d1=pd.Timestamp(dates[a]),pd.Timestamp(dates[b]); T=(d1-d0).days
    F=sum(fl[m] for m in ms); wF=sum(fl[m]*((d1-pd.Timestamp(mid[m])).days/T) for m in ms)
    pl=V1-V0-F; r=pl/(V0+wF); cum*=1+r
    br=lambda c:(1+inst[c].loc[d0+pd.Timedelta(days=1):d1]).prod()-1
    rows.append(dict(period=f'{d0:%d %b}-{d1:%d %b}',V0=V0,flows=F,V1=V1,pnl=pl,ret=r*100,ALLW=br('ALLW')*100,SPY=br('SPY')*100,ES3=br('ES3')*100,A35=br('A35')*100))
R=pd.DataFrame(rows); print(R.round(1).to_string(index=False)); print('chained %.1f%%'%((cum-1)*100))
pickle.dump(dict(R=R,cum=cum,fl=fl,tot_pl=GRAND['2026-10']-GRAND['2026-01']-sum(fl.values())),open('uob_perf.pkl','wb'))
