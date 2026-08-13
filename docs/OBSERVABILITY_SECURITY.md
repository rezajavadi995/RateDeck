# Observability and Security

## Observability goals

Logs must answer operational questions without becoming noise:

- Is the bot running?
- Is Telegram reachable?
- Which provider is degraded and why?
- When was each provider last successfully refreshed?
- Are cached rates fresh or stale?
- Did a rate-limit/cooldown occur?
- Which admin changed a setting/template/button/card config?
- Why did a conversion fail?
- Is card rendering failing for a specific asset/layout?

## Logging layers

### Application log

Structured events for lifecycle, Telegram errors, database failures, scheduler state and unexpected exceptions.

### Provider log/events

Structured provider events such as:

- refresh_started;
- refresh_success;
- refresh_failed;
- cooldown_entered;
- cooldown_skipped_request;
- mapping_ambiguous;
- malformed_market_skipped;
- stale_lkg_used.

Do not log one success line for every ordinary user update unless it adds diagnostic value.

### Durable admin audit trail

Persist important administrative changes:

- provider enable/mode/routing changes;
- API key set/replaced/removed (never value);
- asset enable/family/alias changes;
- caption emoji changes;
- Stars package changes;
- template changes/reset;
- button changes;
- card/theme/layout/branding changes;
- backup/restore/update requests where applicable.

Audit record concept:

- timestamp;
- admin Telegram ID;
- action;
- object type/key;
- safe before fingerprint/summary;
- safe after fingerprint/summary;
- correlation ID;
- result.

## Correlation

Assign a correlation/update identifier at Telegram ingress and a task/run ID for background provider refreshes. Propagate through logs so one error can be traced without printing user-sensitive message content by default.

## Log redaction

Central redaction layer must remove/mask:

- bot token;
- CoinGecko/ExchangeRate keys;
- encryption/master keys;
- authorization headers;
- secret-bearing query/path segments;
- sensitive environment variables.

Do not rely on developers remembering to redact manually at each call site.

## User content privacy

Do not log full arbitrary user messages by default. Parser diagnostics may log normalized intent metadata or bounded/redacted samples when explicitly configured for debugging.

Admin template bodies may contain links/text and should not be dumped casually into logs.

## Error handling

Normalize expected provider/domain errors into safe categories. Unexpected exceptions get stack traces in server logs but user/admin messages remain bounded and do not expose internals/secrets.

Examples:

- provider_timeout;
- provider_rate_limited;
- provider_auth_failed;
- provider_quota_reached;
- invalid_provider_payload;
- ambiguous_asset;
- no_conversion_route;
- stale_data_unavailable;
- template_invalid;
- render_failed.

## Health model

Health is composed, not a single boolean.

Components:

- Telegram connection/runtime;
- database;
- migration/schema version;
- background scheduler;
- Nobitex;
- CoinGecko;
- ExchangeRate;
- card renderer/font/assets;
- disk/data directory.

Statuses:

- healthy;
- degraded;
- stale;
- cooldown;
- disabled;
- unknown;
- failed.

The aggregate may be degraded while the bot remains useful.

## Secret storage

### Environment bootstrap secrets

Bot token and local master secret are not committed.

Recommended install model:

- `/opt/ratedeck/.env` or equivalent runtime env, mode 0600;
- local encryption key stored outside repository and database, mode 0600;
- service user owns required files.

### Admin-managed API keys

Provider keys entered through Telegram admin are encrypted before database storage using authenticated encryption. Implementation may use a well-maintained library such as libsodium/SecretBox; do not invent cryptography.

Requirements:

- random installation master key;
- key not stored in the same DB record as ciphertext;
- authenticated encryption;
- key fingerprint/status can be shown; plaintext cannot;
- rotation path documented;
- backups preserve ciphertext and key backup guidance separately.

## Telegram admin authorization

Every admin router/action is guarded centrally. Do not rely on hiding `/panel` or buttons.

Authorization uses configured Telegram numeric IDs. Sensitive actions re-check authorization at execution time.

If multi-admin roles are later introduced, add a typed permission model rather than scattered ID checks.

## Callback security

- decode/validate namespace/action/version;
- validate referenced record belongs to the expected object type/state;
- never trust callback payload as authorization;
- callbacks <=64 bytes;
- no secrets;
- dedupe/idempotency for mutation actions where double-click matters;
- expired/stale admin action context fails safely.

## Input validation

Free-form admin/user inputs are bounded before parsing/storage:

- text length;
- image size/type/dimensions;
- alias length/character policy;
- numeric ranges;
- URL scheme/length;
- API key max length;
- template size;
- custom layer count/coordinates/font sizes.

## Filesystem safety

Uploads/assets/backups use application-generated filenames and fixed directories. Never concatenate user-provided paths.

Protect against:

- path traversal;
- symlink surprises for privileged installer/restore paths;
- overwrite of code/config by uploaded files;
- unbounded backup growth.

## HTTP security

- HTTPS provider endpoints only by default;
- explicit timeout;
- bounded response size where practical;
- shared async client with sane connection limits;
- no automatic redirect to insecure HTTP;
- validate JSON envelope/content type defensively;
- API keys in headers where provider supports it; if provider requires key-in-URL, redact URL in logs.

## Database safety

- parameterized queries/repository APIs;
- schema migrations versioned;
- backup before destructive schema/update operations;
- transaction boundaries explicit;
- admin mutations audited;
- DB corruption/locked errors surfaced clearly.

## Backup security

Backups may contain encrypted provider secrets and user/admin configuration.

Requirements:

- restrictive permissions;
- bounded retention;
- verification metadata/checksum;
- no plaintext secret export;
- restore validates backup version before replacing current DB;
- automatic pre-restore backup of current state.

## Dependency/security posture

- minimal dependency set;
- pin/lock reproducibly once implementation begins;
- avoid unmaintained convenience packages when stdlib/major maintained library suffices;
- no remote code execution/install from arbitrary URLs;
- installer downloads only expected repository/package-manager content;
- document supported Python/OS versions.

## Abuse/resource controls

RateDeck is read-only market information, but it still needs bounded resource use:

- parser input length limit;
- per-user/card-render throttling where necessary;
- rendered-card cache;
- background provider refresh independent of user spam;
- bounded admin export/log operations;
- bounded image decoding;
- no punitive one-hour ban for ordinary repeated button taps by default; prefer short rate limits/cooldowns appropriate to resource cost.
