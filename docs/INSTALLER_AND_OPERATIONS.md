# Installer and Operations Contract

## Goal

RateDeck must be installable on a fresh supported Debian/Ubuntu server with one short command while preserving operator data safely across updates and remaining isolated from other applications on the host, especially StarzYFire.

The installer is part of the product and receives automated tests/smoke validation; it is not an afterthought.

Read `docs/RESOURCE_AND_ISOLATION.md` for the target 4 GB RAM / 2 vCPU shared-host budget and mandatory StarzYFire isolation rules.

## Target layout

Preferred installation layout separates source, configuration and mutable data:

```text
/opt/ratedeck/                 # source + .venv only
/etc/ratedeck/
├── ratedeck.env               # protected configuration
└── secret.key                 # 0600, never in repo/DB
/var/lib/ratedeck/
├── ratedeck.db
├── assets/
├── cache/
└── history/
/var/log/ratedeck/             # only if file logging is enabled
/var/backups/ratedeck/
/usr/local/bin/price           # symlink to RateDeck venv console script
/etc/systemd/system/ratedeck.service
```

This follows normal Linux separation:

- `/opt/ratedeck` = application source/venv;
- `/etc/ratedeck` = protected configuration/secrets;
- `/var/lib/ratedeck` = mutable application data;
- `/var/backups/ratedeck` = application backups;
- `/usr/local/bin/price` = global operator command.

Exact placement may be adjusted during Phase 2 only if the same isolation/data-preservation properties remain true.

Do not place RateDeck persistent data under `/opt/star` or any StarzYFire-owned path.

## One-line installation

Once the installer exists and passes acceptance tests, README exposes:

```bash
sudo bash -c "$(curl -fsSL https://raw.githubusercontent.com/rezajavadi995/RateDeck/main/install.sh)"
```

The installer validates that downloaded content is actually the expected shell script and fails clearly on network/auth/HTML error responses.

## Supported systems

At minimum target current maintained Ubuntu/Debian families used by the owner. Phase 2 must document exact tested versions rather than claiming all Linux distributions.

## Installer properties

### Idempotent

Re-running installer on an existing valid installation must not delete DB/config/assets/history/backups/master key.

### Fail safe

On failure:

- preserve existing application data;
- print the failing stage/command category;
- avoid half-written secret/config files;
- do not leave a falsely active broken service when a previous service can remain untouched.

### Root awareness

System package installation/systemd/global launcher need root. The RateDeck application runs under a dedicated `ratedeck` service account unless a tested platform constraint prevents it.

The `ratedeck` user must not be added to StarzYFire-specific groups merely for convenience.

## Shared-host isolation

Installer/update/repair/uninstall must only operate on exact RateDeck-owned resources.

They must not modify/restart/remove:

- `/opt/star` or StarzYFire data/config paths;
- `starzyfire-*` units;
- PostgreSQL/Redis/NATS configuration used by StarzYFire;
- StarzYFire DBs/roles/keys/backups;
- StarzYFire firewall/ports;
- StarzYFire users/groups.

No wildcard deletion/service operation may be broad enough to match another application.

RateDeck requires no Redis, PostgreSQL, NATS or inbound application port in the default deployment.

Before using its own paths, installer verifies they are not unexpected symlinks into another application's directories.

## Bootstrap sequence

Conceptual sequence:

1. validate bash/root/platform/architecture;
2. check disk/network prerequisites;
3. wait for apt/dpkg locks safely;
4. install only minimal required system packages without restarting unrelated app services deliberately;
5. create dedicated RateDeck service user/directories;
6. clone or update repository safely into `/opt/ratedeck`;
7. create/reuse RateDeck-only virtual environment;
8. install pinned Python dependencies inside that venv;
9. create/preserve protected `/etc/ratedeck/ratedeck.env`;
10. generate/preserve encryption master key;
11. initialize/upgrade RateDeck SQLite schema with pre-migration backup when appropriate;
12. install the Python console entry point `price` in the RateDeck venv;
13. create/verify `/usr/local/bin/price -> /opt/ratedeck/.venv/bin/price`;
14. write `ratedeck.service` only;
15. run configuration/import/database smoke checks;
16. offer/run Quick Setup when required;
17. optionally enable/start RateDeck service according to installer contract;
18. print clear summary/next steps.

## Global `price` launcher

