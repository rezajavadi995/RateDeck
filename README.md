# RateDeck

RateDeck is a lightweight, production-oriented Telegram market and conversion bot with deeply customizable Persian admin controls, dynamic market discovery, strict parsing, provider-aware rate limiting, complete template/button/placeholder support, professional diagnostics, and an exceptional card renderer in Phase 2.

> **Status:** Phase 1 core runtime is implemented for owner review. Phase 2 cards and
> production operations/installer remain intentionally deferred until that review.

## Phase 1 development

RateDeck requires Python 3.11 or newer. Install the development package and run the
local suite (which uses provider fixtures and makes no live API calls by default):

```bash
python -m pip install -e '.[test]'
pytest -q
python -m compileall -q ratedeck tests
python -c "import ratedeck, ratedeck.market, ratedeck.content, ratedeck.telegram"
```

Runtime configuration is read from `RATEDECK_BOT_TOKEN`, `RATEDECK_ADMIN_IDS`,
`RATEDECK_DATABASE`, `RATEDECK_MASTER_KEY`, and `RATEDECK_LOG_LEVEL`. Secrets and
local database/key files must not be committed.

## Product balance

RateDeck is deliberately neither a toy script nor an enterprise platform.

- one async Python bot process;
- SQLite;
- no Redis/PostgreSQL/NATS/message broker requirement;
- no inbound API/web listener required in the default long-polling deployment;
- plain explicit composition instead of DI frameworks;
- modular packages without one-class-per-file ceremony;
- provider-specific cache/cooldown/request counters;
- bounded local history rather than storing every market forever;
- full dynamic Nobitex discovery, but CoinGecko enrichment only where useful/verified;
- Pillow rendering, not browser/headless infrastructure;
- shared-host design target: 2 vCPU / 4 GB RAM / 40 GB disk while StarzYFire may also be running, with measured coexistence required before production-ready claims.

See `docs/LEAN_IMPLEMENTATION.md` and `docs/RESOURCE_AND_ISOLATION.md`.

## Core product principles

- No monkey patches or runtime function replacement.
- Modular package boundaries; handlers orchestrate, services own actual logic.
- Table/registry-driven behavior instead of large `if/elif` routing trees.
- Explicit handler/router ordering with regression tests.
- No finite hard-coded crypto universe for Nobitex markets.
- Provider calls never happen directly from Telegram handlers.
- Provider-specific freshness/cooldown/LKG/request counters and provenance.
- Strict compact-intent parser accepts Persian/Arabic/Latin input without firing on normal conversation.
- All bot-generated numeric output uses ASCII/Latin digits even in Persian text/cards.
- Canonical financial/rate arithmetic uses `Decimal`.
- Persian Telegram admin is inline-first.
- Telegram limits are centrally enforced, including callback <=64 UTF-8 bytes and safe button-label previews.
- Rich text and Telegram custom/premium emoji are captured/rendered centrally.
- Complete scoped `{placeholder}` registry with descriptions, samples, field fragments and diagnostics.
- Design System + Asset Family + Layout + Chart Style + sparse asset override; no per-asset manual design burden.
- API request volume is budgeted before implementation, not patched after quota failures.
- RateDeck paths/service/database/cache/backups are isolated from StarzYFire and must never operate on `/opt/star`, `starzyfire-*` or StarzYFire-owned DB/Redis/NATS/config/secrets.
- No fake tests or claims of readiness without exact evidence.

## Initial data sources

### Nobitex — Iranian/local market authority

RateDeck dynamically consumes usable markets returned by Nobitex public market data. A live VPS check on 2026-08-13 returned `status=ok` with 495 market keys in one snapshot, including `xaut-rls`, `xaut-usdt`, `paxg-rls`, `paxg-usdt`, `slvon-rls`, and `slvon-usdt`.

Tokenized gold/silver assets keep their real identities; they are not mislabeled as Iranian physical 18K gold.

### CoinGecko — global crypto/USD enrichment

Use verified CoinGecko IDs. Symbol-only ambiguous mapping is not silently accepted. Full Nobitex discovery does not cause CoinGecko calls for every asset; enrichment is batched/demand-aware.

### ExchangeRate-API — fiat rates

Global fiat conversion only. It must not silently replace the Iranian free-market Toman source.

### Telegram Stars — manual only

Admin-managed exact packages such as:

```text
50 125000
```

meaning `50 Stars = 125,000 Toman`. No automatic interpolation by default.

## User commands

Visible command surface stays small:

- `/start`
- `/help`
- `/market`
- `/support`
- `/about` (admin-toggleable)
- `/panel` (admin only)

`/settings` is inside `/panel`. Asset-specific `/gold`, `/usd`, `/crypto`, `/rate` commands are unnecessary. `/price` and `/convert` may be hidden compatibility aliases; normal use is parser-driven.

## Customization

Admin can customize designated:

- command/help/support/market texts;
- price/conversion texts;
- stale/empty/error texts;
- card master caption and field fragments;
- buttons: label, Telegram-supported style, custom emoji icon, safe enable state and allowed layout/order;
- asset aliases/display metadata/caption emoji;
- Stars packages;
- Phase 2 card families/layouts/themes/elements/logos/text layers.

### `{}` placeholders

Every placeholder is centrally registered by scope/type/description/sample. Each template editor shows **only the placeholders valid for that text**.

Unknown/malformed/wrong-scope placeholders, field cycles, expansion overflow and final Telegram length errors block activation. Raw unresolved `{placeholder}` text must never leak to users.

### Premium/custom emoji

