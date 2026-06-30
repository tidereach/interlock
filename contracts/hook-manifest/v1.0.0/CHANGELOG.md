# hook-manifest changelog

All notable changes to this contract are documented here. Semver bumps require a corresponding entry.

## v1.0.0 — 2026-06-30

Initial release. Stage 2 substance per `migration/MAIN.md § 11 Stage 2 gate` (contract 4 of 7).

- 5 fields total: `manifest_version` (const "1.0.0"), `integration` (enum claude/copilot), `hashes` (object: path → SHA-256 hex), `pubkey` (Ed25519 hex 64 chars or null), `created_at` (float epoch seconds UTC).
- Hash algorithm pinned: SHA-256 lowercase hex for script digests.
- Pubkey encoding pinned: Ed25519 32-byte raw public key as lowercase hex (64 chars), or null when unsigned.
- Canonical serialization: sorted-keys JSON, UTF-8, no insignificant whitespace, no trailing newline — matching `audit-envelope/v1.0.0` discipline so consumers share a canonicalization implementation.
- Scope boundary documented: this contract does NOT redefine Anthropic's `settings.json`, does NOT define matcher fixtures (live in hull `integrations/<cli>/fixtures/`), does NOT carry integrity modes (live in `interlockSettings.hook_integrity_mode`), does NOT carry per-call signatures (emitted as `audit-envelope` `event="hook_identity"` records), and does NOT carry a manifest-level signature (v2 future bump).

Known follow-ups (do not block release):

- `integrity-inputs/v1.1.0` to graduate `hook_manifest_digest` from TBD to pinned with the canonical serialization spec cross-referenced. Batched with other TBD graduations (`sandbox_config_hash`, `ruleset_hash`, `engine_ipc_version`) as their owning contracts land.
- hull `integrations/<cli>/` reference impls — the manifest-generator side. Deferred per PR #156 from Stage 1 gating; not blocking this contract.
- v2 manifest-level Ed25519 signature (`signature` + `signed_at` fields) per `migration/layer0_interlock.md § v2 spec`. Lands as a v1.x minor bump.
