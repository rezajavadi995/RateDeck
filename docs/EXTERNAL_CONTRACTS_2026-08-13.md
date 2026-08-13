# External Contract Snapshot — 2026-08-13

This file is a dated implementation reference, not a permanent truth. Codex must re-check current official documentation when implementing a provider/Telegram feature if the contract may have changed.

## Telegram Bot API

Current official Bot API contract relevant to RateDeck:

- Inline keyboard `callback_data`: 1–64 bytes.
- Inline keyboard button style: `primary`, `success`, `danger`; omission means default/app style.
- `icon_custom_emoji_id` is supported for inline keyboard buttons subject to Telegram eligibility rules.
- Exactly one button action field is used in addition to text/icon/style.

RateDeck implications:

- central callback byte validation;
- expose only default/primary/success/danger;
- custom emoji button icon is distinct from message rich-text entities;
- do not store arbitrary text in callback data.

## Nobitex

Official Persian API documentation currently describes the market stats endpoint and a request limit for it, while provider limits can vary/change under load. The documentation warns against repeatedly exceeding limits.

Observed from the owner's VPS on 2026-08-13:

- `https://apiv2.nobitex.ir/market/stats` was reachable;
- a request containing invalid `ton` symbol returned a structured `400 InvalidCurrency`, proving connectivity while identifying the symbol problem;
- an unfiltered market stats request returned HTTP 200 / `status=ok`;
- 495 market keys were returned in one snapshot;
- observed examples: `xaut-rls`, `xaut-usdt`, `paxg-rls`, `paxg-usdt`, `slvon-rls`, `slvon-usdt`;
- the response contained `latest`, `bestBuy`, `bestSell`, `dayLow`, `dayHigh`, `dayChange`, `isClosed`, volumes and other market fields.

RateDeck implication: design for one whole-market refresh, not per-asset calls, while validating that this observed unfiltered behavior still works.

Conservative default should be dramatically below any documented maximum; normal refresh on the order of minutes is enough for the initial product.

## CoinGecko

Official Simple Price documentation supports querying multiple coin IDs in one request and can include additional fields such as 24h change, market cap/volume and last-updated timestamp depending on request parameters/plan.

The docs explicitly prefer unique IDs over names/symbols when multiple lookup parameters are supplied. Symbol lookup can be ambiguous.

RateDeck implications:

- use verified CoinGecko IDs for persistent bindings;
- batch multiple IDs;
- use last-updated metadata for freshness where available;
- keep mapping discovery separate from frequent price refresh;
- do not bind ambiguous symbols silently.

Provider quotas/credentials depend on current CoinGecko plan and must remain configurable/capability-driven.

## ExchangeRate-API

Current official documentation provides:

- Standard keyed endpoint returning all supported conversion rates for a base currency;
- Open/no-key endpoint;
- supported-codes endpoint for keyed usage;
- quota endpoint for plans that expose quota information.

Current open-access documentation states:

- data updates once per day;
- caching is allowed;
- attribution is required for open usage;
- open endpoint is rate limited;
- HTTP 429 is used when rate limited;
- provider guidance says hourly requests are already more frequent than the underlying daily update requires.

RateDeck implications:

- fiat snapshot refresh must be much slower than crypto market refresh;
- open mode carries an attribution requirement capability;
- keyed mode quotas vary by plan;
- querying quota itself can consume quota, so do it sparingly;
- never use this provider's IRR rate as the silent Iranian free-market Toman source.

## Verification rule

If runtime behavior conflicts with this file:

1. preserve safe failure;
2. check current official docs;
3. update provider adapter/tests/docs deliberately;
4. do not silently loosen budgets or fallback semantics just to make the call succeed.
