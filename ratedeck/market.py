from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from decimal import Decimal, InvalidOperation
import json
import re
from typing import Awaitable, Callable, Iterable

DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")

def normalize_text(value: str) -> str:
    return (value.translate(DIGITS).replace("ي", "ی").replace("ك", "ک")
            .replace("٫", ".").replace("٬", ",").replace("\u200c", " ").strip().lower())

def parse_decimal(value: str) -> Decimal:
    value = normalize_text(value).replace(",", "").replace(" ", "")
    try: return Decimal(value)
    except InvalidOperation as exc: raise ValueError("invalid number") from exc

def format_number(value: Decimal, precision: int | None = None, signed: bool = False) -> str:
    if precision is None: precision = 8 if abs(value) < 1 else 2
    rendered = f"{value:,.{precision}f}".rstrip("0").rstrip(".")
    if rendered in ("-0", ""): rendered = "0"
    return "+" + rendered if signed and value > 0 else rendered

@dataclass(slots=True)
class Asset:
    key: str
    symbol: str
    name: str
    family: str = "crypto"
    aliases: set[str] = field(default_factory=set)

class AssetRegistry:
    def __init__(self): self.assets: dict[str, Asset] = {}; self.aliases: dict[str, set[str]] = {}
    def register(self, asset: Asset) -> Asset:
        existing = self.assets.get(asset.key)
        if existing: existing.aliases |= asset.aliases; asset = existing
        else: self.assets[asset.key] = asset
        for alias in {asset.key, asset.symbol, asset.name, *asset.aliases}:
            self.aliases.setdefault(normalize_text(alias), set()).add(asset.key)
        return asset
    def resolve(self, alias: str) -> Asset:
        matches = self.aliases.get(normalize_text(alias), set())
        if len(matches) != 1: raise ValueError("unknown or ambiguous asset")
        return self.assets[next(iter(matches))]

@dataclass(frozen=True, slots=True)
class Rate:
    source: str; target: str; value: Decimal; provider: str; timestamp: datetime; provenance: tuple[str, ...]

@dataclass(slots=True)
class ProviderState:
    last_attempt: datetime | None = None; last_success: datetime | None = None
    last_failure: datetime | None = None; cooldown_until: datetime | None = None
    request_count: int = 0; consecutive_failures: int = 0; last_error: str | None = None
    latency_ms: int | None = None

class ProviderRuntime:
    def __init__(self, provider_id: str, fetch: Callable[[], Awaitable[list[Rate]]], minimum_interval: timedelta = timedelta(seconds=30)):
        self.provider_id, self.fetch, self.minimum_interval = provider_id, fetch, minimum_interval
        self.state, self.snapshot, self._lock = ProviderState(), [], asyncio.Lock()
    async def refresh(self, force: bool = False, now: datetime | None = None) -> list[Rate]:
        now = now or datetime.now(UTC)
        async with self._lock:
            if self.state.cooldown_until and now < self.state.cooldown_until: return self.snapshot
            if not force and self.state.last_attempt and now-self.state.last_attempt < self.minimum_interval: return self.snapshot
            self.state.last_attempt=now; self.state.request_count += 1
            try:
                result=await self.fetch(); self.snapshot=result; self.state.last_success=now
                self.state.consecutive_failures=0; self.state.last_error=None
                return result
            except RateLimited as exc:
                self.state.last_failure=now; self.state.consecutive_failures += 1
                self.state.cooldown_until=now+timedelta(seconds=exc.retry_after); self.state.last_error="rate_limited"; raise
            except Exception as exc:
                self.state.last_failure=now; self.state.consecutive_failures += 1
                self.state.last_error=type(exc).__name__; raise

class RateLimited(RuntimeError):
    def __init__(self, retry_after: int): self.retry_after=retry_after; super().__init__("provider rate limited")

def parse_nobitex(payload: dict, registry: AssetRegistry, at: datetime | None = None) -> list[Rate]:
    if payload.get("status") != "ok" or not isinstance(payload.get("stats"), dict): raise ValueError("invalid Nobitex envelope")
    at=at or datetime.now(UTC); rates=[]
    for market, raw in payload["stats"].items():
        try:
            base, quote=market.lower().split("-"); latest=Decimal(str(raw["latest"]));
            if latest <= 0 or quote not in {"rls", "usdt"}: continue
        except (ValueError, KeyError, InvalidOperation, AttributeError): continue
        registry.register(Asset(base, base.upper(), base.upper()))
        target="irt" if quote == "rls" else "usdt"
        registry.register(Asset(target, target.upper(), target.upper(), "fiat"))
        value=latest/Decimal(10) if quote == "rls" else latest
        rates.append(Rate(base, target, value, "nobitex", at, (f"nobitex:{market}",)))
    return rates

def verified_coingecko_mapping(candidates: dict[str, list[dict]], requested_ids: set[str]) -> dict[str, str]:
    result={}
    for symbol, items in candidates.items():
        verified=[i["id"] for i in items if i.get("id") in requested_ids]
        if len(verified)==1: result[symbol.lower()]=verified[0]
    return result

def parse_exchange_rates(base: str, payload: dict, at: datetime | None = None) -> list[Rate]:
    rates=payload.get("rates") or payload.get("conversion_rates")
    if not isinstance(rates, dict): raise ValueError("invalid ExchangeRate response")
    return [Rate(base.lower(), k.lower(), Decimal(str(v)), "exchangerate", at or datetime.now(UTC), (f"exchangerate:{base}:{k}",)) for k,v in rates.items() if k.upper() != "IRR"]

class History:
    def __init__(self, max_rows: int = 1000, max_age: timedelta = timedelta(days=7)):
        self.max_rows, self.max_age, self.hot, self.rows = max_rows, max_age, set(), []
    def add(self, rate: Rate, now: datetime | None = None):
        if rate.source not in self.hot: return
        now=now or datetime.now(UTC); cutoff=now-self.max_age
        self.rows=[r for r in self.rows if r.timestamp >= cutoff]
        self.rows.append(rate); self.rows=self.rows[-self.max_rows:]
