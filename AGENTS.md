# AGENTS.md — RateDeck Repository Contract

This file is authoritative for Codex/agent work in this repository. Read it before editing any runtime file.

## 1. Scope discipline

- Implement only the requested phase/scope.
- Do not merge, deploy, restart services, run production migrations, or modify production data unless the user explicitly asks.
- Do not rewrite unrelated files “for cleanliness”.
- Do not claim tests passed unless they actually ran and passed on the exact head being reported.
- Do not add fake tests, tests that merely mirror the implementation, or green-only edits that weaken assertions.
- Do not run Ruff. The project owner explicitly does not want Ruff used in task scripts, patches, or validation commands.

## 2. Architecture: non-negotiable

### No monkey patching

Forbidden patterns include runtime replacement of imported functions/classes, bootstrap-time patch installers, mutating another module's function object, and compatibility wrappers that overwrite symbols after import.

If behavior must vary, use explicit composition, a provider/strategy registry, a small protocol at a real boundary, middleware/filter, or a normal service adapter.

### Lean modularity

RateDeck must be modular without becoming an internal framework.

- Follow `docs/LEAN_IMPLEMENTATION.md`.
- Do not create empty modules merely to mirror an architecture diagram.
- Do not create one interface/ABC per service.
- Do not add a DI framework, generic repository framework, event bus, CQRS, plugin framework, microservice boundary or distributed infrastructure.
- Keep related small responsibilities together until a real split trigger exists.
- Clean code is a means, not the product.

Expected dependency direction:

`Telegram/CLI adapters -> application/use-cases -> domain services -> infrastructure boundaries`

Domain code must not import Telegram framework types or shell/process utilities.

### Table/registry-driven behavior

Prefer registries, maps, typed configuration and small strategy objects for provider selection, asset families, aliases, command metadata, buttons, card templates, placeholder contracts, formatters and conversion route policy.

Ordinary validation `if` statements are fine. Large branch-driven architecture (`if provider == ... elif ...`) is not.

### Handler/router order is a contract

Registration order must be explicit and tested. General parser/fallback handlers must never precede more specific admin, FSM/state, command, or callback handlers.

Target priority:

1. critical/admin-only callbacks and recovery actions;
2. active FSM/state-specific handlers;
3. explicit commands;
4. callback namespaces;
5. market/conversion parser;
6. generic help/content handlers;
7. final fallback.

Any change to router order requires a focused regression test.

## 3. Market/provider rules

- Telegram handlers never call provider HTTP methods directly.
- All provider calls go through the market/provider service boundary.
- Use async HTTP; do not block the event loop with synchronous network calls.
- Each provider has independent freshness timestamps, health, request counters, cooldown and last-known-good state.
- A successful refresh of provider A must never make stale data from provider B appear fresh.
- 429/Retry-After and provider quota responses are handled centrally.
- User traffic reads snapshots; a user message must not cause one API call per request.
- Batch provider requests where supported.
- Use in-process singleflight/coalescing for the initial single-process runtime.
- Persist enough provider state that a process restart does not immediately hammer an API in cooldown.
- Do not silently substitute ExchangeRate IRR for Iranian free-market Toman pricing.
- Preserve quote/rate provenance to rendered output.
- Use `Decimal` for canonical rates and conversions.
- Never silently bind an ambiguous CoinGecko symbol to the wrong coin.
- Rate limiting must remain simple unless a real provider requirement proves otherwise: provider policy + minimum interval + counters + Retry-After/429 cooldown is preferred over a generalized quota framework.

## 4. Asset universe and history

RateDeck must not have a finite hard-coded `SUPPORTED_ASSETS` list for the Nobitex universe.

The runtime Asset Registry is composed from built-in fiat/manual metadata, dynamically discovered Nobitex markets, verified/lazy CoinGecko mappings, ExchangeRate fiat codes, admin aliases/overrides and manual assets such as Stars.

Important lean rules:

- full Nobitex discovery does not imply full CoinGecko enrichment for every discovered asset;
- CoinGecko mapping/enrichment is batched and demand-aware;
- unknown/ambiguous assets fail safely and are not guessed;
- asset removal from one refresh does not delete identity/history/admin customization;
- do not persist history for every discovered market on every refresh;
- history uses a bounded hot set (core/favorite/recently used/configured-card assets) with age/row/storage limits;
- insufficient history produces a truthful fallback, never fabricated points.

## 5. Parser and numbers

- Accept Persian, Arabic and Latin digits.
- Normalize Persian/Arabic decimal/grouping separators and common character variants/zero-width separators.
- Parser must be strict enough not to fire on ordinary conversation.
- Parser supports compact forms and configured aliases without requiring a command.
- All bot-generated numeric output uses ASCII/Latin digits only.
- One central number formatter controls grouping, adaptive precision, sign, percent and small-value behavior.

