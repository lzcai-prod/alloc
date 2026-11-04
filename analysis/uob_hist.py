import pandas as pd, numpy as np
from datetime import date
F=['AB','ALZ','FA','FUSD','FMA','JPMH','JPMU','PIM','SAIG','SGT','UNBF']
CCY={'AB':'USD','ALZ':'SGD','FA':'USD','FUSD':'SGD','FMA':'USD','JPMH':'SGD','JPMU':'USD','PIM':'SGD','SAIG':'SGD','SGT':'SGD','UNBF':'SGD'}
# month-end units (from statements: holdings and 'balance from last statement')
U={'2025-12':dict(AB=1186.999,ALZ=704.375,FA=363.22,FUSD=10824.48,FMA=1349.36,JPMU=111.665,SAIG=14021.2,SGT=4889.98,UNBF=5378.65),
 '2026-01':dict(AB=1193.081,ALZ=708.428,FA=363.22,FUSD=10861.65,FMA=1355.47,JPMU=112.018,SAIG=14076.86,SGT=4889.98,UNBF=5378.65),
 '2026-02':dict(AB=1199.204,ALZ=712.511,FA=363.22,FUSD=10899.15,FMA=1361.38,JPMH=1054.815,JPMU=112.366,SAIG=14126.72,SGT=7217.13,UNBF=5378.65),
 '2026-03':dict(AB=1205.329,ALZ=2753.477,FA=363.22,FUSD=10936.45,FMA=1367.22,JPMH=2125.559,JPMU=112.729,SAIG=14177.44,SGT=11727.73,UNBF=10795.47),
 '2026-04':dict(AB=1211.673,ALZ=2769.703,FA=363.22,FUSD=10974.66,FMA=1373.40,JPMH=2896.016,JPMU=113.080,SAIG=35177.13,SGT=18600.58,UNBF=14854.57),
 '2026-05':dict(AB=1218.011,ALZ=2786.172,FA=363.22,FUSD=16532.01,FMA=1379.47,JPMH=2906.122,JPMU=113.473,PIM=254.582,SAIG=35302.21,SGT=40893.28,UNBF=16198.65),
 '2026-06':dict(AB=1224.39,ALZ=2802.769,FA=363.22,FUSD=16590.66,FMA=1385.46,JPMH=3396.414,JPMU=113.842,PIM=381.293,SAIG=35428.31,SGT=52009.33,UNBF=16198.65),
 '2026-07':dict(AB=1230.833,ALZ=2819.591,FA=363.22,FUSD=16649.65,FMA=1391.54,JPMH=3408.045,JPMU=114.228,PIM=381.293,SAIG=35554.67,SGT=52512.03,UNBF=16198.65),
 '2026-09':dict(AB=1244.068,ALZ=2854.004,FA=363.22,FMA=1405.37,JPMH=3429.751,JPMU=114.958,PIM=381.293,SAIG=35808.05,SGT=52512.03,UNBF=16198.65),
 '2026-10':dict(AB=1251.037,ALZ=2871.754,FA=363.22,FMA=1412.56,JPMH=3441.126,JPMU=115.339,PIM=381.293,SAIG=35935.25,SGT=53065.46,UNBF=16198.65)}
# NAV at statement month-ends
N={'2026-01':dict(AB=6.43,ALZ=9.9461,FA=18.34,FUSD=0.931,FMA=8.365,JPMU=107.09,SAIG=0.728,SGT=2.219,UNBF=1.8363),
 '2026-03':dict(AB=6.27,ALZ=9.6484,FA=17.65,FUSD=0.917,FMA=7.918,JPMH=8.93,JPMU=100.33,SAIG=0.712,SGT=2.192,UNBF=1.8068),
 '2026-05':dict(AB=6.30,ALZ=9.6425,FA=18.68,FUSD=0.909,FMA=8.375,JPMH=10.55,JPMU=119.18,PIM=39.45,SAIG=0.713,SGT=2.227,UNBF=1.864),
 '2026-07':dict(AB=6.16,ALZ=9.4961,FA=18.74,FUSD=0.884,FMA=8.133,JPMH=10.11,JPMU=114.77,PIM=38.96,SAIG=0.702,SGT=2.443,UNBF=1.8206),
 '2026-10':dict(AB=6.0,ALZ=9.18150,FA=18.69,FMA=7.811,JPMH=9.67,JPMU=110.62,PIM=38.43,SAIG=0.682,SGT=2.312,UNBF=1.8292)}
FXU={'2026-01':1.2730,'2026-03':1.2904,'2026-05':1.2770,'2026-07':1.2829,'2026-10':1.2790}
GRAND={'2026-01':96084.63,'2026-03':157471.98,'2026-05':279516.64,'2026-07':323338.51,'2026-10':299818.95}
def val(m):
    tot=0
    for f,u in U[m].items():
        v=u*N[m][f]*(FXU[m] if CCY[f]=='USD' else 1); tot+=v
    return tot
for m in N: print(m,'computed',round(val(m),0),'statement',GRAND[m])
# purchases (units added beyond ~1.5% of prior units are treated as buys) with interpolated NAV
months=list(U); import math
def nav_at(f,m):  # interpolate NAV between statement dates by month index
    pts={k:N[k][f] for k in N if f in N[k]}
    ks=sorted(pts); idx={k:i for i,k in enumerate(sorted(U))}
    x=idx[m]; xs=[idx[k] for k in ks]; ys=[pts[k] for k in ks]
    return float(np.interp(x,xs,ys))
FX_m=lambda m: float(np.interp(sorted(U).index(m),[sorted(U).index(k) for k in FXU],[FXU[k] for k in FXU]))
flows={}
keys=sorted(U)
for a,b in zip(keys[:-1],keys[1:]):
    tot=0; det=[]
    for f in set(U[a])|set(U[b]):
        ua,ub=U[a].get(f,0),U[b].get(f,0); d=ub-ua
        if abs(d)<=0.03*max(ua,1) and ua>0 and ub>0: continue   # reinvested dividends
        nav=nav_at(f,b) if f in N['2026-01'] or True else 0
        try: nav=nav_at(f,b)
        except Exception: continue
        amt=d*nav*(FX_m(b) if CCY[f]=='USD' else 1); det.append((f,round(d,1),round(amt))); tot+=amt
    flows[(a,b)]=(tot,det)
for k_,(t,d) in flows.items(): print(k_,round(t),d)
import pickle; pickle.dump(dict(U=U,N=N,FXU=FXU,GRAND=GRAND,flows=flows),open('uob_hist.pkl','wb'))
