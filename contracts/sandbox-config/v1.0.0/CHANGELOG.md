# sandbox-config changelog

All notable changes to this contract are documented here. Semver bumps require a corresponding entry.

## v1.0.0 — 2026-06-30

Initial release. Stage 2 substance per `migration/MAIN.md § 11 Stage 2 gate` (contract 5 of 7).

- 5 fields total: `manifest_version` (const "1.0.0"), `backend` (open string), `files` (object: path → SHA-256 hex, min 1 entry), `combined_hash` (SHA-256 hex 64 chars), `created_at` (float epoch seconds UTC).
- Hash algorithm pinned: SHA-256 lowercase hex for both per-file digests and `combined_hash`.
- `combined_hash` is computed from the canonical-bytes serialization of the `files` object ALONE — `manifest_version`, `backend`, and `created_at` do NOT feed it. This keeps `sandbox_config_hash` (the integrity-input identity) stable across manifest metadata changes and avoids spurious rotation.
- `backend` left as open string (NOT enum), matching `interlockSettings.sandbox_backend`'s removal of the closed Literal per `layer0_interlock.md § 220` so new backends do not require an interlock release.
- Canonical serialization for `combined_hash` input: sorted-keys JSON, UTF-8, no insignificant whitespace, no trailing newline. Same discipline as `audit-envelope/v1.0.0` and `hook-manifest/v1.0.0`.
- v1 file set documented in README (`Containerfile`, `docker-compose.yml`, `proxy/allowed-domains.txt`, `landlock/agent.policy`, `seccomp-agent.json`) per `layer3_airlock.md § 187`; `files` is NOT enum-locked to this set so future backends can publish different file lists without a schema bump.

Known follow-ups (do not block release):

- `integrity-inputs/v1.1.0` to graduate `sandbox_config_hash` from TBD to pinned, citing this contract's canonical serialization. Separate PR; batch with `hook_manifest_digest` and other TBD graduations.
- `governance/audit-event-ownership.md` reconciliation to add `check_sandbox_passed` / `check_sandbox_failed` to the v1 event list (carried over from the audit-envelope event-list reconciliation gap).
- airlock-side reference implementation that GENERATES the manifest at release time. Owned by airlock Stage 4; not blocking.
