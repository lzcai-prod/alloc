from model import *
from scipy.optimize import minimize
# within-bucket proportions
prop={}
for b in BUCKETS:
    s=ibkr_exp[[i for i in ibkr_exp.index if BUCKET[i]==b]]
    if b=='CORE_BONDS': prop[b]=pd.Series({'IEF':1.0})
    else: prop[b]=s/s.sum()
t0=np.array([ibkr_exp[[i for i in ibkr_exp.index if BUCKET[i]==b]].sum() for b in BUCKETS])
def xvec(t):
    x=uob_exp.reindex(ALL).fillna(0).copy()
    for tb,b in zip(t,BUCKETS):
        for k,w in prop[b].items(): x[k]+=tb*w
    return x
def stats(t):
    x=xvec(t); xv=x.values; var=xv@COV.values@xv; mrc=(COV.values@xv)*xv/var
    rc=pd.Series(mrc,index=ALL).groupby(lambda i:BUCKET[i]).sum().reindex(BUCKETS)
    return np.sqrt(var)/BOOK, rc
CRYPTO_CAP=0.03*BOOK
def solve(V=None, fully=False, cap_crypto=True, seeds=40):
    n=len(BUCKETS); rng=np.random.default_rng(1)
    def obj(t): return float(((stats(t)[1].values-1/n)**2).sum())
    cons=[{'type':'ineq','fun':lambda t: IBKR_NAV-t.sum()}]
    if fully: cons=[{'type':'eq','fun':lambda t: IBKR_NAV-t.sum()}]
    if V is not None: cons.append({'type':'eq','fun':lambda t: (stats(t)[0]-V)*100})
    bnds=[(0,IBKR_NAV)]*n
    if cap_crypto: bnds[BUCKETS.index('CRYPTO')]=(0,CRYPTO_CAP)
    best=None
    for k in range(seeds):
        z=rng.dirichlet(np.ones(n))*IBKR_NAV*(rng.uniform(.6,1) if not fully else 1)
        if k==0: z=t0.copy()
        r=minimize(obj,z,method='SLSQP',bounds=bnds,constraints=cons,options={'maxiter':400,'ftol':1e-12})
        if r.success and (best is None or r.fun<best.fun): best=r
    return best
if __name__=='__main__':
    v0,rc0=stats(t0); print('current vol',round(v0*100,2))
    # extremes: min and max vol feasible for fully invested w/ constraint of cap
    def vol(t): return stats(t)[0]
    n=len(BUCKETS)
    mn=minimize(vol,np.ones(n)*IBKR_NAV/n,method='SLSQP',bounds=[(0,IBKR_NAV)]*n,constraints=[{'type':'ineq','fun':lambda t:IBKR_NAV-t.sum()}])
    print('min vol feasible (no leverage)',round(mn.fun*100,2))
    mx=minimize(lambda t:-vol(t),t0,method='SLSQP',bounds=[(0,IBKR_NAV)]*n,constraints=[{'type':'ineq','fun':lambda t:IBKR_NAV-t.sum()}])
    print('max vol feasible (no leverage, unrestricted)',round(-mx.fun*100,2), dict(zip(BUCKETS,(mx.x/IBKR_NAV).round(2))))
    # pro-rata invest cash
    tpr=t0*IBKR_NAV/t0.sum(); print('current holdings scaled to fully invested vol',round(vol(tpr)*100,2))
    r=solve(fully=True); v,rc=stats(r.x); print('ERC fully invested: vol',round(v*100,2),'obj',round(r.fun,5)); print((r.x/IBKR_NAV).round(3), (rc*100).round(1).to_dict())
    for V in [0.08,0.10,0.12,0.14,0.16]:
        r=solve(V=V)
        if r is None: print(V,'infeasible'); continue
        v,rc=stats(r.x); print(f'V={V:.2f} obj={r.fun:.4f} invested={r.x.sum()/IBKR_NAV:.2f} crypto={r.x[8]/BOOK*100:.1f}%book maxRC={rc.max()*100:.0f}%')
