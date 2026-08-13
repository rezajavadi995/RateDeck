# Architecture

## Runtime target

RateDeck is intentionally lightweight:

- Python async runtime;
- aiogram 3.x Telegram adapter;
- one bot process by default;
- SQLite persistence behind repository interfaces;
- local background refresh loop;
- Pillow-based image rendering;
- systemd service on Debian/Ubuntu;
- no Redis/PostgreSQL requirement for initial product scope.

The architecture must allow future replacement of SQLite or single-process locking without rewriting domain logic.

## Dependency rule

The allowed direction is:

```text
Telegram / CLI / Scheduler adapters
              ↓
        Application use-cases
              ↓
          Domain services
              ↓
        Ports / interfaces
              ↓
 Infrastructure adapters
  (SQLite / HTTP / filesystem)
```

Reverse imports are forbidden. In particular:

- market domain code does not import aiogram;
- card domain code does not import bot routers;
- provider adapters do not import handlers;
- repositories do not build Telegram keyboards;
- CLI does not implement duplicate business logic.

## Suggested package tree

```text
ratedeck/
├── __init__.py
├── app/
│   ├── bootstrap.py
│   ├── container.py
│   ├── lifecycle.py
│   └── scheduler.py
├── bot/
│   ├── factory.py
│   ├── callbacks/
│   │   ├── codec.py
│   │   └── models.py
│   ├── filters/
│   ├── middlewares/
│   ├── routers/
│   │   ├── admin/
│   │   │   ├── root.py
│   │   │   ├── providers.py
│   │   │   ├── assets.py
│   │   │   ├── cards.py
│   │   │   ├── content.py
│   │   │   ├── buttons.py
│   │   │   ├── stars.py
│   │   │   ├── logs.py
│   │   │   └── system.py
│   │   ├── commands.py
│   │   ├── market.py
│   │   ├── support.py
│   │   └── fallback.py
│   └── ui/
│       ├── keyboards.py
│       ├── labels.py
│       ├── pagination.py
│       └── safe_preview.py
├── market/
│   ├── models.py
│   ├── registry/
│   │   ├── assets.py
│   │   ├── aliases.py
│   │   ├── families.py
│   │   └── coingecko_mapping.py
│   ├── providers/
│   │   ├── base.py
│   │   ├── registry.py
│   │   ├── nobitex.py
│   │   ├── coingecko.py
│   │   └── exchangerate.py
│   ├── cache/
│   │   ├── snapshots.py
│   │   ├── freshness.py
│   │   └── singleflight.py
│   ├── budget/
│   │   ├── models.py
│   │   └── manager.py
│   ├── parser/
│   │   ├── normalize.py
│   │   ├── lexer.py
│   │   ├── aliases.py
│   │   └── intent.py
│   ├── conversion/
│   │   ├── graph.py
│   │   ├── routing.py
│   │   └── service.py
│   ├── history/
│   │   ├── repository.py
│   │   └── retention.py
│   └── health/
│       ├── models.py
│       └── service.py
├── content/
│   ├── models.py
│   ├── templates.py
│   ├── placeholders.py
│   ├── fields.py
│   └── rich_text/
│       ├── document.py
│       ├── capture.py
│       ├── compiler.py
│       └── utf16.py
├── cards/
│   ├── models.py
│   ├── design_system.py
│   ├── families.py
│   ├── layouts.py
│   ├── themes.py
│   ├── charts.py
│   ├── renderer.py
│   ├── elements.py
│   └── assets.py
├── storage/
│   ├── database.py
│   ├── migrations.py
│   ├── repositories/
│   └── schema/
├── observability/
│   ├── logging.py
│   ├── audit.py
│   ├── redaction.py
│   └── correlation.py
├── security/
│   ├── secrets.py
│   └── admin.py
├── cli/
│   ├── main.py
│   ├── menu.py
│   └── commands/
└── utils/
    ├── numbers.py
    ├── time.py
    └── text.py
```

