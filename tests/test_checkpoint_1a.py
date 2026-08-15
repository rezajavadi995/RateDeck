import sqlite3
import pytest
from ratedeck.storage import Database
from ratedeck.telegram import Callback, CallbackCodec, ROUTER_ORDER, assert_router_order, is_admin, shorten_label

def test_schema_is_compact_and_has_no_phase2_tables():
    db=Database(); db.migrate()
    names={r[0] for r in db.connection.execute("select name from sqlite_master where type='table'")}
    assert {"assets","provider_state","rates_current","text_templates","audit_events"} <= names
    assert not {"card_configs","uploaded_assets","backup_records"} & names

def test_migration_is_idempotent():
    db=Database(); db.migrate(); db.migrate()
    assert db.connection.execute("select count(*) from schema_migrations").fetchone()[0] == 1

def test_callback_byte_limit_and_round_trip():
    codec=CallbackCodec(); value=Callback("admin","edit","42")
    assert codec.decode(codec.encode(value)) == value
    with pytest.raises(ValueError): codec.encode(Callback("n","a","ش"*40))

def test_grapheme_safe_preview_and_auth_and_order():
    assert shorten_label("ábc", 2) == "á…"
    assert is_admin(7, frozenset({7})) and not is_admin(8, frozenset({7}))
    assert_router_order(ROUTER_ORDER)
    with pytest.raises(ValueError): assert_router_order(tuple(reversed(ROUTER_ORDER)))

def test_real_dispatcher_registration_order():
    from ratedeck.telegram import create_dispatcher
    service=type("S",(),{"text":lambda s,k:k,"admin_screen":lambda s,c:c.action,"parse_market":lambda s,t:None})()
    dispatcher=create_dispatcher(service,frozenset({1}))
    assert tuple(router.name for router in dispatcher.sub_routers)==ROUTER_ORDER
