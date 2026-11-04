import json, hashlib, pickle, os
from opt import *
OUT=SP+'report/'; os.makedirs(OUT,exist_ok=True)
FXR={'USD':1.2815,'JPY':0.0080749,'HKD':0.16332,'SGD':1.0}
pos=pd.read_csv(SP+'ibkr_positions_2026-11-03.csv'); pos['symbol']=pos.symbol.astype(str)
pos['inst']=pos.symbol.map(lambda s:{'1330.T':'1330','1631.T':'1631'}.get(s,s))
hold=pos.groupby('inst').agg(ccy=('ccy','first'),price=('price','first'),value_sgd=('value_sgd','sum'))
hold['fx']=hold.ccy.map(FXR); hold['unit_sgd']=hold.price*hold.fx
cashA=pd.read_csv(SP+'ibkr_cash_2026-11-03.csv'); acct_cash=cashA.groupby('acct').value_sgd.sum().to_dict()
BUFFER=0.01*IBKR_NAV; DEPLOY=CASH_SGD-BUFFER
def exposure_from(h):
    x=uob_exp.reindex(ALL).fillna(0).copy()
    for k,v in h.items(): x[k]+=v
    return x
def vr(x):
    var=x.values@COV.values@x.values
    rc=pd.Series((COV.values@x.values)*x.values/var,index=ALL).groupby(lambda i:BUCKET[i]).sum().reindex(BUCKETS)
    return np.sqrt(var)/BOOK, rc
def make_buys(weights,amount):
    """weights: dict inst->share of amount; whole shares, floor; drop lines < SGD 500"""
    sh={}
    for k,w in weights.items():
        n=np.floor(amount*w/hold.loc[k,'unit_sgd'])
        if k=='2823': n=np.floor(n/500)*500
        if n*hold.loc[k,'unit_sgd']>=500: sh[k]=int(n)
    return sh
def new_hold(sh):
    h=hold.value_sgd.copy()
    for k,n in sh.items(): h[k]=h.get(k,0)+n*hold.loc[k,'unit_sgd']
    return h
def assign(sh):
    rem={a:acct_cash[a] for a in 'ABC'}; rows=[]
    for k,n in sorted(sh.items(),key=lambda kv:-kv[1]*hold.loc[kv[0],'unit_sgd']):
        left=n; u=hold.loc[k,'unit_sgd']
        for a in sorted(rem,key=rem.get,reverse=True):
            can=int(rem[a]//u)
            if k=='2823': can=int(can//500*500)
            take=min(left,can)
            if take>0: rows.append((a,k,'BUY',take,hold.loc[k,'price'],hold.loc[k,'ccy'],take*u)); rem[a]-=take*u; left-=take
            if left<=0: break
    return pd.DataFrame(rows,columns=['account','symbol','side','shares','ref_price_3Nov','ccy','est_value_sgd']),rem
def bt(x):
    w=(x/BOOK); w=w[w!=0]; return (inst[w.index]*w).sum(axis=1)
def perf(s):
    cum=(1+s).cumprod()
    return dict(ann_vol=s.std()*np.sqrt(252),maxdd=(cum/cum.cummax()-1).min(),ret_1y=(1+s.iloc[-252:]).prod()-1,vol_1y=s.iloc[-252:].std()*np.sqrt(252))
def bands(s,v,n=21,sims=20000):
    lam=.97; r=s.values; sig=np.zeros(len(r)); sig[0]=r[:60].std()
    for k in range(1,len(r)): sig[k]=np.sqrt(lam*sig[k-1]**2+(1-lam)*r[k-1]**2)
    z=r[1:]/sig[1:]; z=(z-z.mean())/z.std(); rng=np.random.default_rng(7)
    return np.quantile((1+rng.choice(z,size=(sims,n))*(v/np.sqrt(252))).prod(axis=1)-1,[.05,.25,.5,.75,.95])
hv=hold.value_sgd
OPT={}
OPT['O0 Hold (no trades)']=dict(sh={})
OPT['O1 Deploy cash pro-rata']=dict(sh=make_buys((hv/hv.sum()).to_dict(),DEPLOY))
OPT['O2 Deploy cash into VOO+QQQ']=dict(sh=make_buys({'VOO':.5,'QQQ':.5},DEPLOY))
tm=np.array([.106,.091,.13,.027,0,.122,.153,.134,.051,.106,.019,.061])*IBKR_NAV
tgt={}
for tb,b in zip(tm,BUCKETS):
    for k,w in prop[b].items(): tgt[k]=tb*w
OPT['O3 Mechanical ERC (not recommended)']=dict(x=exposure_from(pd.Series(tgt)),tgt=tgt)
RES={}
for nm,o in OPT.items():
    if 'sh' in o:
        h=new_hold(o['sh']); x=exposure_from(h); o['x']=x
        o['trades'],o['cash_left']=assign(o['sh']) if o['sh'] else (pd.DataFrame(columns=['account','symbol','side','shares','ref_price_3Nov','ccy','est_value_sgd']),dict(acct_cash))
    v,rc=vr(o['x']); b=bt(o['x']); RES[nm]=dict(vol=v,rc=rc,perf=perf(b),bands=bands(b,v),maxrc=(rc.idxmax(),rc.max()))
    print(nm,'vol',round(v*100,2),'maxRC',rc.idxmax(),round(rc.max()*100,1),'1y vol',round(RES[nm]['perf']['vol_1y']*100,1),'dd',round(RES[nm]['perf']['maxdd']*100,1),'band',(RES[nm]['bands']*100).round(1))
    if 'sh' in o and o['sh']: print(o['trades'].round(0).to_string(index=False)); print('cash left by acct',{k:round(v) for k,v in o['cash_left'].items()})
# ---- scenario ceilings
def vsleeve(d):
    x=uob_exp.reindex(ALL).fillna(0).copy()
    for k,w in d.items(): x[k]+=w*IBKR_NAV
    return np.sqrt(x.values@COV.values@x.values)/BOOK
SC={'UOB only (IBKR in cash)':vsleeve({}),'Current book':RES['O0 Hold (no trades)']['vol'],
 'Cash deployed pro-rata':RES['O1 Deploy cash pro-rata']['vol'],'Cash into VOO+QQQ':RES['O2 Deploy cash into VOO+QQQ']['vol'],
 'Mechanical ERC':RES['O3 Mechanical ERC (not recommended)']['vol'],
 'IBKR sleeve 100% VOO':vsleeve({'VOO':1}),'IBKR sleeve 100% QQQ':vsleeve({'QQQ':1}),'IBKR sleeve 100% XBI':vsleeve({'XBI':1}),'IBKR sleeve 100% Bitcoin':vsleeve({'BITB':1})}
print({k:round(v*100,1) for k,v in SC.items()})
full=(inst[ALL].fillna(0)*(exposure_from(hold.value_sgd)/BOOK)).sum(axis=1)
# long-run covariance check (full 2020-26 daily)
cov_full=inst[ALL].cov()*252; xx=exposure_from(hold.value_sgd); lr=np.sqrt(xx.values@cov_full.values@xx.values)/BOOK
print('long-run (2020-26) vol of current book',round(lr*100,2))
grid=json.load(open('grid.json'))
pickle.dump(dict(OPT=OPT,RES=RES,SC=SC,lr=lr,grid=grid,hold=hold,DEPLOY=DEPLOY,BUFFER=BUFFER,acct_cash=acct_cash,tm=tm,t0=t0),open(OUT+'opts.pkl','wb'))
