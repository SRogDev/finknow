"""Finkow FastAPI backend — virtual-money investing sandbox (Phase 1)."""

from __future__ import annotations

import os
from decimal import Decimal, InvalidOperation

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app import ai as ai_ops
from app.market import CachedMarketData, MarketDataUnavailable, Quote, SymbolNotFound
from app.money import cash_str, qty_str, to_cash, to_qty
from app.portfolio import average_cost, unrealized_pnl, value_portfolio
from app.store import InMemoryStore, Position, Snapshot, Transaction, new_id, utcnow

app = FastAPI(title="Finkow API", version="0.1.0")


def _cors_origins() -> list[str]:
    """Allowed browser origins.

    Override with ``FINKOW_CORS_ORIGINS`` (comma-separated, e.g.
    ``https://finkow.example.com``). Defaults cover local Next.js dev.
    """
    raw = os.environ.get("FINKOW_CORS_ORIGINS", "")
    if raw.strip():
        return [origin.strip() for origin in raw.split(",") if origin.strip()]
    return ["http://localhost:3000", "http://127.0.0.1:3000"]


# The Next.js frontend calls the API directly from the browser
# (fetch to NEXT_PUBLIC_API_URL), so the backend must serve CORS.
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["content-type"],
    max_age=600,
)

_store = InMemoryStore()
_market: CachedMarketData | None = None


def get_store() -> InMemoryStore:
    return _store


def get_market() -> CachedMarketData:
    global _market
    if _market is None:
        _market = CachedMarketData()
    return _market


def reset_state() -> None:
    """Test hook: fresh store and market between tests."""
    global _store, _market
    _store = InMemoryStore()
    _market = None


# ---------------------------------------------------------------- requests


class CreateAccountRequest(BaseModel):
    email: str | None = None


class OrderRequest(BaseModel):
    account_id: str
    symbol: str
    side: str  # "buy" | "sell"
    quantity: str  # decimal string, e.g. "10" or "0.5"


class ExplainRequest(BaseModel):
    account_id: str
    question: str


# ---------------------------------------------------------------- helpers


@app.get("/api/quotes/{symbol}")
async def get_quote(symbol: str, market: CachedMarketData = Depends(get_market)) -> dict:
    try:
        quote = await market.get_quote(symbol)
    except SymbolNotFound as exc:
        raise HTTPException(status_code=404, detail=f"unknown symbol: {symbol}") from exc
    except MarketDataUnavailable as exc:
        raise HTTPException(status_code=503, detail=f"market data unavailable: {exc}") from exc
    return {
        "symbol": quote.symbol,
        "price": qty_str(quote.price),
        "currency": quote.currency,
        "as_of": quote.as_of.isoformat(),
        "provider": quote.provider,
        "stale": quote.stale,
    }


async def _portfolio_view(account_id: str, store: InMemoryStore, market: CachedMarketData):
    account = store.get_account(account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="account not found")
    positions = store.get_positions(account_id)
    quotes: dict[str, Quote] = {}
    for pos in positions:
        try:
            quotes[pos.symbol] = await market.get_quote(pos.symbol)
        except MarketDataUnavailable:
            pass  # value_portfolio falls back to avg_cost, marked stale
    return value_portfolio(account, positions, quotes)


def _serialize_portfolio(pv) -> dict:
    return {
        "account_id": pv.account_id,
        "cash": cash_str(pv.cash),
        "initial_cash": cash_str(pv.initial_cash),
        "total_value": cash_str(pv.total_value),
        "total_return": cash_str(pv.total_return),
        "total_return_pct": format(pv.total_return_pct, ".2f"),
        "allocation": {k: format(v, ".4f") for k, v in pv.allocation.items()},
        "as_of": pv.as_of.isoformat(),
        "positions": [
            {
                "symbol": p.symbol,
                "quantity": qty_str(p.qty),
                "avg_cost": cash_str(p.avg_cost),
                "price": qty_str(p.price),
                "market_value": cash_str(p.market_value),
                "unrealized_pnl": cash_str(p.unrealized_pnl),
                "unrealized_pnl_pct": format(p.unrealized_pnl_pct, ".2f"),
                "stale": p.stale,
            }
            for p in pv.positions
        ],
    }


# ---------------------------------------------------------------- routes


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "version": "0.1.0"}


@app.post("/api/accounts")
def create_account(body: CreateAccountRequest, store: InMemoryStore = Depends(get_store)) -> dict:
    account = store.create_account(email=body.email)
    return {
        "account_id": account.id,
        "cash": cash_str(account.cash),
        "initial_cash": cash_str(account.initial_cash),
        "created_at": account.created_at.isoformat(),
    }


