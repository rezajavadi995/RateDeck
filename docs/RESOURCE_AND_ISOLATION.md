# Resource Budget and StarzYFire Isolation

RateDeck is intended to coexist safely on the same small VPS as StarzYFire. This document defines the resource and isolation contract for the initial deployment target.

## Target host

Primary sizing target:

- 2 vCPU;
- 4 GB RAM;
- 40 GB disk;
- StarzYFire and its existing services may already be running on the same host.

These are design targets, not a promise that an unmeasured implementation will fit. Phase 2 release validation must measure actual RSS/CPU/disk behavior on a representative host before calling the deployment production-ready.

## Hard isolation rule

RateDeck must not modify, restart, stop, migrate, reconfigure or reuse StarzYFire-owned application resources.

In particular RateDeck must not touch:

- `/opt/star` or other StarzYFire source/data paths;
- `starzyfire-*` systemd units;
- StarzYFire PostgreSQL databases/roles;
- StarzYFire Redis keys/configuration;
- StarzYFire NATS configuration/subjects;
- StarzYFire `.env`, secrets, backups or uploaded assets;
- StarzYFire ports/listeners;
- StarzYFire service user/group membership.

RateDeck must use its own Telegram bot token and its own application identity.

No installer/update/repair/uninstall path may perform wildcard operations that can match StarzYFire resources.

## Runtime topology

Default RateDeck runtime stays deliberately small:

- one Python bot process;
- Telegram long polling by default;
- no inbound HTTP/API listener required;
- one SQLite database;
- one bounded background refresh loop;
- async outbound HTTPS to configured providers;
- Pillow rendering locally;
- no Redis;
- no PostgreSQL;
- no NATS;
- no worker fleet;
- no web panel;
- no headless browser.

This minimizes collision risk and idle resource usage on a shared VPS.

## Filesystem ownership

Preferred Phase 2 installation layout separates code, configuration and mutable data:

```text
/opt/ratedeck/                 # source + venv, RateDeck-owned
/etc/ratedeck/
  ratedeck.env                # 0600/root or service-owned policy
  secret.key                  # 0600, never in repo/DB
/var/lib/ratedeck/
  ratedeck.db
  assets/
  cache/
  history/
/var/log/ratedeck/            # only if file logging is enabled
/var/backups/ratedeck/
/usr/local/bin/price           # verified symlink to RateDeck venv CLI
/etc/systemd/system/ratedeck.service
```

The intended global launcher relation is:

```text
/usr/local/bin/price -> /opt/ratedeck/.venv/bin/price
```

A dedicated `ratedeck` service account should own only the paths it needs. It must not be added to StarzYFire-specific groups merely for convenience.

Persistent data must live outside the git worktree where practical so a source update cannot accidentally target it.

## Memory budget

The implementation should be designed around bounded memory, not an ever-growing in-memory cache.

Initial engineering targets for measurement:

- normal warmed steady-state RateDeck RSS should aim to remain comfortably below ~300 MB;
- a single card render may temporarily raise memory, but normal peak should aim to stay below ~700 MB;
- no feature should require multi-GB resident memory;
- any sustained growth across repeated refresh/render cycles is a release blocker until explained/fixed.

These are acceptance targets, not values to fake in tests. Measure actual usage.

### Rendering memory

A 2160x2160 RGBA image alone is roughly 18 MB before additional layers/buffers. Multiple temporary Pillow surfaces can multiply this.

Therefore:

- default render concurrency on the 4 GB shared host is **1**;
- rendering must be bounded by a semaphore/queue or equivalent simple mechanism;
- do not keep full-resolution intermediate images alive longer than needed;
- close/release image objects promptly;
- card cache stores final bounded artifacts/metadata, not unlimited raw render surfaces;
- expensive rendering must not block Telegram callback acknowledgement/event-loop progress.

Do not add a process pool by default. If CPU isolation is later proven necessary, measure first.

## CPU budget

Normal idle/background CPU should be near-idle outside short provider refresh or card-render bursts.

Rules:

- provider refreshes are batched and modestly staggered;
- no busy polling;
- no one-task-per-market scheduler;
- no continuous recomputation of the full conversion graph when nothing changed;
- card rendering concurrency defaults to 1 on the target host;
- avoid CPU-heavy image filters whose visual value does not justify cost;
- background maintenance/history pruning runs infrequently and bounded.

With 2 vCPU, one render may briefly consume a core. That is acceptable; sustained saturation that harms StarzYFire is not.

