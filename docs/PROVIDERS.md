# Provider Contracts

Provider behavior changes over time. Implementation must validate current official documentation and runtime responses; published provider limits are ceilings, not targets.

## Common provider interface

Every provider adapter exposes typed capabilities rather than leaking HTTP endpoints into application code.

Conceptual capabilities:

- market snapshot;
- asset/market discovery;
- global crypto USD pricing;
- fiat rates;
- supported-code discovery;
- health probe;
- optional quota status.

Every provider result includes:

- provider ID;
- capability;
- fetched_at;
- optional source_updated_at;
- latency;
- validated payload/edges;
- status/error category;
- rate-limit metadata when returned;
- safe diagnostic metadata with secrets removed.

## Nobitex

### Role

Primary Iranian/local market source and dynamic market-universe discovery.

### Normal refresh

Prefer one validated whole-market `market/stats` snapshot when supported by the live API. The owner's VPS successfully received the full current market set in one response on 2026-08-13.

Do not perform one request per asset.

### Market fields

Preserve useful validated fields when present:

- `latest`
- `mark`
- `bestBuy`
- `bestSell`
- `dayOpen`
- `dayClose`
- `dayHigh`
- `dayLow`
- `dayChange`
- `volumeSrc`
- `volumeDst`
- `isClosed`

### Rial/Toman

Nobitex market suffix `rls` means Rial. User-facing Toman uses an explicit `/ 10` conversion. Never accidentally display raw Rials as Toman.

### Rate limit posture

Official Nobitex documentation has published request limits for market endpoints and warns that limits may be reduced during load. RateDeck must operate far below any published ceiling.

Default normal posture:

- background snapshot cadence on the order of minutes, not seconds;
- one whole-market request per cadence when possible;
- singleflight;
- jitter;
- 429/backoff/Retry-After handling;
- admin refresh/test respects hard budget/cooldown.

No authentication token is required for the intended public market snapshot capability.

### Failure policy

- preserve provider-specific last-known-good snapshot with original timestamp;
- do not refresh its age when other providers succeed;
- malformed individual markets are isolated when possible;
- malformed/failed envelope marks the provider attempt failed;
- display stale data only with explicit stale metadata according to product policy.

## CoinGecko

### Role

Global crypto/USD pricing and global market enrichment for assets with safe mappings.

### Identity/mapping

Use CoinGecko unique IDs whenever possible. Symbol lookup is discovery assistance, not a trusted permanent binding when multiple tokens share the symbol.

Mapping lifecycle is separate from price refresh.

### Batching

Use `/simple/price`-style batching for multiple verified IDs where supported. Request useful metadata in the same call when it avoids additional calls, for example 24h change and last-updated time.

Do not query one asset per user message.

### Modes

The adapter should support the modes actually available to the configured CoinGecko plan at implementation time, represented generically as:

- no-key/demo/public capability when supported;
- keyed capability;
- disabled.

Admin UI exposes capabilities, not hard-coded marketing plan names that may change.

### Rate limit posture

CoinGecko limits depend on plan and may change. The provider budget is configurable and conservative. If rate-limit headers/quota information are available, capture them without assuming they are always present.

### Failure policy

- 429 -> cooldown/backoff;
- auth/quota errors distinguished from transient network errors;
- ambiguous mapping -> no price binding;
- stale mapping metadata does not imply stale prices and vice versa.

## ExchangeRate-API

### Role

Global fiat conversions only. It is not an Iranian free-market Toman authority.

### Open mode

The provider has an open/no-key endpoint with daily-updated data and rate limiting. The provider's terms require attribution for open use. RateDeck must carry capability metadata indicating whether attribution is required and ensure the configured user-facing experience satisfies the terms when open mode is enabled.

Open-mode data should be cached for a long interval appropriate to its update frequency. There is no reason to refresh it every minute.

### Keyed mode

Keyed standard requests return rates from one base currency to supported fiat codes. One USD-base snapshot can populate many fiat edges.

Quotas depend on the plan. Where the provider exposes quota status, admin diagnostics may query it sparingly; quota-status checks themselves can count against quota and therefore must not be polled aggressively.

### Secret handling

Keys are encrypted at rest, redacted in logs and never included in callback data or diagnostics.

### Error categories

Normalize provider responses such as:

- invalid key;
- inactive account;
- unsupported code;
- malformed request;
- quota reached;
- HTTP 429;
- network/timeout;
- invalid response.

## Telegram Stars manual provider

Stars is intentionally not an HTTP provider.

### Input

Default admin line:

`<quantity> <toman_price>`

Example:

`50 125000`

Parser accepts Persian/Arabic digits as input but stores normalized Decimal/integer values.

### Behavior

- exact package pricing by default;
- explicit enable/disable per package;
- updated timestamp and admin audit event;
- no automatic provider fallback;
- no automatic proportional pricing unless a later explicit mode is added.

## Iranian 18K gold / oil extensions

Not part of the initial provider set unless a verified provider is selected.

Rules:

- distinct asset identity;
- distinct provider adapter;
- no relabeling XAUT/PAXG as 18K physical gold;
- same budget/freshness/provenance contract as every provider.

## Provider selection policy

Provider routing is capability/domain based, not “whichever returns first”.

Default policy:

- Iranian/local markets -> Nobitex;
- verified global crypto/USD -> CoinGecko;
- global fiat -> ExchangeRate-API;
- Stars -> manual;
- future 18K gold/oil -> explicit dedicated provider.

Fallback across domains is opt-in and must preserve provenance. A global fiat source must not silently become an Iranian free-market source.

## Health model

Admin health should report at least:

- enabled/disabled;
- mode (public/keyed/manual where applicable);
- last attempt;
- last success;
- last failure category;
- latency;
- cache age;
- fresh/stale/no-data;
- cooldown until;
- request budget/counter information available to RateDeck;
- optional external quota remaining when safely available;
- mapping/discovery status where relevant.

Never display full API keys, tokens or secret-bearing URLs.
