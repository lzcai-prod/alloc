"""FIFO holding periods of stock/ETF sales per account (U12/U15/U18). Input: year_raw.pkl built by year.py. Output: hold.pkl"""
import pandas as pd, numpy as np
from collections import deque
D=pd.read_pickle('year_raw.pkl'); num=lambda s: pd.to_numeric(s,errors='coerce')
t=D['trades'].copy(); t['fx']=num(t.FXRateToBase); t['q']=num(t.Quantity); t['px']=num(t.TradePrice)
t['ts']=pd.to_datetime(t.DateTime.str.replace(';',' ')); st=t[t.AssetClass=='STK'].sort_values('ts')
L={'A':'U12','B':'U18','C':'U15'}; rows=[]
for (a,sym),g in st.groupby(['acct','Symbol']):
    q=deque()
    for _,r in g.iterrows():
        if r.q>0: q.append([r.q,r.ts,r.px*r.fx])
        else:
            need=-r.q
            while need>1e-9 and q:
                lot=q[0]; take=min(need,lot[0]); rows.append((a,sym,(r.ts-lot[1]).total_seconds()/86400,take*r.px*r.fx)); lot[0]-=take; need-=take
                if lot[0]<=1e-9: q.popleft()
H=pd.DataFrame(rows,columns=['a','sym','days','val']); H['b']=pd.cut(H.days,[-0.01,7,30,90,10000],labels=['<=7d','8-30d','31-90d','>90d'])
for a in 'ACB':
    x=H[H.a==a]; w=x.groupby('b',observed=False).val.sum(); w=(w/w.sum()*100).round(0)
    print(L[a],'median hold',round(x.days.median()),'d',w.to_dict())
H.to_pickle('hold.pkl')
