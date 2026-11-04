from options_load import *
def vol_of(x,cov=COV): return float(np.sqrt(x.values@cov.values@x.values))
COVF=inst[ALL].cov()*252
def bt_w(w): w=w[w!=0]; return (inst[w.index]*w).sum(axis=1)
def stat(s,rf=0.02):
    cum=(1+s).cumprod(); n=len(s)/252; g=cum.iloc[-1]**(1/n)-1
    return dict(cagr=g,vol=s.std()*np.sqrt(252),dd=(cum/cum.cummax()-1).min())
# growth sleeve candidates (weights of the sleeve)
cands={'G1 QQQ50 SPMO15 XBI15 BTC10 GLD10':{'QQQ':.5,'SPMO':.15,'XBI':.15,'BITB':.10,'GLD':.10},
       'G2 QQQ60 XBI20 BTC10 GLD10':{'QQQ':.6,'XBI':.2,'BITB':.1,'GLD':.1},
       'G3 QQQ40 SPMO20 VOO20 XBI10 BTC10':{'QQQ':.4,'SPMO':.2,'VOO':.2,'XBI':.1,'BITB':.1},
       'G4 QQQ35 VOO25 SPMO15 XBI10 BTC5 GLD10':{'QQQ':.35,'VOO':.25,'SPMO':.15,'XBI':.10,'BITB':.05,'GLD':.10}}
print('--- Growth sleeve candidates (sleeve alone)')
for n,w in cands.items():
    x=pd.Series(0.0,index=ALL)
    for k,v in w.items(): x[k]=v
    s=bt_w(x); st=stat(s)
    print(f'{n:42s} ex-ante vol {vol_of(x)*100:5.1f}% | 2020-26 vol {st["vol"]*100:4.1f}% cagr {st["cagr"]*100:5.1f}% maxDD {st["dd"]*100:5.1f}%')
# size: G=150k using G1
GSZ=150000.0; w=cands['G1 QQQ50 SPMO15 XBI15 BTC10 GLD10']
xG=pd.Series(0.0,index=ALL)
for k,v in w.items(): xG[k]=v*GSZ
x_cur=pd.Series(0.0,index=ALL)
for s_ in (ibkr_exp,uob_exp):
    for k,v in s_.items(): x_cur[k]+=v
need=0.0; buys=pd.Series(0.0,index=ALL)
for k in xG.index:
    if xG[k]>0:
        have=ibkr_exp.get(k,0.0); 
        if k=='GLD': continue
        buys[k]=max(xG[k]-have,0)
cash_used=buys.sum(); cash_left=CASH_SGD-cash_used
print('cash used for G buys',round(cash_used),'cash left in B',round(cash_left))
x_total=x_cur+buys; x_B=x_total-xG
print('min B exposure (should be >=0):',round(x_B.min()))
NAV_B=BOOK-GSZ
for nm,x,nav in [('G (150k)',xG,GSZ),('B (rest IBKR + UOB)',x_B,NAV_B)]:
    print(nm,'ex-ante vol',round(vol_of(x)/nav*100,2),'% | share of book',round(nav/BOOK*100,1))
# contribution to book vol
xt=x_total; vb=vol_of(xt)/BOOK
print('whole book ex-ante vol after plan',round(vb*100,2),'| G contribution share',round((xG.values@COV.values@xt.values)/(xt.values@COV.values@xt.values)*100,1),'%')
# B vs ALLW vol-matched
eA=pd.Series(0.0,index=ALL); eA['ALLW']=1.0
sB=vol_of(x_B)/NAV_B; sA=vol_of(eA)
k=sB/sA
d=x_B/NAV_B-k*eA
te=vol_of(d)
print(f'ALLW ex-ante vol {sA*100:.1f}%, B vol {sB*100:.1f}%, scale k={k:.2f}, ex-ante tracking error vs vol-matched ALLW {te*100:.1f}%')
# backcast B vs ALLW (proxy before Mar 2025)
sBr=bt_w(x_B/NAV_B)  # excl. cash (zero)
sAr=inst['ALLW']
kk=sBr.std()/sAr.std()
act=sBr-kk*sAr
def ann(s): return (1+s).prod()**(252/len(s))-1
print('Backcast 2020-26: B cagr',round(ann(sBr)*100,1),'vol',round(sBr.std()*np.sqrt(252)*100,1),'| ALLW(proxy pre-Mar25) cagr',round(ann(sAr.dropna())*100,1),'vol',round(sAr.std()*np.sqrt(252)*100,1),'| vol-matched ALLW cagr',round(ann(kk*sAr.dropna())*100,1),'k',round(kk,2),'| active ret ann',round(act.mean()*252*100,2),'TE',round(act.std()*np.sqrt(252)*100,1))
post=inst.index>=pd.Timestamp('2025-03-07')
print('Since ALLW launch (Mar-2025, actual ALLW): B ann',round(ann(sBr[post])*100,1),'ALLW ann',round(ann(sAr[post])*100,1),'ALLW vol',round(sAr[post].std()*np.sqrt(252)*100,1),'B vol',round(sBr[post].std()*np.sqrt(252)*100,1))
# UOB alone vs ALLW
xu=pd.Series(0.0,index=ALL)
for k_,v in uob_exp.items(): xu[k_]=v
su=bt_w(xu/UOB_NAV); print('UOB alone: vol',round(su.std()*np.sqrt(252)*100,1),'cagr',round(ann(su)*100,1),'| corr with ALLW',round(su.corr(sAr),2))
print('weights of ALLW proxy',ALLW_FIT['weights'])
# B composition summary by bucket
bb=x_B.groupby(lambda i:BUCKET[i]).sum()/NAV_B*100
print((bb.round(1)).to_dict(),'cash',round(cash_left/NAV_B*100,1))
