# Data Model Plan

This is a conceptual schema contract, not a demand to create one table per possible future feature.

## Storage strategy

- SQLite for the initial single-process deployment.
- Versioned schema migrations from day one.
- Domain-oriented repository helpers own SQL; no generic repository framework.
- Use transactions for multi-row admin/settings changes.
- Store timestamps in UTC and format at presentation boundaries.
- Store money/rates as exact decimal strings or documented scaled integers, never SQLite binary float as canonical financial data.
- Use validated JSON for configuration that does not need relational querying.

## Phase 1 minimum schema

Phase 1 should normally need roughly these persistent domains. Exact table names may vary.

### `schema_migrations`

- version/id;
- applied_at;
- optional checksum/name.

### `app_settings`

Small typed global settings:

- key primary key;
- value_json;
- revision;
- updated_at;
- updated_by_admin_id nullable.

### `assets`

Stable internal asset identity:

- id;
- canonical_key unique;
- symbol;
- display_name;
- family/category;
- enabled;
- discovery_source;
- discovered_at/last_seen_at/missing_since;
- optional caption-emoji rich metadata;
- favorite/admin metadata if global;
- created_at/updated_at.

Do not use symbol alone as permanent identity.

### `asset_aliases`

- id;
- asset_id;
- raw_alias;
- normalized_alias indexed;
- source/language (`builtin`, `provider`, `admin`);
- enabled;
- created/updated/admin metadata.

Provider sync must not delete admin aliases. Ambiguous normalized aliases are explicitly diagnosed/rejected according to parser policy.

### `asset_source_mappings`

Provider identities/enrichment mappings:

- asset_id;
- provider_id;
- provider asset ID/symbol;
- mapping status (`verified`, `auto_unique`, `ambiguous`, `unmapped`, `disabled` where useful);
- compact confidence/notes metadata;
- timestamps.

CoinGecko mapping belongs here. Do not maintain a giant hard-coded mapping dictionary as the only source of truth.

### `markets`

Provider market identity, especially Nobitex:

- id;
- provider_id;
- provider_market_key unique per provider;
- base_asset_id;
- quote_asset_id;
- usable/enabled/is_closed;
- first_seen/last_seen;
- compact validated metadata JSON;
- updated_at.

### `provider_state`

One compact row per provider/capability where useful:

- provider/capability key;
- enabled/mode;
- last_attempt/success/failure;
- last_error_category/latency;
- cooldown_until;
- consecutive_failures/backoff level;
- request counters/window metadata;
- last-known-good/snapshot metadata sufficient for diagnostics;
- updated_at.

No shared provider freshness timestamp.

### `provider_secrets`

Encrypted provider credentials only when keyed mode exists:

- provider/secret key;
- authenticated-encryption ciphertext + nonce/metadata;
- key version/fingerprint metadata (not master key);
- updated/admin metadata.

Plaintext never persists.

### `rates_current`

Normalized current conversion edges used by the in-memory graph:

- source_asset_id;
- target_asset_id;
- provider_id;
- market_id nullable;
- rate_decimal;
- price kind (`latest`, `mark`, etc.) where relevant;
- fetched/source-updated timestamp;
- freshness/quality/status metadata;
- provenance reference/compact metadata;
- unique key across current edge identity.

A separate forever-growing `market_snapshots` table is **not required** in Phase 1. Add bounded snapshot metadata only if debugging/provenance cannot be satisfied by current edge/provider/audit metadata.

### `market_history`

Bounded time-series only for the hot set:

- asset_id;
- quote_asset_id;
- provider_id;
- timestamp;
- value_decimal;
- resolution/source metadata.

Rules:

- do not insert every market every refresh;
- hot set = core/favorites/recently used/configured-card assets;
- enforce age and total-row/storage caps;
- indexed by asset/quote/time;
- pruning tested.

### `stars_packages`

- id;
- exact quantity;
- exact price_toman;
- enabled;
- updated/admin metadata;
- unique active quantity policy.

No interpolation by default.

### `text_templates`

- key primary key;
- scope;
- rich_document_json;
- revision;
- enabled where applicable;
- updated/admin metadata.

Defaults live in source; DB rows represent current overrides.

A dedicated `template_history` table is deferred unless the actual admin UX needs multi-revision rollback. The append-only audit trail may be sufficient initially.

### `button_customizations`

- button_key primary key/reference;
- plain label text;
- Telegram style;
- icon_custom_emoji_id nullable;
- enabled override where permitted;
- row/order override only where owning menu allows it;
- revision;
- updated/admin metadata.

Button action semantics/callback namespace remain source-defined unless a specific menu is intentionally data-driven.

### `audit_events`

Append-only bounded/safe audit trail:

- id/timestamp;
- actor/admin/system;
- action;
- object type/key;
- safe before/after or bounded fingerprints;
- correlation ID;
- result;
- redacted metadata.

Do not store secret plaintext in audit records.

## Phase 2 persistence

Create Phase 2 tables/config only when Phase 2 implements the corresponding feature.

Prefer a compact scoped card-config model rather than many tables if relational queries are unnecessary. A reasonable model may be:

### `card_configs`

- scope (`global`, `family`, `asset`);
- owner key/reference;
- validated config JSON containing theme/layout/chart/element overrides;
- revision;
- updated/admin metadata;
- unique scope/owner key.

This can replace separate `card_global_config`, `card_family_config`, `card_asset_overrides` and `card_text_layers` tables unless implementation evidence shows separate tables are materially better.

### `uploaded_assets`

Metadata for controlled logo/image files:

- id/kind;
- generated relative storage name;
- MIME/format/dimensions/size/checksum;
- created/admin metadata;
- active/reference state.

No user-supplied absolute paths.

### `backup_records` (optional but useful in Phase 2)

Only if the terminal/installer backup UX benefits from persisted metadata:

- generated relative path/name;
- created_at/type;
- app/schema version;
- checksum/size;
- verified status;
- actor.

Do not create it early merely to satisfy a schema diagram.

## Recent/favorite implementation

Favorites may live on asset metadata/settings if globally admin-scoped.

“Recent” does not require a complex analytics subsystem. It can be derived from a small bounded usage table/cache/settings record if needed by actual admin/user navigation.

## Diagnostic metadata

Prefer bounded safe JSON/details attached to existing provider/audit/state rows. Do not create one diagnostics table per category.

## Migration invariants

Tests must prove:

- empty DB reaches current schema;
- migration order/version is deterministic;
- failed migration does not report success;
- data-preserving migrations retain fixture data;
- current schema version is visible to health/terminal diagnostics;
- Phase 2 risky migration/update flows back up data first.

## Anti-overengineering rule

Before adding a table, answer both:

1. Which current user/admin/runtime behavior requires persistence here?
2. Why can the data not live safely in an existing typed row/validated JSON/audit record?

If neither answer is strong, defer the table.