## HTTP/network resource bounds

Use one shared bounded async HTTP client/pool where practical.

Avoid:

- one client/session per request;
- hundreds of simultaneous provider requests;
- per-user provider calls;
- per-asset Nobitex requests when the whole-market snapshot is available.

Provider refresh concurrency should remain small (normally one task per active provider at most, with overall orchestration kept bounded).

## SQLite behavior

SQLite is chosen specifically to avoid adding another database service.

Implementation should use sane single-process settings such as WAL/busy timeout where appropriate and tested, while keeping transactions short.

Do not run large maintenance/vacuum operations in latency-sensitive paths.

## Disk budget

The 40 GB disk must not be treated as an unlimited cache.

Default policy must bound:

- local history by age + row/storage cap;
- rendered-card cache by age/size and/or LRU policy;
- application file logs by rotation/retention, or prefer journal with bounded system policy;
- backups by count/age/size retention;
- uploaded assets by size/type/count policy;
- temporary render files with cleanup on success/failure.

RateDeck should not retain one rendered image forever for every request.

Suggested initial operational objective: RateDeck application data/cache/history/log/backups should normally remain in the low-single-digit GB range, not grow toward the full 40 GB disk. Exact defaults are implemented and measured in Phase 2.

## Backpressure

If render demand exceeds capacity:

- queue a small bounded number of render jobs;
- coalesce/cache identical renders where safe;
- reject/defer excess work gracefully rather than creating unlimited tasks;
- admin preview rendering obeys the same resource gate.

Provider refreshes likewise use singleflight and do not multiply because many users ask simultaneously.

## systemd safeguards

Phase 2 may use conservative systemd protections after measurement, for example:

- dedicated `User=ratedeck`;
- `NoNewPrivileges=true` where compatible;
- explicit writable paths;
- sensible restart delay/limits;
- optional `MemoryHigh`/`MemoryMax` only after measured values prove safe;
- optional CPU scheduling/quota controls only if coexistence testing shows a need.

Do not guess an aggressive memory/CPU hard limit that creates restart loops. Measurement comes first.

## Health/diagnostics resource view

Terminal/App Status should show local, low-cost resource information without external API calls:

- RateDeck service PID/state;
- current RateDeck RSS where available;
- process CPU snapshot where available;
- DB size;
- RateDeck data/cache/history/backups/log path sizes;
- filesystem free space;
- render queue/in-flight count;
- background refresh heartbeat;
- recent OOM/restart indication when detectable.

Opening the global `price` menu must itself remain short-lived/lightweight and must not launch another RateDeck bot/background refresh process.

Do not inspect or alter StarzYFire internals as part of normal RateDeck health checks. Coexistence verification can report host-level memory/load/disk only.

## Installation safety on a shared StarzYFire host

Installer must:

- create only RateDeck-owned user/paths/unit/launcher;
- create `/usr/local/bin/price` only after verifying it does not overwrite an unrelated existing command/path;
- verify `/usr/local/bin/price` points to the RateDeck venv console script after install/repair;
- avoid changing Redis/PostgreSQL/NATS configuration;
- avoid changing firewall rules/ports by default;
- avoid distro-wide Python package mutation outside the RateDeck venv;
- avoid restarting unrelated services after apt operations;
- fail if target RateDeck paths unexpectedly point/symlink into another app path;
- validate that `/opt/ratedeck`, `/var/lib/ratedeck`, `/etc/ratedeck` and backup paths are not symlinked to StarzYFire locations;
- uninstall only exact RateDeck-owned resources, including removing `/usr/local/bin/price` only if ownership/target verification succeeds.

## Coexistence acceptance gate

Before production deployment on the shared 4 GB / 2 vCPU host:

1. record host baseline with StarzYFire running;
2. start RateDeck and record idle/warmed RSS/CPU;
3. run bounded provider refresh;
4. render representative cards serially and in the configured bounded queue;
5. exercise parser/admin/diagnostics;
6. exercise `price` menu/status/update preflight without spawning an extra bot process;
7. observe StarzYFire health/latency during RateDeck bursts without modifying StarzYFire;
8. verify no RateDeck process opens unexpected inbound ports;
9. verify RateDeck has no open files/connections to StarzYFire-owned DB/config/data paths;
10. verify disk/cache/history/backups remain bounded;
11. fail release if RateDeck causes meaningful StarzYFire instability or sustained host resource pressure.

The exact measured results must be reported; do not call coexistence safe based only on architecture assumptions.
