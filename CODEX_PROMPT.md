# CODEX_PROMPT.md

Use this file as the execution prompt for Codex. Do not paste a new ad-hoc architecture prompt over it.

## Mandatory startup

Before changing code:

1. Read `AGENTS.md` completely.
2. Read every document under `docs/` referenced by `AGENTS.md`.
3. Inspect the repository tree and current branch/head.
4. State which phase is being implemented and list the exact files/modules you expect to create or modify.
5. Do not alter requirements or architecture just because a simpler implementation is faster.

## Global constraints

- No monkey patches, runtime symbol replacement, bootstrap patch installers, or hidden compatibility patches.
- No giant `bot.py`, giant admin router, giant provider module, or giant market engine.
- Prefer protocols/interfaces, dependency injection, registries and table-driven dispatch.
- Preserve explicit router/handler ordering and add tests for it.
- Telegram handlers are adapters/orchestrators only; they do not own provider HTTP, SQL, parsing algorithms, rendering algorithms or rate calculations.
- Use async network I/O.
- Use `Decimal` for canonical rates/conversions.
- No finite hard-coded Nobitex asset universe.
- All generated numeric output uses ASCII digits; Persian/Arabic digits remain valid input.
- Inline-first Persian Telegram admin; English terminal UI.
- Centralized rich text/custom emoji handling.
- Centralized callback-data encoding/validation <= 64 UTF-8 bytes.
- Centralized safe button label preview/truncation.
- No separate Premium Emoji admin menu.
- No direct Bitpin integration in RateDeck unless the owner explicitly changes scope later.
- Do not use ExchangeRate IRR as a silent free-market Toman substitute.
- Respect provider-specific caches, health, budgets, cooldowns and provenance.
- No API call per user request.
- Do not run Ruff.
- Do not merge, deploy, restart production services, or run production migrations.

## Phase selection

The user will ask for exactly one of the following.

### Command: Implement Phase 1

Implement only **Phase 1 — Core Market Platform** from `docs/PHASES.md`.

Required result:

- installable Python project skeleton and package boundaries;
- configuration + SQLite repository/migration foundation;
- aiogram Telegram bootstrap;
- admin authentication;
- explicit router ordering;
- number normalization/formatting;
- runtime Asset Registry;
- Nobitex discovery/snapshot provider;
- CoinGecko provider + verified/ambiguous mapping layer;
- ExchangeRate open/keyed provider capability;
- provider budget/cooldown/singleflight/freshness/health;
- strict parser;
- conversion graph with provenance;
- manual Stars package pricing;
- dynamic template/placeholder engine;
- entity-aware rich text/custom emoji foundation;
- central button/callback safety layer;
- Persian inline-first admin for core provider/content/system settings;
- structured logs, provider diagnostics and audit trail;
- background refresh lifecycle;
- tests required by Phase 1;
- documentation updated to match actual code.

Do **not** implement the full professional card designer in Phase 1. A minimal truthful placeholder/text response or simple diagnostic render is acceptable only where needed to prove the core market pipeline.

At the end:

1. run focused tests while developing;
2. run the full test suite;
3. run compile/import smoke checks appropriate to the project;
4. report exact pass/fail counts and skipped tests;
5. show the final tree of newly created top-level packages;
6. list any deferred Phase 2 work without implementing it.

### Command: Implement Phase 2

Phase 2 may start only after Phase 1 is complete and reviewed.

Implement only **Phase 2 — Visual Product & Operations** from `docs/PHASES.md`.

Required result:

- production-quality card design system;
- family-based auto theming;
- multiple compatible layouts/themes/chart styles;
- deterministic high-resolution Pillow renderer;
- local history-backed truthful charts;
- element/layout editor with inline controls;
- logo/custom text layers;
- preview-first card workflow;
- card/caption integration;
- advanced Persian admin polish;
- provider health/routing screens completed;
- terminal control center `ratedeck`;
- safe `install.sh` + systemd unit + one-line README installer;
- backup/restore/update/repair flows;
- card/render/installer/regression tests;
- final readiness checklist.

Do not bypass missing history by inventing chart data. Do not add browser/headless-Chrome rendering unless the owner explicitly changes the architecture.

At the end, run the complete suite and satisfy `docs/DEFINITION_OF_DONE.md` or explicitly identify blockers.

## Implementation style

Use small cohesive modules. Suggested package shape is documented in `docs/ARCHITECTURE.md`; improve names if needed, but preserve boundaries.

Examples of preferred extensibility:

- `ProviderRegistry` mapping IDs to provider adapters;
- `AssetRegistry` assembled from discovered and configured sources;
- `AliasIndex` independent from provider implementations;
- `ConversionGraph` operating on typed rate edges;
- `TemplateRegistry` with per-scope placeholder contracts;
- `CardFamilyRegistry` and `LayoutRegistry`;
- typed callback codec instead of callback string concatenation across handlers.

## Quality rule

When choosing between “works for the current examples” and “correctly models the domain contract”, choose the domain contract without adding unnecessary infrastructure.

RateDeck should stay lightweight: one bot process, SQLite, local assets/history, background refresh and Pillow rendering are the default deployment. Redis/PostgreSQL/multi-worker infrastructure is out of scope unless real deployment requirements later justify it.