## 6. Telegram UI rules

- Admin UX is Persian and inline-first.
- Terminal UX is English-only.
- Use free-form text input only for genuinely arbitrary values such as template body, API key, custom alias/search, logo upload, custom text or manual Stars package line.
- Telegram callback payloads are centralized, versioned, validated and <=64 UTF-8 bytes.
- Never store full template text or arbitrary user text in `callback_data`.
- Button preview labels are centrally shortened safely; never split grapheme clusters/custom emoji.
- Button styles exposed to admin are only Telegram-supported values: default, primary, success, danger.
- Menus with large collections use pagination + favorites/recent + search fallback.
- Prefer editing the current admin message over sending a new one on every click where Telegram permits it.
- Answer callbacks promptly.

## 7. Content, placeholders, buttons and custom emoji

These are core product requirements and must be complete, not superficial.

### Placeholder Registry

- One central registry defines every `{placeholder}` by key, scope, type, Persian description, sample value and availability/required policy.
- Each template editor shows only placeholders valid for that template scope.
- Unknown/malformed placeholders block save.
- Field fragments such as `{field.local_price}` are supported, cycle-checked and expansion-bounded.
- No unresolved placeholder may leak into final user output.
- Literal brace escaping must be explicitly supported/documented.
- Dynamic data is escaped/typed; only declared rich-fragment placeholders may inject validated rich content.

### Templates

- User/admin-configurable prose is not hard-coded inside handlers.
- Templates have stable keys/scopes and sample preview data.
- Save path is validate -> preview -> save where appropriate.
- Telegram target length is checked after realistic expansion.

### Rich/custom emoji

- Rich text capture/rendering is centralized.
- There is no standalone Premium Emoji manager.
- When admin input contains Telegram custom-emoji entities, capture their real IDs/entities; do not infer IDs from Unicode appearance.
- Placeholder expansion occurs before final Telegram entity offset compilation.
- UTF-16 offset handling is centralized/tested.
- Asset caption emoji belongs to asset metadata.

### Buttons

- Central ButtonSpec/customization layer.
- Admin may customize designated button label, style, custom emoji icon, enabled state where safe, and row/order only for menus explicitly declared configurable.
- Admin cannot replace a built-in action with arbitrary callback executable semantics.
- Button text does not pretend to support message rich entities; captured custom emoji uses supported `icon_custom_emoji_id` semantics.

## 8. Diagnostics

Follow `docs/DIAGNOSTICS.md`.

Diagnostics must cover providers, assets/mappings/aliases, templates/placeholders/field cycles, buttons/callback limits/action registration, rich/custom emoji compilation, parser self-test, DB/schema/background refresh, and Phase 2 card/font/logo/render health.

Local diagnostics make no external calls. Live API diagnostics are explicit, bounded and obey provider cooldown/rate-budget policy.

Diagnostics reuse existing validators/services; do not build a second implementation of the application.

## 9. Card engine rules

- No per-asset manual design requirement for the discovered market universe.
- Composition model: Design System x Asset Family x Layout x Chart Style x Admin Overrides.
- Unknown assets fall back to a high-quality generic family.
- Specific asset overrides are optional and sparse.
- Card elements are data-driven with position/size/visibility/layer/style configuration.
- Rendering is deterministic for the same input/config.
- Do not invent historical chart points.
- Prefer lightweight local Pillow rendering; no browser/headless-Chrome renderer unless scope changes.
- Avoid deep inheritance hierarchies for themes/elements; prefer data + reusable drawing primitives.
- On the 4 GB shared-host target, default card-render concurrency is 1 unless measurement proves a higher value safe.
- Rendering/cache/history are bounded; never create unlimited render tasks or persistent artifacts.

## 10. Shared-host resource and StarzYFire isolation

Follow `docs/RESOURCE_AND_ISOLATION.md`.

RateDeck is expected to coexist with StarzYFire on a 2 vCPU / 4 GB RAM / 40 GB host.

Non-negotiable:

- one RateDeck bot process by default;
- no Redis/PostgreSQL/NATS/web/API server requirement;
- Telegram long polling by default with no inbound application port;
- dedicated RateDeck filesystem paths/service account/systemd unit;
- never touch `/opt/star`, `starzyfire-*`, StarzYFire DB/Redis/NATS/config/secrets/backups/ports/users/groups;
- no broad wildcard uninstall/update/repair operations;
- no distro-wide Python dependency mutation outside the RateDeck venv;
- bounded HTTP concurrency, history, rendered cache, logs, backups and uploads;
- terminal status is local-only and must not launch another bot/refresher;
- resource targets are measured before release; do not claim shared-host safety from architecture alone.

