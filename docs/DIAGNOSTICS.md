# Diagnostics Contract

Diagnostics are a first-class admin feature. They must answer “what is wrong, where, and what can I safely do next?” without duplicating core business logic or bypassing provider limits.

## Design

Use one central diagnostics service/registry. Each check returns a compact typed result such as:

```text
id
category
status: ok | warning | error | unknown | skipped
severity
summary
details (bounded)
suggested_action (optional)
checked_at
```

Diagnostics should call existing validators/repositories/provider adapters. They are not a second implementation of parsing, rendering or provider logic.

## Admin UX

Telegram admin diagnostics are Persian and inline-first.

Conceptual root:

```text
🩺 عیب‌یابی RateDeck

[ 🌐 API و Providerها ] [ 🪙 دارایی‌ها ]
[ 📝 متن و آکولادها ]   [ 🔘 دکمه‌ها ]
[ 💎 Rich/Emoji ]        [ 🧠 Parser ]
[ 💾 دیتابیس ]           [ ⚙️ Runtime ]
[ 🖼 کارت/Renderer ]     # Phase 2

[ ▶️ اجرای تست‌های محلی ]
[ 🌍 تست زنده APIها ]
```

“Local diagnostics” must not make external network calls.

“Live API diagnostics” are explicit, bounded and subject to the same cooldown/rate-budget rules as normal provider refreshes.

## Provider/API diagnostics

Per provider display:

- enabled/mode;
- capability (local market/global crypto/fiat);
- last attempt;
- last success;
- last failure + sanitized category;
- current freshness/cache age;
- last latency;
- cooldown until / next allowed call;
- consecutive failure/backoff state;
- RateDeck request count for current tracked windows;
- provider quota/remaining only if reliably supplied by provider;
- current validated edge/asset/mapping counts;
- rejected/malformed item count from last refresh;
- last-known-good age;
- public/keyed configuration status without displaying secrets.

Live probe must:

- reuse provider adapter validation;
- never print API keys;
- respect hard cooldown;
- avoid expensive full-universe calls when a cheaper official health/representative request exists;
- clearly distinguish HTTP connectivity from valid market-data semantics.

## Asset / market diagnostics

Checks include:

- discovered asset count;
- enabled/disabled/missing counts;
- newly discovered assets;
- markets rejected as malformed;
- closed markets;
- zero-volume/low-quality informational count where relevant;
- duplicate/ambiguous normalized aliases;
- provider identity collisions;
- missing/ambiguous CoinGecko mappings;
- verified mapping count;
- stale/missing local-market data;
- orphaned asset mapping/market references;
- invalid caption emoji metadata.

Ambiguous mapping is not automatically an error if the asset still works for local Nobitex pricing; status should reflect degraded enrichment rather than fake total failure.

## Placeholder Registry

Every placeholder has central metadata:

- stable key;
- scope(s);
- type (`text`, `number`, `money`, `percent`, `datetime`, `rich_fragment`, etc.);
- Persian admin description;
- sample value;
- required/optional semantics for each template contract where relevant;
- formatter/escape policy;
- availability conditions if data is optional.

Admin template editor must provide an inline **«🧩 آکولادهای این متن»** view listing only valid placeholders for the selected template scope.

The UI should show examples such as:

```text
{asset_name}      نام دارایی       Bitcoin
{asset_symbol}    نماد              BTC
{price_toman}     قیمت تومان        12,345,678
{change_24h}      تغییر 24h         +2.41%
{updated_at}      زمان بروزرسانی    07:42
```

All generated samples follow the ASCII-digit output policy.

## Template / `{}` diagnostics

A template check validates:

- balanced/parseable braces;
- known placeholder names;
- placeholder allowed in this scope;
- required placeholders if the contract requires them;
- field-fragment references;
- field-fragment dependency cycles;
- maximum field expansion depth;
- maximum expanded size;
- sample-context expansion;
- dynamic-value escaping/type correctness;
- Telegram target length after rendering;
- rich-text/entity compile success;
- link validation;
- unresolved token leakage;
- empty optional fragment behavior.

Unknown placeholder examples such as `{price_tomna}` must block save with a useful Persian error and suggestion when a close valid key exists.

No raw `{...}` placeholder that belongs to the template grammar may leak to a user-facing final result.

Literal braces must have an explicit escaping/literal-brace contract documented by the implementation.

