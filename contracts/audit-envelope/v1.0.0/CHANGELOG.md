# audit-envelope changelog

All notable changes to this contract are documented here. Semver bumps require a corresponding entry.

## v1.0.0 — 2026-06-30

Initial release. Stage 2 pre-parallel contract per `migration/MAIN.md § 10`.

- 13 fields total: 8 required non-nullable, 5 required nullable (classifier-related top-level fields).
- Hash algorithm pinned: SHA-256 lowercase hex.
- Canonical serialization: sorted-keys JSON, UTF-8, no insignificant whitespace; `record_hash` computed over the envelope minus the `record_hash` key.
- `emitter` enum: `interlock`, `sieve`, `arbiter`, `airlock`. Required for cross-layer ownership verification (`audit-verify` enforces).
- `event` is an open string; the canonical namespace lives in `governance/audit-event-ownership.md`.
- Chain-genesis convention: `seq=0`, `event="chain_genesis"`, `prev_hash` = 64 zero hex characters. Re-anchor events (`chain_anchor_after_{rotate,purge,repair}`) reuse the same all-zero `prev_hash` sentinel.

Known follow-ups (do not block release):

- Reconciliation of the v1 event list between `governance/audit-event-ownership.md` and `migration/layer0_interlock.md § Audit events owned` — separate governance PR.
- `model_digest` format is left unconstrained (Ollama-defined). If a non-Ollama model source appears, revisit in a minor bump.
