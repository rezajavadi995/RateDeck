# Implementation Phases

RateDeck implementation is intentionally divided into exactly two major phases. Codex should not collapse both into one large task.

---

# Phase 1 — Core Market Platform

## Objective

Produce a structurally clean, tested, usable market/conversion bot core with provider/admin/content foundations. It must prove the architecture before expensive visual tooling is added.

## Deliverables

### Project/runtime foundation

- Python package structure following `docs/ARCHITECTURE.md`;
- project metadata/dependencies;
- config loader;
- SQLite DB + versioned schema/migration foundation;
- repository interfaces/implementations;
- application composition root;
- aiogram bot factory;
- background lifecycle/scheduler;
- error boundary/correlation logging;
- admin authorization.

### Telegram routing

- explicit router registration order;
- `/start`;
- `/help`;
- `/market`;
- `/support`;
- optional `/about`;
- admin-only `/panel`;
- hidden `/price` and `/convert` compatibility aliases if useful;
- market parser handler;
- final fallback;
- router-order integration tests.

### Numeric/input core

- Persian/Arabic/Latin digit normalization;
- separators/character normalization;
- Decimal parser;
- ASCII-only generated number formatter;
- adaptive precision;
- tests.

### Asset Registry

- built-in fiat/manual/core metadata;
- dynamic discovered Nobitex assets;
- persisted asset identities;
- alias registry;
- admin aliases;
- enabled/disabled;
- family/category field;
- caption emoji metadata model;
- recent/favorite foundation;
- refresh-safe merge semantics.

### Nobitex provider

- validated async public market snapshot;
- whole-market discovery/snapshot path;
- `rls` -> Toman handling;
- useful market metadata;
- partial malformed-market isolation;
- provider-specific cache/state;
- conservative request budget;
- 429/backoff;
- singleflight;
- tests from fixtures.

### CoinGecko provider

- async global crypto/USD provider;
- verified CoinGecko ID mapping store;
- safe auto-unique/ambiguous/unmapped states;
- batched price request;
- 24h/updated metadata where available;
- mapping metadata refresh cadence;
- provider-specific cache/state/budget;
- tests.

### ExchangeRate provider

- open and keyed capability abstraction where current provider supports them;
- USD-base fiat snapshot;
- supported-code sync where applicable;
- no local-Toman authority leak;
- attribution capability metadata for open mode;
- provider-specific cache/state/budget;
- safe secret storage for keyed mode;
- tests.

### Provider orchestration

- provider registry;
- budget manager;
- persisted cooldown;
- singleflight/coalescing;
- background refresh;
- jitter;
- partial-success isolation;
- last-known-good without fake freshness;
- health service;
- provenance.

### Parser

- runtime alias index;
- compact strict grammar;
- dynamic symbols;
- Persian/English conversion words;
- group-safety mode foundation;
- positive + false-positive corpus.

### Conversion graph

- typed edges;
- inverse edges;
- deterministic path search/score;
- direct/bridge conversions;
- domain authority preferences;
- freshness propagation;
- provenance;
- no route/ambiguous behavior;
- Decimal tests.

### Telegram Stars manual pricing

- admin package CRUD;
- compact `quantity price` parser;
- exact package behavior;
- no interpolation by default;
- audit history.

### Content/templates

- template registry/storage;
- scoped placeholder contracts;
- required/allowed validation;
- sample preview context;
- field fragments;
- master captions/content foundation;
- reset/default behavior.

### Rich text/custom emoji

- entity-aware internal rich document representation;
- capture Telegram custom emoji IDs from admin input;
- placeholder expansion before entity compilation;
- UTF-16 offset compiler/tests;
- ordinary emoji support;
- asset caption emoji storage;
- button custom emoji icon capture foundation;
- no separate premium emoji manager.

### Button/callback UI foundation

- central ButtonSpec/registry/storage where customization applies;
- styles: default/primary/success/danger only;
- versioned callback codec <=64 bytes;
- safe label preview/truncation;
- pagination helpers;
- edit-in-place adapter;
- inline-first admin controls.

### Telegram admin core

At minimum usable Persian screens for:

- root panel;
- provider health/mode/enable settings;
- asset list/search/favorites/alias/enable/family/caption emoji basics;
- content/template editors;
- button basics;
- Stars packages;
- health/log/audit summaries;
- backup request foundation if safe.

Full card designer belongs to Phase 2.

### Observability/security

