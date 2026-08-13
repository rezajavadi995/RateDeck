# Admin and Terminal UX

## Design split

RateDeck has two administration surfaces with deliberately different responsibilities.

### Telegram Admin Panel

- Persian
- product configuration
- provider/API configuration
- content/buttons/card customization
- market/asset management
- health/diagnostics
- logs/audit summaries

### Terminal Control Center

- English-only
- operational/server control
- service lifecycle
- logs
- database backup/restore
- update/repair
- connectivity smoke tests
- no provider/API product management

This separation prevents duplicated settings logic and RTL terminal issues.

---

# Telegram Admin Panel

## Root menu

Target conceptual structure:

```text
⚙️ پنل مدیریت RateDeck

[ 📊 بازار و APIها ]   [ 🪙 دارایی‌ها ]
[ 🖼 طراحی کارت ]      [ 📝 متن‌ها و دستورات ]
[ 🔘 دکمه‌ها ]         [ 🎨 ظاهر و برندینگ ]
[ ⭐ قیمت استارز ]     [ 🩺 سلامت ]
[ 📋 لاگ و Audit ]     [ 💾 بکاپ ]
[ 🧰 سیستم ]
```

Actual row structure must respect Telegram UX and mobile width; safe label formatter applies globally.

## Market & APIs

Provider overview should show compact health status and open a detailed page.

Detail should include:

- provider name;
- enabled state;
- mode (public/keyed/manual where applicable);
- last success;
- last failure/category;
- last latency;
- cache age/freshness;
- cooldown/next attempt;
- RateDeck request counters/budget;
- optional provider quota if safely available;
- asset/mapping count when relevant.

Actions should be inline where finite:

- enable/disable;
- public/keyed mode;
- refresh/test;
- routing selection;
- view cache status;
- view mappings/errors.

Entering an API key requires a dedicated admin FSM free-text state. The received message containing the key should be deleted when possible after secure capture. Key is encrypted at rest and never echoed back.

## Assets

Navigation order:

```text
Favorites
Recent
Category/Family
Search
All (paged)
```

Asset page can manage:

- enabled;
- display name;
- aliases;
- family;
- caption emoji;
- card override;
- source mappings/markets;
- favorite;
- reset overrides.

Do not create one permanent menu entry per discovered asset at the root.

## Content & Commands

Sections:

- `/start`
- `/help`
- `/market`
- `/support`
- `/about`
- price response
- conversion response
- card master caption
- card field fragments
- error/empty/stale messages

Every editor page shows:

- full current body in the message;
- safe summary in buttons;
- allowed placeholders;
- validation state;
- preview;
- edit/reset/save/back.

`/about` can be toggled visible/hidden. `/panel` remains admin-only. `/settings` is not a separate command.

## Buttons

Button customization includes:

- text;
- style: default/primary/success/danger;
- optional captured custom emoji icon;
- enabled state where product-safe;
- menu position/order only where that menu is designed as configurable.

Structural safety actions such as destructive confirmations may have fixed action semantics even if label/style is customizable.

## Card Designer

Navigation:

- global design defaults;
- family themes;
- layouts;
- chart styles;
- branding/logo;
- asset overrides;
- text layers;
- preview.

Element editing uses inline movement/size/style controls. Preview before save should be the normal workflow for visual changes.

## Stars Manual Pricing

Page:

- list configured packages;
- add package;
- edit selected package;
- enable/disable;
- delete with confirmation;
- history/audit.

Free-form line format accepts `quantity price`, Persian digits included. Output confirmation uses ASCII digits.

## Health

Unified health summarizes:

- bot runtime;
- database;
- background refresher;
- provider states;
- card renderer prerequisites;
- disk space threshold if available;
- last unhandled exception count/window.

Health is diagnostic, not a fake “all green” badge. Unknown should be shown as unknown.

## Logs & Audit

Admin gets summaries/pagination/filtering, not endless raw log dumps.

Possible filters:

- errors;
- provider events;
- admin changes;
- card/render errors;
- parser/unknown-intent diagnostics (sampled, privacy-safe).

Export may generate a bounded sanitized file.

## Backup

Admin can request a safe application backup. Destructive restore requires strong confirmation and may be restricted to terminal depending on implementation safety.

---

# Terminal Control Center

## Global launcher

Installer creates:

```text
/usr/local/bin/ratedeck
```

which launches the project CLI from any working directory.

## Language and rendering

Terminal menu is English-only. Avoid Persian status text in fixed-width boxes. ANSI/Rich color may be used when TTY is available and gracefully disabled when output is redirected.

Suggested visual style:

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

Use color semantically:

- green: healthy/running/success;
- yellow: warning/degraded;
- red: failure/destructive;
- cyan/blue: information/navigation.

## Service menu

- status;
- start;
- stop;
- restart;
- enable/disable systemd autostart;
- foreground run for debugging if useful.

Actions report exact systemd outcome.

## Logs

- follow service journal;
- recent logs;
- recent errors;
- application file log if configured;
- sanitized diagnostic bundle export.

## Database

- status/path/size/schema version;
- backup now;
- list backups;
- verify backup;
- restore with strong confirmation;
- optional vacuum/maintenance with safe checks.

Do not expose or print encrypted secrets unnecessarily.

## Basic config

Only server-bootstrap values that make sense operationally:

- Telegram bot token;
- admin ID(s);
- log level;
- maybe install/runtime path diagnostics.

Provider API keys and routing belong in Telegram Admin, not here.

## Telegram test

Test should call Telegram `getMe` and optionally send one bounded test message to configured admin. Never print the bot token.

## Render test card

Uses local sample data or current cached data without causing uncontrolled provider refresh. It validates renderer/font/logo/output path.

## Update / Repair

Must be safe and conservative:

- inspect current repo state;
- refuse normal update if tracked local modifications would be overwritten;
- backup DB/config/assets first;
- fetch remote;
- use fast-forward-only update for normal path;
- reinstall dependencies only as required;
- run schema migrations in controlled app-owned step;
- run smoke checks;
- restart only when explicitly selected by the operator/update workflow contract;
- on failure, preserve old data and show recovery instructions.

No normal updater path may blind-reset or clean arbitrary files.

## Uninstall

Destructive and explicit. Offer distinction between:

- remove service/application but preserve data/backups;
- full purge including data, requiring stronger confirmation.

Do not silently remove unrelated system packages/services.

## Shared logic

CLI invokes the same application services/repositories used by Telegram admin where applicable. It does not reimplement backup, health, database or render logic in shell snippets.