## Field-fragment diagnostics

For composable caption fields such as:

```text
{field.asset_header}
{field.local_price}
{field.usd_price}
{field.change}
```

check:

- referenced field exists;
- field is valid for the master scope;
- no direct/indirect cycle exists;
- recursion/depth is bounded;
- optional missing data resolves through declared policy;
- resulting caption remains within Telegram limits.

Admin must be able to preview a field individually and as part of its master template.

## Button diagnostics

For every customizable button/menu check:

- stable button key exists;
- label is valid/non-empty after normalization;
- safe preview truncation succeeds;
- Telegram style is one of `default`, `primary`, `success`, `danger`;
- custom emoji icon ID is valid when configured;
- callback encoding succeeds;
- callback payload <=64 UTF-8 bytes;
- action namespace/action is registered;
- no secret/template/long arbitrary text is embedded in callback payload;
- URL actions contain a valid allowed URL shape;
- enabled/disabled customization is permitted for that button;
- row/order override is permitted for that owning menu;
- menu does not create a giant/unusable keyboard;
- duplicate/conflicting row/order values resolve deterministically.

Admin customization must never be able to rewrite a safe built-in action into arbitrary executable callback semantics.

## Custom/Premium Emoji diagnostics

There is no separate emoji management product page.

Checks happen in context and in diagnostics:

- Telegram custom-emoji entity capture produced a real numeric custom emoji ID;
- fallback text/emoji exists where required;
- stored rich document is structurally valid;
- placeholder expansion + UTF-16 entity compilation succeeds;
- entity boundaries do not split surrogate pairs/grapheme content;
- button icon extraction uses supported button semantics;
- ordinary Unicode emoji remains ordinary text;
- asset caption emoji resolves through asset -> family/default fallback correctly.

Optional live validation of stored custom-emoji IDs may be implemented only as a bounded explicit diagnostic using Telegram APIs; routine rendering must not require an API lookup for every emoji.

## Parser diagnostics

Maintain a deterministic parser self-test corpus with:

- positive Persian/English compact intents;
- Persian/Arabic/Latin digits;
- attached amount+symbol forms;
- conversion words;
- dynamic aliases;
- ambiguous alias cases;
- normal-conversation false-positive cases;
- command/admin-state collision cases.

Admin diagnostics may show corpus pass/fail counts.

Production unknown-intent sampling must be privacy-safe and bounded. Do not log all user messages merely to improve parsing.

## Database/runtime diagnostics

Check:

- database open/read/write smoke (non-destructive);
- schema version/current migration state;
- DB file size;
- history row/storage bounds;
- background refresh loop heartbeat;
- last successful scheduler cycle;
- bot identity/config availability;
- admin configuration;
- encryption master-key availability without revealing it;
- recent unhandled exception count/window;
- disk space threshold.

## Phase 2 card diagnostics

When Card Engine exists, add:

- font availability;
- logo/upload references exist and are within controlled paths;
- renderer sample smoke;
- configured theme/layout/chart IDs exist;
- family fallback resolves;
- sparse asset override schema validates;
- custom text-layer count/bounds are valid;
- render dimensions/resource bounds;
- history sufficiency/fallback behavior;
- deterministic render fixture/golden checks where practical.

## “Run all” behavior

Local Run All:

- no external API calls;
- fast/bounded;
- returns category summary + drill-down.

Live Run All:

- separate explicit action;
- requests strong confirmation if it may consume meaningful quota;
- checks provider policies before calls;
- skips providers in hard cooldown and explains why;
- never retries aggressively;
- never marks a skipped probe as healthy merely from old data.

## Audit

Admin changes to templates, placeholders configuration (where configurable), buttons, asset metadata, provider settings and Stars pricing create audit events.

Diagnostics themselves may log a summary event, but repeated successful checks should not flood application logs.

## Required tests

- placeholder registry metadata/scopes;
- unknown/malformed placeholder diagnostics;
- field cycle detection;
- field expansion bounds;
- Telegram length failure;
- callback 64-byte boundary;
- orphaned callback action detection;
- unsupported button style detection;
- custom emoji capture/compile diagnostics;
- alias ambiguity diagnostics;
- provider cooldown prevents live probe;
- local Run All performs no network calls;
- sanitized diagnostic output contains no configured secrets.