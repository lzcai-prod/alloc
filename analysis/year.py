import csv, pandas as pd, numpy as np, glob
F=glob.glob('/root/.claude/uploads/96af3fac-5838-5648-857b-e9dc3247b73e/98429d35*')[0]
rows=list(csv.reader(open(F,encoding='utf-8')))
hi=[i for i,r in enumerate(rows) if r and r[0] in ('ClientAccountID','Date/Time')]+[len(rows)]
SIG={'equity':('Cash','Total','ReportDate'),'pnl':('StartingValue','TWR'),'mtm_sym':('TransactionMtmPnl','PriorOpenMtmPnl'),
 'trades':('TradeMoney','NetCash','IBOrderID'),'cashtx':('Type','Amount','ActionID'),'transfers':('TransferAccount','PositionAmountInBase'),
 'fees':('TotalCommission','BrokerExecutionCharge'),'realized':('TotalFifoPnl','TotalUnrealizedPnl'),'fxrate':('FromCurrency','ToCurrency','Rate')}
acc_map={}; out={}
for a,b in zip(hi[:-1],hi[1:]):
    h=rows[a]; kind=None
    for k,sig in SIG.items():
        if all(s in h for s in sig): kind=k; break
    if kind is None or b-a<=1: continue
    df=pd.DataFrame(rows[a+1:b],columns=h)
    if 'ClientAccountID' in df.columns:
        for acc in df.ClientAccountID.unique():
            if acc not in acc_map: acc_map[acc]='ABC'[len(acc_map)] if len(acc_map)<3 else acc
        df['acct']=df.ClientAccountID.map(acc_map)
        out.setdefault(kind,[]).append(df)
    else:
        out.setdefault(kind,[]).append(df)
D={k:pd.concat(v,ignore_index=True) for k,v in out.items()}
print({k:(len(v)) for k,v in D.items()}); print(acc_map)
# Account IDs are never stored in git. Provide account_map.json (gitignored), e.g. {"<IBKR account id>": "A", ...} with A=U12, B=U18, C=U15.
import json; want=json.load(open('account_map.json'))
for k,v in D.items():
    if 'ClientAccountID' in v.columns: v['acct']=v.ClientAccountID.map(want)
pd.to_pickle(D,'year_raw.pkl')
p=D['pnl'];
cols=['acct','FromDate','ToDate','StartingValue','EndingValue','Mtm','DepositsWithdrawals','AssetTransfers','Dividends','WithholdingTax','Interest','Commissions','TWR']
print(p[cols].to_string(index=False))
