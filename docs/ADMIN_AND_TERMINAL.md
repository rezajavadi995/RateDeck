# Admin and Terminal UX

## Design split

RateDeck has two administration surfaces with different jobs.

### Telegram Admin Panel

- Persian;
- product configuration;
- providers/API keys/routing;
- assets/aliases;
- complete template/placeholder/button customization;
- card customization in Phase 2;
- health/diagnostics;
- logs/audit.

### Terminal Control Center

- English-only;
- first-run operational setup;
- server/service operations;
- local resource/status view;
- logs/database/backup/update/repair/install lifecycle;
- no provider/API product administration.

This prevents duplicated settings logic and RTL terminal problems.

---

# Telegram Admin Panel

## Root menu

Conceptual structure:

```text
⚙️ پنل مدیریت RateDeck

[ 📊 بازار و APIها ]    [ 🪙 دارایی‌ها ]
[ 📝 متن‌ها و دستورات ] [ 🔘 دکمه‌ها ]
[ 🖼 طراحی کارت ]       [ 🎨 ظاهر و برندینگ ]
[ ⭐ قیمت استارز ]      [ 🩺 سلامت و عیب‌یابی ]
[ 📋 لاگ و Audit ]      [ 🧰 سیستم ]
```

Card design/branding becomes fully active in Phase 2. Actual rows must remain mobile-friendly and use the central safe label formatter.

## Interaction rule

If a value is selected from a finite set, use inline buttons.

Use free-form input only when the value is genuinely arbitrary: API key, template body, alias/search, Stars package line, custom text or uploaded image/logo.

Avoid long wizard flows where one page + inline actions is enough.

## Market & APIs

Provider overview and detail show:

- provider/capability;
- enabled state/mode;
- last success/failure;
- latency;
- cache age/freshness/LKG state;
- cooldown/next allowed call;
- RateDeck request counters;
- provider quota only when reliably available;
- mapping/edge/rejected-item counts where relevant.

Inline actions:

- enable/disable;
- public/keyed mode where applicable;
- routing choice;
- local status/cache details;
- explicit bounded live test/refresh;
- mapping errors/details.

API-key entry uses a dedicated FSM state. Delete the key-containing admin message when possible after secure capture. Store encrypted; never echo it.

## Assets

Navigation:

```text
Favorites
Recent
Family/Category
Search
All (paged)
```

Asset page may manage:

- enabled;
- display name;
- aliases;
- family;
- caption emoji;
- source markets/mappings;
- favorite;
- safe reset;
- Phase 2 card override.

Do not create a root button per discovered asset.

## Content & commands

At minimum sections exist for:

- `/start`;
- `/help`;
- `/market`;
- `/support`;
- `/about`;
- price response;
- conversion response;
- stale/unavailable/empty states;
- card master caption;
- card field fragments.

Each editor page shows:

- current full body in message where possible;
- safe short current-value preview in buttons;
- `🧩 آکولادهای این متن`;
- validation status;
- preview;
- edit/reset/save/back.

`/about` can be enabled/disabled. `/settings` does not exist separately from `/panel`.

## Placeholder browser

For the selected template scope, show only valid placeholders with Persian description and sample output.

Admin does not need to memorize placeholder names.

Example presentation:

```text
{asset_name}    نام دارایی       Bitcoin
{price_toman}   قیمت تومان        12,345,678
{change_24h}    تغییر 24h         +2.41%
```

All sample numbers use ASCII digits.

Field fragments (`{field.*}`) have their own editor/preview and diagnostics.

## Buttons

Admin can customize designated buttons according to their source-defined safety policy:

- label;
- style: default/primary/success/danger;
- custom emoji icon captured automatically in the edit flow;
- enabled state where safe;
- row/order only for menus declared configurable.

Action semantics remain source-defined and cannot be replaced by arbitrary callback text.

For configurable menus, movement/order is inline. Preview the resulting keyboard before activation when layout changes are non-trivial.

## Rich/Premium Emoji behavior

No separate Premium Emoji page.

When admin supplies a real Telegram custom emoji inside a supported text/button edit flow, capture its real entity/ID automatically and preview the resulting message/button.

Asset-specific caption emoji is edited from the asset page.

## Stars manual pricing

Page supports:

- list packages;
- add/edit;
- enable/disable;
- delete with confirmation;
- audit history.

Free-form line accepts `quantity price`, including Persian digits. Confirmation/output uses ASCII digits.