Engineering measurement targets are documented in `docs/RESOURCE_AND_ISOLATION.md`; actual measurements on representative hardware are required in Phase 2 acceptance.

## 11. Storage and secrets

- Phase 1 uses SQLite.
- Keep the schema compact; create tables only for Phase 1 runtime needs.
- Do not materialize Phase 2 card/upload/backup tables early.
- No generic repository framework; small domain repositories are enough.
- Migrations/schema evolution are versioned from the beginning.
- Money/rates are exact decimal strings/scaled integers, not SQLite binary float.
- API keys, bot token and secrets never appear in logs, diagnostics or repo files.
- Provider keys stored through Telegram admin are encrypted at rest using a maintained library/local master key with restrictive permissions.
- `.env` and local secret keys are never committed.

## 12. Installer/update rules

- Installer/terminal product work belongs to Phase 2 except minimal development bootstrap.
- Installer is idempotent and targets supported Debian/Ubuntu systems.
- Global command is `ratedeck`.
- Terminal control center does not duplicate provider/API administration.
- Terminal includes a simple Quick Setup/per-setting Config flow for bot token, admin IDs and log level.
- Update refuses unsafe dirty-tree replacement; never use blind `git reset --hard` + `git clean -fd` as normal update.
- Preserve RateDeck config/DB/assets/keys/backups and operator data.
- Installer/update/repair/uninstall operate only on exact RateDeck-owned resources.
- Destructive actions require explicit confirmation.

## 13. Logging/observability rules

- Structured application logs + provider logs/events + durable admin audit trail.
- Redact secrets by construction.
- Include correlation/update IDs where useful.
- Provider diagnostics expose source, latency, last success/failure, cache age, cooldown and request counters without exposing credentials.
- Avoid noisy per-update success logs that add no operational value.

## 14. Testing gates

At minimum, relevant work covers:

- number/input normalization;
- parser positive + false-positive corpus;
- dynamic Nobitex discovery;
- provider fixtures/errors/429/backoff/freshness isolation;
- conversion graph/path/provenance;
- CoinGecko ambiguity protection;
- Stars manual pricing;
- callback byte limits/action registry/router ordering;
- template/placeholder validation + field-cycle/expansion bounds;
- custom emoji capture/render round trip + UTF-16 offsets;
- button label truncation/customization safety;
- diagnostics local-no-network/live-cooldown behavior;
- admin authorization;
- Phase 2 card structural/golden invariants;
- Phase 2 installer/isolation/safety/smoke behavior;
- Phase 2 bounded render concurrency/cache/history/disk behavior;
- Phase 2 measured shared-host resource/coexistence validation.

Run focused tests while working. Full suite is required at phase completion unless a real environment blocker is documented.

## 15. Phase execution

There are exactly **two major implementation phases**.

Each phase may and should be executed through ordered internal checkpoints with tests after each checkpoint. These checkpoints are not extra product phases and must not expand scope.

Do not start Phase 2 until Phase 1 acceptance is reviewed.

## 16. Source-of-truth docs

Before implementation, read:

- `README.md`
- `docs/DECISIONS.md`
- `docs/LEAN_IMPLEMENTATION.md`
- `docs/RESOURCE_AND_ISOLATION.md`
- `docs/PRODUCT_SCOPE.md`
- `docs/ARCHITECTURE.md`
- `docs/DATA_MODEL.md`
- `docs/REFERENCE_AUDIT.md`
- `docs/MARKET_ENGINE.md`
- `docs/PROVIDERS.md`
- `docs/EXTERNAL_CONTRACTS_2026-08-13.md`
- `docs/PARSER_AND_CONVERSION.md`
- `docs/CONTENT_RICH_TEXT_AND_UI.md`
- `docs/DIAGNOSTICS.md`
- `docs/CARD_ENGINE.md`
- `docs/ADMIN_AND_TERMINAL.md`
- `docs/OBSERVABILITY_SECURITY.md`
- `docs/INSTALLER_AND_OPERATIONS.md`
- `docs/TESTING.md`
- `docs/PHASES.md`
- `docs/DEFINITION_OF_DONE.md`

If docs conflict, `AGENTS.md` safety/architecture constraints take precedence, then `docs/DECISIONS.md`, then `docs/LEAN_IMPLEMENTATION.md`, then `docs/RESOURCE_AND_ISOLATION.md` for deployment/resource/isolation questions, then the more specific domain document, then README.
