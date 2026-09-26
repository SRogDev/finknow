# Finkow API

FastAPI backend for the Finkow virtual-money investing sandbox (Phase 1).

## Layout

```
api/
  app/
    main.py      # routes: accounts, quotes, orders, portfolio, history, ai/explain
    market.py    # provider abstraction: Stooq (stocks/ETFs), CoinGecko (crypto)
    portfolio.py # valuation, P&L, allocation, returns — Decimal-exact
    store.py     # domain records + Store protocol (in-memory impl for the scaffold)
    ai.py        # grounded explain stub (OpenRouter polish optional)
    money.py     # Decimal helpers — no float money, ever
  tests/         # pytest: money math, portfolio math, market providers, API flow
```

## Run

```bash
python3 -m venv .venv && .venv/bin/pip install fastapi "uvicorn[standard]" httpx pytest ruff
.venv/bin/python -m pytest            # 25 tests
.venv/bin/ruff check app tests        # lint
.venv/bin/uvicorn app.main:app --reload --port 8000
```

The frontend calls the API directly from the browser, so the server emits
CORS headers. Defaults allow `http://localhost:3000` and
`http://127.0.0.1:3000`; override in production with a comma-separated list:

```bash
FINKOW_CORS_ORIGINS=https://finkow.example.com .venv/bin/uvicorn app.main:app --port 8000
```

## Design notes

- **Money is exact**: `Decimal` everywhere, quantized at boundaries (`money.py`).
  Tests in `tests/test_money.py` guard against float-money regressions.
- **Market data**: keyless providers (Stooq, CoinGecko) behind `CachedMarketData`
  (60s TTL). Offline → last-known quote marked `stale: true`; 503 only when there
  is nothing cached.
- **Storage**: `InMemoryStore` implements the `Store` protocol for the scaffold;
  `supabase/schema.sql` is the Postgres target. Domain code never touches storage
  details — swap the adapter in Phase 2.
- **AI**: `POST /api/ai/explain` returns a deterministic grounded summary computed
  from the real portfolio. If `OPENROUTER_API_KEY` is set, an LLM only rephrases
  that summary (never invents numbers); failures fall back to the stub text.

## Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/api/health` | liveness |
| POST | `/api/accounts` | create sandbox account ($100,000 virtual) |
| GET | `/api/quotes/{symbol}` | live quote (`AAPL`, `BTC`, …) |
| POST | `/api/orders` | virtual buy/sell |
| GET | `/api/accounts/{id}/portfolio` | valuation, P&L, allocation |
| GET | `/api/accounts/{id}/transactions` | ledger |
| GET | `/api/accounts/{id}/history` | portfolio snapshots |
| POST | `/api/ai/explain` | grounded "what happened to my portfolio?" |
