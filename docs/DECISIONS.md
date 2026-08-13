# Settled Decisions and Open Questions

This file distinguishes decisions already made with the owner from details Codex may choose during implementation.

## Settled decisions

### Product / name

- Repository/product name: RateDeck.
- Greenfield project; do not fork/copy Business Bot as the runtime base.
- Use Business Bot and StarzYFire only as audited references for good/bad patterns.

### Architecture

- Monkey patching/runtime symbol replacement: forbidden.
- Modular package architecture: required.
- Prefer table/registry/strategy-driven dispatch over large conditional chains.
- Handler/router ordering is explicit and tested.
- One lightweight bot process initially.
- SQLite initially, behind repository boundaries.
- Redis/PostgreSQL not required for initial scope.
- Async provider HTTP.
- Pillow card renderer.

### Providers

- Nobitex: local/Iranian dynamic market universe and Toman market authority.
- CoinGecko: global crypto/USD where mapping is verified.
- ExchangeRate-API: global fiat.
- Bitpin: not part of RateDeck initial provider set; preserve it for other project use.
- Telegram Stars: manual exact-package pricing only by default.
- Iranian 18K gold/oil: optional later provider extension; tokenized gold must not be relabeled as 18K physical gold.

### Dynamic markets

- RateDeck should support usable Nobitex markets dynamically rather than a fixed hand-maintained list.
- Admin can disable assets/override metadata without deleting provider-discovered identity.
- Large asset collections use categories/favorites/recent/search/pagination.

### Parser / conversions

- Parser accepts Persian, Arabic and Latin digits.
- Parser normalizes common Persian/Arabic text variants.
- Parser is strict against normal conversation false positives.
- Conversion engine is graph-based with provenance, not a limited pair `if/elif` implementation.
- Canonical arithmetic uses Decimal.
- All generated numeric output uses ASCII/Latin digits.

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

`/price` and `/convert` may be hidden compatibility aliases.

### Telegram Admin UX

- Persian by default.
- Inline-first wherever a bounded choice exists.
- Free typing only for truly arbitrary values.
- API/provider configuration exists only here, not in terminal.
- Admin can configure provider modes/keys/health/routing.
- Admin can edit content/commands/captions/field fragments/placeholders.
- Admin can customize button label and actual Telegram-supported style.
- Admin can manage assets, aliases, caption emoji and card overrides.
- Preview-first visual editing.

### Premium/custom emoji

- No separate Premium Emoji manager/menu.
- Capture custom emoji automatically from Telegram entities when admin supplies them.
- Asset caption emoji is edited within asset configuration.
- Rich-text rendering is central/entity-aware.
- Button custom emoji uses button icon semantics, not fake message entities inside button text.

### Telegram UI safety

- Central callback codec <=64 UTF-8 bytes.
- Long old/current values are shown in the admin message and only safely summarized on buttons.
- Truncation is grapheme-safe.
- Callback-heavy flows acknowledge promptly.
- Button styles exposed: default, primary, success, danger.

### Cards

- Visual quality is a major product requirement.
- Cards should be better/more flexible than the competitor references supplied by owner.
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

### Testing/process

- Two Codex implementation phases only.
- No fake/green-only tests.
- No Ruff commands.
- Do not merge/deploy/restart/migrate production unless explicitly requested.

## Open/implementation-choice details

These do not block Phase 1 and Codex may choose a simple documented implementation consistent with all contracts:

- exact Python minimum version supported;
- exact migration mechanism for SQLite (small internal runner vs Alembic);
- exact terminal UI library (e.g. Rich or equivalent maintained lightweight choice);
- exact authenticated-encryption library, provided it is well-maintained and not custom crypto;
- exact provider refresh intervals within conservative rate-budget policy;
- exact card theme/layout names;
- exact local history retention/downsampling values;
- exact group parser default (`compact` vs `mention_or_reply`) after usability review;
- exact CoinGecko public/demo/keyed capability naming based on current official service behavior;
- exact provider for future Iranian 18K gold/oil.

## Change control

If an implementation choice would alter a settled decision, stop and surface it as a scope/contract change instead of silently implementing the alternative.
