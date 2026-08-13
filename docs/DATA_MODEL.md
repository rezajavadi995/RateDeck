# Data Model Plan

This is a conceptual schema contract for Phase 1. Exact SQL/ORM details may vary, but the identities and invariants should be preserved.

## Storage strategy

- SQLite in the initial single-process deployment.
- Repository layer owns SQL.
- Versioned schema migrations from day one.
- Use transactions for multi-row admin/settings updates.
- Store timestamps in UTC in machine-readable form; format Asia/Tehran only at presentation boundaries.
- Store monetary/rate Decimal values as exact decimal strings or scaled integers according to a documented per-field strategy. Do not use SQLite binary float as canonical money/rate storage.

## `app_settings`

Purpose: small typed global settings not deserving dedicated domain tables.

Fields conceptually:

- key primary key;
- value_json;
- revision;
- updated_at;
- updated_by_admin_id nullable.

Settings services validate typed payloads before persistence.

## `assets`

Stable runtime asset identity.

Fields:

- id integer/UUID primary key;
- canonical_key unique;
- symbol;
- display_name;
- category/family_id;
- enabled;
- discovery_source;
- discovered_at;
- last_seen_at;
- missing_since nullable;
- favorite/admin metadata if global;
- caption emoji rich-token metadata or reference;
- specific card override reference/status;
- created_at/updated_at.

Do not use symbol alone as primary identity forever; provider symbol collisions/renames need stable internal identity.

## `asset_source_mappings`

Maps internal asset to provider identities.

Fields:

- asset_id;
- provider_id;
- provider_asset_id/symbol;
- mapping_status (`verified`, `auto_unique`, `ambiguous`, `unmapped`, `disabled` where applicable);
- confidence/notes metadata;
- discovered_at/verified_at/updated_at;
- unique constraint appropriate to provider identity.

CoinGecko ID mapping belongs here rather than inside a giant source dictionary.

## `asset_aliases`

Fields:

- id;
- asset_id;
- raw_alias;
- normalized_alias;
- language/source (`builtin`, `provider`, `admin`);
- enabled;
- created_at/updated_at;
- admin ID for admin-created alias.

Invariants:

- normalized alias lookup is indexed;
- ambiguous collision is represented explicitly or rejected at admin save according to parser policy;
- provider refresh cannot delete admin aliases.

## `markets`

Provider market identity/metadata, especially Nobitex.

Fields:

- id;
- provider_id;
- provider_market_key unique per provider;
- base_asset_id;
- quote_asset_id;
- enabled/usable;
- is_closed;
- first_seen_at;
- last_seen_at;
- last_metadata_json;
- updated_at.

Market rows identify markets; current rates live in snapshots/edges.

## `provider_state`

One row per provider/capability where useful.

Fields:

- provider_id + capability primary/unique key;
- enabled;
- mode;
- last_attempt_at;
- last_success_at;
- last_failure_at;
- last_error_category;
- last_latency_ms;
- cooldown_until;
- consecutive_failures;
- budget counters/window metadata;
- last_snapshot_id/reference;
- last_good_snapshot_id/reference;
- updated_at.

Never share one success timestamp across providers.

## `provider_secrets`

Encrypted provider credentials.

Fields:

- provider_id;
- secret_name;
- ciphertext;
- nonce/metadata required by chosen authenticated encryption scheme;
- key_version/fingerprint metadata, not master key;
- updated_at;
- updated_by_admin_id.

Plaintext never persists here.

## `market_snapshots`

Validated provider refresh envelope metadata.

Fields:

- id;
- provider_id;
- capability;
- fetched_at;
- source_updated_at nullable;
- status;
- latency_ms;
- raw_hash/safe diagnostic fingerprint;
- edge_count;
- rejected_item_count;
- error_category nullable;
- created_at.

Do not store huge raw provider payload forever unless a bounded diagnostic policy explicitly needs it.

## `market_edges_current`

Optional materialized/current edge store if the engine chooses DB-backed current edges rather than snapshot JSON.

Fields:

- source_asset_id;
- target_asset_id;
- provider_id;
- market_id nullable;
- rate_decimal;
- price_kind (`latest`, `mark`, etc.);
- snapshot_id;
- source_updated_at/fetched_at;
- status/quality metadata;
- updated_at;
- unique key across edge identity.

The in-memory graph can be rebuilt from validated current edges.

## `market_history`

Selected local time-series points for cards.

Fields:

- asset_id;
- quote_asset_id;
- provider_id;
- timestamp;
- value_decimal;
- source_snapshot_id;
- resolution/bucket (`raw`, later aggregate values if used);
- indexes for asset/quote/timestamp.

Retention pruning is explicit and tested.

## `stars_packages`

Fields:

- id;
- quantity exact numeric;
- price_toman exact Decimal/integer;
- enabled;
- updated_at;
- updated_by_admin_id;
- unique active quantity policy as appropriate.

No interpolation flag unless later added intentionally.

## `text_templates`

Fields:

- key primary key;
- scope;
- rich_document_json;
- revision;
- enabled where applicable;
- updated_at;
- updated_by_admin_id.

Default definitions live in source; DB row is override/current revision.

## `template_history` (recommended)

Bounded history for rollback/audit of important template changes.

Fields:

- id;
- template_key;
- revision;
- rich_document_json;
- created_at;
- admin_id.

Retention may cap revisions per template.

## `button_customizations`

Fields:

- button_key primary key/reference;
- text;
- style;
- icon_custom_emoji_id nullable;
- enabled where allowed;
- layout/order overrides only for configurable menus;
- revision;
- updated_at;
- updated_by_admin_id.

Button action semantics/callback namespace remain source-defined unless a menu is intentionally data-driven.

## `card_global_config`

Could be settings rows or dedicated table. Must persist stable IDs for:

- default theme;
- default layout;
- default chart style;
- brand logo reference;
- global renderer options;
- revision.

## `card_family_config`

- family ID;
- theme/layout/chart overrides;
- token overrides JSON validated against schema;
- revision;
- updated_at/admin.

## `card_asset_overrides`

Sparse only:

- asset_id;
- family override optional;
- theme/layout/chart optional;
- element override JSON validated;
- revision;
- updated_at/admin.

Absence means inherit. Provide reset/delete override.

## `card_text_layers`

If modeled separately:

- id;
- scope (`global`, family, asset);
- owner reference;
- rich document/text;
- x/y/bounds/style;
- z-index;
- enabled;
- updated_at/admin.

Bound maximum layers by product policy.

## `uploaded_assets`

Metadata only; file bytes live in controlled filesystem.

Fields:

- id;
- kind (`brand_logo`, `asset_logo`, etc.);
- generated storage name/path relative to fixed root;
- MIME/format;
- width/height;
- size bytes;
- checksum;
- created_at/admin;
- active/reference status.

No user-supplied absolute paths.

## `audit_events`

Fields:

- id;
- timestamp;
- admin_id nullable/system actor;
- action;
- object_type;
- object_key/id;
- safe_before_json/fingerprint nullable;
- safe_after_json/fingerprint nullable;
- correlation_id;
- result;
- metadata_json redacted.

Append-only through application service.

## `backup_records`

- id;
- created_at;
- backup_type;
- relative path/generated name;
- app/schema version;
- checksum;
- verified_at/status;
- size;
- created_by actor.

## Migration invariants

Tests must prove:

- empty database reaches current schema;
- migrations are ordered and recorded;
- failed migration does not report success;
- data-preserving migrations retain prior fixture data;
- current schema version is visible in health/terminal status;
- backup occurs before risky update/restore migration workflows.
