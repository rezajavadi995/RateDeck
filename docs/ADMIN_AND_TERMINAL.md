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
- server/service operations;
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

## Global launcher

Installer creates:

```text
/usr/local/bin/ratedeck
```

## Language/style

English-only. ANSI/Rich color when TTY is available, plain fallback when redirected.

Conceptual menu:

```text
╭──────────────────────────────────────────────╮
│           RateDeck Control Center            │
│            ● RUNNING  PID 1234               │
╰──────────────────────────────────────────────╯

 [1] Service
 [2] App Status
 [3] Logs
 [4] Database
 [5] Backup / Restore
 [6] Basic Config
 [7] Telegram Test
 [8] Render Test Card
 [9] Update / Repair
 [0] Exit
```

Provider/API product settings do not appear here.

## Service

- status/start/stop/restart;
- enable/disable systemd autostart;
- optional foreground debug run.

## Logs

- follow service journal;
- recent logs/errors;
- sanitized diagnostic bundle.

## Database / backup

- DB path/size/schema status;
- backup now/list/verify;
- restore with strong confirmation;
- safe optional maintenance.

## Basic config

Only operational bootstrap values such as Telegram token, admin IDs and log level. Provider keys/routing remain inside Telegram admin.

## Telegram test

Use `getMe` and optional bounded test message to configured admin. Never print token.

## Render test card

Use sample/current cached data without uncontrolled API refresh.

## Update / repair

- inspect repo state;
- refuse unsafe overwrite of tracked modifications;
- back up DB/config/assets/key first;
- fetch and fast-forward-only normal update;
- install changed dependencies as required;
- controlled migrations;
- smoke tests;
- restart only according to explicit update/operator action;
- preserve recoverable old data on failure.

Never use blind normal-path `git reset --hard` + `git clean -fd`.

## Uninstall

Separate:

- application/service removal while preserving data/backups;
- full purge with stronger confirmation.

Do not remove unrelated system services/packages.

## Shared logic

CLI calls the same app services for DB/backup/health/render where applicable. It does not reimplement product logic in shell.