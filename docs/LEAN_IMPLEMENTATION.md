# Lean Implementation Guardrails

RateDeck must be neither a toy script nor a miniature enterprise platform. This document defines the intended middle ground.

## Core rule

Choose the **smallest design that cleanly satisfies a concrete current requirement** and leaves a reasonable seam for the next known requirement.

Do not build infrastructure merely because it might be useful someday.

## What “modular” means here

Modular means responsibilities are separable and testable. It does not mean maximum file count.

Good early shape:

```text
ratedeck/
  app/
  bot/
  market/
  content/
  storage/
  diagnostics/
  observability/
  security/
  cards/          # mostly Phase 2
  cli/            # mostly Phase 2
```

Inside a package, related small classes/functions may share a module until there is a real reason to split them.

Do not create empty directories/files to match a theoretical tree.

## Explicitly avoid

- dependency-injection frameworks;
- generic repository frameworks;
- service locators;
- event buses/CQRS;
- plugin frameworks;
- microservices;
- Redis/PostgreSQL in the initial product;
- distributed locks;
- background worker fleets;
- browser/headless rendering;
- one Protocol/ABC per internal class;
- one table per possible future setting;
- one file per tiny dataclass;
- “manager”, “factory” and “strategy” classes that only forward one call and add no policy.

## Where abstraction is justified

Use a boundary abstraction when at least one is true:

1. multiple concrete implementations exist now (e.g. market providers);
2. the dependency is external/volatile (HTTP provider, storage, Telegram adapter);
3. tests need a clean seam around I/O;
4. the product contract explicitly requires runtime substitution/routing.

Otherwise prefer a normal typed function/class and explicit composition.

## Provider runtime: keep it simple

Default single-process provider runtime should be understandable from a few modules:

- provider adapter(s);
- provider policy/runtime state;
- market service/orchestrator;
- background refresh loop.

A provider policy needs only what is required by real APIs:

- refresh interval/minimum request interval;
- enabled/mode;
- last attempt/success/failure;
- request counters for diagnostics;
- `Retry-After`/429 cooldown;
- consecutive failure/backoff state;
- one in-process singleflight lock.

Do not implement generalized distributed/token-bucket scheduling unless an actual provider contract makes the simpler model insufficient.

## Dynamic Nobitex universe without quota waste

Nobitex discovery may expose hundreds of markets in one whole-market snapshot. RateDeck should ingest that efficiently.

Do **not** interpret “support every Nobitex market” as “call every other provider for every Nobitex asset”.

CoinGecko enrichment should be batched and demand-aware:

- known/core assets;
- favorites;
- recently used assets;
- assets explicitly requested for global USD/card enrichment;
- explicitly verified mappings.

Ambiguous or unused discovered assets may remain local-market-only until needed.

## History must stay bounded

Persisting all 495+ market pairs every refresh is prohibited by default.

Use a hot-set model:

- core assets;
- favorites;
- recently requested assets;
- assets with configured card overrides/active monitoring.

Sample at a bounded cadence and enforce both age retention and total storage/row bounds.

For an asset without enough local history, render a truthful fallback such as current price + 24h high/low/provider metadata or “history collecting”. Never synthesize points.

## SQLite schema discipline

Phase 1 should create only tables needed by Phase 1 runtime behavior.

Prefer compact rows with validated JSON for flexible configuration where relational querying is not needed.

Examples where JSON is appropriate:

- provider capability metadata;
- template rich-document payload;
- sparse card override configuration (Phase 2);
- safe diagnostic metadata.

Do not split every configuration property into a dedicated table.

## Admin state discipline

Use Telegram FSM only while waiting for actual free-form input such as:

- template body;
- API key;
- alias/search term;
- Stars package line;
- uploaded logo/image;
- arbitrary custom text.

Finite settings stay inline and stateless/short-lived where possible.

Do not create long wizard chains when one screen + inline controls is sufficient.

## Content system complexity budget

The content system may be sophisticated because it is a real product requirement, but its complexity must be centralized:

- one Placeholder Registry;
- one template validator;
- one rich-document model;
- one Telegram compiler;
- one safe preview/length layer;
- one button-spec/callback layer.

Do not duplicate rich-text/placeholder/button rendering logic per router.

## Diagnostics complexity budget

Diagnostics should compose existing services and validators rather than create a second implementation of the system.

A diagnostic check should normally be a small read-only function returning a typed result:

```text
id / severity / status / summary / details / suggested_action
```

Live network diagnostics must reuse provider adapters and rate policies.

## Cards

Card quality is allowed to be the most visually sophisticated part of the product, but the implementation should still be data-driven rather than class-heavy.

Prefer:

- token dictionaries/dataclasses;
- registered layout functions/objects;
- reusable drawing primitives;
- sparse per-asset overrides;
- deterministic Pillow renderer.

Avoid a deep inheritance hierarchy for every card element/theme/asset.

## Split triggers

Split a module when one or more is true:

- it owns two distinct domains;
- unrelated imports/tests are accumulating;
- changes to one responsibility repeatedly risk another;
- the module becomes difficult to review because it contains separate workflows.

Do not split solely to satisfy an arbitrary line count.

## Dependency budget

Prefer standard library + a small set of well-maintained dependencies that provide real value (Telegram framework, async HTTP, Pillow, crypto-at-rest helper if needed, test tooling).

Every new dependency should answer: what real problem does this solve better than a small local implementation?

## Completion test

A good RateDeck implementation should be understandable by a competent Python developer without first learning a custom framework invented inside the repo.

If a feature can be removed without changing any real user/admin behavior, operational safety, provider correctness or testability, it is a candidate for deletion/deferment.