@app.post("/api/orders")
async def place_order(
    body: OrderRequest,
    store: InMemoryStore = Depends(get_store),
    market: CachedMarketData = Depends(get_market),
) -> dict:
    side = body.side.lower()
    if side not in ("buy", "sell"):
        raise HTTPException(status_code=400, detail="side must be 'buy' or 'sell'")
    try:
        qty = to_qty(Decimal(body.quantity))
    except (InvalidOperation, ValueError) as exc:
        raise HTTPException(status_code=400, detail="quantity must be a decimal number") from exc
    if qty <= 0:
        raise HTTPException(status_code=400, detail="quantity must be positive")

    account = store.get_account(body.account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="account not found")

    try:
        quote = await market.get_quote(body.symbol)
    except SymbolNotFound as exc:
        raise HTTPException(status_code=404, detail=f"unknown symbol: {body.symbol}") from exc
    except MarketDataUnavailable as exc:
        raise HTTPException(status_code=503, detail=f"market data unavailable: {exc}") from exc
    symbol, price = quote.symbol, quote.price

    realized: Decimal | None = None
    if side == "buy":
        cost = to_cash(price * qty)
        if cost > account.cash:
            raise HTTPException(
                status_code=400,
                detail=f"insufficient funds: need ${cash_str(cost)}, "
                f"have ${cash_str(account.cash)}",
            )
        account.cash = to_cash(account.cash - cost)
        position = store.get_position(account.id, symbol)
        if position is None:
            position = Position(
                account_id=account.id, symbol=symbol, qty=qty, avg_cost=to_cash(price)
            )
        else:
            position.avg_cost = average_cost(position.qty, position.avg_cost, qty, price)
            position.qty = to_qty(position.qty + qty)
        store.upsert_position(position)
        cash_delta = -cost
    else:
        position = store.get_position(account.id, symbol)
        if position is None or position.qty < qty:
            have = qty_str(position.qty) if position else "0"
            raise HTTPException(
                status_code=400,
                detail=f"insufficient position: trying to sell {qty_str(qty)} {symbol}, "
                f"hold {have}",
            )
        proceeds = to_cash(price * qty)
        realized = unrealized_pnl(qty, position.avg_cost, price)
        account.cash = to_cash(account.cash + proceeds)
        remaining = to_qty(position.qty - qty)
        if remaining == 0:
            store.remove_position(account.id, symbol)
        else:
            position.qty = remaining
            store.upsert_position(position)
        cash_delta = proceeds

    txn = Transaction(
        id=new_id(),
        account_id=account.id,
        symbol=symbol,
        side=side,
        qty=qty,
        price=price,
        cash_delta=cash_delta,
        realized_pnl=realized,
        created_at=utcnow(),
    )
    store.add_transaction(txn)

    pv = await _portfolio_view(account.id, store, market)
    store.add_snapshot(
        Snapshot(
            account_id=account.id,
            total_value=pv.total_value,
            cash=account.cash,
            created_at=utcnow(),
        )
    )
    return {
        "transaction_id": txn.id,
        "side": side,
        "symbol": symbol,
        "quantity": qty_str(qty),
        "price": qty_str(price),
        "cash_after": cash_str(account.cash),
        "realized_pnl": cash_str(realized) if realized is not None else None,
        "stale_price": quote.stale,
    }


@app.get("/api/accounts/{account_id}/portfolio")
async def get_portfolio(
    account_id: str,
    store: InMemoryStore = Depends(get_store),
    market: CachedMarketData = Depends(get_market),
) -> dict:
    return _serialize_portfolio(await _portfolio_view(account_id, store, market))


@app.get("/api/accounts/{account_id}/transactions")
def get_transactions(account_id: str, store: InMemoryStore = Depends(get_store)) -> dict:
    if store.get_account(account_id) is None:
        raise HTTPException(status_code=404, detail="account not found")
    return {
        "transactions": [
            {
                "id": t.id,
                "symbol": t.symbol,
                "side": t.side,
                "quantity": qty_str(t.qty),
                "price": qty_str(t.price),
                "cash_delta": cash_str(t.cash_delta),
                "realized_pnl": cash_str(t.realized_pnl) if t.realized_pnl is not None else None,
                "created_at": t.created_at.isoformat(),
            }
            for t in store.list_transactions(account_id)
        ]
    }


@app.get("/api/accounts/{account_id}/history")
def get_history(account_id: str, store: InMemoryStore = Depends(get_store)) -> dict:
    if store.get_account(account_id) is None:
        raise HTTPException(status_code=404, detail="account not found")
    return {
        "snapshots": [
            {
                "total_value": cash_str(s.total_value),
                "cash": cash_str(s.cash),
                "created_at": s.created_at.isoformat(),
            }
            for s in store.list_snapshots(account_id)
        ]
    }


@app.post("/api/ai/explain")
async def ai_explain(
    body: ExplainRequest,
    store: InMemoryStore = Depends(get_store),
    market: CachedMarketData = Depends(get_market),
) -> dict:
    pv = await _portfolio_view(body.account_id, store, market)
    return await ai_ops.explain_portfolio(pv, body.question)
