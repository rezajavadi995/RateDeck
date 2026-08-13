# Settled Decisions and Open Questions

This file is the owner-decision layer for RateDeck. It exists to prevent both under-engineering and unnecessary enterprise architecture. If another domain document suggests a heavier implementation than this file requires, choose the simpler implementation that still satisfies the concrete product contract.

## Settled decisions

### Product / name

- Repository/product name: RateDeck.
- Greenfield project; do not fork/copy Business Bot as the runtime base.
- Business Bot and StarzYFire are audited references only: reuse proven ideas, not their accumulated compatibility debt.
- The defined product is completed in exactly **two major Codex implementation phases**. Internal checkpoints inside a phase are encouraged, but they are not extra product phases.

### Architecture

- Monkey patching/runtime symbol replacement: forbidden.
- Modular package architecture: required.
- Modularity does **not** mean one class per file, one interface per service, or empty folders mirroring a theoretical architecture tree.
- Prefer the smallest cohesive module that has one real responsibility. Split when responsibilities genuinely diverge, not pre-emptively.
- Prefer table/registry/strategy-driven dispatch over large conditional chains.
- Handler/router ordering is explicit and tested.
- One lightweight bot process initially.
- SQLite initially.
- Redis, PostgreSQL, message brokers, web panels, microservices, distributed locks, CQRS/event-bus frameworks and plugin frameworks are out of scope unless a later measured requirement justifies them.
- Async provider HTTP.
- Pillow card renderer.
- Dependency injection should be ordinary explicit composition. Do not introduce a DI framework.
- Protocol/ABC interfaces are justified at volatile external boundaries or where multiple implementations/test substitution need them. Do not create an abstraction layer for every internal class.
- No generic repository framework. Small domain repositories/functions over SQLite are sufficient.

### Provider runtime / rate limits

- Provider traffic is background-first and cache-first; Telegram user traffic never performs one external request per user message.
- Each provider keeps independent freshness, cooldown, last-success/failure and request counters.
- Default single-process singleflight is an `asyncio.Lock`/equivalent per provider capability; no distributed locking.
- Rate limiting starts simple: provider policy + minimum interval + known quota counters + `Retry-After`/429 cooldown + conservative refresh cadence. Do not implement a generalized token-bucket platform unless a real provider requires it.
- Published API limits are ceilings, not targets.
- Admin live probes obey the same hard cooldown/budget rules.

### Providers

- Nobitex: local/Iranian dynamic market universe and Toman market authority.
- CoinGecko: global crypto/USD enrichment where mapping is verified.
- ExchangeRate-API: global fiat.
- Bitpin: not part of RateDeck initial provider set.
- Telegram Stars: manual exact-package pricing only by default.
- Tokenized gold/silver assets exposed by Nobitex may be supported under their real identities. They must not be relabeled as Iranian physical 18K gold.
- Iranian 18K gold/oil are not required for initial completion unless a verified source is explicitly added later.

### Dynamic markets and enrichment

- RateDeck supports usable Nobitex markets dynamically rather than a fixed hand-maintained list.
- Discovering the complete Nobitex universe does **not** imply fetching CoinGecko enrichment for every discovered asset.
- CoinGecko enrichment/mapping is lazy/batched for useful, requested, favorite/core or explicitly mapped assets. Do not burn quota trying to map all Nobitex assets on every sync.
- Admin can disable assets/override metadata without deleting provider-discovered identity.
- Large asset collections use categories/favorites/recent/search/pagination.

### Market history

- Do not persist a time-series point for every market on every provider refresh. That would create unnecessary SQLite growth.
- History is bounded and demand-aware: core/favorite/recently-used assets and assets with configured card use may collect samples.
- A newly requested obscure asset may truthfully show “history collecting”/range-only output until enough local history exists.
- Retention and maximum total rows/storage are bounded and tested.
- Never fabricate chart points.

### Parser / conversions / numbers

- Parser accepts Persian, Arabic and Latin digits.
- Parser normalizes common Persian/Arabic text variants and separators.
- Parser is strict against normal-conversation false positives.
- Conversion engine is graph-based with provenance, not a limited pair `if/elif` implementation.
- Canonical arithmetic uses `Decimal`.
- All generated numeric output uses ASCII/Latin digits, including inside Persian UI/captions/cards.

### Telegram commands

Default public visible:

- `/start`
- `/help`
- `/market`
- `/support`
- `/about` optional/toggleable

Admin:

- `/panel`

Not separate:

- `/settings` (inside `/panel`)
- `/gold`
- `/usd`
- `/crypto`
- `/rate`

`/price` and `/convert` may be hidden compatibility aliases, but the normal UX is parser-driven.

### Telegram Admin UX