## Health & Diagnostics

This is a real troubleshooting center, not a green badge.

Categories follow `docs/DIAGNOSTICS.md`:

- providers/API;
- assets/mappings/aliases;
- templates/placeholders/fields;
- buttons/callbacks;
- rich/custom emoji;
- parser self-test;
- DB/schema/runtime/background refresh;
- Phase 2 card/font/logo/renderer.

Actions include:

- local diagnostics (zero network calls);
- explicit live API diagnostics (quota/cooldown aware);
- category drill-down;
- bounded sanitized diagnostic export if implemented.

Unknown/skipped/degraded states must not be rendered as healthy.

## Logs & Audit

Show summaries/pagination/filtering, not unbounded raw dumps.

Useful filters:

- errors;
- provider events;
- admin changes;
- template/button/config changes;
- card/render errors in Phase 2;
- sampled privacy-safe parser diagnostics.

Do not log every successful Telegram update just to create volume.

## Backup

Full application backup/restore UX belongs to Phase 2 operations. Telegram admin may show status/request a safe backup if implemented through the same application service, but destructive restore should remain strongly confirmed and may be terminal-only.

---

# Terminal Control Center — Phase 2

## Goal

The terminal should feel as convenient as the useful operational parts of StarzYFire while remaining much smaller because RateDeck does not need Redis/PostgreSQL/NATS/API-server administration.

It is a polished operations console, not a second product admin panel.

## Global launcher: `price`

The public shell command is **`price`**.

Installer creates a Python console-script entry point inside the RateDeck virtual environment and then creates a real global symlink:

```text
/usr/local/bin/price -> /opt/ratedeck/.venv/bin/price
```

The package console entry point maps `price` to the RateDeck CLI main function.

Requirements:

- running `price` from **any current working directory** opens the interactive RateDeck Control Center;
- the CLI must not depend on the caller being inside `/opt/ratedeck`;
- the symlink target is validated during install/repair;
- rebuilding the RateDeck venv must recreate/verify the target console script and symlink;
- no unrelated system command/file named `price` may be overwritten silently: installer must detect an existing non-RateDeck path and ask/refuse safely rather than replacing it blindly.

The old `ratedeck` command is not the primary product launcher. Do not create two competing primary command names unless the owner explicitly requests an alias later.

### Non-interactive convenience commands

The same CLI should support a small useful command surface:

```text
price                 # open interactive menu
price status          # local RateDeck status
price start           # start ratedeck.service
price stop            # stop ratedeck.service
price restart         # restart ratedeck.service
```

These subcommands are thin adapters over the same service-control logic used by the menu; they do not duplicate implementation.

## Language/style

English-only. ANSI/Rich color when TTY is available, plain fallback when redirected.

Recommended root menu:

```text
╭──────────────────────────────────────────────────╮
│             RateDeck Control Center              │
│       ● RUNNING   PID 1234   RSS 186 MB          │
╰──────────────────────────────────────────────────╯

 [1]  Setup / Config
 [2]  Service
 [3]  App Status
 [4]  Logs
 [5]  Database
 [6]  Backup / Restore
 [7]  Telegram Test
 [8]  Render Test Card
 [9]  Update / Repair
 [0]  Exit
```

Header status should be fast/local and must not call external market APIs.

Provider/API product settings never appear here.

## Setup / Config

This is intentionally easy and direct.

### Quick Setup

For a fresh install:

```text
RateDeck Quick Setup

 Bot token : NOT CONFIGURED
 Admin IDs : NOT CONFIGURED
 Log level : INFO

 [1] Set bot token
 [2] Set admin IDs
 [3] Change log level
 [4] Validate configuration
 [5] Test Telegram connection
 [6] Start RateDeck
 [0] Back
```

Rules:

- token is never printed after entry;
- existing token shows only `CONFIGURED` or a safe fingerprint if useful;
- admin IDs are validated as numeric IDs;
- log level uses a bounded choice, not arbitrary typing;
- validation does not modify unrelated settings;
- Telegram Test is explicit and bounded;
- Start/Restart affects `ratedeck.service` only;
- changing one value does not force a full wizard rerun.

This provides the configuration convenience wanted from StarzYFire without importing StarzYFire's unrelated infrastructure menus.

## Service

Exact submenu:

```text
Service

 [1] Status
 [2] Start
 [3] Stop
 [4] Restart
 [5] Enable at boot
 [6] Disable at boot
 [7] Foreground debug run   # optional, clearly marked
 [0] Back
```

