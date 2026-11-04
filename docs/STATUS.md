# alloc: status

Repo: `lzcai-prod/alloc` (this repo, created 2026-11-04). Database: Neon project `alloc` (id `lively-dust-00487949`, branch production, database `alloc`, schema `alloc`) · Updated 2026-11-04 · Session `session_01MbUEGfYvwX97CWnHF8dEkA`, branch `claude/plan-review-kyhzxl`
Plan: `PLAN_v2.md` (v1 kept as reference). Decision: `decisions/0010-alloc-two-sleeves-and-hedge.md`.

## What it is
Allocation of the owner's whole SGD book (3 IBKR accounts + UOB unit trusts): two sleeves, a vol-matched ALLW scoreboard, and a whole-book option hedge. PLAN_v2 Stage 0 (daily heartbeat job) is still not built; this work was an interactive review.

## State (2026-11-04)
- Labels: **U18** growth sleeve, **U12** active, **U15** passive, **UOB**. Use these, never full account numbers.
- Book about SGD 737k: U12 126k, U15 222k, U18 90k (61% cash), UOB 300k. IBKR idle cash SGD 91.7k.
- IBKR 12 months (4 Nov 2025 to 3 Nov 2026): loss SGD 11.1k; return -3.5% (own calc) to -2.7% (app-calibrated). ALLW +3.0%, SPY +9.6%, 60/40 +5.1%.
- Realised option P&L -20.8k (U18 -15.4k, U12 -5.4k); without it about +1.7%. Trading about 3.3 times average capital (one side, excluding FX).
- UOB 31 Jan to 31 Oct 2026: +2.7%, +SGD 6.6k, on SGD 212k of purchases and one SGD 14.7k redemption (Fidelity US Dollar Bond fund, Aug to Sep).
- Holding periods: U12 median 31 days; U15 median 102 days with 19% of sold value sold within 30 days.
- Hedge priced live (SPY 767.02, expiry 2027-02-19): H2 690/615 put spread about SGD 2.0k. Nothing placed.

## Open (owner)
1. Hedge: **approved 2026-11-04** (loss cap about 6% at SPY -20%; H2 690/615 put spread). Not placed; CTO re-quotes on the day, owner places by hand.
2. U12/U15 rules: **approved 2026-11-04**. Proposed, awaiting the owner: allocation for U12 and U15 (`docs/ALLOCATION_PROPOSAL_2026-11-04.md`), U18 cash plan (keep about SGD 8k, three tranches), open decision A (core risk budget 7-9% vs about 6% reached; recommend 6-8%), open decision B (QQQ is 39% of U18 against a 30% single-ETF limit: trim about SGD 6.6k, or raise the limit to 40% for broad index ETFs).
3. Set the password for Neon role `alloc_app` in the console; set `main` as the default branch of this repo (first push went to the session branch).
4. Send UOB statements for Nov and Dec 2025 (and Feb, Apr, Jun, Aug, Sep) to complete the UOB record; check the IBKR margin rate for U18.

## Next (CTO)
- Re-quote the hedge on the day the owner wants to trade; give exact contracts.
- Draft the U15 policy mix (asset-class bands) and the first quarterly scorecard per sleeve.
- Turn `analysis/` into a tested package when PLAN v2 Stage 1 starts; keep Neon `alloc` current.
- PLAN_v2 Stage 0 still open. Known fixes before building: use a daily-updating USDSGD source (FRED DEXSIUS is weekly), handle US holidays as success-with-skip, gate definition with a tolerance.

## Files
- `data/*.csv`, `uob_month_end_units.csv`, `uob_flows_inferred.csv`, `holding_periods.csv`, `hedge_quotes_2026-11-04.csv`, `hedge_candidates_2026-11-04.csv`: distilled results (no account numbers, no positions list).
- `decision_record_2026-11-04.json` and `.sha256`: hashed record of inputs and results (hashes only for source files).
- `db/schema.sql` and `db/load_alloc_data.sql`: schema and load statements, APPLIED 2026-11-04 to the Neon project `alloc` (counts verified: 6 decisions, 8 performance periods, 101 UOB unit rows, 18 inferred flows, 3 holding-period rows, 5 quotes, 4 hedge candidates, 1 note; append-only trigger tested).
- The 10-page report (PDF) was given to the owner in chat; it is not stored here (personal portfolio detail; archive on the owner's side).

## Method and limits
- Returns in SGD. Volatility: EWMA (0.97) with Ledoit-Wolf correlation. UOB funds via ETF proxies, checked against actual (right direction, about 3 points high over 9 months). ALLW before March 2025 is a component proxy (R-squared 0.88). IBKR combined return from daily NAV and dated deposits; checked against the app.
- Not covered: tax beyond withholding, option commissions, UOB sales charges, US estate tax on US-listed ETFs for non-US persons (worth a separate check), margin rate.