The operator-facing command is:

```text
price
```

The Python package exposes a console script named `price`, conceptually from project metadata such as:

```text
price = ratedeck.cli.main:main
```

Installer then creates the stable global symlink:

```text
/usr/local/bin/price -> /opt/ratedeck/.venv/bin/price
```

Therefore `price` works from `/root`, `/tmp`, `/opt/star`, the home directory, or any other current working directory without changing directory first.

Rules:

- bare `price` opens the interactive terminal menu;
- the CLI resolves all RateDeck paths explicitly and never assumes current working directory equals the repo;
- installer/repair verifies the symlink target exists and is RateDeck-owned;
- if `/usr/local/bin/price` already exists and is not the expected RateDeck-owned symlink, installer **must not overwrite it silently**;
- venv repair recreates the console entry point and then repairs the symlink if safe;
- uninstall removes the global link only after ownership/target verification.

Small non-interactive convenience commands are allowed and expected:

```text
price status
price start
price stop
price restart
```

They invoke the same Python service-control functions used by the menu.

## Quick Setup / configuration

Initial configuration must be as easy as the useful parts of the StarzYFire terminal flow, without copying its infrastructure complexity.

After installation the operator runs:

```text
price
```

and chooses `Setup / Config`.

Quick Setup should guide through only operational bootstrap values:

1. Telegram bot token — masked in status/output;
2. admin Telegram ID(s);
3. log level from a bounded terminal choice;
4. validate config syntax;
5. test Telegram `getMe` on explicit request;
6. show a final summary with secrets redacted;
7. optionally start/restart **RateDeck only** after confirmation.

Existing values should be shown as `configured / not configured` or masked summaries, not plaintext secrets.

Provider API keys/routing are intentionally **not** part of terminal Quick Setup; they belong in the Persian Telegram admin panel.

Changing one config value must not force the operator through the entire wizard again. Provide both Quick Setup and per-setting edit actions.

## Running the bot

The normal long-running bot is managed only by `ratedeck.service`.

From the terminal menu:

```text
Service -> Start
```

starts the bot.

For first setup, `Setup / Config -> Start RateDeck` may call the exact same service-start operation after configuration validates.

From shell, the convenience command is:

```text
price start
```

No command should launch a second long-running bot if `ratedeck.service` is already active. Bare `price` opens the menu; it does **not** start another bot process.

## Smart Update safety

The terminal update is state-aware. Normal update must **not** blindly run:

```text
git pull
git reset --hard origin/main
git clean -fd
```

### Update preflight

Before mutation, collect and display:

- current local commit;
- fetched remote `main` commit;
- up-to-date / update-available / diverged status;
- expected remote URL/branch validity;
- tracked/untracked working-tree state relevant to safe update;
- current and target app/schema version where available;
- whether dependency manifests changed;
- whether migrations are pending;
- whether launcher/systemd templates changed;
- free disk/backup-space check;
- current `ratedeck.service` state.

If already current, return **UP TO DATE** with no update mutation.

### Update algorithm

1. verify expected RateDeck repository/remote/branch/path;
2. refuse normal update if unsafe tracked local changes or divergence exist;
3. fetch remote and calculate exact commit delta;
4. optionally show changed commits/files before confirmation;
5. validate enough disk/backup space;
6. create and verify pre-update backup for RateDeck persistent data/config/key metadata under policy;
7. perform fast-forward-only code update;
8. reinstall dependencies only if dependency files changed or repair explicitly requests it;
9. run only pending RateDeck migrations, with pre-migration safety checks;
10. recreate/verify `price` venv entry point and `/usr/local/bin/price` only if necessary;
11. update/verify `ratedeck.service` only if its template changed;
12. run compile/import/config/database smoke checks;
13. if RateDeck was running, use the explicit update restart policy for `ratedeck.service` only;
14. verify post-update RateDeck health;
15. report old/new commit plus steps executed/skipped.

A failed preflight stops before mutation. A post-update validation failure preserves backup/recovery information and never broadens repair scope to StarzYFire or unrelated host services.

Do not delete untracked files in persistent RateDeck data directories and do not inspect/reset unrelated repositories.

## Persistent data boundaries

These survive reinstall/update:

