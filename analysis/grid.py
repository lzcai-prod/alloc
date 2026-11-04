from opt import *
import json
out={}
for V in [0.07,0.08,0.09,0.10,0.12,0.16]:
    r=solve(V=V,seeds=6)
    if r is None: out[V]=None; print(V,'infeasible',flush=True); continue
    v,rc=stats(r.x); out[V]=dict(obj=r.fun,invested=r.x.sum()/IBKR_NAV,crypto_pct_book=r.x[8]/BOOK*100,maxRC=rc.max()*100,vol=v*100,t=list(r.x))
    print(f'V={V:.2f} vol={v*100:.2f} obj={r.fun:.4f} invested={r.x.sum()/IBKR_NAV:.2f} crypto={r.x[8]/BOOK*100:.1f}%book maxRC={rc.max()*100:.0f}%',flush=True)
json.dump(out,open('grid.json','w'))
