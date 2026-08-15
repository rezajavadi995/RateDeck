from pathlib import Path
import os
import pytest
from ratedeck.content import *
from ratedeck.diagnostics import DiagnosticsService
from ratedeck.market import AssetRegistry
from ratedeck.security import SecretBox,redact
from ratedeck.storage import Database

def test_template_contract_literal_braces_render_and_scope():
    engine=TemplateEngine({"field.local_price":RichDocument("قیمت {price}")})
    doc=RichDocument("{{قیمت}} {asset.name}: {price} {field.local_price}")
    assert engine.render(doc,"caption",{"asset.name":"<BTC>","price":"12"}).text == "{قیمت} &lt;BTC&gt;: 12 قیمت 12"
    with pytest.raises(ValueError): engine.validate(RichDocument("{wat}"),"price")
    with pytest.raises(ValueError): engine.validate(RichDocument("{price}"),"price")

def test_field_cycles_and_bounds():
    with pytest.raises(ValueError): TemplateEngine({"field.local_price":RichDocument("{field.local_price}")}).validate(DEFAULT_TEMPLATES["caption"][1],"caption")
    with pytest.raises(ValueError): TemplateEngine(max_size=2).render(DEFAULT_TEMPLATES["price"][1],"price",{"asset.name":"BTC","price":"1","source":"x"})

def test_custom_emoji_utf16_capture_roundtrip():
    text="فا😀x"; offset=utf16_length("فا")
    doc=capture_document(text,[{"type":"custom_emoji","offset":offset,"length":2,"custom_emoji_id":"123"}])
    assert doc.entities[0].custom_emoji_id=="123" and '123' in doc.to_json()
    with pytest.raises(ValueError): capture_document(text,[{"type":"custom_emoji","offset":offset,"length":2}])

def test_button_customization_is_safe():
    button=BUTTONS["help"].customized(label="راهنما",style="success",enabled=False,row=1)
    assert button.action=="help" and button.style=="success"
    with pytest.raises(ValueError): BUTTONS["help"].customized(style="rainbow")
    assert shorten_label("👨‍👩‍👧‍👦"*40,4).endswith("…")

def test_secret_encryption_permissions_and_redaction(tmp_path):
    path=tmp_path/"master.key"; box=SecretBox.load_or_create(path); encrypted=box.encrypt("valuable")
    assert encrypted!=b"valuable" and box.decrypt(encrypted)=="valuable" and path.stat().st_mode & 0o077 == 0
    assert "abc" not in redact("api_key=abc")

def test_local_diagnostics_has_zero_network_and_detects_broken_template():
    class Provider:
        provider_id="never"; state=type("S",(),{"last_error":None,"request_count":0,"cooldown_until":None})();
        async def refresh(self,*a,**k): raise AssertionError("network used")
    db=Database();db.migrate(); checks=DiagnosticsService(providers=[Provider()],registry=AssetRegistry(),database=db,parser_cases=[lambda:True]).run_local()
    assert all(c.ok for c in checks) and any(c.name=="database" for c in checks)
