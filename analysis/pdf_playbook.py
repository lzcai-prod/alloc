import pickle, glob, json, hashlib
import numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether
SP='/tmp/claude-0/-home-user/96af3fac-5838-5648-857b-e9dc3247b73e/scratchpad/'; OUT=SP+'report/'
MV=pd.read_pickle('moves.pkl'); MB=pickle.load(open('moves_book.pkl','rb')); AGE=pd.read_pickle('pos_age.pkl'); AP=pickle.load(open('alloc_prop.pkl','rb')); HD=pickle.load(open(OUT+'hedge.pkl','rb'))
VIX=pd.read_pickle('vix.pkl'); T=HD['T']; DF=HD['df']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False})
# ---------------- charts (grayscale only) ----------------
sel=['SPY (S&P 500)','QQQ (Nasdaq 100)','XLF (financials)','EZU (Eurozone)','EEM (EM)','XBI (biotech)','HYG (high yield)','IEF (7-10y Treasuries)','ES3 (Singapore, SGX)','Bitcoin','GLD (gold)','PDBC (commodities)','XLE (energy)']
m=MV.loc[sel,'4 Nov'].sort_values()
fig,ax=plt.subplots(figsize=(7.2,3.6))
ax.barh(m.index,m.values,color=['#bdbdbd' if v<0 else '#404040' for v in m.values],edgecolor='black',hatch=None)
for i,(k,v) in enumerate(m.items()): ax.text(v+(0.12 if v>=0 else -0.12),i,f'{v:+.1f}%',va='center',ha='left' if v>=0 else 'right',fontsize=8)
ax.axvline(0,color='black',lw=.8); ax.set_xlabel('Move on 4 Nov 2026 (%, local currency)'); ax.set_xlim(-6.5,5)
fig.tight_layout(); fig.savefig(OUT+'p_fig1.png',dpi=170); plt.close(fig)
# core weights before/after
rb,ra=AP['rc_b'],AP['rc_a']
fig,ax=plt.subplots(figsize=(7.2,3.2)); names=list(rb.index); x=np.arange(len(names)); w=.38
ax.bar(x-w/2,rb.values,w,color='#bdbdbd',edgecolor='black',label='Share of core risk now'); ax.bar(x+w/2,ra.values,w,color='white',edgecolor='black',hatch='////',label='Share of core risk after plan')
LAB={'US_EQ':'US equity','US_THEME':'US theme','INTL_DM':'Intl dev.','EM_EQ':'EM','SG_EQ':'Singapore eq.','REAL_ESTATE':'REIT','COMMOD':'Commod.','GOLD':'Gold','CRYPTO':'Bitcoin','ALLW':'ALLW','CREDIT':'Credit','CORE_BONDS':'Bonds'}
ax.set_xticks(x); ax.set_xticklabels([LAB[n] for n in names],rotation=35,ha='right',fontsize=8); ax.set_ylabel('% of core risk'); ax.legend(frameon=False,fontsize=8)
fig.tight_layout(); fig.savefig(OUT+'p_fig2.png',dpi=170); plt.close(fig)
# hedge payoff in grayscale
Q=HD['Q']; S0=HD['S']; N=HD['N']; FX=HD['FX']; BOOK=737469.0
def book_move(r): return 0.45*r if r>=0 else (0.50*r if r>=-0.20 else -0.10+0.70*(r+0.20))
def ps(legs,s): return sum(q*max(k-s,0) for k,q in legs)
def cost(legs): return sum((Q[k][1] if q>0 else -Q[k][0]) for k,q in legs)
H2=[(690,1),(615,-1)]; H3=[(690,1)]; H1=[(730,1),(650,-1)]
rs=np.linspace(-0.40,0.10,101); fig,ax=plt.subplots(figsize=(7.2,3.4))
ax.plot(rs*100,[book_move(r)*BOOK/1000 for r in rs],color='black',lw=2.2,label='No hedge')
for lg,ls,lab in [(H2,'--','H2 690/615 put spread (recommended)'),(H3,':','H3 outright 690 put'),(H1,'-.','H1 730/650 put spread')]:
    ax.plot(rs*100,[(book_move(r)*BOOK+(ps(lg,S0*(1+r))-cost(lg))*N*100*FX)/1000 for r in rs],color='#404040',ls=ls,lw=1.6,label=lab)
