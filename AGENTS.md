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

If behavior must vary, use one of:

- protocol/ABC + implementation;
- dependency injection;
- strategy/registry;
- middleware/filter;
- decorator applied statically at definition time;
- repository/service adapter;
- explicit composition at application bootstrap.

### Modular package boundaries

Keep modules cohesive. Do not create a giant `bot.py`, giant admin router, or single market engine containing parsing, HTTP, storage, rendering and Telegram delivery.

Expected dependency direction:

`Telegram/CLI adapters -> application/use-cases -> domain services -> ports/interfaces -> infrastructure adapters`

Domain code must not import Telegram framework types or shell/process utilities.

### Table/registry-driven behavior

Prefer registries, maps, typed configuration and strategy objects for:

- provider selection;
- asset families;
- parser aliases;
- command metadata;
- button specifications;
- card templates;
- placeholder contracts;
- formatters;
- conversion route scoring.

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
- All provider calls go through a central provider service/orchestrator.
- Use async HTTP; do not block the event loop with synchronous network calls.
- Each provider has independent freshness timestamps, health, request budget, cooldown and last-known-good state.
- A successful refresh of provider A must never make stale data from provider B appear fresh.
- 429/Retry-After and provider quota responses must be handled centrally.
- User traffic reads snapshots; a user message must not cause one API call per request.
- Batch provider requests where supported.
- Use singleflight/coalescing for concurrent refresh attempts.
- Persist enough provider state that a process restart does not immediately hammer an API that was in cooldown.
- Do not silently substitute ExchangeRate IRR for Iranian free-market Toman pricing.
- Preserve quote/rate provenance all the way to the rendered result.
- Use `Decimal` for canonical rates and conversions.
- Never silently bind an ambiguous CoinGecko symbol to the wrong coin. Prefer verified CoinGecko IDs.

## 4. Asset universe rules

RateDeck must not have a finite hard-coded `SUPPORTED_ASSETS` list for the Nobitex universe.

The runtime Asset Registry is composed from:

- core built-in aliases/fiat/manual assets;
- dynamically discovered usable Nobitex markets;
- verified CoinGecko mappings;
- ExchangeRate supported fiat codes;
- administrator overrides/aliases;
- manual-only assets such as Telegram Stars.

An asset may be disabled without deleting its historical identity/configuration.

Unknown or ambiguous assets fail safely; they are not guessed.

## 5. Parser and numbers

- Accept Persian, Arabic and Latin digits.
- Normalize Persian/Arabic decimal and grouping separators.
- Normalize common Arabic/Persian character variants and zero-width separators.
- Parser must be strict enough not to fire on ordinary conversation.
- Parser must support compact forms and configured aliases without requiring a command.
- All bot-generated numeric output uses ASCII/Latin digits only.
- One central number formatter controls grouping, adaptive precision, sign, percent and scientific/small-value behavior.

## 6. Telegram UI rules

- Admin UX is Persian and inline-first.
- Terminal UX is English-only.
- Use free-form text input only for arbitrary values such as template body, API key, custom alias, search term, logo upload or manual Stars package line.
- Telegram callback payloads are centralized, versioned, validated and <= 64 UTF-8 bytes.
- Never store full template text or arbitrary user text in `callback_data`.
- Button preview labels must be centrally shortened safely; never split grapheme clusters/custom emoji and never allow a long current value to destroy keyboard layout.
- Button styles exposed to admin are only Telegram-supported values: default, primary, success, danger.
- Menus with large collections use pagination + favorites/recent + search fallback.
- Prefer editing the current admin message over sending a new message on every click where Telegram permits it.
- Answer callbacks promptly.

## 7. Content, placeholders and premium/custom emoji

