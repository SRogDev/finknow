# finknow — Build Plan

> MVP target: functional in days. Each phase ships something usable.

## Proposed stack (to confirm)

- **App**: Next.js (App Router) + Tailwind + shadcn/ui
- **DB/Auth**: Supabase (Postgres + Auth)
- **AI**: OpenRouter (mid-tier models; finance reasoning doesn't need the frontier)
- **Integrations**: Composio (bank/broker/crypto connections)
- **Investing**: Alpaca (stocks, paper trading first) — Stripe is for payments, not investing
- **Design**: Swiss-minimalist, gold `#F59E0B` on deep dark (`#0F172A`)

## Phase 1 — See your money (days 1–3)

- Auth + workspace (Supabase)
- Connect first account via Composio (Plaid for banks — to confirm)
- Unified dashboard: balances, accounts, simple net-worth view
- Manual account/asset entry as fallback

## Phase 2 — AI guide (days 4–6)

- "Explain my money": AI summary of accounts, cash flow, fees
- Opportunity scanner (rules first): idle cash, high fees, yield gaps
- Teach mode: every insight links to a plain-language explanation

## Phase 3 — AI actions with permissions (week 2)

- Permission model: read-only → suggest → act-with-approval → autonomous (per-action caps)
- Paper-trading sandbox via Alpaca (prove it before real money)
- Real investing behind explicit per-action approval + full audit log

## Open questions (for Roger)

- [ ] Bank connections: Plaid via Composio, or which first?
- [ ] Crypto in v1 or later?
- [ ] Language: English-first like Agentropy?
- [ ] Monetization of hosted version (Polar subscriptions?) or pure OSS?
- [ ] Which AI actions should exist in v1 (rebalance? sweep idle cash?)?

## Non-goals for MVP

- Tax optimization engine, multi-currency accounting, mobile app.
