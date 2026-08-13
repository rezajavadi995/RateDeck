# Codex Phase 1 Request

This branch exists only to host the RateDeck Phase 1 implementation.

Codex must read `AGENTS.md`, `CODEX_PROMPT.md`, and every source-of-truth document referenced by `AGENTS.md` before editing runtime code.

Implement **Phase 1 only**, checkpoint-by-checkpoint (`1A -> 1B -> 1C -> 1D`) exactly as defined in `docs/PHASES.md`.

Important execution constraints:

- Do not implement Phase 2.
- Do not merge the PR.
- Do not deploy, restart production services, or run production migrations.
- Do not touch `/opt/star`, `starzyfire-*`, or any StarzYFire-owned resource.
- No monkey patching.
- Do not run Ruff.
- Keep the implementation modular but lean; do not create speculative infrastructure.
- GitHub Actions budget is currently exhausted and there is no self-hosted runner. Do **not** wait for GitHub Actions, do not add workflows merely to obtain CI, and do not report missing CI as an implementation failure.
- Run all feasible focused tests and the full local test suite in the Codex execution environment, plus compile/import smoke checks, and report exact pass/fail/skip counts and any environment blockers.
- Stop after Phase 1 acceptance work is complete so the owner can review the PR before Phase 2.

This task marker may be removed before finalizing the PR once Phase 1 implementation changes exist.