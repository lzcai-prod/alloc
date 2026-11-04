# 0010 — alloc: growth sleeve, active and passive accounts, whole-book hedge

Date: 2026-11-04 · Status: items 1-4 **accepted (owner)**; items 5-6 **proposed**, owner decision pending · Refines `projects/alloc/PLAN_v2.md`

## Decision
Accepted by the owner on 2026-11-04:
1. **Structure.** Three IBKR accounts plus UOB, labelled by short ID (never full account numbers): **U18** growth sleeve (derivatives and margin allowed), **U12** active (hold 1 week to 1 month), **U15** passive (hold over 1 month), **UOB** unit trusts. Core = U12 + U15 + UOB.
2. **U18 guard-rails.** Gross leverage at most 1.5 times NAV; IBKR excess liquidity above 40% of NAV; drawdown ladder (-15% cut to 1.0 times, -25% halve, -30% stop and review); no naked short options; at most 30% of the sleeve in one ETF; Bitcoin at most 5-10%; stock and ETF turnover at most 2 times NAV a year (one side counted); 12-month probation, close or cut if net Sharpe below 0.3. U18 stays at or below about 15% of the book.
3. **Scoreboard.** "Beat ALLW" means **vol-matched**: core SGD return against ALLW scaled to the core's volatility, after costs, over rolling 12 and 36 months. Raw return is shown as a second view. The core does not copy ALLW (no tracking-error limit).
4. **Option hedge scope.** One hedge for the **whole book including UOB**, held in U18. Hedge cost at most 2% of hedged value a year.

Proposed, not yet decided:
5. **Hedge choice and loss cap.** Proposal: cap the book loss at about 6% if SPY falls 20% over three months, using H2 (buy 4 SPY 690 puts, sell 4 SPY 615 puts, expiry 2027-02-19, about SGD 2.0k, about 0.9% of the book a year if rolled). Upgrades (H3 outright put, H4 wider spread) exceed the 2% budget or cost more.
6. **Account rules.** U12: review at 30 days, stop -10% from entry, at most 15% of U12 in one name, U12 at most 20% of the book, turnover at most 6 times NAV one side. U15: hold at least 30 days, rebalance by bands, turnover at most 1 time NAV. No options in U12 or U15.

## Why
- IBKR returned about -3.5% to -2.7% over 4 Nov 2025 to 3 Nov 2026 (loss SGD 11.1k; calibrated to the IBKR app's +1.33% YTD) against ALLW +3.0%, SPY +9.6%. Realised option P&L was -20.8k; without it about +1.7%. UOB returned about +2.7% from 31 Jan to 31 Oct 2026 (+SGD 6.6k). The book grew from about SGD 305k to 737k through about SGD 435k of new money.
- A 16% volatility book is not reachable without leverage (UOB fixed and low-risk; a mechanical equal-risk-contribution allocation was unstable and gave 6-7% volatility). Putting the 12% target in one account where leverage is allowed removes that limit. 12% compound needs a Sharpe near 0.7 at 16% volatility, which last year's record does not show, hence the probation.
- The book moves about 0.5 times with SPY (0.45 normal weeks, 0.54 down weeks), so about 4 SPY puts' worth of cover.

## Consequences
- Analysis lives in `projects/alloc/` (status, plan, data, decision record). Scripts are not stored here (no application code in this repo); they go to the `alloc` repo once the owner creates it.
- Neon: a separate project `alloc` (`lively-dust-00487949`) holds the schema and data (owner asked for a new db). Role `alloc_app` needs its password set by the owner.
- Nothing was traded. The owner places any hedge or trade by hand after the CTO re-quotes on the day.
- Corrections recorded: turnover is about 3.3 times average capital, one side (an earlier 7.3 counted both sides and currency conversions); UOB was not a fixed SGD 300k (it grew from 96k through 212k of purchases).