- Persian by default.
- Inline-first wherever a bounded choice exists.
- Free typing only for genuinely arbitrary values.
- API/provider configuration exists only here, not in terminal.
- Admin can configure provider modes/keys/health/routing.
- Admin can manage assets, aliases, caption emoji and safe asset overrides.
- Admin can customize all designated user-facing templates/command texts/card captions/field fragments.
- Admin can customize designated buttons: label, supported Telegram style, optional custom-emoji icon, enabled state where safe, and row/order only for menus intentionally declared configurable.
- Button action semantics/callback targets are not arbitrary admin text and cannot be replaced with unvalidated callback code.
- Current values are shown fully in the admin message where possible and only safely summarized/truncated in buttons.
- Preview-first for text/rich-text/button/card changes where preview materially prevents mistakes.

### Placeholder / `{}` contract

- Placeholder support is a first-class product feature, not an implementation detail.
- A central Placeholder Registry defines each placeholder by stable key, scope, type, description, sample value and optional/required status.
- Each editable template shows the placeholders valid for **that exact scope**.
- Admin may freely mix placeholders with manual text, punctuation and ordinary/custom emoji.
- Unknown, malformed, unavailable or cyclic field placeholders must be diagnosed before save/send.
- No raw unresolved `{placeholder}` may leak to users.
- Field fragments such as `{field.local_price}` are composable but cycle-checked and depth/size bounded.
- Dynamic user/provider values are escaped/typed; only explicitly rich placeholders may inject validated rich fragments.

### Premium/custom emoji

- No separate Premium Emoji manager/menu.
- Capture custom emoji automatically from Telegram entities whenever admin supplies rich text or a button label in a supported editor.
- Asset caption emoji is edited inside asset configuration.
- Rich-text rendering is central/entity-aware.
- Button custom emoji uses Telegram button icon semantics; button text itself is not treated as rich message entities.

### Telegram UI safety

- Central callback codec <=64 UTF-8 bytes.
- Long old/current values are shown in the admin message and only safely summarized on buttons.
- Truncation is grapheme-safe.
- Callback-heavy flows acknowledge promptly.
- Button styles exposed: default, primary, success, danger.
- Menus must respect Telegram practical size/width limits and use pagination rather than giant keyboards.

### Diagnostics

Diagnostics are required and must be useful, not decorative.

The Telegram admin diagnostics surface must cover, at minimum:

- provider/API state, latency, freshness, cooldown, next allowed refresh, request counters and last error;
- asset discovery/mapping/alias ambiguity and unusable market counts;
- templates/placeholders/field fragments, including unknown placeholders, cycles, expansion/length failures and preview compile failures;
- buttons/callbacks, including unsupported styles, overlong callback payloads, orphaned action keys and unsafe menu layout;
- rich text/custom emoji compile/capture health;
- parser corpus/sampled unknown-intent diagnostics without logging sensitive user content by default;
- database/schema/background-refresh health;
- Phase 2 card/font/logo/render checks.

A “Run all diagnostics” action may aggregate local checks, but it must not bypass provider API budgets. Live provider probes are explicit/bounded and quota-aware.

### Cards

- Visual quality is a major product requirement.
- Avoid one repeated template for every asset.
- Avoid per-asset hand-design requirement.
- Use family + layout + theme + chart + sparse override composition.
- Asset logo, brand logo, custom text layers and element position/style editing are supported.
- Render 1080x1080 primary cards, preferably from 2x internal resolution where feasible.
- Local history builds truthful charts; never fabricate history.

### Terminal

- English-only.
- Global command: `ratedeck`.
- Colored/polished operational menu.
- No API/provider administration.
- Service/log/database/backup/config/test-card/update/repair/uninstall functions.

### Installer

- `install.sh` + README one-line installer.
- Safe/idempotent update/install.
- Do not use blind hard reset + clean as normal update.
- Preserve config/DB/assets/keys/backups.
- Installer/terminal operational work belongs to Phase 2, not Phase 1 except minimal development/bootstrap needs.

### Storage scope

Phase 1 should keep the schema compact. Mandatory persistent domains are limited to what the product actually needs: schema/versioning, settings, assets/aliases/provider mappings/markets, provider runtime/secrets/current rates, bounded history, Stars packages, templates, button customizations and audit events.

Do not create Phase 2 card/upload/backup tables in Phase 1 merely because a future schema document mentions them. Do not create template-history tables if the append-only audit trail already satisfies rollback/audit needs; add dedicated history only if an actual UX requires it.

### Testing/process

- Exactly two major Codex implementation phases.
- Each phase should be executed through small internal checkpoints with focused tests, rather than one uncontrolled giant edit.
- No fake/green-only tests.
- No Ruff commands.
- Do not merge/deploy/restart/migrate production unless explicitly requested.

## Open/implementation-choice details

Codex may choose the simplest documented implementation consistent with all contracts for:

- exact Python minimum version;
- small internal SQLite migration runner vs a lightweight migration dependency;
- terminal UI library;
- authenticated-encryption library (maintained library only; no custom crypto);
- conservative provider refresh intervals;
- exact card theme/layout names;
- exact bounded history hot-set/retention values;
- exact group parser default after usability review;
- exact CoinGecko public/demo/keyed capability naming based on current official service behavior.

## Change control

If an implementation choice would alter a settled decision, stop and surface it as a scope/contract change instead of silently implementing the alternative.