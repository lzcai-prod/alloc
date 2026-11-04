import numpy as np, pandas as pd, pickle
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
SP_='/tmp/claude-0/-home-user/96af3fac-5838-5648-857b-e9dc3247b73e/scratchpad/'
BOOK=737469.0; FX=1.2815; S=767.02; N=4; MULT=100; DAYS=107   # to 19 Feb 2027
# live IBKR quotes 4 Nov 2026 (SPY Feb-19-2027 puts): strike -> (bid, ask, iv)
Q={765:(20.2,20.3,.1475),730:(11.60,11.65,.1774),690:(6.70,6.74,.2124),650:(4.14,4.18,.2479),615:(2.87,2.90,.2838)}
def spread(long_k,short_k): return Q[long_k][1]-Q[short_k][0]   # pay ask, receive bid
H={'H1 buy 730 / sell 650 put spread':dict(legs=[(730,1),(650,-1)]),
   'H2 buy 690 / sell 615 put spread':dict(legs=[(690,1),(615,-1)]),
   'H3 buy 690 put (outright)':dict(legs=[(690,1)]),
   'H4 buy 730 / sell 615 put spread':dict(legs=[(730,1),(615,-1)])}
def cost_ps(legs): return sum((Q[k][1] if q>0 else -Q[k][0]) for k,q in legs)
def payoff_ps(legs,s): return sum(q*max(k-s,0) for k,q in legs)
EQ_EXPO=0.50*BOOK
def book_move(r): return 0.45*r if r>=0 else (0.50*r if r>=-0.20 else -0.10+0.70*(r+0.20))
rows=[]
for nm,h in H.items():
    c=cost_ps(h['legs']); cost_sgd=c*N*MULT*FX; maxp=max(payoff_ps(h['legs'],s) for s in np.linspace(300,800,501))
    rows.append(dict(name=nm,cost_pts=c,cost_usd=c*N*MULT,cost_sgd=cost_sgd,cost_pct_book=cost_sgd/BOOK*100,ann_pct_book=cost_sgd/BOOK*100*365/DAYS,ann_pct_hedged=cost_sgd/EQ_EXPO*100*365/DAYS,
      max_sgd=maxp*N*MULT*FX,legs=h['legs']))
df=pd.DataFrame(rows); print(df[['name','cost_pts','cost_usd','cost_sgd','cost_pct_book','ann_pct_book','ann_pct_hedged','max_sgd']].round(2).to_string(index=False))
sc=[-0.05,-0.10,-0.20,-0.30,-0.40]
tab=[]
for r in sc:
    s=S*(1+r); b=book_move(r)*BOOK; row={'SPY move':r,'Book unhedged':b}
    for nm,h in H.items():
        c=cost_ps(h['legs']); pay=payoff_ps(h['legs'],s); row[nm.split()[0]]=b+(pay-c)*N*MULT*FX
    tab.append(row)
T=pd.DataFrame(tab).set_index('SPY move'); print((T/1000).round(1).to_string()); print((T/BOOK*100).round(1).to_string())
# chart: net book P&L at expiry vs SPY move
rs=np.linspace(-0.40,0.10,101); fig,ax=plt.subplots(figsize=(7.2,3.6))
ax.plot(rs*100,[book_move(r)*BOOK/1000 for r in rs],color='k',lw=2,label='No hedge')
cols={'H1':'#2A9D8F','H2':'#1F3864','H3':'#E76F51','H4':'#8D99AE'}
for nm,h in H.items():
    k=nm.split()[0]; c=cost_ps(h['legs']); y=[(book_move(r)*BOOK+(payoff_ps(h['legs'],S*(1+r))-c)*N*MULT*FX)/1000 for r in rs]
    ax.plot(rs*100,y,color=cols[k],lw=1.8 if k=='H2' else 1.2,label=k+' '+nm.split(' ',1)[1])
ax.axhline(0,color='k',lw=.5); ax.set_xlabel('SPY move to 19 Feb 2027 (%)'); ax.set_ylabel('Whole-book P&L (SGD thousand)'); ax.legend(frameon=False,fontsize=7.5,loc='lower right'); ax.spines[['top','right']].set_visible(False)
fig.tight_layout(); fig.savefig(SP_+'report/h_fig1.png',dpi=170); plt.close(fig)
pickle.dump(dict(df=df,T=T,S=S,N=N,FX=FX,DAYS=DAYS,Q=Q),open(SP_+'report/hedge.pkl','wb'))
# contracts needed for beta-equivalent
print('beta-equivalent SPY contracts:',round(0.5*BOOK/FX/(S*MULT),2),'| notional USD',round(N*MULT*S))