**The normal menu action that runs the bot is `Service -> Start`.**

Quick Setup also exposes `Start RateDeck` after valid configuration for first-run convenience.

Every action targets exactly `ratedeck.service` and reports the real systemd outcome. Starting the service must not spawn a second instance if systemd already reports it active.

## App Status

Local-only status page, no provider/API call:

```text
Service        RUNNING
PID            1234
RSS            186 MB
CPU            1.2%
Uptime         03:12:41
DB             OK / 28 MB / schema 7
Disk free      24.8 GB
History        42 MB
Render cache   118 MB
Backups        390 MB
Render queue   0 / 1 active
Refresh loop   healthy
Last restart   ...
```

Values are examples only; implementation reports real measured data.

Also surface recent OOM/restart evidence where safely detectable.

Do not inspect/modify StarzYFire internals from this page. Host-level memory/load/disk may be shown as coexistence context.

## Logs

- follow RateDeck service journal;
- recent logs/errors;
- bounded sanitized diagnostic bundle.

Never tail unrelated StarzYFire/shared-service logs from this menu.

## Database

- RateDeck DB path/size/schema status;
- integrity/read-write smoke;
- safe optional maintenance;
- no PostgreSQL menu because RateDeck uses its own SQLite database.

## Backup / Restore

- backup now;
- list backups;
- verify backup;
- retention/size summary;
- restore with strong confirmation and pre-restore safety backup.

Only RateDeck-owned data is included.

## Telegram test

Use `getMe` and optionally send one bounded test message to a configured admin. Never print the token.

## Render test card

Use local sample data or current cache without uncontrolled provider refresh.

This action must use the same render concurrency/resource gate as normal card rendering so terminal tests cannot overload the shared server.

## Smart Update / Repair

`Update / Repair` is deliberately **state-aware**, not a blind `git pull` button.

### Update screen

Before changing anything, show a compact preflight such as:

```text
Current commit     abc1234
Remote main        def5678
Status             UPDATE AVAILABLE
Working tree       CLEAN
DB schema          7 -> 8 pending
Dependencies       changed / unchanged
Backup space       OK
Service            RUNNING

 [1] View changed files/commits
 [2] Run preflight again
 [3] Update RateDeck
 [4] Repair installation
 [0] Back
```

### Update algorithm

1. verify this is the expected RateDeck repository/remote/branch;
2. inspect tracked/untracked state and refuse unsafe overwrite;
3. `git fetch` and compare exact local/remote commits;
4. if already current, report **UP TO DATE** and make no mutation;
5. check disk space and writable RateDeck paths;
6. determine whether dependency manifests, schema migrations, service/unit/launcher files changed;
7. create and verify a pre-update backup of RateDeck DB/config/assets/master-key metadata according to backup policy;
8. perform fast-forward-only code update;
9. reinstall dependencies **only when required** or when repair policy explicitly requests it;
10. run only pending RateDeck migrations, with migration backup/safety rules;
11. verify `/usr/local/bin/price` symlink/CLI entry point if launcher-related files changed;
12. run compile/import/config/DB smoke checks;
13. if the service was running, present/perform the explicit update restart policy for **ratedeck.service only**;
14. verify service health after restart;
15. report old/new commit and every performed/skipped step.

If any preflight fails, normal update stops before destructive mutation. If a post-update validation fails, preserve backups and present bounded recovery/repair options; never start touching StarzYFire or another repository.

Never use blind normal-path `git reset --hard` + `git clean -fd`, never operate on `/opt/star`, and never restart `starzyfire-*` units.

## Uninstall

Separate:

- RateDeck application/service removal while preserving RateDeck data/backups;
- RateDeck full purge with stronger confirmation.

Do not remove unrelated system services/packages or StarzYFire resources.

Uninstall removes `/usr/local/bin/price` only after verifying that it is the RateDeck-owned symlink/launcher.

## Shared logic

CLI calls the same app services for DB/backup/health/render/config where applicable. It does not reimplement product logic in shell.

## Resource behavior

Terminal itself should be lightweight and short-lived. Opening `price` must not launch a second long-running bot, background scheduler or provider refresher.

Status/config/database views use local state. Live external API diagnostics stay in Telegram Admin and remain quota-aware.

Read `docs/RESOURCE_AND_ISOLATION.md` for the target VPS budget and coexistence acceptance gate.