There is no separate Premium Emoji Manager. When admin supplies a real Telegram custom emoji in a supported text/button editor, RateDeck captures the real entity/ID automatically and uses the central rich-text/button renderer.

## Diagnostics

Diagnostics are a first-class admin product surface, covering:

- APIs/providers: health, latency, freshness, cooldown, request counters, last error;
- assets/mappings/aliases;
- templates/placeholders/field fragments;
- buttons/callback registration/64-byte limits/menu layout;
- rich/custom emoji capture and UTF-16 compile health;
- parser self-tests;
- DB/schema/background refresh/runtime;
- Phase 2 card/font/logo/renderer health.

Local diagnostics make no network calls. Live API diagnostics are explicit and obey the same rate limits/cooldowns as normal providers.

See `docs/DIAGNOSTICS.md`.

## Cards

Visual quality is a major requirement. Cards use family-based design rather than one repeated layout or thousands of manually designed asset configs.

Phase 2 provides:

- professional Pillow rendering;
- 1080x1080 output, preferably rendered larger then downsampled;
- family/theme/layout/chart composition;
- sparse asset overrides;
- truthful bounded local-history charts;
- editable elements/positions/fonts/opacity/layers;
- logos and custom text layers;
- preview-first Persian card designer;
- bounded render queue/concurrency and cache so image work cannot grow without limit on the shared VPS.

## Terminal control center

Phase 2 terminal UI is English-only. The global command is:

```bash
price
```

Installer creates `/usr/local/bin/price` as a verified symlink to the RateDeck console entry point inside `/opt/ratedeck/.venv/bin/price`, so `price` opens the terminal menu from any working directory.

Useful shell shortcuts use the same service-control code:

```bash
price status
price start
price stop
price restart
```

Inside the menu the normal action that runs the bot is **`Service -> Start`**. Bare `price` opens the menu and does not create a second bot process.

The terminal includes a simple **Setup / Config** flow for bot token, admin IDs and log level, plus service lifecycle, local App Status, logs, database/backup, Telegram/render tests, smart update/repair and uninstall.

The update flow is state-aware: it checks local/remote commit state, dirty tree, pending dependencies/migrations, backup space and service state; performs fast-forward-only update; installs/migrates only when needed; smoke-checks; then verifies `ratedeck.service`. It is not a blind `git pull` button.

App Status is local-only and is intended to show RateDeck service state, RSS/CPU snapshot, DB size/schema, disk free space, history/cache/backups, render queue and refresh-loop health without consuming provider API quota.

Provider/API product management remains inside Telegram.

## Installation target

Phase 2 must provide a safe idempotent `install.sh`, dedicated `ratedeck` service account, isolated RateDeck paths, systemd unit, global `price` symlink and one-line installer.

Final command shape:

```bash
sudo bash -c "$(curl -fsSL https://raw.githubusercontent.com/rezajavadi995/RateDeck/main/install.sh)"
```

Do not present the project as ready to install until installer, isolation, resource/coexistence and data-preservation acceptance tests pass.

## Exactly two major implementation phases

1. **Phase 1 — Core Market, Conversion, Content and Admin**: providers, parser/conversion, complete template/button/placeholder/custom-emoji customization, diagnostics, Stars and Persian admin.
2. **Phase 2 — Exceptional Cards + Operations/Installer**: finished visual product, card designer, shared-host resource hardening, terminal, backups, systemd and one-installer.

Each phase has internal checkpoints for reviewability; those checkpoints are not extra phases. After Phase 2 the currently defined product scope is complete.

## Documentation map

Read these before implementation:

- `AGENTS.md` — non-negotiable agent rules.
- `CODEX_PROMPT.md` — execution prompt.
- `docs/DECISIONS.md` — settled owner decisions.
- `docs/LEAN_IMPLEMENTATION.md` — anti-overengineering guardrails.
- `docs/RESOURCE_AND_ISOLATION.md` — 4 GB / 2 vCPU resource budget and StarzYFire coexistence contract.
- `docs/PRODUCT_SCOPE.md` — product behavior/scope.
- `docs/ARCHITECTURE.md` — practical module/dependency boundaries.
- `docs/DATA_MODEL.md` — compact Phase 1 schema + deferred Phase 2 persistence.
- `docs/REFERENCE_AUDIT.md` — audited lessons from older projects.
- `docs/MARKET_ENGINE.md` — market/asset/cache/provenance/history contract.
- `docs/PROVIDERS.md` — provider contracts/routing.
- `docs/EXTERNAL_CONTRACTS_2026-08-13.md` — dated external API/Telegram snapshot.
- `docs/PARSER_AND_CONVERSION.md` — normalization/parser/conversion graph.
- `docs/CONTENT_RICH_TEXT_AND_UI.md` — templates/placeholders/buttons/custom emoji/UI.
- `docs/DIAGNOSTICS.md` — complete diagnostics contract.
- `docs/CARD_ENGINE.md` — Phase 2 visual system.
- `docs/ADMIN_AND_TERMINAL.md` — admin/terminal UX split.
- `docs/OBSERVABILITY_SECURITY.md` — logging/audit/secrets.
- `docs/INSTALLER_AND_OPERATIONS.md` — Phase 2 installer/runtime operations.
- `docs/TESTING.md` — mandatory test strategy.
- `docs/PHASES.md` — exact two-phase plan + checkpoints.
- `docs/DEFINITION_OF_DONE.md` — acceptance gates.

## Implementation rule

Codex must not “simplify” by deleting real product requirements, and must not “future-proof” by inventing infrastructure. When two designs satisfy the same contract, choose the simpler design with fewer moving parts.
