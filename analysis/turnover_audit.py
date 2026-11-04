"""Turnover audit: option value is premium (TradeMoney = qty x price x multiplier), FX conversions excluded, one side counted. Needs year_raw.pkl."""
import pandas as pd, numpy as np
D=pd.read_pickle('year_raw.pkl'); num=lambda s: pd.to_numeric(s,errors='coerce')
t=D['trades'].copy(); t['mon']=num(t.TradeMoney).abs()*num(t.FXRateToBase)
ex=t[t.AssetClass.isin(['STK','OPT'])]; print('bought+sold SGD',round(ex.mon.sum()),'one side / avg capital 392,810 =',round(ex.mon.sum()/2/392810,2))
o=t[t.AssetClass=='OPT'].copy()
for c in ['Quantity','TradePrice','TradeMoney','Multiplier','Strike']: o[c]=num(o[c])
print('TradeMoney == premium:',np.allclose(o.TradeMoney.abs(),o.Quantity.abs()*o.TradePrice*o.Multiplier,rtol=1e-6),'| notional would be SGD',round((o.Quantity.abs()*o.Strike*o.Multiplier*num(o.FXRateToBase)).sum()))
