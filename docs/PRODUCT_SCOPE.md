# Product Scope

## Product identity

RateDeck is a Telegram-first market, conversion and market-card platform. It is not an exchange, wallet, payment bot, trading bot, portfolio manager or order-execution system.

Its core jobs are:

1. recognize compact market/conversion intents in Persian/English mixed input;
2. maintain a trustworthy cached market universe and rate graph;
3. convert between supported assets with explicit provenance;
4. render useful text responses and premium-quality visual market cards;
5. let an administrator customize content, buttons, card design and provider settings without editing code;
6. operate safely on a small VPS with conservative API consumption.

## Supported market universe

### Dynamic Nobitex universe

Every usable market returned by Nobitex discovery should be represented unless validation rejects it or the administrator disables it. This is intentionally dynamic; no static list of hundreds of symbols is maintained in source code.

Observed live on the owner's VPS on 2026-08-13:

- API reachable successfully;
- an unfiltered market stats snapshot returned `status=ok`;
- 495 market keys were present;
- examples included BTC/TRX/USDT pairs as well as tokenized-market symbols such as XAUT, PAXG and SLVON.

This observation is runtime evidence, not a permanent provider contract. Provider parsing must validate every response.

### Fiat

Global fiat currencies come from the configured fiat provider registry, initially ExchangeRate-API. Fiat codes should be discovered/synced where the provider supports a code-list endpoint rather than maintained as an unnecessarily narrow list.

### Global crypto/USD

CoinGecko is the primary global crypto/USD source where an asset has a verified mapping. CoinGecko mapping is not required for the asset to exist in RateDeck; the asset can still exist through Nobitex/local market data.

### Manual assets

Telegram Stars is a manual-only asset family. Admin may define exact packages such as:

`50 125000`

which means 50 Stars map to 125,000 Toman. Exact-package mode is the default. No interpolation or extrapolation occurs unless a later explicit product setting enables and defines that policy.

### Iranian 18K gold and oil

These are optional extensions, not blockers for initial launch. Do not alias tokenized gold such as XAUT/PAXG to Iranian 18K physical gold. If Iranian 18K gold or oil is added, it receives a distinct asset/provider contract backed by a verified source.

## User interaction

### Public commands

Default visible commands:

- `/start`
- `/help`
- `/market`
- `/support`
- `/about` (optional/admin-toggleable)

Admin-only:

- `/panel`

Not visible by default:

- `/price`
- `/convert`

These may remain hidden compatibility aliases for parser entry points.

Not required:

- `/gold`
- `/usd`
- `/crypto`
- `/rate`
- `/settings`

`/settings` belongs inside `/panel`.

### Natural compact intents

Examples that should be supported when their assets exist:

- `btc`
- `قیمت بیت کوین`
- `10 btc`
- `۱۰ بیت کوین`
- `10btc`
- `10 btc toman`
- `۱۰ بیت کوین به تومان`
- `1,500 usdt`
- `۱٬۵۰۰ تتر`
- `1.25 trx`
- `۱٫۲۵ ترون`
- `500000 toman xaut`
- `btc to usdt`
- `btc به usdt`
- `2 paxg trx`

Ordinary conversation must not be consumed as a market intent merely because it contains an asset word.

## Numeric display policy

All RateDeck-generated numbers are ASCII/Latin digits. Persian text may surround the number, but output must look like:

- `125,450 تومان`
- `$4,393.25`
- `+2.43%`
- `24h`

Input accepts Persian, Arabic and Latin digits and their common separators.

## Telegram admin scope

The Telegram admin panel is Persian and inline-first.

Primary areas:

- Market & Providers
- Assets & Aliases
- Card Designer
- Content & Commands
- Buttons
- Themes & Branding
- Stars Manual Pricing
- Logs & Audit
- Health
- Backup / Restore
- System

### Market & Providers

Admin can:

- inspect provider health;
- inspect last success/failure/latency/cache age/cooldown/budget;
- test provider connectivity without bypassing hard budgets;
- enable/disable provider capabilities;
- choose public/keyed mode where supported;
- choose routing policy within allowed domain boundaries;
- inspect mapping/provenance;
- inspect cache and refresh status.

API/provider management is not duplicated in the terminal menu.

### Assets & Aliases

Admin can:

- enable/disable discovered assets;
- add/remove custom aliases;
- choose or override family/category;
- set caption emoji/custom emoji;
- set card-specific override only when needed;
- favorite frequently managed assets;
- search large asset collections.

### Content & Commands

Admin can edit the user-visible templates for start/help/market/support/about and market-card captions.

Templates are label/field based where useful while still allowing arbitrary text between fields.

Example master caption:

```text
{field.asset_header}

{field.local_price}
{field.usd_price}
{field.change}

{field.high_low}
{field.updated_at}
```

Field fragments are themselves editable templates. Admin may also type fixed prose/emoji/punctuation directly around them.

Every template editor shows:

- current content;
- safely shortened preview;
- allowed placeholders for that exact scope;
- validation errors;
- preview before save.

### Buttons

Admin can customize button text, supported Telegram style, icon custom emoji and relevant layout/order settings.

Only Telegram-supported styles are exposed: default, primary, success, danger.

### Card Designer

Admin can select family/layout/theme/chart style and edit card elements via inline controls. Free-form inputs are reserved for arbitrary text/logo uploads/settings that cannot reasonably be represented as buttons.

### Premium/custom emoji

There is no separate premium emoji settings section. Custom emoji are captured wherever the admin supplies rich text or an asset/button emoji. The system stores the Telegram entity/ID and renders it centrally.

## Terminal scope

The terminal is English-only and operational:

- service status/start/stop/restart;
- application status;
- logs/errors;
- database status;
- backup/restore;
- basic environment configuration;
- Telegram connectivity test;
- render test card;
- safe update/repair;
- uninstall.

The global launcher is `ratedeck`.

## Explicit non-goals for Phase 1/2

- trade execution;
- wallet custody;
- user deposits/withdrawals;
- KYC;
- referrals;
- discounts;
- product checkout/invoices;
- automatic purchase execution;
- Redis/PostgreSQL requirement;
- web admin panel;
- per-asset hand-designed card requirement;
- Bitpin dependency.
