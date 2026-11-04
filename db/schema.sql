-- alloc schema: APPLIED 2026-11-04 to the SEPARATE Neon project `alloc` (id lively-dust-00487949), branch production (br-bitter-paper-bdnk7r2n), database alloc.
-- Owner asked for a new repo and db for alloc, so nothing was written to LzCai_AgentDB.
-- The role alloc_app has no password yet: the owner sets it in the Neon console (never in git).
-- Data loaded from data/*.csv (see data/load_alloc_data.sql).

create schema if not exists alloc;

create table alloc.decisions (
  id serial primary key,
  decided_on date not null,
  key text not null,
  title text not null,
  status text not null check (status in ('proposed','approved','rejected','superseded')),
  detail text,
  repo_ref text,                                  -- e.g. decisions/0010-alloc-two-sleeves-and-hedge.md
  created_at timestamptz not null default now()
);

create table alloc.performance_periods (           -- loads data/performance_periods.csv
  id serial primary key,
  label text not null,                             -- U12, U15, U18, UOB, IBKR combined (short labels only)
  period_start date, period_end date,
  start_value_sgd numeric(14,2), new_money_sgd numeric(14,2), end_value_sgd numeric(14,2), pnl_sgd numeric(14,2),
  return_pct numeric(8,3), method text, source text,
  created_at timestamptz not null default now()
);

create table alloc.uob_month_end_units (           -- loads data/uob_month_end_units.csv
  month_end text not null, fund text not null, currency text not null,
  units numeric(18,6) not null, nav numeric(12,4), source text,
  primary key (month_end, fund)
);

create table alloc.uob_flows_inferred (            -- loads data/uob_flows_inferred.csv
  id serial primary key,
  period_start text, period_end text, fund text, units_delta numeric(18,6), amount_sgd numeric(14,2),
  kind text check (kind in ('purchase','redemption')), method text
);

create table alloc.holding_periods (               -- loads data/holding_periods.csv
  id serial primary key,
  as_of date not null default date '2026-11-03', label text not null,
  sold_value_matched_sgd numeric(14,2), median_hold_days int,
  pct_7d_or_less int, pct_8_30d int, pct_31_90d int, pct_over_90d int, method text
);

create table alloc.hedge_quotes (                  -- loads data/hedge_quotes_2026-11-04.csv
  quoted_on date not null, underlying text not null, spot numeric(10,2), expiry date not null,
  strike numeric(10,2) not null, "right" text not null check ("right" in ('P','C')),
  bid numeric(10,4), ask numeric(10,4), implied_vol numeric(8,4), source text,
  primary key (quoted_on, underlying, expiry, strike, "right")
);

create table alloc.hedge_candidates (              -- loads data/hedge_candidates_2026-11-04.csv
  id serial primary key,
  quoted_on date not null default date '2026-11-04', name text not null, contracts int,
  cost_usd numeric(12,2), cost_sgd numeric(12,2), cost_pct_book numeric(8,3),
  ann_pct_book numeric(8,3), ann_pct_hedged numeric(8,3), max_payoff_sgd numeric(14,2), status text
);

create table alloc.notes (                         -- run notes, open questions (same idea as recruit.notes)
  id serial primary key,
  created_at timestamptz not null default now(),
  session text, topic text, body text not null
);

-- Append-only: block UPDATE/DELETE on everything except decisions.status, even for the owner role.
create or replace function alloc.block_mutation() returns trigger language plpgsql as $$
begin raise exception 'alloc.% is append-only', tg_table_name; end $$;
do $$
declare t text;
begin
  foreach t in array array['performance_periods','uob_month_end_units','uob_flows_inferred','holding_periods','hedge_quotes','hedge_candidates','notes'] loop
    execute format('create trigger %I_append_only before update or delete on alloc.%I for each row execute function alloc.block_mutation()', t, t);
  end loop;
end $$;

-- Scoped role (owner sets the password in the Neon console; never in git).
create role alloc_app login;
grant usage on schema alloc to alloc_app;
grant select, insert on all tables in schema alloc to alloc_app;
grant usage on all sequences in schema alloc to alloc_app;
grant update (status) on alloc.decisions to alloc_app;
-- no DELETE anywhere; no access to other schemas.
