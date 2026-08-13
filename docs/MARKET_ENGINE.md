# Market Engine Contract

## Goals

The market engine owns the normalized, validated, cached view of rates and market metadata. It is provider-aware but provider-agnostic at its public boundary.

Telegram handlers and card renderers consume domain snapshots from this engine; they do not fetch external APIs.

## Core domain objects

### Asset

Conceptual fields:

- canonical key (stable internal identifier);
- symbol;
- display name;
- category/family;
- aliases;
- enabled state;
- source identities (Nobitex symbol, CoinGecko ID, fiat code, manual ID);
- available quote currencies/markets;
- caption emoji metadata;
- card-family override;
- mapping confidence/status;
- created/discovered/updated timestamps.

### MarketEdge

A directed conversion edge with:

- source asset;
- target asset;
- rate as Decimal;
- provider/source;
- source market/pair;
- fetched/snapshot timestamp;
- validation/freshness status;
- bid/ask/latest/mark metadata where available;
- direct vs derived classification;
- optional confidence/quality score.

The graph may synthesize an inverse edge from a valid positive direct edge while preserving provenance.

### ProviderSnapshot

Provider-specific snapshot with:

- provider ID;
- fetched_at;
- source_updated_at when supplied by provider;
- status;
- validated edges;
- metadata;
- latency;
- error code/category if failed;
- last-known-good linkage/age.

No global timestamp may refresh all providers at once.

### Quote/ConversionResult

Must include:

- input amount/source/target;
- final Decimal value;
- selected path;
- every path edge/provider;
- oldest edge timestamp/freshness;
- whether any edge is stale/derived/manual;
- human-readable source summary;
- warnings if appropriate.

## Dynamic Nobitex discovery

The primary Nobitex refresh should use the most efficient validated whole-market snapshot available from the public market stats surface.

Observed live behavior on 2026-08-13: an unfiltered stats request returned 495 market keys in a single successful response. RateDeck may use this efficient behavior while treating it as provider behavior that can change.

### Parsing market keys

A key such as:

`xaut-rls`

is parsed into source `xaut` and quote `rls` at the provider adapter boundary.

Nobitex `rls` is Rial. RateDeck user-facing `IRT/Toman` conversion must explicitly divide Rial-denominated values by 10 when creating the Toman edge. Keep both identities distinct internally when useful; never label raw Rial as Toman.

### Validation

For every market entry:

- key shape must be parseable;
- numeric values must parse as finite Decimal;
- latest/mark/bid/ask values used as rates must be > 0;
- absurd/invalid structures are rejected, not cached as valid;
- `isClosed` is preserved as market metadata;
- zero-volume markets may still be represented but should carry quality metadata;
- asset identity must remain stable across refreshes.

One malformed market must not poison the entire valid snapshot unless the response envelope itself is unusable.

### Asset registry sync

A refresh can discover new assets. Sync behavior:

- insert new discovered identity;
- update markets/metadata for existing assets;
- never delete an asset merely because it disappears for one refresh;
- mark missing/retired state only after an explicit policy/threshold;
- preserve admin aliases/style overrides;
- preserve history.

## CoinGecko mapping

CoinGecko is global crypto/USD enrichment, not the source of truth for asset identity.

Mapping states:

- `verified` — explicit built-in/admin-confirmed CoinGecko ID;
- `auto_unique` — automatically resolved only when mapping evidence is uniquely safe;
- `ambiguous` — multiple candidates; no automatic USD binding;
- `unmapped` — no candidate;
- `disabled` — admin declined mapping.

Never silently choose a CoinGecko asset solely because its symbol matches when multiple candidates exist.

### Mapping sync cadence

Coin list/mapping metadata changes much less frequently than price data. Cache mapping discovery for a long period (for example daily) and do not call the full coin list per user request or per short price refresh.

### Price batching

Request multiple verified CoinGecko IDs per provider call within provider-supported request constraints. Do not make one call per asset.

## Fiat registry

