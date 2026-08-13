# CODEX_PROMPT.md

Use this file as the execution prompt for Codex. Do not paste an ad-hoc architecture over it.

## Mandatory startup

Before changing runtime code:

1. Read `AGENTS.md` completely.
2. Read every source-of-truth document referenced by `AGENTS.md`, especially `docs/DECISIONS.md`, `docs/LEAN_IMPLEMENTATION.md`, `docs/DIAGNOSTICS.md` and `docs/PHASES.md`.
3. Inspect repository tree, current branch and exact head.
4. State which major phase is being implemented.
5. Break that phase into the checkpoints already defined in `docs/PHASES.md` and list the exact modules/files expected for the **first checkpoint only**.
6. Do not create the whole theoretical architecture tree up front. Create files only when their real responsibility is implemented.

## Global constraints

- No monkey patches, runtime symbol replacement or bootstrap patch installers.
- Modular, but lean: no giant `bot.py`, and no explosion of tiny forwarding files/interfaces.
- No DI framework, generic repository framework, event bus, CQRS, plugin framework, microservices, Redis, PostgreSQL or distributed locks in the defined initial scope.
- Prefer plain explicit composition, typed models, registries and table-driven policy.
- Handler/router ordering is explicit and tested.
- Telegram handlers are adapters/orchestrators only; they do not own provider HTTP, SQL, parser algorithms, card rendering algorithms or financial calculations.
- Async network I/O.
- `Decimal` for canonical rates/conversions.
- No finite hard-coded Nobitex asset universe.
- Full Nobitex discovery does not imply full CoinGecko enrichment; CoinGecko mapping/enrichment is safe, lazy/demand-aware and batched.
- Do not persist history for all markets on every refresh; use bounded hot-set history.
- All generated numeric output uses ASCII digits; Persian/Arabic digits remain valid input.
- Inline-first Persian Telegram admin; English terminal UI.
- Central rich-text/custom-emoji handling.
- Central Placeholder Registry with complete per-scope `{}` contracts.
- Central ButtonSpec/customization + callback codec <=64 UTF-8 bytes.
- No separate Premium Emoji admin menu.
- No direct Bitpin integration unless owner explicitly changes scope.
- Do not use ExchangeRate IRR as a silent free-market Toman substitute.
- Provider-specific freshness/cooldown/request counters/provenance.
- Rate policy stays simple unless a real provider requires more: minimum interval + counters + Retry-After/429 cooldown/backoff + singleflight.
- No API call per user request.
- Diagnostics reuse real validators/services; local diagnostics perform zero network calls, live diagnostics obey provider limits.
- Do not run Ruff.
- Do not merge, deploy, restart production services or run production migrations.

## Major Phase 1 command

When the owner says **Implement Phase 1**, implement only **Phase 1 — Core Market, Conversion, Content and Admin** from `docs/PHASES.md`.

Work in order:

- Checkpoint 1A: runtime/storage/routing;
- Checkpoint 1B: providers/market runtime;
- Checkpoint 1C: parser/conversion/Stars;
- Checkpoint 1D: complete templates/placeholders/rich emoji/buttons/admin/diagnostics/security.

After each checkpoint:

1. run focused tests;
2. show changed module boundaries;
3. confirm no later-checkpoint work was pulled forward without need;
4. continue only if the current checkpoint is internally coherent.

Phase 1 required outcome includes:

- installable development Python package skeleton (not production installer yet);
- compact SQLite schema/migrations;
- aiogram bootstrap/admin authorization/router order;
- dynamic Nobitex universe;
- safe CoinGecko/ExchangeRate integration;
- provider-specific runtime/cooldown/singleflight/freshness;
- bounded history;
- strict parser + graph conversion + provenance;
- manual exact Stars package pricing;
- complete customizable template/command/caption foundation;
- complete Placeholder Registry and `{}` diagnostics;
- field fragments with cycle/depth/size guards;
- entity-aware custom emoji capture/render/UTF-16 handling;
- customizable safe button labels/styles/icons/allowed layout order;
- Persian inline-first admin for providers/assets/content/buttons/Stars/diagnostics/logs/health;
- structured logs/audit/secret redaction + encrypted keyed provider secrets;
- local diagnostics + bounded quota-aware live diagnostics;
- Phase 1 test coverage in `docs/TESTING.md` and `docs/PHASES.md`.

Do **not** implement the full professional card designer, terminal control center, systemd production installer or backup/restore product in Phase 1.

At Phase 1 completion:

- run focused and full suite;
- run compile/import smoke checks;
- report exact pass/fail/skip counts;
- show top-level package tree;
- report any contract deviation/blocker;
- stop for review before Phase 2.

## Major Phase 2 command

Phase 2 starts only after Phase 1 review.

Implement only **Phase 2 — Exceptional Cards + Operations/Installer** from `docs/PHASES.md`.

Work in order:

- Checkpoint 2A: design system/renderer;
- Checkpoint 2B: truthful charts/elements;
- Checkpoint 2C: Persian card designer/caption delivery/card diagnostics;
- Checkpoint 2D: terminal/installer/systemd/backups/update/final hardening.

Required result:

- exceptional deterministic Pillow cards;
- family-based theming + compatible layouts/themes/chart styles;
- sparse asset overrides rather than per-asset design burden;
- truthful bounded local-history charts and missing-history fallback;
- data-driven editable card elements;
- preview-first Persian card designer;
- rich customizable card captions using Phase 1 placeholder/rich-text engine;
- complete card renderer diagnostics;
- English `ratedeck` terminal control center;
- safe idempotent `install.sh` + systemd + README one-liner;
- backup/restore/update/repair flows with data preservation;
- final full regression/readiness evidence.

Do not invent history, add browser/headless rendering, or expand into unrelated infrastructure.

## Implementation style

Follow `docs/LEAN_IMPLEMENTATION.md`.

Examples of appropriate constructs:

- `AssetRegistry` assembled from discovered/configured sources;
- small provider adapter contract + provider runtime state/policy;
- `AliasIndex` independent of provider parsing;
- `ConversionGraph` over typed rate edges;
- one Placeholder Registry + template validator;
- one rich-document compiler;
- one ButtonSpec/callback codec;
- one DiagnosticsService composing existing checks;
- data registries + reusable drawing primitives for cards.

Examples of unnecessary complexity:

- `IService`/`IRepository` abstractions for every class;
- dozens of empty packages created before behavior exists;
- generalized distributed rate limiter;
- full CoinGecko mapping of every Nobitex asset on each sync;
- all-market historical persistence;
- separate table/class for every card property;
- deep inheritance trees for card themes/elements.

## Quality rule

When choosing between “works only for current examples” and “correctly models the actual product contract”, choose the product contract.

When choosing between two designs that both satisfy the contract, choose the simpler one with fewer moving parts.