This is a boundary guide, not a mandate to create empty files. Codex should create only modules with real responsibility.

## Composition root

`app/container.py` or equivalent is the single explicit composition root. It constructs:

- configuration;
- repositories;
- shared async HTTP client(s);
- provider registry;
- provider budget manager;
- asset/alias registries;
- market refresh/orchestration service;
- conversion service;
- template/rich-text service;
- card renderer;
- audit/logging services;
- Telegram routers/middlewares;
- background refresh lifecycle.

No hidden process-wide installation step may rewrite imported modules.

## Provider boundary

Providers implement a typed interface such as conceptually:

```text
Provider
├── id
├── capabilities
├── fetch_snapshot(...)
├── health_probe(...)
└── optional discovery/mapping methods
```

A provider returns domain DTOs. Raw HTTP JSON is validated at the adapter boundary and is not passed into handlers.

## Repositories

SQLite access is encapsulated by repositories. Core repositories likely include:

- SettingsRepository
- AssetRepository
- AliasRepository
- ProviderStateRepository
- MarketSnapshotRepository
- HistoryRepository
- TemplateRepository
- ButtonRepository
- CardConfigRepository
- StarsPricingRepository
- AuditRepository

Repository interfaces make tests independent from Telegram and make future storage replacement possible.

## Router/handler ordering

Registration is explicit in one bot factory. No router imports itself for side effects.

Required order:

```text
Admin critical/recovery
→ Admin FSM/state handlers
→ User state handlers (if any)
→ Explicit commands
→ Typed callback namespaces
→ Market parser handler
→ Generic content/help
→ Fallback
```

Why: compact market parsing is intentionally broad enough to understand `btc`, `100 usdt`, etc.; it must never consume `/panel`, an admin free-text state, or a callback-related flow.

Add a test that inspects dispatcher/router registration or exercises collision cases through the real dispatcher.

## Middleware order

Keep middleware minimal. Likely responsibilities:

1. correlation/update context;
2. admin authorization context;
3. callback acknowledgement/dedupe safety where applicable;
4. state/context injection;
5. error boundary.

Do not reproduce a complex stack of compatibility middlewares from older projects unless RateDeck genuinely requires them.

## Callback architecture

Use a typed/versioned callback codec. Requirements:

- <= 64 UTF-8 bytes before creating the button;
- namespace/action/compact ID payload;
- never embed templates, API keys, long asset names, JSON or user text;
- reject malformed/unknown versions;
- support pagination tokens/IDs compactly;
- central tests for byte length.

## Admin interaction state

Use explicit FSM/state objects for free-form admin input. State must include enough context to know exactly what is being edited without inferring from previous message text.

Admin navigation should prefer editing the existing control message, with safe fallback when Telegram cannot edit it.

## Background work

A single scheduler/lifecycle component refreshes provider snapshots. It must:

- obey provider budgets;
- coalesce refreshes;
- add small jitter so providers are not hit on an exact synchronized cadence;
- persist success/failure/cooldown timestamps;
- record local history after successful validated snapshots;
- continue partial provider availability without marking unrelated stale providers fresh.

## Data model versioning

Even with SQLite, schema evolution is versioned from the first release. Do not rely on ad-hoc `CREATE TABLE IF NOT EXISTS` mutations scattered through runtime code.

A tiny internal migration runner is acceptable if the project remains lightweight; Alembic is optional, not mandatory. Whatever is chosen must be deterministic, testable and backup-safe.

## File-size/code-quality guidance

There is no arbitrary hard line limit, but large files are a design smell. Split a module when it contains multiple domains or when tests/imports indicate unrelated responsibilities.

Avoid:

- 1000-line router files;
- all providers in one module;
- parser + HTTP + DB + renderer in one service;
- helper dumping grounds such as `utils.py` with unrelated functions.

Clean code is a means, not the product. Prefer obvious, typed, testable code over abstraction for its own sake.
