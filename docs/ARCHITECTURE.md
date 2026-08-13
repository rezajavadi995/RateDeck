# Architecture

## Runtime target

RateDeck is intentionally lightweight:

- Python async runtime;
- aiogram 3.x;
- one bot process;
- SQLite;
- one local background refresh loop;
- Pillow-based rendering in Phase 2;
- systemd on Debian/Ubuntu in Phase 2;
- no Redis/PostgreSQL/message broker requirement.

The code should remain replaceable at real boundaries, but future hypothetical scaling must not distort the initial implementation.

## Dependency direction

```text
Telegram / CLI / scheduler adapters
              ↓
        application services
              ↓
     market/content/card domain
              ↓
   SQLite / HTTP / filesystem adapters
```

Rules:

- market logic does not import aiogram;
- provider adapters do not import routers;
- repositories do not build keyboards;
- CLI invokes application services instead of duplicating them;
- no hidden bootstrap step mutates imported runtime symbols.

## Preferred compact package shape

This is the **starting shape**, not a mandate to create every file immediately:

```text
ratedeck/
├── app/
│   ├── bootstrap.py
│   └── lifecycle.py
├── bot/
│   ├── factory.py
│   ├── callbacks.py
│   ├── ui.py
│   └── routers/
│       ├── admin/
│       ├── commands.py
│       ├── market.py
│       ├── support.py
│       └── fallback.py
├── market/
│   ├── models.py
│   ├── registry.py
│   ├── providers/
│   │   ├── base.py
│   │   ├── nobitex.py
│   │   ├── coingecko.py
│   │   └── exchangerate.py
│   ├── provider_runtime.py
│   ├── parser.py
│   ├── conversion.py
│   ├── history.py
│   └── service.py
├── content/
│   ├── models.py
│   ├── placeholders.py
│   ├── rich_text.py
│   └── service.py
├── diagnostics/
│   └── service.py
├── storage/
│   ├── database.py
│   ├── migrations.py
│   └── repositories.py
├── observability/
│   ├── logging.py
│   └── audit.py
├── security/
│   └── secrets.py
├── cards/            # mainly Phase 2; split when real renderer responsibilities exist
└── cli/              # mainly Phase 2
```

If a module gains clearly separate responsibilities, split it then. Do not pre-create nested `cache/`, `budget/`, `health/`, `registry/`, `repositories/` packages just because a previous design sketch listed them.

## Composition root

Use one explicit bootstrap/composition location to construct:

- config;
- SQLite connection/repositories;
- shared async HTTP client;
- provider adapters + provider runtime policies;
- asset registry/alias index;
- market service + conversion service;
- content/placeholder/rich-text service;
- diagnostics service;
- audit/logging;
- Telegram bot/routers;
- background refresh loop;
- Phase 2 renderer/CLI when implemented.

Plain constructor arguments/objects are sufficient. No DI framework.

## Provider boundary

Providers need a small typed contract around real I/O, conceptually:

```text
provider_id
capabilities
fetch_snapshot(...)
optional discovery/mapping operation
```

A separate `health_probe()` is only needed when an official cheap health operation materially differs from normal snapshot validation. Otherwise a bounded normal provider call can serve as the live diagnostic.

Raw provider JSON is validated/normalized at the adapter boundary and does not reach handlers.

## Provider runtime policy

Keep provider runtime state simple and provider-specific:

- enabled/mode;
- refresh/minimum interval;
- last attempt/success/failure;
- last error category/latency;
- request counters used by RateDeck;
- cooldown/Retry-After/backoff;
- last-known-good metadata;
- one in-process singleflight lock.

Do not build distributed locks or a generic quota platform.

## Storage boundary

SQLite is app-owned. A small repository layer groups SQL by domain, but no generic ORM/repository framework is required.

It is acceptable for one `repositories.py` to contain several small cohesive repositories initially. Split it only when it becomes hard to review/test.

Schema evolution is versioned from release one. A small deterministic migration runner is acceptable.

## Router/handler ordering

Registration is explicit in one bot factory. No side-effect router registration.

Required priority:

```text
Admin critical callbacks
→ active admin/user FSM handlers
→ explicit commands
→ typed callback namespaces
→ market parser
→ generic content handlers
→ fallback
```

Collision tests must use the real dispatcher path so `/panel`, admin input states and commands cannot be consumed by the broad market parser.

## Middleware

Keep middleware small. Likely needs:

- correlation/update context;
- admin context/authorization helper;
- central error boundary;
- optional callback dedupe/ack helper only if the implementation proves it useful.

Do not reproduce older projects' compatibility middleware stacks.

## Callback architecture

One typed/versioned callback codec:

- <=64 UTF-8 bytes;
- namespace/action/compact record ID;
- no templates/API keys/JSON/long names/user prose;
- malformed/unknown actions fail safely;
- diagnostics can validate registered actions against button specs.

## Admin interaction state

Use FSM only while awaiting arbitrary input. Finite choices stay inline.

The state stores the exact object/key being edited; never infer edit context from previous displayed prose.

Prefer editing the existing control message, with one shared fallback helper when Telegram requires replacement.

## Background refresh

One lightweight application lifecycle loop can schedule providers independently.

It must:

- obey provider policy/cooldowns;
- coalesce concurrent refreshes;
- add modest jitter;
- persist independent timestamps/state;
- commit partial provider success independently;
- update bounded history only for the configured hot set;
- never make stale provider data fresh because another provider succeeded.

A full scheduling framework is unnecessary unless implementation evidence shows the simple loop is insufficient.

## Asset discovery vs enrichment

Nobitex whole-market discovery can register the full usable local universe efficiently.

CoinGecko mapping/enrichment is not required for every discovered asset immediately. Use batched lazy/demand-aware mapping to avoid unnecessary API traffic.

## Content architecture

Centralize the genuinely complex parts:

- Placeholder Registry;
- template contracts + validator;
- rich-document capture/model;
- placeholder expansion;
- Telegram entity compiler/UTF-16 offsets;
- ButtonSpec/callback codec;
- safe preview/Telegram length validation.

Do not create separate versions of these rules in each router.

## Diagnostics architecture

`DiagnosticsService` composes existing validators/services and returns typed bounded results. It does not reimplement provider/parser/template/button logic.

Local diagnostics never use the network. Live provider diagnostics reuse provider adapters/runtime policy and therefore respect cooldowns/limits.

See `docs/DIAGNOSTICS.md`.

## Phase 2 cards

Start with data-driven composition and reusable Pillow primitives. Avoid a deep class inheritance tree.

Split `cards/` only along real responsibilities such as renderer, layouts/themes, charts/history integration, typography/assets and admin editor support.

## Code-quality guidance

There is no arbitrary file-length limit.

Split when a module owns unrelated domains or becomes risky to change. Do not split simply to make the tree look “clean”.

Avoid both extremes:

- one 1500-line `bot.py` containing everything;
- forty 20-line files that only forward calls.

Prefer direct, typed, testable code with obvious control flow.