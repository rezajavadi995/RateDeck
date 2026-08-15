from __future__ import annotations
from dataclasses import dataclass, field, replace
import html, json, re
from typing import Any
from ratedeck.telegram import Callback, CallbackCodec, shorten_label

@dataclass(frozen=True, slots=True)
class Placeholder:
    key: str; scopes: frozenset[str]; kind: str; description_fa: str; sample: str; required: bool=False; rich: bool=False

PLACEHOLDERS={p.key:p for p in (
    Placeholder("asset.name",frozenset({"price","conversion","caption"}),"text","نام دارایی","Bitcoin",True),
    Placeholder("price",frozenset({"price","caption"}),"number","قیمت","60,000",True),
    Placeholder("amount",frozenset({"conversion"}),"number","مقدار","2",True),
    Placeholder("result",frozenset({"conversion"}),"number","نتیجه","120,000",True),
    Placeholder("source",frozenset({"price","conversion","caption"}),"text","منبع","Nobitex"),
    Placeholder("field.local_price",frozenset({"caption"}),"rich","بخش قیمت محلی","قیمت: 60,000",rich=True),
)}

@dataclass(frozen=True, slots=True)
class Entity:
    kind: str; offset: int; length: int; custom_emoji_id: str | None=None

@dataclass(frozen=True, slots=True)
class RichDocument:
    text: str; entities: tuple[Entity,...]=()
    def to_json(self): return json.dumps({"text":self.text,"entities":[e.__dict__ if hasattr(e,"__dict__") else {"kind":e.kind,"offset":e.offset,"length":e.length,"custom_emoji_id":e.custom_emoji_id} for e in self.entities]},ensure_ascii=False)

def utf16_length(text: str) -> int: return len(text.encode("utf-16-le"))//2
def py_index_from_utf16(text: str, offset: int) -> int:
    used=0
    for i,char in enumerate(text):
        if used==offset:return i
        used+=utf16_length(char)
        if used>offset: raise ValueError("offset splits surrogate pair")
    if used==offset:return len(text)
    raise ValueError("offset out of range")

def capture_document(text: str, telegram_entities: list[Any]) -> RichDocument:
    entities=[]
    for raw in telegram_entities:
        kind=getattr(raw,"type",None) or raw.get("type")
        offset=getattr(raw,"offset",None) if not isinstance(raw,dict) else raw["offset"]
        length=getattr(raw,"length",None) if not isinstance(raw,dict) else raw["length"]
        emoji=getattr(raw,"custom_emoji_id",None) if not isinstance(raw,dict) else raw.get("custom_emoji_id")
        if kind == "custom_emoji" and not emoji: raise ValueError("custom emoji entity lacks real ID")
        py_index_from_utf16(text,offset); py_index_from_utf16(text,offset+length)
        entities.append(Entity(str(kind),offset,length,emoji))
    return RichDocument(text,tuple(entities))

FIELD_RE=re.compile(r"(?<!\{)\{([a-z][a-z0-9_.]*)\}(?!\})")
def referenced(text: str) -> set[str]: return set(FIELD_RE.findall(text.replace("{{","").replace("}}","")))

class TemplateEngine:
    def __init__(self, fields: dict[str,RichDocument] | None=None, max_depth=5,max_size=4096): self.fields=fields or {}; self.max_depth=max_depth; self.max_size=max_size
    def validate(self, doc: RichDocument, scope: str):
        # After legal brace escaping, stray braces are malformed.
        scrubbed=FIELD_RE.sub("",doc.text).replace("{{","").replace("}}","")
        if "{" in scrubbed or "}" in scrubbed: raise ValueError("malformed placeholder or brace")
        keys=referenced(doc.text)
        for key in keys:
            p=PLACEHOLDERS.get(key)
            if not p or scope not in p.scopes: raise ValueError(f"unknown or wrong-scope placeholder: {key}")
        required={p.key for p in PLACEHOLDERS.values() if scope in p.scopes and p.required}
        if not required <= keys: raise ValueError("required placeholders missing")
        self._check_cycles()
    def _check_cycles(self):
        def walk(key,stack,depth):
            if depth>self.max_depth: raise ValueError("field expansion depth exceeded")
            if key in stack: raise ValueError("field cycle")
            for child in referenced(self.fields.get(key,RichDocument("")).text):
                if child.startswith("field."): walk(child,stack|{key},depth+1)
        for key in self.fields: walk(key,set(),0)
    def render(self,doc: RichDocument,scope: str,values: dict[str,str]) -> RichDocument:
        self.validate(doc,scope)
        def expand(text,depth=0):
            if depth>self.max_depth: raise ValueError("field expansion depth exceeded")
            def sub(match):
                key=match.group(1)
                if key.startswith("field."): return expand(self.fields[key].text,depth+1)
                if key not in values: raise ValueError(f"unresolved placeholder: {key}")
                return values[key] if PLACEHOLDERS[key].rich else html.escape(str(values[key]))
            value=FIELD_RE.sub(sub,text).replace("{{","{").replace("}}","}")
            if utf16_length(value)>self.max_size: raise ValueError("expanded Telegram text too long")
            return value
        # Entity offsets from input are intentionally not reused after expansion; final
        # entities are compiled from rich fragments at the final-text boundary.
        return RichDocument(expand(doc.text))

DEFAULT_TEMPLATES={
 "start":("start",RichDocument("به RateDeck خوش آمدید")), "help":("help",RichDocument("مقدار و نام دارایی را بفرستید")),
 "market":("market",RichDocument("بازار")), "support":("support",RichDocument("پشتیبانی")), "about":("about",RichDocument("درباره RateDeck")),
 "price":("price",RichDocument("{asset.name}: {price} ({source})")),
 "conversion":("conversion",RichDocument("{amount} {asset.name} = {result}")),
 "caption":("caption",RichDocument("{asset.name}\n{price}\n{field.local_price}")),
}

STYLES=frozenset({"default","primary","success","danger"})
@dataclass(frozen=True, slots=True)
class ButtonSpec:
    key: str; label: str; action: str; style: str="default"; icon_custom_emoji_id: str|None=None
    allow_disable: bool=False; configurable_layout: bool=False; enabled: bool=True; row: int=0; order: int=0
    def customized(self,*,label=None,style=None,icon=None,enabled=None,row=None,order=None):
        style=style or self.style
        if style not in STYLES: raise ValueError("unsupported Telegram button style")
        if enabled is not None and not self.allow_disable: raise ValueError("button cannot be disabled")
        if (row is not None or order is not None) and not self.configurable_layout: raise ValueError("layout is fixed")
        return replace(self,label=label or self.label,style=style,icon_custom_emoji_id=icon if icon is not None else self.icon_custom_emoji_id,
                       enabled=self.enabled if enabled is None else enabled,row=self.row if row is None else row,order=self.order if order is None else order)

BUTTONS={"help":ButtonSpec("help","راهنما","help",allow_disable=True,configurable_layout=True)}

