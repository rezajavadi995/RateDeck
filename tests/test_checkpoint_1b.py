from datetime import UTC, datetime
from decimal import Decimal
import asyncio
import pytest
from ratedeck.market import *

def test_numbers_and_dynamic_nobitex_discovery():
    assert parse_decimal("۱۲٬۳۴۵٫۶") == Decimal("12345.6")
    assert format_number(Decimal("1234.500")) == "1,234.5"
    reg=AssetRegistry(); rates=parse_nobitex({"status":"ok","stats":{"brandnew-rls":{"latest":"1250"},"bad":{},"btc-usdt":{"latest":"2"}}},reg)
    assert reg.resolve("BRANDNEW").key == "brandnew"
    assert rates[0].value == Decimal("125") and rates[0].target == "irt"

def test_alias_ambiguity_and_coingecko_verification():
    reg=AssetRegistry(); reg.register(Asset("a","A","A",aliases={"x"})); reg.register(Asset("b","B","B",aliases={"x"}))
    with pytest.raises(ValueError): reg.resolve("x")
    assert verified_coingecko_mapping({"foo":[{"id":"foo-one"},{"id":"foo-two"}]},{"foo-one","foo-two"}) == {}

@pytest.mark.asyncio
async def test_provider_freshness_isolation_lkg_and_cooldown():
    t=datetime.now(UTC); calls=0
    async def good(): return [Rate("a","b",Decimal(1),"a",t,("a",))]
    async def limited(): raise RateLimited(60)
    a=ProviderRuntime("a",good); b=ProviderRuntime("b",limited)
    await a.refresh(now=t); old=a.state.last_success
    with pytest.raises(RateLimited): await b.refresh(now=t)
    assert a.state.last_success == old and b.state.last_success is None and b.state.cooldown_until > t
    assert await b.refresh(now=t) == []

@pytest.mark.asyncio
async def test_singleflight_coalesces_and_history_is_bounded():
    calls=0
    async def fetch():
        nonlocal calls; calls+=1; await asyncio.sleep(.01); return []
    runtime=ProviderRuntime("x",fetch)
    await asyncio.gather(runtime.refresh(now=datetime.now(UTC)),runtime.refresh(now=datetime.now(UTC)))
    assert calls == 1
    h=History(max_rows=2); h.hot={"a"}; t=datetime.now(UTC)
    for n in range(4): h.add(Rate("a","b",Decimal(n),"x",t,("x",)),t)
    h.add(Rate("cold","b",Decimal(1),"x",t,("x",)),t)
    assert len(h.rows)==2 and all(r.source=="a" for r in h.rows)

def test_exchange_rate_never_supplies_iranian_market_rate():
    rates=parse_exchange_rates("USD",{"rates":{"EUR":.9,"IRR":42000}})
    assert [r.target for r in rates] == ["eur"]
