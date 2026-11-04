import pickle, json, hashlib, glob
import numpy as np, pandas as pd
from options_load import *
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
OUT=SP+'report/'; Y=pickle.load(open(OUT+'year.pkl','rb')); A,tot,fin,GR=Y['A'],Y['tot'],Y['fin'],Y['GR']
HD=pickle.load(open(OUT+'hedge.pkl','rb')); UP=pickle.load(open('uob_perf.pkl','rb')); HOLD=pd.read_pickle('hold.pkl')
df,T=HD['df'],HD['T']; R=UP['R']; fl=UP['fl']; buys=sum(v for v in fl.values() if v>0); redeem=-fl['2026-09']
_D=pd.read_pickle('year_raw.pkl'); _t=_D['trades'].copy(); _t['mon']=pd.to_numeric(_t.TradeMoney,errors='coerce').abs()*pd.to_numeric(_t.FXRateToBase,errors='coerce'); _ex=_t[_t.AssetClass.isin(['STK','OPT'])]
GROSS=float(_ex.mon.sum()); ONEWAY=GROSS/2; AVGCAP=392810.0; TO={a_:float(_ex[_ex.acct==a_].mon.sum()) for a_ in 'ABC'}; OPTP={a_:float(_ex[(_ex.acct==a_)&(_ex.AssetClass=='OPT')].mon.sum()) for a_ in 'ABC'}
s,e=pd.Timestamp('2025-11-04'),pd.Timestamp('2026-11-03')
NAVYc=colors.HexColor('#1F3864'); LIGHT=colors.HexColor('#EEF1F6'); GREYT=colors.HexColor('#555555')
ss=getSampleStyleSheet()
B=ParagraphStyle('B',parent=ss['BodyText'],fontName='Helvetica',fontSize=9.5,leading=13.2,spaceAfter=5)
Sm=ParagraphStyle('Sm',parent=B,fontSize=8,leading=10.5,textColor=GREYT)
H1=ParagraphStyle('H1',parent=B,fontName='Helvetica-Bold',fontSize=14,leading=18,textColor=NAVYc,spaceBefore=8,spaceAfter=6)
H2=ParagraphStyle('H2',parent=B,fontName='Helvetica-Bold',fontSize=10.5,leading=14,textColor=NAVYc,spaceBefore=6,spaceAfter=3)
Ti=ParagraphStyle('Ti',parent=B,fontName='Helvetica-Bold',fontSize=22,leading=27,textColor=NAVYc,spaceAfter=2)
Bu=ParagraphStyle('Bu',parent=B,leftIndent=12,bulletIndent=2,spaceAfter=3)
C=ParagraphStyle('C',parent=B,fontSize=8,leading=10,spaceAfter=0); CB=ParagraphStyle('CB',parent=C,fontName='Helvetica-Bold')
P=lambda t,s_=B: Paragraph(t,s_); bl=lambda t: Paragraph(t,Bu,bulletText='•')
def tbl(data,widths):
    rows=[[Paragraph(str(c),CB if i==0 else C) for c in r] for i,r in enumerate(data)]
    t=Table(rows,colWidths=widths,repeatRows=1)
    t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LINEBELOW',(0,0),(-1,0),0.8,NAVYc),('LINEBELOW',(0,1),(-1,-1),0.25,colors.HexColor('#CCCCCC')),('TOPPADDING',(0,0),(-1,-1),2.5),('BOTTOMPADDING',(0,0),(-1,-1),2.5),('BACKGROUND',(0,0),(-1,0),LIGHT)])); return t
