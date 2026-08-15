from datetime import UTC, datetime, timedelta
from decimal import Decimal
import pytest
from ratedeck.market import Asset,AssetRegistry,Rate
from ratedeck.conversion import *

def registry():
    r=AssetRegistry()
    for a in [Asset("btc","BTC","Bitcoin",aliases={"بیتکوین"}),Asset("usdt","USDT","Tether",aliases={"تتر"}),Asset("irt","IRT","Toman",aliases={"تومان"})]: r.register(a)
    return r

@pytest.mark.parametrize("text,expected",[("۲ btc",("btc","irt",2)),("2بیتکوین به تتر",("btc","usdt",2)),("٣ USDT to IRT",("usdt","irt",3))])
def test_parser_positive_corpus(text,expected):
    got=IntentParser(registry()).parse(text); assert (got.source,got.target,got.amount)==expected

@pytest.mark.parametrize("text",["سلام خوبی", "من 2 تا کتاب دارم", "/panel", "btc چنده؟", "", "1 unknown"])
def test_parser_false_positive_corpus(text): assert IntentParser(registry()).parse(text) is None

def test_graph_direct_inverse_bridge_provenance_and_freshness():
    now=datetime.now(UTC); old=now-timedelta(minutes=2)
    rates=[Rate("btc","usdt",Decimal("50000"),"cg",now,("cg:bitcoin",)),Rate("usdt","irt",Decimal("60000"),"nobitex",old,("nobitex:usdt-rls",))]
    graph=ConversionGraph(rates); result=graph.convert(Decimal(2),"btc","irt")
    assert result.amount==Decimal("6000000000") and result.provenance==("cg:bitcoin","nobitex:usdt-rls") and result.oldest_timestamp==old
    assert graph.convert(Decimal(60000),"irt","usdt").amount==Decimal(1)
    with pytest.raises(ValueError): graph.convert(Decimal(1),"btc","missing")

def test_stars_are_exact_and_accept_persian_digits():
    stars=StarsPackages(); stars.set_line("۵۰ ۱۲۵۰۰۰")
    assert stars.price(Decimal(50))==Decimal(125000)
    with pytest.raises(ValueError): stars.price(Decimal(100))
