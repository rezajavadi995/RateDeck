# Definition of Done

This file prevents “implemented” from meaning “code exists”. A phase/release is done only when the applicable gates below are evidenced on the exact head.

## Architecture gates

- [ ] No monkey patch/runtime symbol replacement exists.
- [ ] No bootstrap installer rewrites imported functions/classes.
- [ ] No Telegram handler calls external market HTTP directly.
- [ ] No market/provider adapter imports Telegram routers/types.
- [ ] Provider selection is registry/strategy driven rather than a large conditional tree.
- [ ] Dynamic Nobitex market universe is not constrained by a static finite asset list.
- [ ] Router/handler order is explicit and regression-tested.
- [ ] Core modules are cohesive; no accidental mega `bot.py`/admin/provider/engine file owns multiple domains.

## Market/provider gates

- [ ] Nobitex whole-market discovery/snapshot parses valid markets and isolates malformed entries.
- [ ] RLS->Toman conversion is tested.
- [ ] Provider A success cannot refresh provider B freshness.
- [ ] Last-known-good retains original success timestamp.
- [ ] 429/backoff/cooldown behavior is tested and persisted.
- [ ] Normal user traffic does not cause one provider request per user request.
- [ ] Concurrent refresh attempts coalesce.
- [ ] Provider provenance survives derived conversions.
- [ ] CoinGecko ambiguous symbol mapping does not silently resolve.
- [ ] ExchangeRate fiat logic cannot silently become Iranian free-market Toman source.
- [ ] Admin health displays fresh/stale/cooldown/disabled/no-data accurately.
- [ ] API keys never appear in logs/diagnostics/callback data.

## Parser/conversion gates

- [ ] Persian digits accepted.
- [ ] Arabic-Indic digits accepted.
- [ ] Latin digits accepted.
- [ ] Persian decimal/grouping accepted where valid.
- [ ] Compact no-space market forms covered.
- [ ] Persian/English aliases covered.
- [ ] Dynamic discovered symbols covered.
- [ ] Natural-language false-positive corpus passes.
- [ ] Group parser safety mode passes.
- [ ] Decimal arithmetic used canonically.
- [ ] Direct/inverse/bridge conversion paths tested.
- [ ] Loop/max-hop/no-route behavior tested.
- [ ] Full path provenance tested.
- [ ] All generated numeric values use ASCII digits.

## Content/UI gates

- [ ] All admin-configurable texts are template-backed rather than hard-coded in handlers.
- [ ] Template scopes define allowed placeholders.
- [ ] Required/unknown/malformed placeholder behavior tested.
- [ ] Every editable template has preview/sample data.
- [ ] Field fragments and master caption compose safely.
- [ ] Telegram custom emoji capture/render round-trip tested.
- [ ] UTF-16 entity offsets tested with Persian + emoji + placeholder expansion.
- [ ] There is no separate Premium Emoji manager.
- [ ] Asset caption emoji is editable asset metadata.
- [ ] Button custom emoji icon behavior is centralized.
- [ ] Exposed button styles are default/primary/success/danger only.
- [ ] callback_data <=64 UTF-8 bytes enforced before button creation.
- [ ] Long admin values are safely summarized in button labels.
- [ ] Large lists paginate and have practical search/recent/favorites navigation.
- [ ] Admin UI defaults to Persian.
- [ ] Terminal UI is English-only.

## Stars gates

- [ ] Admin can create exact Stars package using Persian or Latin numeric input.
- [ ] Stored/rendered numbers are normalized/ASCII output.
- [ ] Exact package query works.
- [ ] Non-configured quantity does not interpolate by default.
- [ ] Package mutation is audited.

## Card gates — Phase 2

- [ ] Generic unknown asset renders professionally.
- [ ] Asset-family auto style works without per-asset manual config.
- [ ] Multiple layouts/themes/chart styles exist behind registries.
- [ ] Incompatible combinations are blocked/fallback safely.
- [ ] 1080x1080 final card generated correctly.
- [ ] High-resolution/downsample path validated where enabled.
- [ ] Long names, large prices, tiny prices, positive/negative change covered.
- [ ] Missing logo/font/history has graceful fallback.
- [ ] No fabricated historical chart points.
- [ ] History-building/no-history state is truthful.
- [ ] Asset override/reset hierarchy works.
- [ ] Uploaded logo validation/path safety tested.
- [ ] Representative visual/golden changes reviewed intentionally.

## Security/observability gates

- [ ] Admin authorization enforced at action execution, not just menu visibility.
- [ ] Forged admin callback cannot mutate state.
- [ ] Provider keys encrypted at rest.
- [ ] Master key stored outside repository/database with restrictive permissions.
- [ ] Secret redaction tests exist.
- [ ] Structured provider events exist.
- [ ] Durable admin audit events exist.
- [ ] Arbitrary user messages are not logged in full by default.
- [ ] File uploads/path operations are bounded and traversal-safe.
- [ ] Backups are bounded, permission-safe and verifiable.

## Installer/operations gates — Phase 2

- [ ] One-line installer in README matches real `install.sh`.
- [ ] Fresh supported Debian/Ubuntu install smoke passes.
- [ ] Re-running installer preserves `.env`, DB, assets and master key.
- [ ] `ratedeck` launcher works outside project directory.
- [ ] systemd service uses expected venv/working directory and starts cleanly.
- [ ] Dirty tracked repo causes normal update to stop safely.
- [ ] Normal updater does not blind `reset --hard`/`clean -fd` operator state.
- [ ] Pre-update backup is created/verified.
- [ ] Backup/restore has pre-restore safety backup.
- [ ] Uninstall preserve-data vs full-purge scopes are distinct.
- [ ] Terminal does not duplicate provider/API product settings.
- [ ] CLI/status/log output does not expose secrets.

## Test/reporting gates

- [ ] Relevant focused tests were run during work.
- [ ] Full test suite ran at phase completion.
- [ ] Exact pass/fail/skip counts reported.
- [ ] Compile/import smoke checks ran.
- [ ] Live provider checks, if not run, are explicitly reported as not run.
- [ ] Live Telegram validation, if not run, is explicitly reported as not run.
- [ ] No unexecuted test is described as passed.
- [ ] Documentation updated to actual implementation.

## Release readiness statement

A release may be called production-ready only after every applicable gate is satisfied or a clearly documented accepted exception exists with owner approval. “Unit tests pass” alone is not production readiness.
