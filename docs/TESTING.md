# Testing Strategy

## Testing philosophy

Tests must validate behavior/contracts, not implementation trivia. A green suite is evidence only when it exercises the real boundaries relevant to the change.

Forbidden:

- weakening assertions to make a failing change pass;
- tests that merely duplicate the implementation expression;
- synthetic monkey-patch installation tests;
- claiming live provider/Telegram behavior from mocked tests;
- deleting meaningful regression tests without replacing the behavior coverage;
- updating visual golden files without reviewing the visual change.

Do not use Ruff as a validation step in this repository.

## Test layers

### Unit

Small deterministic domain logic:

- numeric normalization/formatting;
- alias normalization/index;
- parser grammar;
- conversion route scoring;
- placeholder validation;
- callback codec;
- rich-text AST/UTF-16 offsets;
- card token/layout resolution;
- rate-budget state transitions.

### Adapter/provider fixture tests

Use captured/minimal fixtures for provider JSON:

- valid Nobitex full snapshot;
- invalid envelope;
- one malformed market among many;
- closed/zero-volume market;
- RLS -> Toman conversion;
- CoinGecko multi-ID response;
- ambiguous/missing CoinGecko mapping;
- ExchangeRate open/keyed success/errors;
- 429/Retry-After/quota conditions.

Network is not required for default unit suite.

### Repository/integration

Temporary SQLite DB:

- schema initialization/migrations;
- provider state persistence;
- template revisions;
- encrypted secret round-trip with test key;
- audit events;
- history retention;
- backup consistency helpers.

### Dispatcher/router integration

Use the actual aiogram dispatcher composition where practical to prove:

- `/panel` beats market parser;
- admin FSM text beats market parser;
- explicit commands beat generic parser;
- callbacks go to correct namespace;
- fallback does not steal valid market intent;
- non-admin cannot execute admin callback by forging callback data;
- group parser strictness modes.

Router order is behavior and receives dedicated regression coverage.

### Rendering tests

Phase 2:

- dimensions/mode;
- deterministic config resolution;
- generic unknown asset;
- extreme number lengths;
- positive/negative/zero change;
- long Persian/Latin asset name;
- missing logo/font/history;
- stale state;
- theme/family/layout compatibility;
- logo upload validation;
- history chart truthfulness;
- visual/golden representative set.

### Installer/CLI tests

- shell/static syntax checks where appropriate;
- config preservation;
- update dirty-tree refusal;
- launcher resolution;
- CLI command dispatch;
- backup/restore helpers;
- systemd template sanity;
- disposable environment smoke when available.

## Parser corpus

Maintain data-driven cases rather than one test method per spelling.

Categories:

1. Latin inputs;
2. Persian digits;
3. Arabic digits;
4. Persian decimal/grouping;
5. zero-width variants;
6. Persian aliases;
7. multi-word aliases;
8. compact no-space form;
9. dynamic discovered symbols;
10. conversion words `به`, `to`;
11. default-target conversions;
12. ambiguous aliases;
13. ordinary conversation false positives;
14. long input rejection;
15. group strictness.

Every production parser bug should add a regression case.

## Number-output contract test

Add a helper assertion that RateDeck-generated numeric fields never contain Persian/Arabic digit codepoints.

Use it across representative text and card-data formatting tests.

This does not mean user-authored template prose is rewritten; it applies to generated number values/placeholders.

## Dynamic universe tests

Prove:

- new Nobitex market appears after sync without source-code asset list edit;
- admin alias/disable/family override survives refresh;
- temporarily missing market is not immediately hard-deleted;
- malformed asset key is skipped safely;
- RLS market yields correct IRT edge;
- many markets are processed from one snapshot;
- no per-asset HTTP behavior exists in the normal refresh path.

## Freshness/cooldown regression tests

Critical regression:

1. provider A data is old;
2. provider B refreshes successfully;
3. provider A remains old/stale.

Also test:

- failed provider refresh retains original LKG success timestamp;
- 429 persists cooldown;
- process/service object recreation reads persisted cooldown;
- manual refresh respects hard cooldown;
- concurrent refresh calls coalesce.

## Conversion graph tests

- direct pair preferred;
- inverse edge;
- USDT bridge;
- IRT bridge;
- crypto/USD via verified CoinGecko;
- fiat path;
- no route;
- loop prevention;
- max hops;
- stale path vs fresher path;
- domain authority scoring;
- full provenance preserved;
- ambiguous CoinGecko edge excluded.

Use exact Decimal expected values where practical.

## Rich-text/custom emoji tests

Must include:

- Telegram custom emoji entity capture;
- ordinary Unicode emoji;
- Persian prefix before emoji;
- emoji before/after placeholder;
- placeholder expands to longer/shorter text;
- surrogate pairs and UTF-16 offset correctness;
- formatting entity nesting/overlap rules supported by Telegram;
- dynamic placeholder escaping;
- button icon extraction;
- unsupported multiple custom emoji on button handled deterministically.

## Telegram UI safety tests

- callback at 64 bytes accepted;
- 65+ bytes rejected before button creation;
- no secret in callback payload;
- long current template label safely truncated;
- grapheme cluster not split;
- pagination boundaries (empty/first/middle/last);
- callback promptly answered in representative admin path;
- `Message is not modified`/edit fallback handled centrally without duplicate mutations.

## Provider integration/live smoke

Live provider tests must be separate/opt-in and conservative. They should:

- not run on every normal unit invocation;
- honor provider budgets;
- perform a bounded number of calls;
- never require real secret values in source;
- report “not run” distinctly from “passed”.

Likewise Telegram live smoke is owner-run/staging evidence, not implied by mocks.

## Phase completion commands

Codex must define the project's actual commands once scaffolding exists. Expected categories:

- focused pytest modules while developing;
- full `python -m pytest` at phase completion;
- `python -m compileall` / import smoke as appropriate;
- installer shell syntax/smoke checks in Phase 2.

If optional system tools/dependencies are unavailable, report the blocker and what did/did not run. Never turn “not runnable” into “passed”.

## Coverage quality

A raw percentage is secondary. Critical contracts require direct tests even if overall coverage is high:

- router ordering;
- provider freshness isolation;
- rate limit cooldown;
- dynamic discovery;
- conversion provenance;
- custom emoji offsets;
- callback 64-byte limit;
- update/data safety.