The fiat provider supplies supported currency codes and a USD-based conversion snapshot. Cache supported-code discovery separately from rate refresh.

Fiat edges must not override local-market Toman edges.

## Manual Stars pricing

Stars packages are separate from the normal continuous rate graph unless an explicit package conversion use-case is valid.

Stored package example:

- quantity: Decimal/integer `50`;
- price_toman: Decimal `125000`;
- source: `manual_stars_package`;
- updated_at;
- enabled.

Default behavior:

- exact package matches are valid;
- no interpolation;
- no extrapolation;
- no fabricated USD/TON conversion unless explicitly requested and supported through a truthful conversion path.

## Cache model

### Provider-specific state

For each provider persist:

- last_attempt_at;
- last_success_at;
- last_failure_at;
- last_error_category;
- cooldown_until;
- consecutive_failures/penalty level;
- latest validated snapshot reference;
- last-known-good snapshot reference;
- configured refresh interval;
- hard/min request interval;
- request budget counters where meaningful.

### Freshness

Freshness is evaluated per edge/provider. A conversion path's effective freshness is constrained by its oldest/least-fresh required edge.

A successful CoinGecko refresh cannot refresh Nobitex age. A successful fiat refresh cannot refresh CoinGecko age.

### Last-known-good

When policy permits display use, a stale LKG snapshot may be returned with explicit stale metadata. It is never written back with a new success timestamp.

Admin health surfaces must distinguish:

- fresh success;
- stale LKG;
- cooldown;
- disabled;
- no data;
- malformed response;
- auth/quota error.

## Refresh orchestration

### Background-first

Normal user requests read cached snapshots. Background refresh owns provider traffic.

### Singleflight

For each provider/capability, at most one refresh leader runs at a time in the default single-process runtime. Followers reuse the leader result or current valid cache.

### Jitter

Scheduled refreshes use small jitter rather than all providers firing at the same second.

### Partial success

If CoinGecko fails while Nobitex and fiat succeed:

- record CoinGecko failure;
- keep CoinGecko LKG with old timestamp if allowed;
- commit valid Nobitex/fiat snapshots independently;
- do not label the whole market engine “fresh” as one undifferentiated state.

## Rate budget manager

Provider calls must pass through a central budget gate.

Conceptual state:

- min interval;
- rolling/minute allowance when known;
- monthly/daily quota if known;
- request count observed by RateDeck;
- Retry-After support;
- 429 penalty/cooldown;
- manual refresh cooldown;
- next allowed request time.

Provider published maximums are **ceilings, not targets**. RateDeck should operate far below them through batching/caching.

A manual admin “test/refresh” does not bypass a hard cooldown. It should report when the next safe attempt is allowed.

## History

After each validated market snapshot, persist selected normalized points needed for cards/history.

Do not store every redundant field forever. Use retention/downsampling policy:

- short-window raw samples for recent charts;
- optional aggregated older points;
- prune by age/asset activity.

The exact retention policy is configurable and tested.

## Derived routes

Examples:

- TON -> USD via verified CoinGecko direct price;
- TON -> IRT via a direct local market when available;
- asset -> USDT -> IRT via Nobitex when no direct IRT pair exists;
- fiat EUR -> USD via ExchangeRate;
- BTC -> EUR via BTC/USD (CoinGecko) + USD/EUR (fiat), if that route is selected by policy.

Derived rates must carry the full component path. Never render “Source: Nobitex” when the actual result used Nobitex + CoinGecko + ExchangeRate.

## Route quality/scoring

Conversion route selection should be table-driven. Factors may include:

1. direct edge preferred;
2. domain-authoritative source preferred for target market;
3. fewer hops;
4. fresher edges;
5. non-stale over stale;
6. verified mapping over ambiguous/derived mapping;
7. avoid loops and unnecessary round-trips.

Policy examples:

- IRT/Toman target: prefer direct Nobitex local edge.
- USD crypto target: prefer verified CoinGecko direct USD edge.
- global fiat: prefer ExchangeRate fiat edge.

The routing service should be deterministic for the same graph/policy.