def box(txt):
    t=Table([[Paragraph(txt,B)]],colWidths=[174*mm]); t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),LIGHT),('BOX',(0,0),(-1,-1),0.8,NAVYc),('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),5)])); return t
pct=lambda x,d=1:f'{x*100:.{d}f}%'; pc=lambda x,d=1:f'{x:.{d}f}%'; k=lambda x:f'{x/1000:,.1f}k'
h2=df[df.name.str.startswith('H2')].iloc[0]; h3=df[df.name.str.startswith('H3')].iloc[0]; h4=df[df.name.str.startswith('H4')].iloc[0]
story=[]
# ===== 1 summary =====
story+=[P('Rebalance review: consolidated',Ti),P('Prepared 4 Nov 2026 &nbsp;|&nbsp; Merges updates 2 and 3, with your decisions, the UOB statements and the priced hedge &nbsp;|&nbsp; <b>Draft for your decision. No orders placed.</b>',Sm),Spacer(1,6)]
story+=[box(f'<b>Bottom line</b><br/>Over the last 12 months your three IBKR accounts returned <b>between {fin["IBKR combined (TWR)"]*100:+.1f}% and -2.7%</b> and lost <b>SGD {abs(tot.pl)/1000:,.1f}k</b>, against {fin["ALLW"]*100:+.1f}% for ALLW and {fin["SPY"]*100:+.1f}% for SPY. UOB returned about <b>+2.7%</b> from Jan to Oct (+SGD 6.6k). The book grew from about SGD 305k to SGD 737k almost entirely through SGD 435k of new money, not performance. '
 f'The main drag was the <b>option hedges</b> (realised {tot.real_opt/1000:+,.1f}k; without them IBKR would have made about +1.7%). The structure you approved (U18 growth, U12 active, U15 passive, UOB, ALLW scored vol-matched) is set out below, with a <b>whole-book hedge priced from live quotes</b> that fits your budget.')]
story+=[Spacer(1,8),P('Your decisions',H2),
 tbl([['Item','Status','Detail'],
 ['Two-sleeve structure and U18 guard-rails','Approved','U18 growth sleeve, leverage at most 1.5 times, hedge budget (page 6)'],
 ['Beat ALLW','Approved: vol-matched','Core scored against ALLW scaled to its volatility (page 7)'],
 ['U12 and U15 style','Decided','U12 active (1 week to 1 month). U15 passive (over 1 month). Rules proposed on page 5'],
 ['Option hedge scope','Decided','Whole book including UOB, held in U18 (page 8)'],
 ['Loss the hedge must cap','<b>Open</b>','My proposal: book loss of no more than about 6% if SPY falls 20% over three months'],
 ['Hedge choice','<b>Open</b>','H2 (690/615 put spread) or an upgrade'],
 ['U12 and U15 rules; idle cash in U18','<b>Open</b>','Confirm the rules (page 5); decide how to deploy U18\'s SGD 54.5k cash']],[54*mm,34*mm,86*mm])]
story+=[P('Headlines',H2),
 bl(f'<b>IBKR record.</b> Commissions and taxes were small (SGD {abs(tot.comm+tot.taxes):,.0f}). The shortfall came from option hedges (-20.8k realised against +10.9k on stocks and ETFs) and from trading timing: today\'s U12 and U15 holdings, held unchanged, would have returned about 14%; the accounts earned -2.1% and +1.1%.'),
 bl(f'<b>UOB record.</b> UOB went from SGD 96k to 300k through SGD {buys/1000:,.0f}k of purchases (Schroder Singapore Trust five times, Feb to Jun) and one redemption (Fidelity US Dollar Bond fund, about SGD 14.7k, Aug to Sep). Its return of +2.7% compares with ALLW +1.5% and SPY +10.7% over the same dates.'),
 bl('<b>Holding periods.</b> U12: median 31 days (fits). U15: median 102 days, but 19% of sold value went within 30 days (USO, JNK, VOO, BNDX, ALLW).'),
 bl('<b>Growth sleeve.</b> 12% a year needs a Sharpe ratio near 0.7 at 16% volatility. I propose a 12-month probation with hard limits.'),
 bl(f'<b>Hedge.</b> The book moves about 0.5 times with SPY, so 4 SPY puts\' worth. H2 costs about SGD {h2.cost_sgd/1000:,.1f}k ({h2.cost_pct_book:.2f}% of the book, about {h2.ann_pct_book:.1f}% a year if rolled) and cuts the loss in a 20% fall from about 10% to about 5%.'),PageBreak()]
# ===== 2 IBKR record =====
story+=[P('1. Your IBKR record: last 12 months',H1),P('Figures are from your Flex file (SGD), 4 Nov 2025 to 3 Nov 2026. Moves between your own accounts are excluded from performance.')]
M_={'A':'U12','B':'U18','C':'U15'}
rows=[['','Start value','Added (cash + in-kind)','End value','P&amp;L (SGD)','IBKR time-weighted return']]
for a_ in 'ABC':
    q=A.loc[a_]; rows.append([M_[a_],k(q.start),k(q.deposits+q.inkind),k(q.end),f'{q.pl/1000:+,.1f}k',('n/a (opened in year)' if a_=='B' else f'{q.twr:+.1f}%')])
rows.append(['<b>All three</b>',k(tot.start),k(tot.deposits),k(tot.end),f'<b>{tot.pl/1000:+,.1f}k</b>',f'<b>{fin["IBKR combined (TWR)"]*100:+.1f}%</b> (my calc; about -2.7% on the app)'])
story+=[tbl(rows,[26*mm,24*mm,38*mm,24*mm,24*mm,38*mm]),P('U18 opened during the year, so IBKR\'s -39% for it is distorted by its first small deposit; I use SGD profit (it received SGD 99.6k and ended at 89.8k).',Sm),
 P('<b>Calibration against the IBKR app.</b> The app shows <b>+1.33% year to date</b>. My method gives +0.6% for the same dates, with the same low (-2.2% around 23 Mar) and high (+8.2% around 3 Jun). The 0.7-point gap is most likely deposit timing. Nov and Dec 2025 lost about 4.0%, so the 12 months come to about -3.5% (my numbers) or -2.7% (using the app). The SGD 11.1k loss does not depend on the method.',Sm),
 Image(OUT+'y_fig1.png',width=160*mm,height=75.5*mm)]
bt_=[['In SGD, same dates','Return','Volatility (1y)']]
for nm in ['SPY','QQQ','ALLW','60/40 (ACWI/AGG)']:
    r=Y['bench'][nm].loc[s:e]; bt_.append([nm,f'{fin[nm]*100:+.1f}%',pct(r.std()*np.sqrt(252))])
rr=Y['cum'].pct_change().dropna(); bt_.append(['<b>Your IBKR (3 accounts)</b>',f'<b>{fin["IBKR combined (TWR)"]*100:+.1f}%</b>',pct(rr.std()*np.sqrt(252))])
story+=[tbl(bt_,[60*mm,30*mm,34*mm]),P('Same year: commodities (PDBC +43.8%), Singapore equities (ES3 +22.0%), Japan (EWJ +13.5%), gold -4.3%, Bitcoin -28.5%, US Treasuries (IEF) -3.5%.',Sm),PageBreak()]
# ===== 3 drivers =====
story+=[P('2. What drove the IBKR result',H1),Image(OUT+'y_fig2.png',width=118*mm,height=52.5*mm)]
cost=[['Item (SGD, all 3 accounts)','Amount'],['Price and trading P&amp;L (IBKR "MTM")',f'{tot.mtm:+,.0f}'],['Dividends',f'{tot["div"]:+,.0f}'],['Dividend withholding tax',f'{tot.wht:+,.0f}'],['Interest, net (U18\'s net interest cost was SGD 1,479)',f'{tot.interest:+,.0f}'],['Commissions and taxes',f'{tot.comm+tot.taxes:+,.0f}'],['<b>Total profit and loss</b>',f'<b>{tot.pl:+,.0f}</b>']]
story+=[tbl(cost,[110*mm,34*mm]),P('Findings',H2),
 bl(f'<b>Options as a hedge.</b> Realised option losses were {abs(tot.real_opt)/1000:,.1f}k (U18 {A.loc["B","real_opt"]/1000:+,.1f}k; U12 {A.loc["A","real_opt"]/1000:+,.1f}k, mostly TSLA and URA). In U18: bought puts about -36k, sold puts about +20k; by underlying QQQ -7.0k, SMH -6.6k, TLT -2.3k, NVDA +1.9k. The contracts were large (SGD 125k to 355k notional each), so they must have covered more than U18.'),
 bl(f'<b>Trading activity</b> (stocks, ETFs and option premium; currency conversions excluded; one side counted): U12 {TO["A"]/2/A.loc["A","avgnav"]:.1f} times its average value, across {int(A.loc["A","nsym"])} symbols; U18 {TO["B"]/2/A.loc["B","end"]:.1f} times its year-end value; U15 {TO["C"]/2/A.loc["C","avgnav"]:.1f} times. Whole book: SGD {GROSS/1e6:,.2f}M bought and sold, about {ONEWAY/AVGCAP:.1f} times average capital. Options use premium, not notional.'),
 bl('<b>What worked</b> (IBKR performance by instrument; ranking only): USO (+6.6k), XBI (+3.8k), CPER (+2.1k), MU and VOO in U15 (+5.1k, +4.5k).'),
 bl('<b>What did not:</b> URA (-3.6k), UNL (-2.4k), IBIT (-2.1k), TSLA options (about -7k), ALLW in U15 (-2.1k), CLR and GLD (-1.7k, -1.5k).'),
 bl(f'<b>Dividend tax.</b> About {abs(tot.wht)/tot["div"]*100:.0f}% of dividends went to withholding (30% on US-listed ETFs; Irish-domiciled equivalents are usually 15%). Saving about SGD 1k a year, so minor.')]
story+=[P('Did the option hedge work?',H2),tbl([['Test (SGD, all accounts)','With option P&amp;L','Without option P&amp;L'],['12-month return','-3.5%','+1.7%'],['Maximum drawdown','-7.0%','-6.8%'],['Worst 5-day drop','-4.4%','-5.3%'],['Daily volatility, annualised','10.5%','10.8%'],['Option P&amp;L in the 6 months SPY fell','-8.7k',''],['Option P&amp;L in the 7 months SPY rose','-12.1k','']],[78*mm,38*mm,38*mm]),P('Counterfactual: realised option P&amp;L removed from daily values; it ignores how you would have traded otherwise and the monthly split is approximate. The hedge cut the worst week by about 0.9 points and volatility by 0.3, cost about 5 points of return, and did not reduce the maximum drawdown.',Sm),PageBreak()]
# ===== 4 UOB =====
story+=[P('3. Your UOB record: Jan to Oct 2026',H1),P('Source: UOB statements for Jan, Mar, May, Jul and Oct 2026. The units each statement carries over from the previous month let me rebuild the months in between; rebuilt values match the statement totals to within SGD 20. Nov and Dec 2025 are not covered.'),Image(OUT+'u_fig1.png',width=150*mm,height=64.5*mm)]
rows=[['Period','Start value','New money','End value','P&amp;L','Return','ALLW','SPY','ES3']]
for _,r in R.iterrows(): rows.append([r.period,k(r.V0),f'{r.flows/1000:+,.1f}k',k(r.V1),f'{r.pnl/1000:+,.1f}k',pc(r.ret),pc(r.ALLW),pc(r.SPY),pc(r.ES3)])
rows.append(['<b>31 Jan to 31 Oct</b>',k(96084.63),f'<b>{(buys-redeem)/1000:+,.1f}k</b>',k(299818.95),f'<b>{UP["tot_pl"]/1000:+,.1f}k</b>',f'<b>{(UP["cum"]-1)*100:.1f}%</b>','1.5%','10.7%','12.7%'])
story+=[tbl(rows,[30*mm,19*mm,19*mm,19*mm,17*mm,15*mm,15*mm,15*mm,15*mm]),P('Modified Dietz per period, chained. Flow dates assumed mid-month where a statement does not show one.',Sm),
 bl(f'<b>Purchases</b> SGD {buys/1000:,.0f}k: Feb 14.6k, Mar 48.9k, Apr 45.1k, May 67.2k, Jun 36.0k. Schroder Singapore Trust took about SGD 106k across five months (bought at NAV 2.2 to 2.3; now 2.312).'),
 bl(f'<b>Redemption.</b> The Fidelity US Dollar Bond fund (SGD-hedged, about SGD {redeem/1000:,.1f}k) is in the July statement and gone by the September balance. After that UOB shows only dividend reinvestments.'),
 bl('<b>Concentration.</b> Schroder Singapore Trust is 41% of UOB (SGD 122.7k). Its NAV rose to 2.443 in July and fell to 2.312 by October, which explains most of the -2.8% in the last period.'),
 bl('<b>Proxy check.</b> My ETF stand-ins for the UOB funds gave -0.5%, +5.0%, +3.1% and -1.8% against actual -1.7%, +4.8%, +2.6% and -2.8%: right direction and size, about 3 points high over the 9 months (fees and timing). Fine for risk and the hedge.'),
 P('<b>Whole-book picture.</b> IBKR lost SGD 11.1k over 12 months and UOB gained SGD 6.6k over 10 months: about SGD 4k to 5k down on roughly SGD 435k of new money added since Nov 2025. <b>Correction to my earlier pages:</b> I treated UOB as a fixed SGD 300k and quoted a proxy return of about +11%. That used today\'s weights; the actual record is smaller because most money arrived from March to June.'),PageBreak()]
# ===== 5 structure + holding periods =====
story+=[P('4. Structure: three accounts and UOB',H1),
 tbl([['','U18 growth','U12 active','U15 passive','UOB'],
 ['Size (SGD, share of book)','89.8k (12%)','126.2k (17%)','221.8k (30%)','299.8k (41%)'],
 ['Style','Growth sleeve: leverage and derivatives allowed','Active: hold 1 week to 1 month','Passive: hold over 1 month','Funds; buy and hold'],
 ['Goal','12% a year compound (stretch), 12-month probation','Part of core','Part of core','Part of core'],
 ['Risk budget','About 16% volatility; leverage at most 1.5 times','Core about 7 to 9% volatility (today 6.4%)','as U12','as U12'],
 ['Turnover cap (one side)','Stocks and ETFs 2 times NAV a year','6 times (last year 3.9)','1 time (last year 1.8)','n/a'],
 ['Options','Whole-book hedge only','None','None','None'],
 ['Scoreboard','Your 12% target; SPY and QQQ for reference','Core (U12 + U15 + UOB) vs ALLW scaled to its volatility, rolling 12 and 36 months','','']],[28*mm,40*mm,36*mm,36*mm,34*mm]),
 P('<b>Why this split.</b> A 12% target needs about 16% volatility, which the core cannot and should not carry. One account with its own rules (U18) keeps the aggressive risk away from the rest and gives you clean per-account records. Keep U18 at or below about 15% of the book (SGD 110k) during the probation; a 40% fall then costs about 5% of the book. Do not top it up from the core until it has earned it.',B),
 P('5. Do U12 and U15 follow your holding periods?',H1),
 P('For each stock or ETF sale in the last 12 months I matched it to the earlier purchase (first in, first out) and measured how long it was held. About 80% of sales could be matched. Options are excluded.')]
L={'A':'U12','C':'U15','B':'U18'}
def hp(a):
    x=HOLD[HOLD.a==a]; w=x.groupby('b',observed=False).val.sum(); w=w/w.sum()*100
    return [L[a],f'{x.val.sum()/1000:,.0f}k',f'{x.days.median():.0f} days',f'{w["<=7d"]:.0f}%',f'{w["8-30d"]:.0f}%',f'{w["31-90d"]:.0f}%',f'{w[">90d"]:.0f}%']
story+=[tbl([['Account','Sold value matched','Median hold','7 days or less','8 to 30 days','31 to 90 days','Over 90 days']]+[hp('A'),hp('C'),hp('B')],[24*mm,32*mm,24*mm,24*mm,24*mm,24*mm,22*mm]),Spacer(1,3),
 bl('<b>U12.</b> Half of the value was sold within 30 days, which fits. 22% was sold within a week (ALLW 24k, GOP 12k, QQQ 8k, URA 8k, GLD 5k, SMH 5k). The other half was held over 30 days (LVHI, 3033, ITA, WEAT, ICLN, 2823), which looks like trades that went against you and stayed open.'),
 bl('<b>U15.</b> 81% of sold value was held over 30 days (median 102). 19% (SGD 48k) was sold within 30 days: USO 14k, JNK 10k, VOO 10k, BNDX 8k, ALLW 5k.'),
 bl('<b>U18.</b> Median hold 106 days for stock and ETF sales, so its high turnover came from options.'),
 P('Proposed rules',H2),
 tbl([['','U12 (active)','U15 (passive)'],
 ['Holding period','Plan 1 week to 1 month. At 30 days: close, or move to U15 with a written reason','At least 30 days. Early sale needs a written reason'],
 ['Size','No more than 15% of U12 in one name; U12 no more than 20% of the book (today 17%)','Policy mix with bands; rebalance only when a band is breached'],
 ['Stops','Cut at -10% from entry, or at 30 days if still underwater','None; review at each band breach'],
 ['Review','Monthly trade journal and hit rate','Quarterly']],[26*mm,76*mm,72*mm]),PageBreak()]
# ===== 6 U18 =====
story+=[P('6. Growth sleeve (U18): design and guard-rails',H1),
 P('Three ways to build a roughly 16% volatility sleeve. Ex-ante volatility uses recent (calm) daily data. The 2020 to 2026 columns are hindsight from a strong market and are not forecasts.')]
gr=[['Design','Ex-ante vol','2020-26 vol','2020-26 return a year','Worst drop','Leverage for 16% vol']]
for n,v in GR.items(): gr.append([n,pct(v['exante']),pct(v['vol_lr']),pct(v['cagr']),pct(v['dd'],0),(f'{0.16/v["exante"]:.1f}x' if v['exante']<0.15 else 'none needed')])
story+=[tbl(gr,[62*mm,18*mm,20*mm,26*mm,18*mm,30*mm]),Spacer(1,4),
 P('<b>What 12% takes.</b> Compound return is roughly the cash rate (I assume 2%) plus Sharpe times volatility minus half the variance. For 12% you need a Sharpe of 0.89 at 12% volatility, 0.71 at 16%, 0.60 at 20% and 0.53 at 25%. Broad equity indexes have long-run Sharpe ratios of about 0.4 to 0.5. Leverage scales risk and return together, so it cannot raise the Sharpe, and margin interest lowers it. The diversified design needs 2.0 times leverage for 16%, above the 1.5 times cap, so the cap steers you to the equity-heavy designs, which are more concentrated. So 12% needs a real edge, and last year\'s record does not yet show one. That is why U18 starts with a 12-month probation.',B),
 P('Guard-rails (approved; the numbers can still be changed)',H2),
 bl('<b>Leverage:</b> gross exposure at most 1.5 times NAV. Keep IBKR excess liquidity above 40% of NAV at all times.'),
 bl('<b>Drawdown ladder:</b> down 15% from the peak, cut to 1.0 times. Down 25%, halve the risk. Down 30%, stop and review.'),
 bl('<b>Options:</b> only the whole-book hedge on page 8, with a cost of at most 2% of hedged value a year (about SGD 7.4k). No other option positions; no naked short options.'),
 bl('<b>Vehicles:</b> prefer index futures (micro E-mini or Nikkei and similar) over many single-name trades. U18 traded 40 symbols last year.'),
 bl('<b>Single position:</b> no more than 30% of the sleeve in one ETF. Bitcoin at most 5 to 10%.'),
 bl('<b>Turnover:</b> stocks and ETFs at most 2 times NAV a year (one side counted), reported quarterly.'),
 bl('<b>Review:</b> quarterly; cut or close if the net Sharpe ratio is below 0.3 after 12 months.'),
 P('I have not seen your IBKR margin rate. U18\'s net interest cost was SGD 1,479 last year. Please check the rate before using leverage.',Sm),PageBreak()]
# ===== 7 core =====
story+=[P('7. Core sleeve (U12, U15 and UOB): beating ALLW without copying it',H1),
 P(f'The core is U12 and U15 (SGD {(A.loc["A","end"]+A.loc["C","end"])/1000:,.0f}k) plus UOB (SGD {UOB_NAV/1000:,.0f}k). ALLW returned {fin["ALLW"]*100:+.1f}% over the last 12 months at 9.5% volatility. You approved the <b>vol-matched</b> scoreboard: compare the core\'s SGD return with ALLW scaled to the core\'s volatility (today a factor of about 0.7), after costs, over rolling 12 and 36 months. I would also show raw return against ALLW as a tougher second view. ALLW launched in March 2025, so only about 20 months are live; earlier figures are my component proxy.')]
fc=[['Core today (today\'s weights)','Core','ALLW','ALLW scaled to core volatility'],
 ['Ex-ante volatility',pct(Y['vcore']),'8.5%','6.1%'],
 ['2020-26 return a year (backcast)',pct(Y['core_cagr']),'8.8%','6.5%'],
 ['2020-26 volatility',pct(Y['core_vol']),'11.4%','8.3%'],
 ['Last 12 months, today\'s weights held throughout (hindsight)',pct(Y['core12']),pct(fin['ALLW']),'2.3%'],
 ['Last 12 months, U12 and U15 holdings today, held throughout (hindsight)','14.4%',pct(fin['ALLW']),''],
 ['Last 12 months, what U12 and U15 actually earned','U12: -2.1%, U15: +1.1% (IBKR)',pct(fin['ALLW']),''],
 ['31 Jan to 31 Oct, UOB actual','+2.7%','+1.5%','']]
story+=[tbl(fc,[62*mm,40*mm,26*mm,46*mm]),P('What you hold has been stronger than how it was traded: today\'s weights would have returned 13.0% for the whole core and 14.4% for U12 and U15, but the accounts earned -2.1% and +1.1%. The backcasts are hindsight and ALLW\'s pre-2025 figures are a proxy, so read them as direction, not proof.',Sm),
 P('How to run the core',H2),
 bl('<b>Follow the account rules</b> on page 5: U12 trades actively inside its limits, U15 stays passive, and neither holds options.'),
 bl('<b>Write a policy mix once</b> (for example by asset class, with a band around each) for U15 and rebalance only when a band is breached. This replaces the ad hoc trading that cost you last year.'),
 bl(f'<b>Put cash to work by rule.</b> U12 and U15 hold SGD {Y["cashAC"]/1000:,.0f}k of cash (6% of the core). Keep a buffer of 3 to 5% and invest the rest on a schedule.'),
 bl('<b>Where an edge could come from:</b> lower costs and turnover, and carry from equities, credit and Singapore assets that UOB holds. None of this is guaranteed, and some of last year\'s gains (oil, Singapore equity) will not repeat.'),
 bl('<b>Risk budget:</b> ex-ante volatility 7 to 9% and a worst-year drop of about 15%. Today is 6.4%.'),PageBreak()]
# ===== 8 hedge =====
story+=[P('8. Whole-book hedge: size and cost',H1),
 P('<b>What the hedge covers.</b> The whole book (IBKR and UOB, SGD 737k) rises and falls with US shares. Regressing today\'s weights on SPY (in SGD) gives a sensitivity of 0.45 in normal weeks and 0.54 in down weeks; in past crashes the book fell 40% to 65% as much as SPY (Covid 2020: book -18.9% against SPY -30.1%; 2022 first half: -8.4% against -20.6%; April 2025: -8.6% against -17.9%). The weekly correlation is 0.87, so SPY is a good, not perfect, hedge for a book holding Singapore shares and credit.'),
 P('<b>Sizing.</b> About 0.5 x SGD 737k = SGD 369k of equity-like exposure, or 3.75 SPY contracts at 767 and USDSGD 1.2815. I use 4 contracts (USD 307k of notional).'),
 P('<b>Live prices</b> (IBKR, 4 Nov 2026; SPY 767.02; options expire 19 Feb 2027, 107 days). I assume you pay the ask and receive the bid.')]
hr=[['Hedge (4 contracts)','Cost (SGD)','% of book','Cost a year if rolled','% of hedged value a year','Most it can pay (SGD)']]
for _,r in df.iterrows(): hr.append([r['name'],f'{r.cost_sgd:,.0f}',f'{r.cost_pct_book:.2f}%',f'{r.ann_pct_book:.1f}% of book',f'{r.ann_pct_hedged:.1f}%',('no cap' if r.max_sgd>150000 else f'{r.max_sgd:,.0f}')])
story+=[tbl(hr,[52*mm,20*mm,17*mm,26*mm,30*mm,29*mm]),P('Hedged value = SGD 369k. Your guard-rail is a cost of at most 2% of hedged value a year; only H2 fits. Rolled costs assume four three-month hedges a year and no payoff.',Sm),Image(OUT+'h_fig1.png',width=150*mm,height=75*mm)]
sc=[['SPY move','Book, no hedge','H1','H2','H3','H4']]
for r_,row in T.iterrows(): sc.append([f'{r_*100:+.0f}%']+[f'{row[c]/737469*100:+.1f}%' for c in ['Book unhedged','H1','H2','H3','H4']])
story+=[P('Whole-book result at expiry (including the cost of the hedge)',H2),tbl(sc,[30*mm,32*mm,24*mm,24*mm,24*mm,24*mm]),P('Book move is my approximation: 0.5 times the SPY move up to -20%, then steeper, matching the 2020 history. Results at expiry; before expiry the value is smoother because options keep time value.',Sm),PageBreak()]
# ===== 9 recommendation =====
story+=[P('9. Hedge recommendation and next steps',H1),
 P(f'<b>Base hedge: H2.</b> Buy 4 SPY 690 puts and sell 4 SPY 615 puts (19 Feb 2027). Net cost about USD {h2.cost_usd:,.0f} (SGD {h2.cost_sgd:,.0f}). It pays from a 10% fall in SPY to a 20% fall, up to about SGD {h2.max_sgd/1000:,.0f}k. The book loss in a 20% fall is about 5.1% against 10.0% unhedged. It fits your 2% budget (1.8% of hedged value a year).'),
 P('<b>Know the gaps.</b> The first 10% of a fall in SPY is unprotected (a book loss of about 5%), and below a 20% fall the protection stops growing. In a 30% crash the book loses about 12% against 17% unhedged.'),
 P(f'<b>Upgrades if your loss cap is stricter.</b> H3 (outright 690 put) keeps protecting in a crash (book -6.8% at SPY -30%, -8.5% at -40%) at SGD {h3.cost_sgd:,.0f} per three months, but at {h3.ann_pct_hedged:.1f}% of hedged value a year it breaks your budget. H4 (730/615) protects from -5% but costs {h4.ann_pct_book:.1f}% of the book a year.'),
 P('<b>Compare with simply holding less equity.</b> Selling about SGD 175k of equity (0.24 of book) cuts the 20%-fall loss by about SGD 35k, similar to H2. At an assumed 5% a year equity premium it gives up about SGD 8.8k a year, against about SGD 6.8k a year for H2 rolled. Selling protects in every scenario and size of fall; H2 is cheaper but protects only a band. Both are reasonable; the choice is yours.'),
 P('Running the hedge in U18',H2),
 bl('<b>Structure:</b> debit put spread, so the most you can lose is the premium and U18 needs no margin beyond it. U18 holds SGD 54.5k of cash.'),
 bl('<b>Roll</b> 30 to 45 days before expiry (mid-Jan 2027) and re-estimate the contract count each quarter.'),
 bl('<b>Budget:</b> at most 2% of hedged value a year (SGD 7.4k). Last year\'s option cost was SGD 20.8k (2.8% of the book).'),
 bl('<b>Scorecard each quarter:</b> premium paid, payoff, and book drawdown with and without the hedge (as in the table on page 3).'),
 bl('<b>Limits:</b> SPY does not track Singapore shares or credit exactly; the US dollar moves against the Singapore dollar; quotes change.'),
 P('Next steps',H2),
 tbl([['Step','Who'],['1. Choose the loss cap and the hedge (H2 or an upgrade)','You'],['2. Confirm the U12 and U15 rules (page 5) and decide how to deploy U18\'s cash','You'],['3. I re-quote the hedge on the day you want to trade and give exact contracts','Me'],['4. You place the order by hand in U18','You'],['5. I draft the U15 policy mix and the first quarterly scorecard for each sleeve','Me']],[130*mm,44*mm]),
 P('Nothing here requires an immediate trade. The only time-sensitive items are the hedge decision and the SGD 91.7k of idle cash.',Sm),PageBreak()]
# ===== 10 method =====
files=[glob.glob(f'/root/.claude/uploads/96af3fac-5838-5648-857b-e9dc3247b73e/*{m}_unittrust.pdf')[0] for m in ['202601','202603','202605','202607']]
rec={'record':'alloc review consolidated','status':'PROPOSED - hedge and rules not yet approved','as_of':'2026-11-04',
 'decisions':{'structure_and_guardrails':'approved','beat_ALLW':'vol-matched','U12':'active 1w-1m','U15':'passive >1m','hedge_scope':'whole book incl UOB, in U18'},
 'ibkr_year':{'pnl_sgd':round(float(tot.pl)),'twr_pct_my_calc':round(fin['IBKR combined (TWR)']*100,2),'ytd_twr_ibkr_app_pct':1.33,'ytd_twr_my_calc_pct':0.59,'bought_and_sold_sgd_excl_fx':round(GROSS),'one_side_vs_avg_capital':round(ONEWAY/AVGCAP,2),'year_file_sha256':hashlib.sha256(open(glob.glob('/root/.claude/uploads/96af3fac-5838-5648-857b-e9dc3247b73e/98429d35*')[0],'rb').read()).hexdigest()},
 'benchmarks_12m_pct':{k_:round(v*100,2) for k_,v in fin.items()},
 'uob':{'pnl_sgd_jan31_oct31':round(UP['tot_pl']),'return_pct':round((UP['cum']-1)*100,2),'buys_sgd':round(buys),'redemption_sgd':round(redeem),'statement_sha256':[hashlib.sha256(open(f,'rb').read()).hexdigest() for f in files]},
 'hedge_quotes_4Nov2026':{'underlying':'SPY 767.02','expiry':'2027-02-19','puts':{str(k_):list(v) for k_,v in HD['Q'].items()},'candidates':df[['name','cost_sgd','ann_pct_book','ann_pct_hedged','max_sgd']].round(2).to_dict(orient='records')},
 'recommendation':'H2: buy 4 SPY 690P, sell 4 SPY 615P (19 Feb 2027), in U18','input_hashes':FILEHASH}
js=json.dumps(rec,sort_keys=True,default=float,indent=1); H=hashlib.sha256(js.encode()).hexdigest()
open(OUT+'decision_record_consolidated.json','w',encoding='utf-8').write(js); open(OUT+'decision_record_consolidated.sha256','w').write(H+'\n')
story+=[P('10. Method, data and limits',H1),P('Data',H2),
 bl('IBKR Flex file (4 Nov 2025 to 3 Nov 2026) for all three accounts; UOB statements for Jan, Mar, May, Jul and Oct 2026 (other months rebuilt from unit balances and NAVs); Bloomberg and Yahoo series for risk and benchmarks; IBKR live quotes for SPY options (4 Nov 2026).'),
 bl('Benchmarks use total returns converted to SGD. Volatility: EWMA (decay 0.97) with Ledoit-Wolf correlation. UOB funds are modelled through ETF proxies (checked against the actual record on page 4). ALLW before March 2025 is a proxy (fit R-squared 0.88).'),
 P('Method',H2),
 bl('IBKR combined return from daily net asset value and dated deposits (internal transfers cancel); checked against the IBKR app (page 2). UOB: Modified Dietz per statement period, chained; dividend reinvestments count as return.'),
 bl('Holding periods: first-in, first-out matching of stock and ETF sales to earlier purchases in the same account. Hedge: sensitivity of today\'s weights to SPY in SGD (2020 to 2026); costs at ask for bought puts and bid for sold puts; results at expiry.'),
 P('Not covered',H2),
 bl('Return forecasts: none; no sleeve is ranked by expected return.'),
 bl('Tax beyond withholding, commissions on the options, UOB sales charges, bid-ask changes before you trade, and US estate tax on US-listed holdings (worth a separate check).'),
 bl('The hedge reduces drawdown risk, not expected loss: it costs money in most years and does not cover falls unrelated to SPY.'),
 bl('Per-instrument profit figures are IBKR\'s performance report and do not sum exactly to net profit; use them for ranking only.'),
 P(f'Decision record (proposed): SHA-256 <font face="Courier" size="7.5">{H}</font>. Statements and files are fingerprinted, not copied; account numbers are not stored.',Sm)]
def foot(c,d):
    c.saveState(); c.setFont('Helvetica',7.5); c.setFillColor(GREYT); c.drawString(18*mm,10*mm,'Rebalance review, consolidated - draft for owner decision. Not investment advice. No orders placed.'); c.drawRightString(192*mm,10*mm,f'Page {d.page}'); c.restoreState()
doc=SimpleDocTemplate(OUT+'Rebalance_Review_consolidated_2026-11-04.pdf',pagesize=A4,leftMargin=18*mm,rightMargin=18*mm,topMargin=16*mm,bottomMargin=18*mm,title='Rebalance review: consolidated',author='CTO office')
doc.build(story,onFirstPage=foot,onLaterPages=foot); print('ok',H)
