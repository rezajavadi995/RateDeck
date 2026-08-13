# Market Engine Contract

## Goal

The market engine owns the normalized, validated, cached view of rates and conversion metadata. Telegram handlers and card renderers consume this service; they do not fetch providers directly.

The implementation must stay lightweight: a few typed models/services are preferred over a framework of manager classes.

## Core models

### Asset

Conceptual fields:

- stable internal key/id;
- symbol/display name;
- family/category;
- enabled state;
- aliases;
- provider identities/mappings;
- available markets/quote currencies;
- caption emoji metadata;
- mapping status/confidence;
- discovery/update timestamps.

### MarketEdge

Directed conversion edge:

- source asset;
- target asset;
- exact Decimal rate;
- provider/source market;
- fetched/source timestamp;
- status/freshness;
- optional bid/ask/latest/mark quality metadata;
- direct/derived classification;
- provenance.

A valid positive direct edge may produce an inverse edge while retaining provenance.

### ProviderResult

Normalized provider refresh result:

- provider ID/capability;
- fetched_at/source_updated_at;
- validated edges;
- discovered assets/markets where relevant;
- latency;
- rejected-item count;
- sanitized failure category/details when failed.

Provider runtime timestamps live independently per provider/capability.

### ConversionResult

Includes:

- source amount/source/target;
- exact final Decimal value;
- selected edge path;
- providers/markets used;
- oldest/effective freshness;
- stale/manual/derived flags;
- source summary/warnings.

## Dynamic Nobitex discovery

Use the efficient whole-market public snapshot when validated/current behavior supports it.

Observed live on 2026-08-13: unfiltered stats returned 495 market keys in one successful response.

Do not maintain a finite manual Nobitex symbol list.

### Market key parsing

Example:

`xaut-rls`

Provider adapter resolves base `xaut`, quote `rls`.

Nobitex `rls` is Rial. User-facing Toman is explicitly derived by dividing Rial values by 10. Never label raw Rial as Toman.

### Validation

Per market:

- parseable key;
- finite Decimal numeric fields;
- rate used for conversion >0;
- malformed market isolated rather than poisoning other valid entries;
- `isClosed` preserved;
- zero-volume may remain informational/low-quality, not silently equivalent to healthy liquid market;
- stable asset identity preserved across refreshes.

### Asset sync

Refresh may insert new assets/markets and update existing provider metadata.

It must not:

- delete an asset from one missing refresh;
- delete admin aliases/customization;
- discard history because a market temporarily disappears.

## CoinGecko enrichment

CoinGecko provides global crypto/USD enrichment; it is not the master identity source for all assets.

Mapping states may include:

- `verified`;
- safe `auto_unique`;
- `ambiguous`;
- `unmapped`;
- `disabled`.

Never silently choose among symbol collisions.

### Demand-aware mapping

Supporting all Nobitex markets does **not** require resolving all of them against CoinGecko.

Mapping/price enrichment should prioritize:

- known/core assets;
- favorites;
- recently requested assets;
- explicitly verified/admin-selected mappings;
- assets currently needing global USD/card enrichment.

Batch within provider constraints. Cache mapping metadata much longer than price data.

Unused/ambiguous assets may remain fully functional for Nobitex local-market conversion without CoinGecko enrichment.

## Fiat provider

ExchangeRate-like fiat provider supplies supported global fiat codes/rates.

Its official IRR rate is not silently treated as Iranian free-market Toman authority.

## Stars

Telegram Stars uses exact admin-defined packages, separate from continuous market rates by default.

Example:

`50 Stars = 125000 Toman`

Rules:

- exact package match;
- no interpolation/extrapolation by default;
- audit changes;
- no fabricated USD/TON conversion unless a truthful explicit policy/path exists.

## Provider runtime state

Keep each provider/capability independent:

- enabled/mode;
- configured refresh/minimum interval;
- last attempt/success/failure;
- last error category/latency;
- cooldown until;
- consecutive failure/backoff state;
- RateDeck request counters/window metadata;
- last-known-good metadata.

No global success timestamp.

## Background-first refresh

Normal user requests read current validated state.

One lightweight lifecycle loop schedules providers independently and:

- obeys policy/cooldown;
- uses modest jitter;
- coalesces concurrent refreshes;
- commits partial provider success independently;
- does not rewrite stale LKG timestamps as new success.

## Singleflight

Default deployment is one process. One `asyncio.Lock`/equivalent per provider/capability is sufficient.

Do not add distributed locking infrastructure.

## Rate-limit policy

Provider call permission is based on a simple provider policy/runtime state:

- minimum request interval;
- configured refresh interval;
- known quota/request counters where meaningful;
- `Retry-After`;
- 429 cooldown/backoff;
- next allowed call.

Manual admin live test/refresh obeys hard cooldown. It does not contain a “force bypass quota” path.

Do not build a generalized token-bucket/distributed quota platform unless real provider behavior proves the simple model insufficient.

## Freshness / LKG

Freshness is per edge/provider.

A conversion path inherits the weakest/oldest required edge freshness.

A stale last-known-good value may be used only according to display policy and always retains its original success timestamp/stale label.

Admin distinguishes:

- fresh;
- stale LKG;
- cooldown;
- disabled;
- no data;
- malformed/auth/quota failure.

## Conversion graph

The graph is rebuilt/updated from current validated edges.

Examples:

- direct Nobitex local pair;
- Nobitex asset -> USDT -> IRT bridge;
- verified CoinGecko crypto -> USD;
- fiat -> USD;
- BTC -> USD -> EUR when policy selects that truthful path.

Derived result includes every component provider/edge.

## Route policy

Keep deterministic and table/policy driven.

Typical priorities:

1. usable direct edge;
2. authoritative provider for target domain;
3. non-stale over stale;
4. fewer hops;
5. fresher path;
6. verified mapping over unsafe/ambiguous mapping;
7. no loops/unnecessary round trips.

Examples:

- IRT target prefers direct valid Nobitex local edge;
- crypto/USD prefers verified CoinGecko direct edge when available;
- global fiat prefers fiat provider.

## Bounded history

History exists to support cards, not to become a market-data warehouse.

Never write all discovered market pairs on every provider refresh by default.

Maintain a bounded hot set such as:

- core assets;
- favorites;
- recently requested assets;
- assets with active card customization/usage.

Use a bounded sample cadence plus:

- age retention;
- per-series cap where useful;
- global row/storage cap;
- pruning tests.

For an asset without enough history, Phase 2 renders a truthful fallback using current/range metadata or “history collecting”. No synthetic line chart.

## Diagnostics

Market/provider diagnostics are defined in `docs/DIAGNOSTICS.md` and reuse these same provider/runtime/registry objects.

Local diagnostics do not call providers. Live diagnostics obey provider policy/cooldown.

## Anti-overengineering checks

Before adding market infrastructure, ask:

- Does a current provider require it?
- Does single-process SQLite runtime actually need it?
- Can the same behavior be expressed by provider policy + lock + state + service?

If yes to the simple path, use it.