ax.axhline(0,color='black',lw=.5); ax.set_xlabel('SPY move to 19 Feb 2027 (%)'); ax.set_ylabel('Whole-book P&L (SGD thousand)'); ax.legend(frameon=False,fontsize=8,loc='lower right')
fig.tight_layout(); fig.savefig(OUT+'p_fig3.png',dpi=170); plt.close(fig)
# ---------------- styles (black and white) ----------------
BK=colors.black; G1=colors.HexColor('#E6E6E6'); G2=colors.HexColor('#BDBDBD'); GT=colors.HexColor('#404040')
ss=getSampleStyleSheet()
B=ParagraphStyle('B',parent=ss['BodyText'],fontName='Helvetica',fontSize=9.3,leading=12.8,spaceAfter=4,textColor=BK)
Sm=ParagraphStyle('Sm',parent=B,fontSize=7.8,leading=10,textColor=GT)
H1=ParagraphStyle('H1',parent=B,fontName='Helvetica-Bold',fontSize=14,leading=18,spaceBefore=4,spaceAfter=5)
H2=ParagraphStyle('H2',parent=B,fontName='Helvetica-Bold',fontSize=10.3,leading=13.5,spaceBefore=5,spaceAfter=2)
Ti=ParagraphStyle('Ti',parent=B,fontName='Helvetica-Bold',fontSize=22,leading=26)
Bu=ParagraphStyle('Bu',parent=B,leftIndent=12,bulletIndent=2,spaceAfter=2.5)
C=ParagraphStyle('C',parent=B,fontSize=7.9,leading=9.8,spaceAfter=0); CB=ParagraphStyle('CB',parent=C,fontName='Helvetica-Bold')
P=lambda t,s=B: Paragraph(t,s); bl=lambda t: Paragraph(t,Bu,bulletText='-'); ck=lambda t: Paragraph('[ ]&nbsp; '+t,Bu)
def tbl(data,widths,grey_first_col=False):
    rows=[[Paragraph(str(c),CB if (i==0) else C) for c in r] for i,r in enumerate(data)]
    t=Table(rows,colWidths=widths,repeatRows=1)
    st=[('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LINEBELOW',(0,0),(-1,0),1,BK),('LINEBELOW',(0,1),(-1,-1),0.3,G2),('TOPPADDING',(0,0),(-1,-1),2.4),('BOTTOMPADDING',(0,0),(-1,-1),2.4),('BACKGROUND',(0,0),(-1,0),G1),('BOX',(0,0),(-1,-1),0.5,BK)]
    t.setStyle(TableStyle(st)); return t
