# RateDeck

RateDeck is a lightweight, production-oriented Telegram market and conversion bot with a highly customizable card renderer, Persian inline-first administration, dynamic market discovery, strict parsing, provider-aware rate limiting, and a safe terminal control center.

> **Status:** specification/foundation only. Runtime implementation is intentionally deferred to Codex Phase 1 and Phase 2. Do not treat this repository as runnable until the phase gates in `docs/PHASES.md` are satisfied.

## Product principles

- No monkey patches or runtime function replacement.
- Modular package boundaries; handlers orchestrate, services own business logic.
- Table/registry/strategy-driven behavior instead of large `if/elif` routing trees.
- Explicit handler/router ordering with regression tests.
- No hard-coded finite crypto universe: usable Nobitex markets are discovered dynamically.
- Provider calls never happen directly from Telegram handlers.
- Provider-specific cache freshness, budgets, cooldowns, health, and provenance.
- Strict compact-intent parser that accepts Persian/Arabic/Latin input without firing on ordinary conversation.
- All bot-generated numeric output uses ASCII/Latin digits even inside Persian text.
- Financial/rate arithmetic uses `Decimal`, never binary floating-point as the canonical representation.
- Inline-first admin UX. Free-form typing is reserved for values that genuinely require arbitrary input.
- Telegram limits are enforced centrally before render/send, including callback-data byte limits and safe button-label previews.
- Rich text and Telegram custom/premium emoji are captured and rendered centrally.
- High-quality cards use a design system + family theme + layout + chart style + optional asset override; thousands of assets must not require per-asset manual design.
- API request volume is budgeted before implementation, not patched after rate-limit failures.
- No fake tests, green-only tests, or claims of production readiness without evidence.

## Initial data sources

### Nobitex — Iranian/local market authority

RateDeck should dynamically consume usable markets returned by the Nobitex public market stats surface. A live VPS check on 2026-08-13 returned `status=ok` with 495 market keys in one snapshot, including examples such as `xaut-rls`, `xaut-usdt`, `paxg-rls`, `paxg-usdt`, `slvon-rls`, and `slvon-usdt`.

Important: XAUT/PAXG/tokenized metal markets are **not** to be mislabeled as Iranian 18K physical gold. Iranian 18K gold, if later added, must use an explicit verified source and distinct asset identity.

### CoinGecko — global crypto market data

Use verified CoinGecko IDs where possible for global USD pricing and global crypto metadata. Symbol-only matching must not silently bind ambiguous coins.

### ExchangeRate-API — fiat rates

Use for global fiat conversions. It must **not** silently replace the Iranian free-market Toman source. Public/open and keyed modes are separate capabilities; terms/attribution and quota behavior must be respected.

### Telegram Stars — manual only

Stars pricing is admin-managed only. The intended input contract is a compact sample/package line such as `50 125000`, meaning `50 Stars = 125,000 Toman`. No automatic interpolation is enabled by default.

## User commands

Visible command surface should remain small:

- `/start`
- `/help`
- `/market`
- `/support`
- `/about` (admin-toggleable)
- `/panel` (admin only)

`/settings` is merged into `/panel`. Asset-specific commands such as `/gold`, `/usd`, `/crypto`, and `/rate` are not part of the public command menu. `/price` and `/convert` may exist only as hidden compatibility aliases; normal market/conversion use is parser-driven.

## Administration

Telegram admin UI is Persian and inline-first. It manages market/provider health and routing, public/keyed provider modes, cache/budget/cooldown status, dynamic assets and aliases, card design, dynamic content/templates, buttons, asset caption emoji, manual Stars pricing, logs, audit, backups, and health summaries.

There is no separate “Premium Emoji Manager”. Custom emoji are captured in context when an admin supplies rich text or a button label, and stored/rendered through the central rich-text system. Asset caption emoji are configurable as asset metadata.

## Terminal control center

The terminal UI is English-only to avoid RTL rendering problems. The global command is intended to be:

```bash
ratedeck
```

The terminal is intentionally operational, not a duplicate product admin panel. It covers service status, start/stop/restart, logs, database backup/restore, basic configuration, Telegram connectivity test, test-card rendering, safe update/repair, and uninstall. Provider/API management stays inside Telegram.

## Installation target

The finished project must provide a safe, idempotent `install.sh` and a short public one-liner in this README. The updater must never use a blind `git reset --hard` / `git clean` strategy against operator data or unreviewed local changes.

The final installation command will have this shape once `install.sh` exists:

```bash
sudo bash -c "$(curl -fsSL https://raw.githubusercontent.com/rezajavadi995/RateDeck/main/install.sh)"
```

Do not publish this as “ready to install” until the installer acceptance tests pass.

## Documentation map

Read these before implementation:

- `AGENTS.md` — non-negotiable repository/Codex rules.
- `CODEX_PROMPT.md` — execution prompt for Phase 1 and Phase 2.
- `docs/PRODUCT_SCOPE.md` — product behavior and command/admin scope.
- `docs/ARCHITECTURE.md` — module boundaries, dependency rules, router ordering.
- `docs/REFERENCE_AUDIT.md` — what to reuse conceptually from Business Bot and StarzYFire, and what to avoid.
- `docs/MARKET_ENGINE.md` — asset registry, cache, rate budget, provenance, history.
- `docs/PROVIDERS.md` — provider contracts and routing policy.
- `docs/PARSER_AND_CONVERSION.md` — normalization, strict parser, conversion graph.
- `docs/CARD_ENGINE.md` — card design/rendering system.
- `docs/CONTENT_RICH_TEXT_AND_UI.md` — templates, placeholders, custom emoji, buttons.
- `docs/ADMIN_AND_TERMINAL.md` — Telegram admin and terminal UX.
- `docs/OBSERVABILITY_SECURITY.md` — logging, audit, secret handling and safety.
- `docs/INSTALLER_AND_OPERATIONS.md` — installer/update/runtime requirements.
- `docs/TESTING.md` — mandatory test strategy.
- `docs/PHASES.md` — the two implementation phases.
- `docs/DEFINITION_OF_DONE.md` — acceptance gates.

## Implementation rule

Codex must not begin by “simplifying” these contracts. When a requirement is unclear, it must stop at that boundary, document the ambiguity, and implement the smallest behavior that preserves the safety and extensibility described here.
