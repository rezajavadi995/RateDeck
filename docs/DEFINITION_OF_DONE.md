# Definition of Done

A phase/release is done only when applicable gates below are evidenced on the exact head.

## Architecture / lean gates

- [ ] No monkey patch/runtime symbol replacement/bootstrap patch installer exists.
- [ ] No Telegram handler calls external provider HTTP directly.
- [ ] No market/provider adapter imports Telegram routers/types.
- [ ] Provider selection/routing is registry/policy driven rather than a large branch tree.
- [ ] Dynamic Nobitex universe is not constrained by a finite static asset list.
- [ ] Router/handler order is explicit and regression-tested.
- [ ] No accidental mega `bot.py`/admin/provider/engine file owns unrelated domains.
- [ ] No unnecessary DI framework, generic repository framework, event bus, plugin framework, Redis/PostgreSQL/distributed lock was added to the defined initial scope.
- [ ] Architecture did not create dozens of empty/forwarding modules merely to match diagrams.
- [ ] Phase 1 did not prematurely create Phase 2 card/upload/backup infrastructure.

## Market/provider gates

- [ ] Nobitex whole-market discovery parses valid markets and isolates malformed entries.
- [ ] RLS -> Toman conversion is tested.
- [ ] Provider A success cannot refresh provider B freshness.
- [ ] Last-known-good retains original success timestamp.
- [ ] 429/Retry-After/backoff/cooldown behavior is tested and persisted.
- [ ] Normal user traffic does not cause one provider request per user request.
- [ ] Concurrent refresh attempts coalesce in-process.
- [ ] Provider provenance survives derived conversions.
- [ ] CoinGecko ambiguous symbol mapping does not silently resolve.
- [ ] Full Nobitex discovery does not trigger wasteful full CoinGecko enrichment of all assets.
- [ ] ExchangeRate fiat logic cannot silently become Iranian free-market Toman source.
- [ ] History persistence is bounded/hot-set based and cannot grow by writing all markets on every refresh.
- [ ] Admin health displays fresh/stale/cooldown/disabled/no-data accurately.
- [ ] API keys never appear in logs/diagnostics/callback data.

## Parser/conversion/number gates

- [ ] Persian digits accepted.
- [ ] Arabic-Indic digits accepted.
- [ ] Latin digits accepted.
- [ ] Persian decimal/grouping separators accepted where valid.
- [ ] Compact no-space market forms covered.
- [ ] Persian/English aliases covered.
- [ ] Dynamic discovered symbols covered.
- [ ] Natural-language false-positive corpus passes.
- [ ] Command/admin-state collisions do not fall into market parser.
- [ ] Decimal arithmetic used canonically.
- [ ] Direct/inverse/bridge paths tested.
- [ ] Loop/max-hop/no-route behavior tested.
- [ ] Full path provenance tested.
- [ ] All generated numeric values use ASCII digits.

## Content / `{}` / rich-text gates

- [ ] All designated admin-configurable texts are template-backed rather than hard-coded in handlers.
- [ ] Central Placeholder Registry defines scope/type/Persian description/sample for supported placeholders.
- [ ] Template editor can show valid placeholders for the exact selected scope.
- [ ] Required/unknown/malformed/wrong-scope placeholder behavior tested.
- [ ] Literal-brace behavior is documented/tested.
- [ ] Every editable template has realistic preview/sample data.
- [ ] Field fragments and master caption compose safely.
- [ ] Direct/indirect field cycles are detected.
- [ ] Expansion depth/size is bounded.
- [ ] Final Telegram target length is validated after expansion.
- [ ] No unresolved template placeholder leaks to final user output.
- [ ] Dynamic placeholder data is safely escaped/typed.
- [ ] Telegram custom emoji capture -> storage -> render round-trip tested.
- [ ] UTF-16 entity offsets tested with Persian + emoji + placeholder expansion.
- [ ] There is no separate Premium Emoji manager.
- [ ] Asset caption emoji is editable asset metadata.

## Button / Telegram UI gates

