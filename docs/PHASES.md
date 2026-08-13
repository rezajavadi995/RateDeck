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

No generalized distributed quota framework, distributed lock, Redis, PostgreSQL, NATS or worker process.

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

Turn the correct Phase 1 core into the finished polished RateDeck product: exceptional customizable cards plus safe server operations and one-command installation, while fitting the documented 4 GB RAM / 2 vCPU shared-host target without destabilizing StarzYFire.

Read `docs/RESOURCE_AND_ISOLATION.md` before Phase 2 implementation.

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
- bounded render cache;
- default render concurrency 1 on target shared host unless measurement proves more safe;
- no deep inheritance tree.

## Checkpoint 2B — Truthful charts + card elements

- bounded hot-set local-history integration;
- explicit age/row/storage retention;
- truthful recent windows where enough samples exist;
- smooth line/area styles;
- high/low/current markers;
- range/history-collecting fallback when insufficient;
- no fabricated trend points;
- data-driven elements: price, asset/logo, brand logo, title/subtitle, changes, high/low, source, timestamp, custom text, etc.;
- position/size/alignment/font/weight/opacity/visibility/layer controls;
- bounded render queue/backpressure and cleanup of temporary/intermediate images.

## Checkpoint 2C — Persian Card Designer + caption delivery

- global defaults;
- family configuration;
- layout/theme/chart selection;
- asset override editor;
- inline move controls + step sizes;
- size/font/alignment/opacity/visibility/layer controls;
- logo upload/replace/remove with size/type/count bounds;
- custom text layers;
- preview-first workflow;
- reset/inheritance behavior;
- parser result -> cached quote -> card -> customizable rich caption -> Telegram delivery;
- source/freshness/stale presentation;
- graceful text fallback on renderer failure according to policy;
- Phase 2 card diagnostics (font/logo/config/render/history/resource queue).

## Checkpoint 2D — Terminal + installer + shared-host production hardening

### Terminal

English colored RateDeck control center with **global shell command `price`**:

- bare `price` opens the interactive menu from any working directory;
- `/usr/local/bin/price -> /opt/ratedeck/.venv/bin/price` verified symlink;
- `price status|start|stop|restart` convenience subcommands;
- Quick Setup / per-setting Config for bot token, admin IDs, log level;
- exact Service submenu with `Status / Start / Stop / Restart / Enable at boot / Disable at boot`;
- `Service -> Start` is the normal menu action that runs the bot;
- local App Status with RateDeck RSS/CPU/DB/disk/cache/history/backups/render queue/refresh heartbeat;
- logs/errors;
- DB status;
- backup/list/verify/restore;
- Telegram smoke;
- render test card using the normal render resource gate;
- smart update/repair;
- uninstall scopes.

No provider/API product configuration in terminal.

Opening `price` must not start a second bot, scheduler or provider refresher.

### Smart update

- validate RateDeck repo/path/remote/branch;
- fetch/compare exact local/remote commits;
- show up-to-date/update-available/diverged state;
- refuse unsafe dirty/diverged normal update;
- no-op cleanly when already current;
- show changed commits/files on request;
- verify disk/backup capacity;
- create/verify pre-update backup;
- fast-forward-only normal code update;
- reinstall dependencies only if manifests changed or repair requests it;
- run only pending RateDeck migrations;
- repair/verify `price` launcher/systemd only when relevant;
- smoke-check then restart/verify `ratedeck.service` according to explicit update policy;
- report every executed/skipped step;
- no blind `git pull`, `reset --hard` or `clean -fd` normal path.

### Installer/systemd

- safe idempotent `install.sh`;
- supported Debian/Ubuntu detection;
- exact RateDeck-owned paths separated from StarzYFire;
- dedicated `ratedeck` service user;
- venv/dependencies isolated from system Python/StarzYFire;
- protected config/master key outside git worktree;
- SQLite DB/data/cache/history in RateDeck-owned data path;
- DB init/migration;
- `ratedeck.service` only;
- Python console entry point `price` inside RateDeck venv;
- verified `/usr/local/bin/price` symlink, with safe refusal on unrelated existing command collision;
- README one-line installer;
- backups before risky update/restore/migration;
- no Redis/PostgreSQL/NATS changes;
- no firewall/inbound port changes by default;
- no operations against `/opt/star`, `starzyfire-*` or StarzYFire-owned resources.

### Resource/coexistence validation

On representative 2 vCPU / 4 GB RAM / 40 GB hardware before production-ready claim:

- record baseline with StarzYFire running;
- measure RateDeck idle/warmed RSS/CPU;
- measure bounded provider refresh behavior;
- measure representative card-render peak with configured concurrency;
- repeat refresh/render cycles to detect sustained memory growth;
- exercise `price` menu/status/update preflight without spawning another bot;
- verify no unexpected inbound listener;
- verify cache/history/log/backups remain bounded;
- observe StarzYFire health/latency during RateDeck bursts without modifying it;
- treat meaningful StarzYFire instability or sustained host pressure as a release blocker.

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
- installer smoke + rerun/data-preservation/isolation evidence;
- `price` launcher works from arbitrary paths and service shortcuts/menu actions are consistent;
- smart update handles no-op/dirty/update/dependency/migration/backup/restart verification correctly;
- terminal Quick Setup and local resource status work as specified;
- provider budget/stale-state behavior remains correct;
- diagnostics Phase 2 card checks pass;
- resource/coexistence measurements are reported rather than assumed;
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
