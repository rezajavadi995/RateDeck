# Implementation Phases

RateDeck is implemented in exactly **two major phases**. Do not invent Phase 3 for requirements already defined in this repository.

Each phase should be executed through small internal **checkpoints** with focused tests. Checkpoints are not extra product phases; they are a way to keep Codex changes reviewable.

---

# Phase 1 — Core Market, Conversion, Content and Admin

## Objective

Produce a clean, usable market/conversion bot core with dynamic providers, complete text/button/placeholder customization, diagnostics and Persian inline-first administration. Prove the architecture before building the expensive visual card product and server installer.

## Checkpoint 1A — Runtime + storage + routing

- Python project/package bootstrap;
- config loader;
- compact SQLite schema + deterministic migrations;
- audit/logging foundation;
- aiogram bot factory;
- admin authorization;
- explicit router ordering;
- `/start`, `/help`, `/market`, `/support`, optional `/about`, admin `/panel`;
- parser/fallback route collision tests;
- central callback codec and safe Telegram UI helpers.

Do not create Phase 2 card/upload/backup tables here.

## Checkpoint 1B — Market/provider core

- ASCII-output number formatter + Persian/Arabic/Latin input normalization;
- runtime Asset Registry and Alias Index;
- dynamic whole-market Nobitex discovery/snapshot;
- correct Rial -> Toman normalization;
- CoinGecko verified/lazy/batched mapping/enrichment;
- ExchangeRate fiat snapshot, public/keyed capability as supported;
- provider-specific state/freshness/cooldown/request counters;
- simple conservative provider runtime policy;
- `Retry-After`/429 backoff;
- one in-process singleflight lock per provider/capability;
- background refresh loop with modest jitter;
- partial-provider success isolation;
- last-known-good without fake freshness;
- bounded hot-set history only.

No generalized distributed quota framework, distributed lock, Redis or worker process.

## Checkpoint 1C — Parser + conversion + Stars

- strict compact parser using runtime aliases;
- Persian/English conversion words/forms;
- positive and false-positive corpus;
- group-safety foundation;
- graph-based conversion with inverse/direct/bridge edges;
- deterministic route policy;
- full provenance/freshness propagation;
- no-route/ambiguous handling;
- manual exact-package Telegram Stars pricing (`quantity price`), Persian-digit input accepted;
- no Stars interpolation by default.

## Checkpoint 1D — Complete content/button/custom-emoji admin + diagnostics

### Templates / commands / captions

- stable template registry/storage;
- customizable `/start`, `/help`, `/market`, `/support`, optional `/about` content;
- customizable price/conversion texts;
- card-caption master + field-fragment foundation ready for Phase 2;
- default/reset behavior;
- current-value display + safe button preview.

### Placeholder `{}` system

- central Placeholder Registry;
- per-placeholder key, scope, type, Persian description and sample;
- per-template allowed/required contracts;
- admin inline view of valid placeholders for the selected template;
- unknown/malformed placeholder rejection;
- literal-brace contract;
- field fragments (`{field.*}`);
- field cycle/depth/expanded-size guards;
- sample preview context;
- no unresolved placeholder leakage.

### Rich text / Premium Emoji

- entity-aware serializable rich document;
- automatic Telegram custom-emoji capture from admin input;
- no separate Premium Emoji manager;
- placeholder expansion before final entity compilation;
- central UTF-16 offset compiler/tests;
- ordinary emoji support;
- asset caption emoji metadata/editing;
- button custom-emoji icon capture using Telegram button semantics.

### Buttons

- central stable ButtonSpec/customization store;
- customizable designated label;
- styles only `default`, `primary`, `success`, `danger`;
- optional custom emoji icon;
- enable/disable only where safe;
- row/order only for menus declared configurable;
- admin cannot replace safe built-in action semantics with arbitrary callback text;
- callback <=64 UTF-8 bytes;
- safe grapheme-aware old/current label previews.

### Admin screens

Persian, inline-first, practically usable screens for:

- root panel;
- providers/API modes/keys/health/routing;
- assets/search/favorites/aliases/enable/family/caption emoji/mappings;
- templates/commands/fields/placeholders;
- buttons;
- Stars packages;
- diagnostics;
- logs/audit/system health.

Free text only where genuinely arbitrary.

### Diagnostics

Implement `docs/DIAGNOSTICS.md` Phase 1 checks:

- provider/API health/freshness/cooldown/counters/errors;
- asset/mapping/alias health;
- template/placeholder/field-cycle/length/compile diagnostics;
- button/callback/action diagnostics;
- rich/custom emoji diagnostics;
- parser self-test counts;
- DB/schema/background refresh/runtime checks;
- local Run All with **zero network calls**;
- explicit quota-aware Live API diagnostics.

### Security

