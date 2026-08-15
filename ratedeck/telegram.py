from __future__ import annotations

from dataclasses import dataclass
import regex

ROUTER_ORDER = ("admin_critical", "fsm", "commands", "callbacks", "market_parser", "content", "fallback")

@dataclass(frozen=True, slots=True)
class Callback:
    namespace: str
    action: str
    record: str = ""

class CallbackCodec:
    version = "1"
    def encode(self, value: Callback) -> str:
        if any(":" in p for p in (value.namespace, value.action, value.record)):
            raise ValueError("callback component contains separator")
        raw = ":".join((self.version, value.namespace, value.action, value.record)).rstrip(":")
        if len(raw.encode()) > 64: raise ValueError("callback_data exceeds 64 UTF-8 bytes")
        return raw
    def decode(self, raw: str) -> Callback:
        if len(raw.encode()) > 64: raise ValueError("callback_data exceeds 64 UTF-8 bytes")
        parts = raw.split(":")
        if len(parts) not in (3, 4) or parts[0] != self.version or not all(parts[:3]): raise ValueError("malformed callback")
        return Callback(parts[1], parts[2], parts[3] if len(parts) == 4 else "")

def shorten_label(text: str, limit: int = 32) -> str:
    clusters = regex.findall(r"\X", text)
    return text if len(clusters) <= limit else "".join(clusters[: max(1, limit - 1)]) + "…"

def is_admin(user_id: int | None, admin_ids: frozenset[int]) -> bool:
    return user_id is not None and user_id in admin_ids

def assert_router_order(order: tuple[str, ...]) -> None:
    if tuple(order) != ROUTER_ORDER: raise ValueError("unsafe router registration order")

def create_dispatcher(services: object, admin_ids: frozenset[int]):
    """Build the real aiogram dispatcher without import-time registration side effects."""
    from aiogram import Dispatcher, Router, F
    from aiogram.filters import Command
    from aiogram.types import CallbackQuery, Message
    dispatcher = Dispatcher()
    routers = {}
    for name in ROUTER_ORDER:
        router = Router(name=name)
        routers[name] = router
        dispatcher.include_router(router)
    async def command(message: Message):
        key=(message.text or "/help").split()[0].removeprefix("/").split("@")[0]
        if key == "panel" and not is_admin(message.from_user.id if message.from_user else None,admin_ids): return
        await message.answer(services.text(key if key in {"start","help","market","support","about","panel"} else "help"))
    routers["commands"].message.register(command,Command("start","help","market","support","about","panel"))
    async def admin_callback(query: CallbackQuery):
        # Authorization is repeated at execution, not inferred from menu visibility.
        if not is_admin(query.from_user.id,admin_ids):
            await query.answer("دسترسی ندارید",show_alert=True); return
        await query.answer(); await query.message.edit_text(services.admin_screen(CallbackCodec().decode(query.data or "")))
    routers["admin_critical"].callback_query.register(admin_callback,F.data.startswith("1:admin:"))
    async def market(message: Message):
        result=services.parse_market(message.text or "")
        if result is not None: await message.answer(result)
    routers["market_parser"].message.register(market,F.text)
    async def fallback(message: Message): await message.answer(services.text("help"))
    routers["fallback"].message.register(fallback)
    assert_router_order(tuple(r.name for r in dispatcher.sub_routers))
    return dispatcher