def box(txt):
    t=Table([[Paragraph(txt,B)]],colWidths=[174*mm]); t.setStyle(TableStyle([('BOX',(0,0),(-1,-1),1.2,BK),('BACKGROUND',(0,0),(-1,-1),G1),('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),4)])); return t
k=lambda x: f'{x/1000:,.1f}k'
est=MB['est']; vx0,vx1,vx2=VIX['VIX0'],VIX['VIX1'],VIX['VIX2']
story=[]
# ===== p1 at a glance =====
story+=[P('Allocation playbook',Ti),P('Black and white, for printing. Prepared 4 Nov 2026 (prices to the 4 Nov close). Draft for the owner. Nothing here places an order; you place trades by hand.',Sm),Spacer(1,5)]
story+=[box('<b>The book in one view.</b> SGD 737k: U12 126k (active), U15 222k (passive), U18 90k (growth, margin allowed), UOB 300k (unit trusts, buy and hold). Approved: hedge cap about 6% if SPY falls 20% over three months, using the H2 put spread (690/615, 19 Feb 2027, about SGD 2.0k). Not yet placed.'),Spacer(1,5)]
story+=[tbl([['Piece','Size (SGD)','Style','Hard limits (approved or proposed)'],
 ['U18 growth','89.8k (12%)','Index ETFs and futures. Margin allowed','Leverage at most 1.5x; excess liquidity above 40%; drawdown ladder -15%/-25%/-30%; no naked short options; turnover at most 2x NAV a year'],
 ['U12 active','126.2k (17%)','Hold 1 week to 1 month','Review at 30 days; stop -10%; at most 15% in one name; sleeve at most 20% of book; no options; turnover at most 6x'],
 ['U15 passive','221.8k (30%)','Hold over 1 month','Policy mix with bands; rebalance only on a band breach; no options; turnover at most 1x'],
 ['UOB funds','299.8k (41%)','Buy and hold','Stop adding to Schroder Singapore Trust (41% of UOB); no more purchases until the rest of the book is in balance']],[24*mm,24*mm,38*mm,88*mm])]
story+=[P('Today: what to do and in what order',H2),
 ck('<b>Stand down for one day.</b> 4 Nov was a big move day (page 2). Place no new trade today; decide on 5 Nov using the checklist on page 3.'),
 ck('<b>Decide the hedge.</b> It is approved. Volatility fell sharply (VIX 20.8 to 17.3), so protection is cheaper now than yesterday. Ask me to re-quote and place the order by hand in U18.'),
 ck('<b>Review U12.</b> Every U12 position is older than 30 days (page 6). Apply the default actions: move to U15, sell, or keep with a written thesis.'),
 ck('<b>Re-balance U15</b> toward its target (page 5) in three steps, not one.'),
 ck('<b>Deploy U18 cash</b> in three monthly tranches (page 7). First tranche on the first calm trading day after payrolls (6 Nov): Monday 9 Nov at the earliest.'),
 ck('<b>Decide two open items:</b> (a) QQQ is 39% of U18, above the 30% single-ETF limit; (b) the core risk budget of 7 to 9% is above what this plan reaches (page 4).'),
 P('Rules that never change',H2),
 bl('No orders from me. No margin outside U18. No naked short options. No account numbers or statements in any file.'),
 bl('If a rule is broken, write it in the journal (page 10) the same day with the reason.'),PageBreak()]
# ===== p2 midterm shock =====
story+=[P('1. Midterm shock desk: what moved on 3 and 4 Nov',H1),
 P('You asked about yesterday and today. I could not find reliable news coverage of this year\'s result, so I do not state a cause. What I can show is the price pattern, measured from your data. 3 Nov (yesterday) was quiet. <b>4 Nov (today) was the big day.</b>')]
rows=[['Asset','3 Nov','4 Nov','2 days']]
for nm in ['SPY (S&P 500)','QQQ (Nasdaq 100)','IWM (small caps)','XLF (financials)','XLE (energy)','EZU (Eurozone)','EEM (EM)','XBI (biotech)','TLT (long Treasuries)','HYG (high yield)','GLD (gold)','PDBC (commodities)','Bitcoin','UUP (US dollar)','ES3 (Singapore, SGX)']:
    r=MV.loc[nm]; rows.append([nm,f'{r["3 Nov"]:+.1f}%',f'{r["4 Nov"]:+.1f}%',f'{r["2 days"]:+.1f}%'])
rows.append(['VIX (level)',f'{vx0:.1f} to {vx1:.1f}',f'{vx1:.1f} to {vx2:.1f}',f'{(vx2/vx0-1)*100:+.0f}%'])
story+=[tbl(rows,[60*mm,38*mm,38*mm,38*mm]),Image(OUT+'p_fig1.png',width=150*mm,height=75*mm)]
story+=[P('How your book reacted (estimate, current holdings, SGD)',H2),
 tbl([['Piece','3 Nov','4 Nov','Largest effects on 4 Nov'],
 ['U12',f'{est["U12"][1]:+.2f}%',f'{est["U12"][2]:+.2f}% ({est["U12"][3]:+,.0f})','USO -8.8%, XLP +3.6%, EWU +2.9%'],
 ['U15',f'{est["U15"][1]:+.2f}%',f'{est["U15"][2]:+.2f}% ({est["U15"][3]:+,.0f})','GLD +3.4% (+950), VOO +1.6% (+880), PDBC -4.0% (-740), USO -8.8% (-540)'],
 ['U18',f'{est["U18"][1]:+.2f}%',f'{est["U18"][2]:+.2f}% ({est["U18"][3]:+,.0f})','QQQ only; 61% is cash'],
 ['UOB (by proxy)',f'{MB["u3"]:+.2f}%',f'{MB["u4"]:+.2f}%','Singapore and credit funds barely moved'],
 ['<b>Whole book</b>','',f'<b>{MB["tot4"]/737469*100:+.2f}% ({MB["tot4"]:+,.0f})</b>','SPY rose 1.7%; the book rose about a third as much']],[26*mm,22*mm,38*mm,88*mm]),
 P('<b>Reading the pattern (not a verified cause).</b> Volatility fell 17% in a day, financials and Europe jumped about 2.8%, energy fell 5.2% and commodities 3.6%, gold gained 3.6%, Bitcoin 3.1%, bonds edged up and the dollar was flat. That looks like a relief rally with a sharp drop in oil. The practical points are: protection is cheaper after a volatility drop; oil and commodity holdings (USO in U12 and U15, PDBC) took the hit; and your book is low-beta, so it rose far less than the S&amp;P.',B),PageBreak()]
# ===== p3 event playbook =====
story+=[P('2. Event and shock rules',H1),P('Use these on any day the market moves a lot (an election, a central bank, a jobs report), not only today.'),
 tbl([['Trigger','What to do','Account'],
 ['SPY moves more than 1.5% in a day, or VIX moves more than 15%','Stand down: no new orders that day. Decide at the next close with the checklist below','All'],
 ['SPY moves more than 4% in a week','Emergency review on the same day: stops, hedge mark, cash, margin headroom','All'],
 ['Event day (payrolls, CPI, FOMC)','No new U12 entry until 30 minutes after the release. Use limit orders at the mid for spreads','U12, U18'],
 ['A sharp drop in VIX (like 4 Nov)','After the stand-down day, buy protection: puts are cheaper than before. Re-quote the hedge and place it, not after a spike','U18'],
 ['A sharp rise in VIX above 25','Do not buy new puts (dear). Hold the hedge you have. No tranches into the spike','U18, U12'],
 ['One sector or commodity moves more than 5% in a day (energy -5.2% on 4 Nov)','Check every position in it. Apply the position rules: stop, size cap, thesis still true?','U12, U15'],
 ['Any position breaks a stop or size cap','Act at the next close. Write the reason in the journal','U12, U18']],[58*mm,88*mm,28*mm])]
story+=[P('Day-after checklist (use it on 5 Nov)',H2),
 ck('Read account values for U12, U15 and U18. Compare with the estimates on page 2.'),
 ck('List every position moved more than 5% and check its stop and size cap.'),
 ck('Check that each U15 position is still inside its band (page 5).'),
 ck('Check U18: excess liquidity above 40%, no margin used, QQQ weight.'),
 ck('Re-quote the SPY puts (four contracts, 19 Feb 2027): the spread cost should be near or below SGD 2.0k at today\'s lower volatility.'),
 ck('Decide, then act on at most two items per day. Write the decisions in the journal.'),
 P('If/then table for the next weeks (SPY from 767)',H2),
 tbl([['If','Book effect (approx.)','Action'],
 ['SPY up 5% or more','+2% (with H2 hedge: about -0.3% net cost)','Do nothing new. Let U15 drift inside bands. Do not chase in U12. Roll the hedge on schedule'],
 ['SPY down 5%','-2.5%','No action unless a stop is hit. Do not add risk. Note the hedge has no payoff yet'],
 ['SPY down 10%','-5.0%','Review all stops. U18 ladder at -15% from its peak. Hedge begins to pay below 690'],
 ['SPY down 15%','-7.5% unhedged; about -5.2% with H2','Hedge pays in full from 615. Cut U18 to 1.0x if it is down 15% from its peak. No new U12 entries'],
 ['SPY down 20% or more','-10% unhedged; about -5.1% with H2','Stop adds everywhere. U18 ladder at -25%. Consider closing half the hedge spread if its value is above 70% of the maximum and the market stabilises'],
 ['VIX above 30','Stress','See the volatility table on page 9']],[38*mm,50*mm,86*mm]),PageBreak()]
# ===== p4 overall allocation =====
story+=[P('3. Allocation: whole book and the core',H1),
 P('Core = U12 + U15 + UOB (SGD 648k). UOB is fixed. The plan below moves long-held U12 positions into U15, trims ALLW and drops duplicated or stale positions.'),Image(OUT+'p_fig2.png',width=150*mm,height=67*mm)]
story+=[tbl([['Measure','Now','After the plan'],['Core volatility (ex-ante)',f'{AP["vb"]*100:.1f}%',f'{AP["va"]*100:.1f}%'],['Singapore equity share of core risk (UOB fixed)','26%','27%'],['US equity share of core risk','16%','24%'],['Commodities share of core risk','8%','1%'],['2020-26 return a year, backcast (hindsight)','9.4%','8.2%'],['ALLW scaled to the same volatility, backcast','6.5%','6.0%']],[90*mm,40*mm,44*mm]),
 P('<b>Open decision A: core risk budget.</b> The approved budget was 7 to 9% volatility. The plan lands near 6%, because the core is dominated by UOB bonds and Singapore equity and a passive mix is diversified. Even with U12 fully invested, the core reaches about 6.5%. I recommend widening the budget to <b>6 to 8%</b> and leaving the extra risk to U18. The alternative is a heavier equity mix in U15, which raises risk but lowers diversification.',B),
 P('<b>What stays concentrated.</b> Singapore equity (Schroder Singapore Trust, about 19% of the core) is about a quarter of core risk. The plan adds no more of it and sells U15\'s D05 holding for that reason.',B),
 P('Backcasts use today\'s weights over 2020 to 2026. They are hindsight, not forecasts. ALLW before March 2025 is a proxy.',Sm),PageBreak()]
# ===== p5 U15 =====
new15,post15,size15=AP['new15'],AP['post15'],AP['size15']
pos=pd.read_csv(SP+'ibkr_positions_2026-11-03.csv'); pos['symbol']=pos.symbol.astype(str); pos['inst']=pos.symbol.map(lambda x:{'1330.T':'1330','1631.T':'1631'}.get(x,x))
px_sgd=pos.groupby('inst').apply(lambda d:(d.price*d.fx).iloc[0]) if 'fx' in pos else None
FXR={'USD':1.2815,'JPY':0.0080749,'HKD':0.16332,'SGD':1.0}; pos['unit']=pos.price*pos.ccy.map(FXR); unit=pos.groupby('inst').unit.first().to_dict(); unit['IEF']=91.16*1.2815
today15=pos[pos.acct=='C'].groupby('inst').value_sgd.sum()
band=lambda w: 3 if w>=10 else (2 if w>=4 else 1)
rows=[['Holding','U15 today','After move from U12','Target %','Band','Target (SGD)','Change (SGD)','About (shares)','Action']]
order=list(post15.sort_values(ascending=False).index)+[i for i in new15.index if i not in post15.index]
for h in order:
    t=post15.get(h,0.0); a=new15.get(h,0.0); now=today15.get(h,0.0); ch=t-a; w=t/size15*100
    if abs(ch)<500 and h not in ('D05','USO','DBA'): act='Hold'
    elif ch>0: act='Buy'
    else: act='Sell'
    if h in ['LVHI','XLP','EWU','EZU','EWJ','1330','1631'] and now==0 or (h in ['LVHI','XLP','EWU','EZU','EWJ','1330','1631'] and act=='Hold'): act='Move in from U12' if act=='Hold' else act
    if t==0 and a>0: act='Sell'
    sh=(f'{abs(ch)/unit[h]:,.0f}' if h in unit and abs(ch)>=500 else '')
    rows.append([h,k(now) if now else '-',k(a),f'{w:.1f}%',f'+/-{band(w)} pp',k(t),f'{ch:+,.0f}' if abs(ch)>=500 else '-',sh,act])
rows.append(['Cash',k(AP['c15']),k(AP['c15']),f'{AP["cash15"]/size15*100:.1f}%','+/-2 pp',k(AP['cash15']),f'{AP["cash15"]-AP["c15"]:+,.0f}','',''])
rows.append(['<b>Total</b>',k(today15.sum()+AP['c15']),k(size15),'100%','',k(size15),'','',''])
story+=[P('4. U15 (passive): target allocation and bands',H1),P(f'U15 grows from SGD {k(today15.sum()+AP["c15"])} to about SGD {k(size15)} when the long-held U12 positions move in (in-kind transfer between your own accounts, no sale). Targets are weights of U15. A band says how far a holding may drift before you trade it.')]
story+=[tbl(rows,[17*mm,18*mm,22*mm,14*mm,15*mm,19*mm,19*mm,17*mm,33*mm]),
 P('Shares are approximate at 3 Nov prices. Recompute on the day. Do the trades in three steps over three weeks (not one day), starting after the stand-down day.',Sm),
 P('Why these changes',H2),
 bl('<b>ALLW 25% to 10%.</b> It is the benchmark and a levered all-weather fund; holding a quarter of U15 in it makes the core look like ALLW and charges its fee. Ten per cent keeps it as one diversifier.'),
 bl('<b>Commodities to PDBC only.</b> Sell DBA, USO (and CPER in U12). Oil fell 8.8% on 4 Nov; one broad fund is enough.'),
 bl('<b>Sell D05.</b> A single Singapore stock duplicates the Singapore equity you already hold through UOB.'),
 bl('<b>Add VOO, IEF and VNQ; move the international ETFs in from U12.</b> More US equity and government bonds, a little real estate, and international developed markets grouped in one account.'),
 bl('<b>Gold stays about 10%.</b> It is down 14.5% on cost but within its band; gold gained 3.6% on 4 Nov.'),
 P('Rebalance rule: look weekly; trade only a holding outside its band, back to target; no more than two trades a day.',B),PageBreak()]
# ===== p6 U12 =====
story+=[P('5. U12 (active): position review and the sleeve you keep',H1),
 P('Rule check (approved): hold 1 week to 1 month; review at 30 days; stop -10% from entry. Today every U12 position is older than 30 days (about 2 to 11 months). Default actions below; you may keep any position by writing a thesis and a new 30-day review date.')]
dest={'XBI':'Trim to about SGD 9k (15% cap); keep with a thesis','CPER':'Sell (commodities live in U15 as PDBC)','LVHI':'Move to U15','XLP':'Move to U15','EWU':'Move to U15','EZU':'Move to U15 (underwater: reason = policy holding)','EWJ':'Move to U15','BITB':'Move to U18 (Bitcoin allocation)','1631.T':'Move to U15 (Japan)','USO':'Sell (take profit)','1330.T':'Move to U15 (Japan)','2823':'Sell (-9.3%, near the -10% stop)'}
a12=AGE[AGE.acct=='U12'].copy(); tot12=126196.0
rows=[['Position','Value (SGD)','% of U12','Gain/loss','Age (days, avg)','Rule check','Default action']]
for _,r in a12.iterrows():
    chk=[]; 
    if r.value_sgd/tot12>0.15: chk.append('over 15% cap')
    chk.append('over 30 days')
    if r.pnl_pct<0: chk.append('underwater')
    rows.append([r.symbol,f'{r.value_sgd:,.0f}',f'{r.value_sgd/tot12*100:.0f}%',f'{r.pnl_pct:+.1f}%',f'{r.wavg_days:.0f}' if r.wavg_days==r.wavg_days else 'n/a','; '.join(chk),dest.get(r.symbol,'review')])
rows.append(['Cash','16,002','13%','','','',''])
story+=[tbl(rows,[16*mm,19*mm,15*mm,17*mm,20*mm,40*mm,47*mm]),P('Ages come from matching your purchases in the Flex file; parts bought before 4 Nov 2025 or moved in from another account have no purchase date, so treat these as minimums.',Sm),
 P('After the plan, U12 is small and mostly cash',H2),
 P('XBI trimmed (about SGD 9k) plus about SGD 52k of cash from the sales. That cash is dry powder for new active ideas, not idle money: if no idea qualifies in 60 days, move the unused cash to U15 or U18. Size of U12 after the plan: about SGD 61k, 8% of the book (cap 20%).',B),
 P('Entry checklist for any new U12 position',H2),
 ck('One sentence: what is the thesis, and what would prove it wrong?'),
 ck('Entry price, stop (-10%), and a review date no more than 30 days ahead.'),
 ck('Size at most 15% of U12 (about SGD 9k at 61k), at most 8 positions, Bitcoin at most 6%.'),
 ck('No entry on a shock day or the half hour after an event (page 3).'),
 ck('Not already held in U15 or U18 (avoid duplicates).'),
 P('Exit rules',H2),
 bl('Stop hit: sell at the next close. Day 30: close, or move to U15 with a written reason, or renew the thesis once.'),
 bl('Gain above 15% with the thesis done: sell half and move the stop to entry.'),PageBreak()]
# ===== p7 U18 =====
story+=[P('6. U18 (growth): cash plan and guard-rails',H1),
 P('U18 holds QQQ (SGD 35.1k, 39% of the account) and SGD 54.5k cash. Bitcoin (BITB, SGD 5.4k) moves in from U12, so U18 becomes about SGD 95k. Keep SGD 8k cash for the hedge premium and a safety margin; deploy about SGD 46k in three tranches, no margin during the probation.'),
 tbl([['Step','When (earliest)','Amount (SGD)','Split of each tranche'],
 ['Tranche 1','Mon 9 Nov, if the day before was calm (page 3)','about 15.5k','VOO 54%, SPMO 26%, GLD 20%'],
 ['Tranche 2','Thu 10 Dec (after the 8 to 9 Dec Fed meeting)','about 15.5k','same'],
 ['Tranche 3','Mon 11 Jan 2027','about 15.5k','same']],[24*mm,66*mm,26*mm,58*mm]),
 P('After all three tranches: QQQ about 37%, VOO 26%, SPMO 13%, GLD 10%, Bitcoin 6%, cash 8%. Expected volatility about 15%. The tranche dates are rules; if a stand-down trigger fires, move to the next calm day.',B),
 P('<b>Open decision B: QQQ is above the 30% single-ETF limit.</b> It is 39% of U18 and stays near 37% after the plan. Choose one: (1) trim QQQ by about SGD 6.6k (7 to 8 shares) so it is 30% of the account; or (2) change the limit to 40% for broad index ETFs (QQQ, VOO) and 15% for theme ETFs. I lean to (2): QQQ is the growth core. It is your guard-rail, so you decide.',B),
 P('Guard-rail dashboard (check weekly, write it on page 10)',H2),
 tbl([['Item','Limit','Action when breached'],
 ['Gross leverage','at most 1.5x NAV (use 1.0x now)','Cut to 1.0x within one day'],
 ['Excess liquidity','above 40% of NAV','Reduce positions until restored'],
 ['Drawdown from peak','-15% / -25% / -30%','Cut to 1.0x / halve risk / stop and review'],
 ['One broad ETF','at most 30% (or 40%, see B)','Trim at the next close'],
 ['One theme ETF','at most 15%','Trim at the next close'],
 ['Bitcoin','at most 6% (cap 5 to 10%)','Trim at the next close'],
 ['Hedge cost','at most 2% of hedged value a year (about SGD 7.4k)','Do not add; review at the quarterly scorecard']],[44*mm,66*mm,64*mm]),PageBreak()]
# ===== p8 hedge =====
h2=DF[DF.name.str.startswith('H2')].iloc[0]
story+=[P('7. Hedge playbook (whole book, held in U18)',H1),
 P(f'<b>What.</b> Buy 4 SPY 690 puts and sell 4 SPY 615 puts, expiry 19 Feb 2027 (107 days). Quote on 4 Nov: net about USD {h2.cost_usd:,.0f} (SGD {h2.cost_sgd:,.0f}), about {h2.ann_pct_book:.1f}% of the book a year if rolled. Protection runs from a 10% fall in SPY (690) to a 20% fall (615), worth up to about SGD {h2.max_sgd/1000:,.0f}k. It is a debit spread: the most you can lose is the premium and U18 needs no margin for it.'),
 Image(OUT+'p_fig3.png',width=150*mm,height=71*mm)]
story+=[tbl([['SPY move at expiry','Book, no hedge','With H2'],['-5%',f'{T.loc[-0.05,"Book unhedged"]/BOOK*100:+.1f}%',f'{T.loc[-0.05,"H2"]/BOOK*100:+.1f}%'],['-10%',f'{T.loc[-0.10,"Book unhedged"]/BOOK*100:+.1f}%',f'{T.loc[-0.10,"H2"]/BOOK*100:+.1f}%'],['-20%',f'{T.loc[-0.20,"Book unhedged"]/BOOK*100:+.1f}%',f'{T.loc[-0.20,"H2"]/BOOK*100:+.1f}%'],['-30%',f'{T.loc[-0.30,"Book unhedged"]/BOOK*100:+.1f}%',f'{T.loc[-0.30,"H2"]/BOOK*100:+.1f}%']],[50*mm,50*mm,50*mm]),
 P('Placing it (by hand, in U18)',H2),
 ck('Ask the CTO session to re-quote on the day and confirm four contracts (3.75 is the exact need).'),
 ck('Enter it as one spread order (combo) with a limit at the mid price; never leg in. Allow up to 15 minutes, then lift the limit by one tick at a time.'),
 ck('Check the fill: net debit near USD 1,550 total; margin required should equal the debit.'),
 ck('Record it on page 10: date, price, SPY level, VIX.'),
 P('Running and rolling it',H2),
 bl('<b>Roll window:</b> 15 to 29 Jan 2027 (30 to 45 days before expiry). Re-estimate the contract count: 0.5 x book value / (SPY x 100 x USDSGD).'),
 bl('<b>Take profit:</b> if SPY has fallen more than 10% and the spread is worth more than 70% of its maximum, close half and keep half.'),
 bl('<b>Do not</b> add legs, sell extra puts, or hold through expiry with a loss you could close; do not buy more cover when VIX is above 25.'),
 bl('<b>Budget:</b> at most 2% of hedged value a year (about SGD 7.4k). Last year\'s options cost SGD 20.8k.'),
 P('Limits: SPY does not track Singapore shares or credit exactly; the dollar moves against the Singapore dollar; the hedge costs money in most years.',Sm),PageBreak()]
# ===== p9 volatility regimes + calendar + routines =====
story+=[P('8. Volatility regimes, calendar and routines',H1),
 tbl([['VIX level','Regime','U12','U15','U18'],
 ['Below 15','Calm','Full size allowed','Normal bands','Normal. A good time to buy protection'],
 ['15 to 20 (now 17.3)','Normal','Standard rules','Normal bands','Tranches as scheduled'],
 ['20 to 30','Elevated','New entries at half size','Widen bands by 1 pp; trade in thirds','No leverage increase; pause tranches on days VIX rises 10%+'],
 ['Above 30','Stress','No new entries; close weakest positions','Rebalance into weakness only in three steps over weeks','Ladder rules; hold hedge; no new puts; no margin']],[32*mm,22*mm,38*mm,38*mm,44*mm]),
 P('Calendar (dates from your Bloomberg data and the public Fed calendar; check the exact dates before use)',H2),
 tbl([['Date','Event','What to do'],
 ['Thu 5 Nov','Day after the move','Run the day-after checklist (page 3)'],
 ['Fri 6 Nov','US payrolls (survey about 65k)','Event rules: no U12 entry until 30 min after'],
 ['Mon 9 Nov','Earliest U18 tranche 1 and U15 step 1','Only if the day before was calm'],
 ['Wed 25 Nov','US core PCE (October data)','Event rules'],
 ['8 to 9 Dec','Fed meeting (FOMC)','Event rules; U18 tranche 2 on 10 Dec'],
 ['15 to 29 Jan 2027','Hedge roll window','Re-quote, roll, update the contract count'],
 ['11 Jan 2027','U18 tranche 3','Calm-day rule'],
 ['Fri 19 Feb 2027','Hedge expiry','Must be rolled or closed before this date'],
 ['End Dec, Mar, Jun, Sep','Quarterly scorecard','Page 10']],[34*mm,60*mm,80*mm]),
 P('Routines',H2),
 tbl([['When','Do'],
 ['Daily (5 minutes)','Account values; VIX; hedge mark; any stop hit; note the day if SPY moved more than 1.5%'],
 ['Weekly (Monday)','U15 bands; U12 ages and stops; U18 dashboard (page 7); cash levels'],
 ['Monthly','U12 30-day reviews and journal; tranche due; hedge cost to date; statement check (UOB, IBKR)'],
 ['Quarterly','Scorecard per sleeve vs the benchmark (page 10); hedge cost vs protection; roll; margin rate check; update this playbook'],
 ['Yearly','Whole-plan review: risk budget, benchmark, sleeve sizes, the 12-month probation of U18 (close or cut if net Sharpe is below 0.3)']],[34*mm,140*mm]),PageBreak()]
# ===== p10 journal templates =====
blank=lambda n: ['']*n
story+=[P('9. Journal and scorecard (print and fill in)',H1),P('U12 trade journal',H2),
 tbl([['Date','Symbol','Thesis (one sentence)','Entry','Stop','Review date','Result / why']]+[blank(7) for _ in range(6)],[17*mm,18*mm,52*mm,16*mm,16*mm,20*mm,35*mm]),
 P('Event and shock log',H2),
 tbl([['Date','What moved','Book effect','Action taken','Rule used']]+[blank(5) for _ in range(4)],[18*mm,48*mm,28*mm,52*mm,28*mm]),
 P('Hedge log',H2),
 tbl([['Date','Contracts','Net debit','SPY / VIX','Mark now','Next step (roll / close)']]+[blank(6) for _ in range(3)],[18*mm,22*mm,26*mm,28*mm,26*mm,54*mm]),
 P('Quarterly scorecard',H2),
 tbl([['Quarter','U18 return','U12 return','U15 return','Core vs ALLW (vol-matched)','Hedge cost / payoff','Rule breaks']]+[blank(7) for _ in range(3)],[18*mm,22*mm,22*mm,22*mm,38*mm,28*mm,24*mm]),
 P('Weekly guard-rail check',H2),
 tbl([['Week of','Leverage','Excess liquidity','U18 drawdown','Largest single ETF','Bitcoin %','OK?']]+[blank(7) for _ in range(3)],[20*mm,22*mm,28*mm,26*mm,34*mm,22*mm,22*mm]),
 P('Limits of this playbook',H2),
 bl('Planning aid, not advice. No return forecasts. Targets and limits are proposals the owner can change.'),
 bl('Tax, commissions, spreads, US estate tax on US-listed ETFs, and your IBKR margin rate are not covered.'),
 bl('Prices: Bloomberg and Yahoo to the 4 Nov close; option quotes from IBKR on 4 Nov. Recompute shares and costs on the day.'),
 bl('I could not find coverage of the 2026 election result, so no political cause is stated; only price evidence is used.')]
def foot(c,d):
    c.saveState(); c.setFont('Helvetica',7.5); c.setFillColor(GT); c.drawString(18*mm,10*mm,'Allocation playbook - draft for the owner - no orders placed'); c.drawRightString(192*mm,10*mm,f'Page {d.page}'); c.restoreState()
doc=SimpleDocTemplate(OUT+'Allocation_Playbook_BW_2026-11-04.pdf',pagesize=A4,leftMargin=18*mm,rightMargin=18*mm,topMargin=15*mm,bottomMargin=17*mm,title='Allocation playbook',author='CTO office')
doc.build(story,onFirstPage=foot,onLaterPages=foot); print('ok')
