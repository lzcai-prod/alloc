# Plan v2: auto-run first

The two earlier attempts failed because automation came last. In v2 the scheduled, unattended run is the first deliverable, and nothing is added until the previous stage has run on its own. This plan replaces the v1 design; v1 stays as reference.

## Five rules

1. **Auto-run before features.** Each stage ships as a scheduled job. A stage passes only after a set number of consecutive scheduled runs succeed with no human touch.
2. **Cloud runs everything scheduled; the Dell is optional.** No scheduled job depends on the Dell or on remote control of it.
3. **Standard tools only.** No in-house framework. Every run stores the code commit, the data hash, the executed notebook and the PDF, so a third party can re-run it.
4. **AI-independent.** The system produces identical outputs with no AI involvement. AI enters only through an input table that you approve.
5. **PDF out, status page in.** Reports are PDFs. Job status is a hosted dashboard, not something you build.

## Stack

| Need | Tool | Cost |
| --- | --- | --- |
| Scheduler and runner | GitHub Actions cron, private repo | Free tier |
| System of record | Neon Postgres | Free tier |
| Analysis | pandas, statsmodels, arch, scikit-learn, skfolio | Free |
| Reports | Jupyter notebooks run by papermill, rendered to PDF by Quarto (Typst, no LaTeX) | Free |
| Job status WebUI | healthchecks.io Hobbyist: dashboard of every job, Telegram alerts on missed or failed runs | Free (20 jobs) |
| Delivery | Existing Telegram bot sends each PDF; PDFs archived in object storage | Free |
| Positions | IBKR Flex Web Service (read-only, token over HTTPS, no gateway) | Free |

healthchecks.io's free plan monitors 20 jobs and keeps 100 log entries per job ([pricing](https://healthchecks.io/pricing)), which is enough for this system.

## Data sources

Total recurring cost: about USD 22 a month, well under the USD 100 budget.

| Data | Source | Cost | Automation |
| --- | --- | --- | --- |
| US ETF and stock EOD, dividend-adjusted | Tiingo | Free tier (1,000 requests a day, 500 symbols a month); Power USD 30 if outgrown | API, daily job |
| SGX ETFs (ES3, A35) and backup FX | EODHD EOD All World | About EUR 20 a month | API, daily job |
| USDSGD daily | FRED series DEXSIUS | Free | API |
| Macro data with real-time vintages | FRED and ALFRED | Free | API |
| Factor returns (FF5, momentum, daily) | Ken French data library | Free | pandas-datareader |
| VIX, VIX3M | Cboe historical CSVs | Free | HTTP download |
| SGD rates, SGS T-bills | MAS statistics | Free | API or CSV |
| Public nowcasts | Atlanta Fed GDPNow, NY Fed Staff Nowcast, Cleveland Fed inflation nowcast, Philadelphia Fed ADS index, NY Fed Weekly Economic Index | Free | HTTP download |
| Positions | IBKR Flex Web Service | Free | API |
| CRSP, Compustat (optional) | WRDS via the `wrds` Python package, run weekly from the Dell | Duke access | Scheduled on the Dell |
| Bloomberg (optional) | Library terminal, one prebuilt Excel workbook | Duke access | One macro button |

