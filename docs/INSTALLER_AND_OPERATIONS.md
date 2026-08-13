# Installer and Operations Contract

## Goal

RateDeck must be installable on a fresh supported Debian/Ubuntu server with one short command while preserving operator data safely across updates.

The installer is part of the product and receives automated tests/smoke validation; it is not an afterthought.

## Target layout

Default installation layout:

```text
/opt/ratedeck/
├── .venv/
├── .env
├── ratedeck/           # source package
├── data/
│   ├── ratedeck.db
│   ├── assets/
│   ├── rendered/
│   └── history/        # only if separate files are actually needed
├── logs/
└── backups/

/etc/ratedeck/
└── secret.key          # if this layout is chosen; mode 0600

/usr/local/bin/ratedeck
/etc/systemd/system/ratedeck.service
```

Exact placement may be adjusted during Phase 2, but code, persistent data and master secrets must have explicit boundaries.

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

Re-running installer on an existing valid installation must not delete DB/config/assets.

### Fail safe

On failure:

- preserve existing application data;
- print the failing stage/command category;
- avoid half-written secret/config files;
- do not leave a falsely active broken service when a previous service can remain untouched.

### Root awareness

System package installation/systemd/global launcher need root. Application process should use a dedicated service account if practical; do not run as root merely because the installer runs as root.

## Bootstrap sequence

Conceptual sequence:

1. validate bash/root/platform/architecture;
2. check disk/network prerequisites;
3. wait for apt/dpkg locks safely;
4. install minimal system packages;
5. create service user/directories;
6. clone or update repository safely;
7. create/reuse virtual environment;
8. install pinned Python dependencies;
9. create/preserve `.env`;
10. generate/preserve encryption master key;
11. initialize/upgrade DB schema with pre-migration backup when appropriate;
12. install `ratedeck` launcher;
13. write systemd unit;
14. run configuration/import/database smoke checks;
15. optionally enable/start service according to installer contract;
16. print clear summary/next steps.

## Update safety

Normal update flow must **not** do this blindly:

```text
git reset --hard origin/main
git clean -fd
```

Instead:

1. inspect repository state;
2. if tracked local modifications exist, stop and report them unless an explicit recovery mode is chosen;
3. create DB/config/assets backup;
4. `git fetch`;
5. verify expected branch/remote;
6. perform fast-forward-only update where possible;
7. update venv dependencies;
8. run app-owned schema migration;
9. run smoke checks;
10. restart service only in the explicit update workflow;
11. verify service health.

Do not delete untracked files in persistent data directories.

## Persistent data boundaries

These survive reinstall/update:

- `.env`;
- database;
- encrypted provider secrets;
- encryption master key;
- uploaded logos/assets;
- card configuration;
- templates/buttons/aliases;
- local market history;
- backups;
- operator logs subject to rotation policy.

Do not place persistent user/operator data inside a directory that a git clean operation would target.

## systemd service

Requirements:

- explicit WorkingDirectory;
- venv Python executable;
- restart-on-failure with sensible delay;
- environment file;
- unbuffered/structured logs as appropriate;
- dedicated user if feasible;
- restrictive filesystem permissions;
- no shell interpolation of secrets into ExecStart command line.

Optional hardening directives may be added after verifying they do not block required asset/database writes/network access.

## `ratedeck` launcher

`/usr/local/bin/ratedeck` should be a tiny stable launcher into the Python CLI package, not a second implementation of all operational logic.

It resolves the install directory and executes something conceptually equivalent to:

```text
/opt/ratedeck/.venv/bin/python -m ratedeck.cli
```

The actual CLI uses a terminal library/ANSI support to provide a polished English menu with graceful non-TTY behavior.

## Backups

### What to back up

- SQLite DB using a consistent SQLite backup mechanism, not unsafe raw copy during writes;
- `.env` in a protected archive or separate secured copy if product policy permits;
- encryption master key with explicit security warning;
- uploaded assets;
- optional configuration manifests.

Never print secrets during backup.

### Metadata

Each backup records:

- timestamp;
- app/schema version;
- source paths/components;
- checksum;
- backup type (manual/pre-update/pre-restore);
- verification status.

### Retention

Configurable bounded retention. Pre-update/pre-restore safety backups may have a minimum retention independent from routine backups.

## Restore

Restore flow:

1. stop or quiesce app writes;
2. validate backup/checksum/schema compatibility;
3. create pre-restore backup of current state;
4. restore to temporary path;
5. validate database/open/schema;
6. atomically replace where feasible;
7. restore assets/config components explicitly;
8. run smoke check;
9. start/restart only when safe;
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

## Logs

Use systemd journal plus optional rotating application files if they provide value. Terminal menu should access both through shared helpers.

Do not create uncontrolled log growth.

## Repair mode

Repair may:

- recreate venv;
- reinstall dependencies;
- validate permissions;
- rewrite known systemd unit/launcher from repository templates;
- run DB integrity/schema checks;
- validate font/assets directories.

Repair must not reset application data/settings by default.

## Uninstall

Offer two scopes:

### Application uninstall, preserve data

Remove/disable service, launcher, venv/source as appropriate while preserving DB/backups/assets/secrets for reinstall.

### Full purge

Requires strong typed confirmation. Removes RateDeck-owned data only.

Never remove shared Redis/PostgreSQL/etc. because RateDeck does not own them in the default architecture.

## Installer tests

Phase 2 must include automated/static tests and at least a controlled disposable-environment smoke sequence covering:

- fresh install path;
- rerun/idempotency;
- existing `.env` preservation;
- existing DB preservation;
- dirty git tree update refusal;
- fast-forward update;
- broken venv repair;
- backup creation/verification;
- launcher works from arbitrary directory;
- systemd unit content sanity;
- no plaintext secret leak in normal output.