- User-facing/admin-configurable texts are not hard-coded inside handlers.
- Templates have explicit scopes and allowed/required placeholder contracts.
- Unknown or malformed placeholders block save and show a useful error.
- Every editable template has preview sample data.
- Rich text capture/rendering is centralized.
- There is no standalone Premium Emoji manager.
- When admin input contains Telegram custom-emoji entities, capture their real IDs/entities; do not infer IDs from Unicode appearance.
- Internal rich-text representation must survive placeholder expansion without corrupting Telegram UTF-16 entity offsets.
- For button labels, map at most the supported custom emoji icon semantics into `icon_custom_emoji_id`; do not pretend button text supports normal message entities.
- Asset caption emoji is asset metadata and may be ordinary or custom emoji.

## 8. Card engine rules

- No per-asset manual design requirement for the discovered market universe.
- Composition model: Design System x Asset Family x Layout x Chart Style x Admin Overrides.
- Unknown assets fall back to a high-quality generic family.
- Specific asset overrides are optional and sparse.
- Card elements are data-driven objects with position/size/visibility/layer/style configuration.
- Rendering must be deterministic for the same input snapshot/config.
- Do not invent historical chart points. If local history is insufficient, render a truthful alternative state/range component.
- Prefer lightweight local rendering (Pillow-based architecture) over browser/headless-Chrome rendering unless the spec is explicitly changed.

## 9. Storage and secrets

- Phase 1 uses SQLite behind repository interfaces; business/domain code must not depend on raw SQLite calls.
- Migrations/schema evolution must be versioned from the beginning.
- API keys, bot token and secrets must never appear in logs, exception messages, exported diagnostics or repository files.
- API keys stored through Telegram admin must be encrypted at rest using a local master key with restrictive file permissions.
- Backups must preserve encrypted secret material without printing plaintext.
- `.env` and local secret keys are never committed.

## 10. Installer/update rules

- Installer is idempotent and targets supported Debian/Ubuntu systems.
- Global command is `ratedeck`.
- Terminal control center must not duplicate provider/API administration.
- Update must refuse unsafe dirty-tree replacement; never use blind `git reset --hard` + `git clean -fd` as the normal update path.
- Preserve `.env`, database, uploaded assets, master secret key, backups and operator data.
- Destructive actions require explicit confirmation and clear scope.

## 11. Logging/observability rules

- Structured application logs + provider logs + durable admin audit trail.
- Redact secrets by construction.
- Include correlation/update IDs where useful.
- Provider diagnostics expose source, latency, last success/failure, cache age, cooldown and quota/budget state without exposing credentials.
- Avoid noisy per-update “success” logs that add no operational value.

## 12. Testing gates

At minimum, Phase 1/2 work must cover the relevant parts of:

- number/input normalization;
- parser positive corpus and false-positive corpus;
- dynamic Nobitex discovery;
- provider fixtures/errors/429/backoff;
- provider-specific freshness;
- conversion graph/path/provenance;
- CoinGecko ambiguity protection;
- Stars manual pricing;
- callback byte limits and normalization;
- handler/router ordering;
- template placeholder validation;
- premium emoji capture/render round-trip;
- button label truncation;
- admin authorization;
- card structural/golden invariants;
- installer safety/smoke behavior.

Run the most relevant tests before reporting completion. Full suite is required at phase completion unless an explicit environment blocker is documented.

## 13. Source-of-truth docs

Before implementation, read:

- `README.md`
- `docs/PRODUCT_SCOPE.md`
- `docs/ARCHITECTURE.md`
- `docs/REFERENCE_AUDIT.md`
- `docs/MARKET_ENGINE.md`
- `docs/PROVIDERS.md`
- `docs/PARSER_AND_CONVERSION.md`
- `docs/CARD_ENGINE.md`
- `docs/CONTENT_RICH_TEXT_AND_UI.md`
- `docs/ADMIN_AND_TERMINAL.md`
- `docs/OBSERVABILITY_SECURITY.md`
- `docs/INSTALLER_AND_OPERATIONS.md`
- `docs/TESTING.md`
- `docs/PHASES.md`
- `docs/DEFINITION_OF_DONE.md`

If docs conflict, `AGENTS.md` safety/architecture constraints take precedence, then the more specific domain document, then README.
