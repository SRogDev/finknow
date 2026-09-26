# Finkow — Build Plan

> Spec: `docs/product-context.md`. Stack: Next.js + FastAPI + Supabase + OpenRouter.
> MVP proves: "Can a person develop financial intuition by interacting with a realistic financial sandbox through AI?"

## Confirmed decisions (2026-09-26)

- **Architecture**: Next.js frontend → **FastAPI backend** (financial domain logic) → Supabase (Postgres + Auth)
- **AI**: OpenRouter; AI calls **structured financial operations**, never mutates DB directly
- **Market data**: real data, keyless providers first (e.g. Stooq for stocks, CoinGecko for crypto) behind a provider abstraction; Alpaca paper-trading later
- **Money**: 100% virtual in MVP. Real-money mode is a future phase.
- **Language**: English-first
- **License**: MIT (open source)
- **Brand**: gold `#F59E0B` on deep dark, Swiss-minimalist (see ui-ux-pro-max design system)

## Phase 1 — Sandbox core (MVP)

- [ ] Supabase schema: users, sandbox_accounts, positions, transactions, portfolio_snapshots
- [ ] FastAPI: `create_account`, `get_quote(symbol)`, `buy`/`sell` (virtual), `get_portfolio`, `get_history`
- [ ] Market data providers: stocks + crypto, with caching; graceful degradation when offline
- [ ] Next.js: dashboard (portfolio, positions, allocation), asset inspector, buy/sell UI
- [ ] Virtual cash: $100,000 on signup; transaction ledger; portfolio valuation over time
- [ ] Tests: financial math (P&L, allocation, returns) — pytest, no float-money bugs

## Phase 2 — AI interface

- [ ] OpenRouter chat wired to structured ops (get_portfolio, get_quote, simulate, explain)
- [ ] "What happened?" — AI explains portfolio changes from real market movement
- [ ] "What if I invest X?" — simulation without executing
- [ ] Contextual teaching: concepts explained from the user's own actions

## Phase 3 — Opportunities + scenarios (post-MVP)

- [ ] Opportunity scanner (rules first, AI explanation)
- [ ] Scenario engine: crash, inflation, boom, rate shock…

## Explicitly NOT in MVP

Real-money accounts, real execution, compliance infra, every instrument/exchange,
curriculum-style lessons, advertising.

## Open questions (for Roger)

- [ ] Product name spelling: **Finkow** (doc) vs **finknow** (repo)?
- [ ] Confirm MIT license for finknow?
