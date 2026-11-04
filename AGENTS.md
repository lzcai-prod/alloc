# alloc

Allocation and review of the owner's whole SGD book: three IBKR accounts (**U12**, **U15**, **U18**) plus UOB unit trusts. Coordinated from `lzcai-prod/CTO_Office` (read its `AGENTS.md` and `decisions/0010-alloc-two-sleeves-and-hedge.md` first).

## Read first
1. `docs/PLAN.md` (PLAN v2: auto-run first; v1 is reference only).
2. `docs/STATUS.md` (current state and open decisions) and `docs/DECISION_0010.md`.

## Rules
- Account labels are **U12** (active, hold 1 week to 1 month), **U15** (passive, over 1 month), **U18** (growth sleeve, margin and derivatives allowed). **Never write full account numbers**, names, addresses or raw statements anywhere in this repo.
- **Never place orders** or send anything that moves money. The owner places trades by hand after the CTO re-quotes. Option hedge: proposed only (see decision 0010).
- No secrets in git. Inputs (Flex files, UOB PDFs, Bloomberg CSVs) stay out of git (see `.gitignore`); only distilled results go in `data/`.
- Write files as UTF-8. Keep tasks PR-sized; one branch and PR per task; the owner merges.
- Neon: project `alloc` (id `lively-dust-00487949`), database `alloc`, schema `alloc`, tables are append-only (decisions.status is the only editable column). Use the scoped role `alloc_app`, never the owner role, from jobs. The owner sets its password.
- Ask the owner before: any trade or hedge placement, deleting data, changing guard-rails (decision 0010), or sending messages.