- structured logging;
- redaction;
- provider events;
- admin audit table/service;
- encrypted provider keys at rest;
- master-key handling foundation;
- no plaintext key echo.

## Phase 1 visual requirement

A minimal text response and/or deliberately simple diagnostic image may be used to prove the market pipeline. Do not spend Phase 1 building the full card design product.

## Phase 1 acceptance gate

Phase 1 is complete only when:

- core commands run through real dispatcher composition;
- dynamic Nobitex discovery works from fixture and optional live smoke;
- provider freshness isolation regression passes;
- parser corpus passes;
- conversion graph/provenance passes;
- admin cannot be forged by callback;
- template/custom emoji core passes;
- Stars exact-package behavior passes;
- full test suite passes on exact head;
- docs match runtime;
- no monkey patch exists;
- no provider HTTP call is found in handlers;
- no unbounded hard-coded Nobitex asset list exists.

Do not start Phase 2 until this gate is reviewed.

---

# Phase 2 — Visual Product & Operations

## Objective

Turn the correct Phase 1 core into the polished RateDeck product: exceptional cards, advanced admin customization and safe server operations/install.

## Deliverables

### Card design system

- design tokens;
- family registry;
- theme registry;
- layout registry;
- chart-style registry;
- compatibility rules;
- generic fallback family;
- sparse asset overrides.

### Professional renderer

- Pillow renderer;
- 2x high-resolution internal render and high-quality downsample where feasible;
- 1080x1080 primary output;
- shapes/gradients/glass/surfaces/shadows;
- robust Persian text layout;
- ASCII numeric glyph policy through formatted values;
- deterministic output;
- render cache.

### Chart/history product

- persisted local snapshot history;
- retention/downsampling;
- recent chart windows as data permits;
- smooth truthful line/area styles;
- high/low/current markers;
- missing-history fallback/range state;
- no fabricated trend points.

### Card element model

- standard data-driven elements;
- position/size/alignment;
- font/size/weight;
- visibility/opacity/layer;
- logo slots;
- custom text layers;
- reset-to-default resolution.

### Card Designer admin

- global theme/layout/chart selection;
- family configuration;
- asset override editor;
- inline movement controls;
- step sizes;
- size/font/alignment/opacity/visibility/layer controls;
- logo upload/replace/remove;
- custom text layers;
- preview-first workflow;
- reset override;
- safe pagination/search for assets.

### Card/caption delivery

- parser result -> cached quote -> card render/cache -> Telegram send;
- customizable rich caption;
- source/freshness fields;
- stale indication;
- graceful text fallback if rendering fails according to product policy.

### Admin polish

Complete/clean Persian inline-first UX for:

- providers/API key/public-keyed modes;
- mapping diagnostics;
- rate budgets/cooldowns;
- asset metadata;
- content/fields/placeholders;
- buttons/styles/custom emoji;
- card designer;
- Stars;
- logs/audit;
- backups;
- system/health.

### Terminal control center

- English colored menu;
- global `ratedeck` launcher;
- service start/stop/restart/status;
- app status;
- logs/errors;
- DB status;
- backup/list/verify/restore;
- basic config;
- Telegram test;
- render test card;
- safe update/repair;
- uninstall scopes.

No API/provider product settings in terminal.

### Installer/systemd

- safe idempotent `install.sh`;
- supported Debian/Ubuntu detection;
- service user/directories;
- venv/dependencies;
- `.env` preservation;
- encryption key preservation;
- DB initialization/migration;
- systemd unit;
- launcher;
- README one-liner;
- fast-forward safe updater;
- no blind hard reset/clean;
- backups before update/restore/risky migration.

### Final hardening

- rendering resource bounds;
- upload validation/path safety;
- callback/button limits;
- rate-budget regression;
- provider terms/capability docs;
- log redaction audit;
- dependency/config docs;
- production checklist.

## Phase 2 acceptance gate

Must satisfy `docs/DEFINITION_OF_DONE.md`, including:

- representative visual review/golden evidence;
- full test suite pass;
- installer smoke evidence;
- rerun/update/data-preservation checks;
- provider budget and stale-state behavior;
- no fake history;
- no monkey patches;
- docs/README installation instructions match actual commands.

---

# Scope-change rule

If the owner asks for a new major feature during implementation, do not silently squeeze it into the active phase. Classify it as:

- required correction to existing contract;
- small additive feature in active phase;
- deferred post-Phase-2 feature.

Document the decision before adding architecture that expands the product unexpectedly.