**WRDS.** The WRDS Python module needs a Duo approval per connection, but the MFA session is kept for up to 30 days as long as your IP address stays the same ([WRDS MFA guide](https://wrds-www.wharton.upenn.edu/pages/about/log-in-to-wrds-using-two-factor-authentication/)). That rules out GitHub Actions (new IP every run) but suits the Dell on your home connection: approve once a month, and the weekly pull runs unattended. Nothing in the core plan needs WRDS; it is for research only.

**Bloomberg.** Keep one workbook of BDH formulas for the series you cannot get free. A single macro button refreshes it and saves CSVs to a USB stick or a synced folder; at home, the `ingest-bbg` job loads whatever new files it finds. Expect to need this rarely, if at all.

## Stages

No calendar. A stage is done when its gate is met, and the gate is measured by the scheduled runs themselves, not claimed by the coding agent.

| Stage | What gets built | Gate to move on |
| --- | --- | --- |
| 0 Heartbeat | Repo, one daily workflow, Neon tables, one job that fetches SPY and USDSGD, writes to Neon, renders a one-page PDF, sends it to Telegram, pings healthchecks | 7 consecutive scheduled runs succeed with no commits in between |
| 1 Data | All free sources above into Neon, with schema and range checks (pandera); a failed check fails the run loudly | 10 consecutive green scheduled runs |
| 2 Weekly econometrics brief | The educational PDF (next section) | 3 weekly PDFs delivered on schedule |
| 3 Rebalance proposal | Weekly PDF: positions from Flex, current risk, ERC targets at the vol target, trade list with 2 pp bands, hashed decision record. You approve with a GitHub "approve-decision" button; trades stay manual | One proposal approved, executed and logged |
| 4 Forecast and scoring | Monthly bands for the book, ALLW, SPY and QQQ in SGD at matched vol; scoring of past records | 2 monthly records frozen and scored on schedule |
| 5 Research track | Nowcasting and Hong-Yun (below), separate from the allocation jobs | Per model: passes out-of-sample tests before its output is used |
| 6 AI inputs | The approved-input table and desktop workflow (below) | Optional; the system is complete without it |

## Weekly econometrics brief

This PDF is the basis for judging whether a rebalance proposal makes sense. Every chart comes with a short plain-language note generated from fixed templates, so the explanation is reproducible and contains no AI text.

- **What is driving returns:** each holding's proxy regressed on Fama-French five factors plus momentum, with Newey-West standard errors; rolling 1-year betas.
- **Risk now vs normal:** GARCH and HAR volatility forecasts with bands; correlation regime; each bucket's share of total risk in SGD.
- **FX:** the USDSGD contribution to SGD returns, split into local return, FX and cross term.
- **Rotation:** sector and region relative strength, breadth and dispersion, with the regime read on growth and inflation axes.
- **Macro:** your nowcasts next to the public nowcasts and the latest releases.
- **Valuation:** status of the cointegration and error-correction test for the SPX fair-value relation.
- **Appendix:** methods, sample windows and library versions used, so a reader can reproduce every number.

## Neon record standard

Neon is the single source of truth for both the running system and the build history, so any session, human or agent, starts from the same facts.

| Table | One row per | Key columns |
| --- | --- | --- |
| `jobs` | Job definition | name, schedule, healthcheck URL, owner stage |
| `runs` | Job execution | job, started, finished, status, git SHA, data hash, PDF link, error |
| `datasets` | Data pull | source, as-of date, rows, SHA-256 |
| `decisions` | Rebalance proposal | inputs hash, targets, trades, status (proposed, approved, rejected, executed) |
| `forecasts` | Monthly record | quantiles, probabilities, hash, published time |
| `ai_inputs` | AI contribution | kind, JSON payload, rationale, source, status (pending, approved, rejected) |
| `stage_log` | Build session | stage, change made, files, commit, gate progress, open problems, next step |

All tables are append-only, except the status column on `decisions` and `ai_inputs`. A `docs/STATE.md` file is regenerated from `stage_log` on every run, so a coding agent can read the state without database access.

## The Dell

Take the Dell off the critical path instead of trying to control it remotely.

- **Use it only for:** the weekly WRDS pull, heavy research runs, and the Claude desktop app.
- **It schedules itself:** its own OS scheduler (systemd timer or Windows Task Scheduler) runs its jobs. No remote session needs to start anything.
- **It reports itself:** every Dell job pings healthchecks.io like the cloud jobs, so an outage shows on the same status page and alerts you on Telegram.
- **It recovers itself:** set the BIOS to power on after power loss, and schedule OS updates for a fixed weekly window.
- **Remote access** goes through Tailscale SSH or remote desktop for maintenance, not through Claude Code remote control.

If the Dell is off for a week, every scheduled report still arrives; only WRDS refreshes wait.

## AI as an input, through the desktop app

AI work happens interactively in the Claude desktop app on your monthly subscription, with the Neon connector. Nothing in the pipeline calls an AI API.

- **AI reads:** `runs`, `decisions`, `forecasts`, `datasets` and the PDFs, through the Neon connector or by attaching the PDF.
- **AI writes:** only rows in `ai_inputs`, in a fixed JSON schema. Kinds: a view on an asset (direction, size cap, expiry, rationale), a note on a report, a proposed playbook rule, or a coding task.
- **You approve:** with the same GitHub approve button. Pending inputs are ignored by every job.
- **Audit:** an approved input's hash is stored in the decision record that used it. Rerun the decision without it to measure what the AI changed.

The Neon connector acts with your account's permissions, so the protection is the approval step and the append-only rule, not a database role.

## Nowcasting research, built the Hong-Yun way

Hong-Yun's advantage is daily proprietary data used as an early read on macro releases. You can build the same process with public data, and it should run as its own research track.

1. **Targets:** CPI, core PCE, payrolls, ISM, retail sales and claims, using ALFRED first-release values and release dates.
2. **Daily and weekly proxies:** breakevens, the yield curve, oil, copper/gold, credit spreads and sector ratios from markets; claims, EIA gasoline prices, the Weekly Economic Index and the ADS index from public sources.
3. **As-of panel:** for each release date, keep only data available the day before. Store it in Neon so every test is pseudo-real-time.
4. **Models:** bridge regressions, MIDAS, and the mixed-frequency dynamic factor model in statsmodels (DynamicFactorMQ).
5. **Evaluation:** nowcast error against the first release; compare with the public nowcasts. The useful output is the predicted surprise, release minus consensus or prior.
6. **Use:** only a model that beats the public nowcasts out of sample publishes into a `signals` table, which the allocation may use after your approval.

**Keep it independent.** It runs as a separate job with its own gate and writes only to `signals`. Then it cannot leak look-ahead into allocation tests, it can fail without stopping the reports, and you can measure its value by comparing decisions with and without it. The public nowcasts already approximate some of Hong-Yun's proprietary edge, so they are both your free input and the benchmark to beat.

## Prompt for the coding agent

Paste this into Claude Code to build Stage 0. For later stages, reuse it and replace the Stage 0 block with the next stage's row from the table above.

```text
ROLE
You are the build engineer for "alloc", an automated SGD asset-allocation reporting system. You build one stage at a time. Its most important property is that it runs unattended on schedule.

START OF EVERY SESSION
1. Read docs/PLAN.md (the design; do not change it without my approval), then docs/STATE.md and the latest 20 rows of the Neon table stage_log. PLAN.md says what to build; stage_log says what is done.
2. Work only on the current stage. Do not start the next one until stage_log shows its gate met.

END OF EVERY SESSION
Append one row to stage_log: stage, what changed, files touched, commit SHA, gate progress, open problems, next step. Regenerate docs/STATE.md and commit it.

HARD RULES
- Standard, widely used libraries only: pandas, numpy, statsmodels, arch, scikit-learn, skfolio, pandera, papermill, Quarto, psycopg, requests. No custom frameworks, ORMs or plugin systems. If you need anything else, stop and ask.
- One entry point: python -m alloc <job>. Every job pings healthchecks at start, does its work, writes one row to runs, then pings success or failure with the error text. No job may fail silently.
- Every run records the git SHA, the SHA-256 of its input data, and the uv.lock hash.
- Secrets come only from environment variables (GitHub Actions secrets). Never print or log them.
- Tables are append-only. No UPDATE or DELETE except the status column of decisions and ai_inputs.
- Outputs must be identical when ai_inputs is empty.
- Nothing places orders. IBKR access is read-only Flex Web Service.
- Build nothing outside the current stage. The simplest thing that runs on schedule wins.

STAGE 0: HEARTBEAT (build now)
Goal: one job that runs every weekday after the US close with no human touch.
- Private GitHub repo alloc, Python 3.12, uv lockfile.
- Neon tables jobs, runs, stage_log, created by a migration in db/migrations/.
- Job heartbeat: fetch SPY adjusted close from Tiingo and USDSGD from FRED (DEXSIUS), compute the SPY return in SGD, write it to Neon, execute notebooks/heartbeat.ipynb with papermill, render it to PDF with Quarto (Typst), send the PDF to my Telegram chat, ping healthchecks.io.
- Workflow .github/workflows/daily.yml: cron 30 22 * * 1-5 plus workflow_dispatch; one retry on network errors; upload the PDF and executed notebook as run artifacts.
- docs/RUNBOOK.md: how to rerun a job, how to read a failure, which secrets exist and where.
Gate, measured by the job itself: 7 consecutive scheduled runs with status success in runs and no commits to .github/ or alloc/ in that window. The job writes the gate count to stage_log each day.

LATER STAGES (context only, do not build)
1 Data from all sources with pandera checks. 2 Weekly econometrics PDF. 3 Weekly rebalance proposal PDF and approve-decision workflow. 4 Monthly forecasts and scoring vs ALLW, SPY and QQQ in SGD. 5 Nowcasting research track writing to signals. 6 ai_inputs workflow.

FIRST REPLY
Before writing code, reply with the file tree, db/migrations/001.sql, and the exact list of secrets I must add. Then wait for my go.
```
