from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Awaitable
from ratedeck.content import BUTTONS, Callback, CallbackCodec, DEFAULT_TEMPLATES, STYLES, TemplateEngine, utf16_length

@dataclass(frozen=True,slots=True)
class Check: name:str; ok:bool; detail:str

class DiagnosticsService:
    def __init__(self, *, providers=(), registry=None, database=None, parser_cases=()): self.providers=providers; self.registry=registry; self.database=database; self.parser_cases=parser_cases
    def run_local(self)->list[Check]:
        checks=[]
        for provider in self.providers:
            s=provider.state; checks.append(Check(f"provider:{provider.provider_id}",not bool(s.last_error),f"requests={s.request_count}; cooldown={s.cooldown_until}; error={s.last_error or '-'}"))
        engine=TemplateEngine({"field.local_price":DEFAULT_TEMPLATES["price"][1]})
        for key,(scope,doc) in DEFAULT_TEMPLATES.items():
            try: engine.validate(doc,scope); checks.append(Check(f"template:{key}",True,"valid"))
            except ValueError as e: checks.append(Check(f"template:{key}",False,str(e)))
        codec=CallbackCodec()
        for key,spec in BUTTONS.items():
            try: codec.encode(Callback("ui",spec.action,key)); assert spec.style in STYLES; checks.append(Check(f"button:{key}",True,"valid"))
            except (ValueError,AssertionError) as e: checks.append(Check(f"button:{key}",False,str(e)))
        if self.database:
            version=self.database.connection.execute("select max(version) from schema_migrations").fetchone()[0]
            checks.append(Check("database",version is not None,f"schema={version}"))
        checks.append(Check("rich:utf16",utf16_length("الف😀")==5,"compiler self-test"))
        checks.append(Check("assets:aliases",not any(len(v)>1 for v in getattr(self.registry,"aliases",{}).values()),"ambiguity scan"))
        checks.append(Check("parser:self-test",all(fn() for fn in self.parser_cases),f"cases={len(self.parser_cases)}"))
        return checks
    async def run_live(self)->list[Check]:
        result=[]
        for provider in self.providers:
            try: await provider.refresh(force=True); result.append(Check(f"live:{provider.provider_id}",True,"bounded refresh completed"))
            except Exception as exc: result.append(Check(f"live:{provider.provider_id}",False,type(exc).__name__))
        return result

