# Finkow — Web Frontend

Next.js (App Router) frontend for **Finkow**, the open-source AI-native
financial learning sandbox. English-first UI, dark OLED fintech dashboard,
gold (`#F59E0B`) brand accent.

## Pages

- `/` — Dashboard: portfolio value (gold hero stat), total return + cash,
  allocation bars, positions table, "Ask about your portfolio" AI panel, and
  quick asset shortcuts (AAPL, MSFT, BTC, ETH).
- `/assets/[symbol]` — Asset inspector: live quote card (price, provider,
  as-of, stale badge), buy/sell form with estimated-cost preview, your current
  position, and recent trades for the symbol.

On first load the app creates a sandbox account (`POST /api/accounts`,
$100,000 virtual cash) and persists the `account_id` in `localStorage` so
later visits reuse it. If the API is unreachable, every page shows an honest
error state with a retry button — nothing is faked.

## Money handling

The API sends **all money as decimal strings**. The frontend never does
money math: `src/lib/format.ts` only formats strings for display
(`Intl.NumberFormat`, USD), and `src/lib/order.ts` only validates the
quantity input.

## Run it

```bash
npm install
npm run dev        # http://localhost:3000
```

Point at a different backend with:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

## Quality gates

```bash
npm test           # unit tests (node:test, zero deps)
npm run lint       # Biome check — must be clean
npm run build      # Next.js production build — must pass with zero errors
```

## Layout

```
src/
  app/
    page.tsx                 # dashboard route
    assets/[symbol]/page.tsx  # asset inspector route
    layout.tsx               # header, footer, metadata
    globals.css              # design tokens (dark OLED, IBM Plex Sans)
  components/
    dashboard.tsx            # dashboard client components
    inspector.tsx            # asset inspector client components
    ui.tsx                   # shared primitives (cards, buttons, badges, states)
  lib/
    api.ts                   # typed FastAPI client + account bootstrap
    format.ts                # display-only money formatting
    order.ts                 # quantity validation
    *.test.ts                # unit tests
```