- [ ] Designated buttons can be customized for label/style/custom-emoji icon as allowed.
- [ ] Enable/disable and row/order changes are available only for menus/buttons explicitly declared configurable.
- [ ] Admin cannot replace source-defined safe button action semantics with arbitrary callback text/code.
- [ ] Exposed styles are exactly default/primary/success/danger.
- [ ] callback_data <=64 UTF-8 bytes enforced before button creation.
- [ ] Callback action registry can diagnose orphaned/unregistered actions.
- [ ] Long current values are shown safely and button preview truncation is grapheme-safe.
- [ ] Large lists paginate and have practical filters/search/favorites/recent where useful.
- [ ] Admin UI defaults to Persian.
- [ ] Terminal UI is English-only.

## Diagnostics gates

- [ ] Provider diagnostics expose freshness, latency, cooldown, next allowed call, request counters and sanitized last error.
- [ ] Asset diagnostics detect mapping/alias ambiguity and malformed/unusable markets.
- [ ] Template diagnostics detect placeholder errors, field cycles, expansion/length failures and rich compile failures.
- [ ] Button diagnostics detect unsupported styles, overlong callbacks, orphaned actions and unsafe layout overrides.
- [ ] Rich/custom emoji diagnostics cover capture and UTF-16 compile health.
- [ ] Parser deterministic self-test corpus is exposed through diagnostics.
- [ ] DB/schema/background-refresh/runtime checks exist.
- [ ] Local “Run all” diagnostics performs zero network calls.
- [ ] Live provider diagnostics respect cooldown/rate policy and do not expose secrets.
- [ ] Phase 2 adds card/font/logo/renderer/history diagnostics.

## Stars gates

- [ ] Admin can create exact Stars package using Persian or Latin numeric input.
- [ ] Stored/rendered numbers normalize to ASCII output.
- [ ] Exact configured package query works.
- [ ] Non-configured quantity does not interpolate by default.
- [ ] Package mutation is audited.

## Card gates — Phase 2

- [ ] Generic unknown asset renders professionally.
- [ ] Asset-family auto style works without per-asset manual config.
- [ ] Multiple layouts/themes/chart styles exist behind compact registries.
- [ ] Incompatible combinations are blocked/fallback safely.
- [ ] 1080x1080 final card generated correctly.
- [ ] High-resolution/downsample path validated where enabled.
- [ ] Long names, large prices, tiny prices and positive/negative change covered.
- [ ] Missing logo/font/history has graceful truthful fallback.
- [ ] No fabricated historical chart points.
- [ ] History-collecting/no-history state is truthful.
- [ ] Asset override/reset inheritance works.
- [ ] Uploaded logo validation/path safety tested.
- [ ] Card implementation does not use a deep unnecessary inheritance hierarchy.
- [ ] Representative visual/golden changes reviewed intentionally.

## Security/observability gates

- [ ] Admin authorization enforced at action execution, not just menu visibility.
- [ ] Forged admin callback cannot mutate state.
- [ ] Provider keys encrypted at rest.
- [ ] Master key stored outside repo/DB with restrictive permissions.
- [ ] Secret redaction tests exist.
- [ ] Structured provider events exist.
- [ ] Durable admin audit events exist.
- [ ] Arbitrary user messages are not logged in full by default.
- [ ] Phase 2 file upload/path operations are bounded and traversal-safe.

## Installer/operations gates — Phase 2

- [ ] One-line README installer matches real `install.sh`.
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

- [ ] Relevant focused tests ran after internal checkpoints.
- [ ] Full test suite ran at major phase completion.
- [ ] Exact pass/fail/skip counts reported.
- [ ] Compile/import smoke checks ran.
- [ ] Live provider checks, if not run, are explicitly reported as not run.
- [ ] Live Telegram validation, if not run, is explicitly reported as not run.
- [ ] No unexecuted test is described as passed.
- [ ] Docs match actual implementation.

## Completion statement

- Phase 1 is complete only when its Phase 1 gates are satisfied and reviewed.
- Phase 2 is complete only when all applicable final gates are satisfied.
- After Phase 2, the currently defined RateDeck product scope is complete. Future unrelated features are not an automatic Phase 3.

A release may be called production-ready only after every applicable gate is satisfied or a clearly documented exception is explicitly accepted by the owner.