- `/etc/ratedeck/ratedeck.env`;
- RateDeck SQLite DB;
- encrypted provider secrets;
- encryption master key;
- uploaded logos/assets;
- card configuration;
- templates/buttons/aliases;
- bounded local market history;
- RateDeck backups;
- operator logs subject to rotation policy.

Persistent data should remain outside the git worktree where practical.

## systemd service

Requirements:

- exact unit name `ratedeck.service`;
- explicit WorkingDirectory;
- RateDeck venv Python executable;
- dedicated `User=ratedeck` where feasible;
- restart-on-failure with sensible delay/limits;
- protected environment file;
- unbuffered/structured logs as appropriate;
- restrictive filesystem permissions;
- no shell interpolation of secrets into ExecStart command line;
- no unexpected inbound port/listener in default long-polling deployment.

Optional systemd memory/CPU limits are added only after measured coexistence tests. Do not guess aggressive hard limits that create restart loops.

## Backups

### What to back up

- SQLite DB using a consistent SQLite backup mechanism, not unsafe raw copy during writes;
- protected environment/config according to product policy;
- encryption master key with explicit security warning;
- uploaded assets;
- optional configuration manifests.

Never print secrets during backup.

### Metadata

Each backup records or exposes enough metadata for:

- timestamp;
- app/schema version;
- source components;
- checksum;
- backup type (manual/pre-update/pre-restore);
- verification status.

A dedicated backup metadata table is optional if filesystem metadata/indexing is simpler and sufficient.

### Retention

Configurable bounded retention by count/age/size. Pre-update/pre-restore safety backups may have a minimum retention independent from routine backups.

## Restore

Restore flow:

1. stop/quiesce RateDeck writes only;
2. validate backup/checksum/schema compatibility;
3. create pre-restore backup of current RateDeck state;
4. restore to temporary RateDeck-owned path;
5. validate database/open/schema;
6. atomically replace where feasible;
7. restore RateDeck assets/config explicitly;
8. run smoke check;
9. start/restart RateDeck only when safe;
10. report result.

A failed restore must not destroy both current state and backup.

## Database migration

Even SQLite requires versioned schema evolution.

Migration runner requirements:

- current schema version table;
- ordered migrations;
- transactional migration where SQLite permits;
- backup before risky migration/update;
- idempotent version detection;
- no automatic downgrade;
- tests from empty DB and prior fixture versions.

## Logs and disk bounds

Prefer journal plus optional rotating application files only when they add value.

RateDeck must not create uncontrolled growth from:

- logs;
- rendered cards;
- local history;
- backups;
- uploads;
- temporary render files.

Implement age/count/size cleanup policies as specified in `docs/RESOURCE_AND_ISOLATION.md`.

## Repair mode

Repair may:

- recreate RateDeck venv;
- reinstall RateDeck dependencies;
- validate RateDeck permissions;
- recreate/verify the `price` console entry point and `/usr/local/bin/price` symlink;
- rewrite only known RateDeck systemd unit/launcher from repository templates;
- run RateDeck DB integrity/schema checks;
- validate RateDeck font/assets directories.

Repair must not reset application data/settings by default and must never repair/reconfigure StarzYFire/shared services.

## Uninstall

Offer two scopes:

### Application uninstall, preserve data

Remove/disable only RateDeck service/verified `price` launcher/source/venv as appropriate while preserving RateDeck DB/backups/assets/secrets.

### Full purge

Requires strong typed confirmation. Removes exact RateDeck-owned data only.

Never remove shared Redis/PostgreSQL/NATS or any StarzYFire resource.

## Installer tests

Phase 2 must include automated/static tests and at least a controlled disposable-environment smoke sequence covering:

- fresh install path;
- rerun/idempotency;
- existing config/master-key preservation;
- existing DB preservation;
- dedicated service user/path ownership;
- symlink/path escape rejection;
- existing unrelated `/usr/local/bin/price` collision refusal;
- `price` opens menu from arbitrary working directories;
- `price status/start/stop/restart` use the same service logic;
- dirty RateDeck git tree update refusal;
- already-up-to-date no-op;
- fast-forward update;
- dependency reinstall only when required;
- pending migration handling;
- broken venv/launcher repair;
- backup creation/verification;
- systemd unit content sanity;
- no plaintext secret leak in normal output;
- no operation against `/opt/star`, `starzyfire-*`, Redis, PostgreSQL or NATS;
- no unexpected inbound listener;
- bounded cache/log/history/backup behavior.
