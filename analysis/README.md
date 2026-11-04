# analysis

Exploratory scripts used for the 2026-11-04 review. They are path-dependent and need private inputs that are not in git:
- Bloomberg CSV pulls (`build_bbg*.py` in `bloomberg/` build the Excel workbooks that produced them),
- the IBKR Flex file (4 Nov 2025 to 3 Nov 2026) and a local `account_map.json` (never committed),
- UOB statements (their units and NAVs are typed into `uob_hist.py`).

Order: `data.py` (series) -> `model.py` (risk model) -> `year.py`, `year2.py`, `year3.py` (IBKR record) -> `uob_hist.py`, `uob_perf.py` -> `holding_periods.py`, `turnover_audit.py` -> `hedge.py` (needs live option quotes), `book_beta.py`, `sleeves.py` -> `pdf_all.py` (report). `opt.py` and `grid.py` are the equal-risk-contribution experiments (found unstable; see docs).

These should be turned into a tested package when PLAN v2 Stage 1 starts.