- secrets redaction;
- keyed provider secret encryption at rest using maintained crypto library;
- master-key handling;
- delete API-key input message when possible;
- no plaintext key echo/log/diagnostic output.

## Phase 1 visual requirement

Do not build the professional card designer yet. A truthful text market response and a minimal diagnostic/simple render only if required to prove integration is enough.

## Phase 1 acceptance gate

Phase 1 is complete only when:

- real dispatcher commands/parser/admin work together;
- dynamic Nobitex discovery passes fixtures and optional bounded live smoke;
- provider freshness isolation and rate-limit/backoff tests pass;
- parser corpus and conversion provenance tests pass;
- all generated numbers are ASCII-digit formatted;
- admin authorization cannot be forged by callback;
- text/button/placeholder customization is genuinely usable, not stubbed;
- custom emoji capture/render/UTF-16 tests pass;
- diagnostics find intentionally broken fixture templates/buttons/callbacks and local Run All makes no network call;
- Stars exact-package behavior passes;
- full suite passes on exact head;
- no monkey patch;
- no provider HTTP in Telegram handlers;
- no finite hard-coded Nobitex universe;
- no all-market history explosion;
- no premature Phase 2 infrastructure.

Review Phase 1 before starting Phase 2.

---

# Phase 2 — Exceptional Cards + Operations/Installer

## Objective

Turn the correct Phase 1 core into the finished polished RateDeck product: exceptional customizable cards plus safe server operations and one-command installation.

## Checkpoint 2A — Card design system + renderer

- compact design-token model;
- asset-family registry;
- themes/layouts/chart-style registries;
- compatibility rules;
- generic fallback family;
- sparse asset overrides;
- deterministic Pillow renderer;
- 1080x1080 primary output, preferably 2x internal render/downsample where feasible;
- gradients/glass/surfaces/shadows/typography;
- robust Persian text + ASCII numeric values;
- render cache;
- no deep inheritance tree.

## Checkpoint 2B — Truthful charts + card elements

- bounded local-history integration;
- truthful recent windows where enough samples exist;
- smooth line/area styles;
- high/low/current markers;
- range/history-collecting fallback when insufficient;
- no fabricated trend points;
- data-driven elements: price, asset/logo, brand logo, title/subtitle, changes, high/low, source, timestamp, custom text, etc.;
- position/size/alignment/font/weight/opacity/visibility/layer controls.

## Checkpoint 2C — Persian Card Designer + caption delivery

- global defaults;
- family configuration;
- layout/theme/chart selection;
- asset override editor;
- inline move controls + step sizes;
- size/font/alignment/opacity/visibility/layer controls;
- logo upload/replace/remove;
- custom text layers;
- preview-first workflow;
- reset/inheritance behavior;
- parser result -> cached quote -> card -> customizable rich caption -> Telegram delivery;
- source/freshness/stale presentation;
- graceful text fallback on renderer failure according to policy;
- Phase 2 card diagnostics (font/logo/config/render/history).

## Checkpoint 2D — Terminal + installer + production hardening

### Terminal

English colored `ratedeck` control center:

- service status/start/stop/restart;
- logs/errors;
- DB status;
- backup/list/verify/restore;
- basic config;
- Telegram smoke;
- render test card;
- safe update/repair;
- uninstall scopes.

No provider/API product configuration in terminal.

### Installer/systemd

- safe idempotent `install.sh`;
- supported Debian/Ubuntu detection;
- app service user/directories as appropriate;
- venv/dependencies;
- `.env`/master-key/DB/assets preservation;
- DB init/migration;
- systemd unit;
- `/usr/local/bin/ratedeck` launcher;
- README one-line installer;
- fast-forward-safe updater;
- no blind hard reset/clean;
- backups before risky update/restore/migration.

### Final hardening

- rendering resource bounds;
- upload MIME/size/path safety;
- callback/button limits;
- provider rate-limit regression;
- log/diagnostic secret-redaction audit;
- dependency/config docs;
- production checklist.

## Phase 2 acceptance gate

Must satisfy `docs/DEFINITION_OF_DONE.md`, including:

- representative visual review/golden evidence;
- all card customizations work through real admin UI;
- full test suite pass;
- installer smoke + rerun/data-preservation evidence;
- provider budget/stale-state behavior remains correct;
- diagnostics Phase 2 card checks pass;
- no fake history;
- no monkey patches;
- docs/README installation commands match reality.

At this point the currently defined RateDeck scope is complete. New unrelated product ideas after this are future features, not an automatic Phase 3.

---

# Scope-change rule

If the owner requests a major feature during implementation, classify it as:

- correction required by the existing contract;
- small additive work in the active phase;
- future feature after the defined two-phase product.

Do not silently expand architecture to anticipate unspecified future features.