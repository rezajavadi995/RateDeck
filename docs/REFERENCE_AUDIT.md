# Reference Audit — Business Bot and StarzYFire

This document records design lessons from the owner's existing projects. RateDeck should reuse **principles**, not blindly copy implementation.

## Business Bot — concepts worth carrying forward

### Strict market parser

Business Bot already demonstrates useful input normalization:

- Persian/Arabic digits -> ASCII internally;
- Persian/Arabic decimal/grouping variants;
- `ي/ی`, `ك/ک`, zero-width normalization;
- compact asset/amount parsing;
- explicit tests rejecting normal sentences that merely contain asset names.

RateDeck should preserve these behaviors while replacing the finite alias/asset model with a runtime registry.

### Parser tests as a corpus

Business Bot tests include positive examples, mixed-language forms and negative natural-language examples. RateDeck should make this a larger first-class parser corpus, not a few unit examples.

### Callback normalization and 64-byte enforcement

Business Bot centralizes callback normalization and checks Telegram's callback byte limit before creating callback data. Keep the centralized concept, but RateDeck starts with one canonical versioned format and does not need legacy alias baggage on day one.

### Dedupe/idempotency awareness

Business Bot contains callback/panel dedupe protections. RateDeck should preserve the principle for admin actions that could be double-clicked, while avoiding overly punitive user bans for harmless repeated taps.

### Market/card separation

Business Bot has a distinct market-card renderer and a market engine. Preserve the separation, but make the RateDeck card subsystem substantially more capable and the market engine more modular.

### Installer/control-menu ergonomics

Business Bot proves that a single global management command is convenient. RateDeck keeps the idea but uses a safer update strategy and an English-only terminal UI.

## Business Bot — patterns not to carry forward

### Finite hard-coded asset universe

Business Bot's core market engine defines fixed aliases/crypto IDs/supported assets. That becomes a maintenance bottleneck once the provider exposes hundreds of markets.

RateDeck uses dynamic provider discovery + runtime asset registry + admin alias overlays.

### Shared/global cache age

A global cache timestamp can accidentally make stale data from one provider look fresh when another provider refreshes successfully. RateDeck requires provider-specific success/failure/freshness timestamps and validates edge freshness during conversion.

### Synchronous HTTP in market code

Business Bot's market module uses synchronous `requests`. RateDeck is async-first and provider HTTP must not block the Telegram event loop.

### Large orchestration surface

A large root `bot.py` is difficult to reason about when parser, admin, callbacks, settings and delivery all evolve. RateDeck uses small routers/use-cases and one composition root.

### Unsafe updater pattern

A normal update flow must not blindly run `git reset --hard origin/main` plus `git clean -fd`. Operator configuration/assets/data must be protected and a dirty code tree must cause a safe stop or explicit recovery path.

## StarzYFire — concepts worth carrying forward

### Explicit router ordering

StarzYFire's dispatcher registration demonstrates that order is behavior. Some classifiers/routers must run before generic callbacks/handlers. RateDeck makes this smaller, explicit and regression-tested from the beginning.

### Central content/template contracts

StarzYFire has central text-template definitions and allowed placeholder sets. This is one of the strongest ideas to keep.

RateDeck improves it with:

- per-template scope;
- allowed + required placeholders;
- field fragments;
- sample preview data;
- rich-text AST/entity preservation;
- save-time validation;
- no handler-level string formatting contracts.

### Central button registry/builder

StarzYFire models button text/callback/style/custom emoji centrally. RateDeck keeps this pattern but exposes only actual Telegram styles and uses a typed callback codec.

### Central premium/custom emoji rendering

StarzYFire has a central HTML custom-emoji preservation helper. RateDeck keeps the centralization requirement but uses entity-aware capture/compilation so placeholder expansion cannot corrupt offsets.

### Market-rate hardening principles

Useful principles from StarzYFire include:

- validate rates before they enter pricing paths;
- explicit provider provenance;
- short retry cooldown after provider failure;
- fail closed at a financial boundary when required data is unusable;
- serialize/coalesce refresh leadership;
- do not silently fall back from an authoritative provider when the product contract forbids it;
- preserve previous good data as previous data, not as a fake fresh success.

RateDeck is not an invoice/payment system, so it can display clearly marked stale last-known-good data where product policy allows. It must still never lie about freshness/source.

### Audit/operator diagnostics

StarzYFire's operator tooling, audit concepts and health summaries are worth preserving in a much smaller form.

## StarzYFire — patterns not to carry forward

### Runtime monkey patches

Some StarzYFire compatibility/hardening layers install wrappers by importing a module and replacing its functions at runtime. This creates hidden call graphs and import-order coupling.

RateDeck forbids this absolutely. The equivalent behavior must be explicit through composition, middleware, strategy or a service boundary.

### Compatibility-first architecture

StarzYFire has accumulated legacy callbacks, compatibility guards and layered runtime behavior because it is an evolved production product. RateDeck is greenfield and should not manufacture compatibility debt before it exists.

### Infrastructure beyond actual need

StarzYFire legitimately uses Redis/PostgreSQL/advisory locks/multiple services for financial workflows. RateDeck starts as a lightweight read-only market product. Do not copy heavy infrastructure unless actual deployment requirements later demand it.

### Narrow hard-coded rate symbols

StarzYFire's central pricing flow is intentionally focused on TON/TRX/USDT for its products. RateDeck's purpose is the opposite: broad dynamic market coverage. Do not reuse a three-symbol market model.

### Synthetic or patch-state-sensitive tests

Tests that depend on process-global monkey-patch state or only prove a wrapper was installed are not suitable for RateDeck. Prefer tests against explicit service boundaries and the real dispatcher composition.

## Net architecture decision

RateDeck should feel operationally familiar to the owner's existing projects while being structurally cleaner:

```text
Business Bot parser/callback ergonomics
+
StarzYFire template/button/hardening discipline
+
new dynamic asset registry
+
new conversion graph
+
new provider-specific budget/freshness model
+
new rich-text entity model
+
new card design system
-
monkey patches
-
legacy compatibility debt
-
mega routers/files
-
unnecessary infrastructure
```
