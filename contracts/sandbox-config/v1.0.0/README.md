# sandbox-config v1.0.0

Static integrity record for an execution-plane sandbox's configuration. Published by airlock's release pipeline alongside the sandbox image; consumed by interlock's `check-sandbox` subcommand and the `SandboxCheck(backend, config_paths, config_hash)` class. The manifest's `combined_hash` is the integrity-input source for `integrity-inputs/v1.0.0`'s currently-TBD `sandbox_config_hash` entry.

## Fields

| Field | Type | Nullable | Description |
|---|---|---|---|
| `manifest_version` | const `"1.0.0"` | no | Locked to schema directory version. |
| `backend` | string (open) | no | Sandbox backend identifier (e.g., `podman-compose`). Open string per interlock's removal of the closed Literal. |
| `files` | object (path → hex SHA-256), min 1 entry | no | Per-file content digests. |
| `combined_hash` | hex SHA-256 (64 chars) | no | SHA-256 of the canonical-bytes serialization of `files`. This is what operators pin in `interlockSettings.sandbox_config_hash`. |
| `created_at` | float (epoch seconds UTC) | no | When the manifest was published. Audit-correlation only; does NOT contribute to `combined_hash`. |

## Schema exhaustiveness

The schema is **exhaustive** (`additionalProperties: false` at the top level). All five fields are required and non-nullable. `files` has `minProperties: 1` — a sandbox with zero config files is meaningless; an empty manifest is a generation bug.

## Hash algorithm

All digests in this contract use **SHA-256, lowercase hex (64 chars)**:

- **Per-file digests** in `files` values: SHA-256 over the file's raw bytes. No NFC normalization, no whitespace stripping — the byte sequence on disk is the input.
- **Combined hash** (`combined_hash`): SHA-256 over the canonical-bytes serialization of the `files` object (see [Canonical serialization](#canonical-serialization)).

Matches `audit-envelope/v1.0.0` and `hook-manifest/v1.0.0` so consumers share one canonicalization + hashing implementation.

## Canonical serialization

`combined_hash` is computed from the canonical bytes of the `files` object alone (NOT the whole manifest):

1. Serialize `files` as a JSON object.
2. Sort object keys lexicographically.
3. Use UTF-8 encoding, no insignificant whitespace, no trailing newline.
4. Hash through SHA-256; format as lowercase hex.

Why scope the hash to `files` only:

- **Stability**: `manifest_version`, `backend`, and `created_at` can change without rotating `sandbox_config_hash` (the value operators pin). Stability is desirable when the underlying file set is unchanged but the manifest is regenerated.
- **Integrity-input alignment**: `integrity-inputs/v1.0.0`'s `sandbox_config_hash` entry is conceptually "the hash of the sandbox config files," not "the hash of the manifest object." Scoping `combined_hash` to `files` keeps these two consistent.

`backend` and `created_at` are still recorded in the manifest for forensics — they are just not part of the load-bearing identity.

> **Note on file-on-disk vs canonical form for `files`.** Operators MAY pretty-print the manifest file on disk for readability. Verifiers re-canonicalize the `files` map before hashing, so on-disk formatting does not affect `combined_hash`.

## The v1 file set

Per `tidereach/hull/migration/layer3_airlock.md § 187`, airlock's v1 sandbox publishes these five files' hashes as the `check-sandbox` input. v1 manifests SHOULD include exactly these keys (under airlock's path convention; paths are relative to airlock's `infra/sandbox/` root):

| Path (airlock-relative) | Source / role |
|---|---|
| `Containerfile` | Multi-stage hardened image build (layer3 § 131) |
| `docker-compose.yml` | Two-service compose: proxy + agent (layer3 § 132-137) |
| `proxy/allowed-domains.txt` | Squid egress allowlist (layer3 § 108) |
| `landlock/agent.policy` | Per-path FS isolation declarative policy (layer3 § 110) |
| `seccomp-agent.json` | Seccomp profile (#138 deliverable; layer3 § 112) |

This list is the **v1 reference set**; it is documented in this README rather than schema-locked so future backends (gVisor / Landlock-only / containerd-shim / …) can publish different file sets without bumping the schema. The `files` map is open by `additionalProperties`; the airlock side decides which paths it lists.

Per `integrity-inputs/v1.0.0/README.md`'s TBD note ("Airlock Stage 4 spec locks the set of files hashed"), the v1 set above satisfies the graduation condition for `integrity-inputs`'s `sandbox_config_hash` entry. The graduation itself (TBD → pinned) is a minor bump on `integrity-inputs`, deferred to a batch update; this contract pins the canonical-bytes serialization that the graduated entry will reference.

## Backend convention

`backend` is an open string (not enum). Per `tidereach/hull/migration/layer0_interlock.md § 220`, interlock's `interlockSettings.sandbox_backend` removed its closed Literal "so new backends don't require an interlock release." The same posture flows into this contract.

The v1 expected backend identifier (the airlock-published value) is documented in airlock's release notes, not pinned here. Naming convention is short kebab-case. Multiple backends MAY publish manifests with the same `backend` value at different `created_at` timestamps (e.g., on each release); operators pick which to pin.

## Runtime check flow

1. Airlock's release pipeline generates the manifest at image build time, populating `files` with one entry per config file in the v1 set, computing each SHA-256, computing `combined_hash`, stamping `created_at` and `backend`.
2. Operator copies the manifest into their interlock state directory (or operator pre-pins `interlockSettings.sandbox_config_hash` to `combined_hash`).
3. interlock's `SandboxCheck.run()` walks `interlockSettings.sandbox_config_paths` (derived from `sandbox_backend`), reads each file's bytes, computes the canonical-bytes form of the resulting `files`-like map, hashes through SHA-256.
4. Result is compared against the operator-pinned `interlockSettings.sandbox_config_hash`:
   - **Pinned mode** (`sandbox_config_hash` non-null): mismatch is a `check-sandbox` failure.
   - **Detect-only mode** (`sandbox_config_hash` is null per `layer0_interlock.md § 222`): the computed hash is reported but not enforced.

## What this contract does NOT define

- **Per-file content schema**: the manifest hashes raw bytes; whether `Containerfile` is a valid Containerfile, or `seccomp-agent.json` is valid seccomp JSON, is airlock's concern (and asserted by airlock's CI), not this contract's.
- **Sandbox rotation policy**: how often the manifest is regenerated, when an operator should re-pin, what triggers a rotation. Rotation lives in airlock's release notes and `interlock/docs/SANDBOX_ALTERNATIVES.md` (when authored, per `layer0_interlock.md` Doc audit row).
- **Backend interoperability**: a `gVisor` manifest and a `podman-compose` manifest are not interchangeable; operators set `sandbox_backend` once per deployment.
- **Modes** (`off` / `detect-only` / `enforce`): live in `interlockSettings.sandbox_config_hash` being null / non-null, not in the manifest.
- **Settings.example.json shape**: the operator pins via interlock's TOML / env, not via a sandbox-side config file. Settings live in `layer0_interlock.md § Settings`.

## Versioning

- Adding a top-level field → **v1.1 minor bump**
- Tightening or loosening any constraint → **v1.1 minor bump**
- Removing or retyping a field, removing a required-set member, renaming → **v2 major bump** (breaking; affects `check-sandbox`, `integrity-inputs.sandbox_config_hash`, every consumer that pinned v1)
- Changing the `combined_hash` algorithm (e.g., to BLAKE2b, or to cover the whole manifest instead of just `files`) → **v2 major bump** (every existing pinned `sandbox_config_hash` value becomes invalid)

See `contracts/README.md` for repo-tag vs inner-schema-version semantics.

## Cross-contract

- **`integrity-inputs/v1.0.0`**: lists `sandbox_config_hash` as TBD with the graduation condition "Airlock Stage 4 spec locks the set of files hashed." Layer3 § 187 locks the set; this contract pins the canonical-bytes serialization. Graduation (TBD → pinned in integrity-inputs) is a separate minor bump on that contract; batched with the other TBD entries.
- **`audit-envelope/v1.0.0`**: `check-sandbox` emits success/failure via the audit envelope. The envelope's `event` is `check_sandbox_passed` or `check_sandbox_failed` (governance-namespaced; not yet enumerated in `governance/audit-event-ownership.md` v1 — see the event-list reconciliation gap flagged in `audit-envelope` README).

## Consumers

- interlock `SandboxCheck.run()` and the `check-sandbox` CLI subcommand — in-process, no submodule pin
- tidereach/airlock — generates the manifest at release time; pins via `interlock-contracts` git submodule
- tidereach/sieve / arbiter — do NOT consume sandbox-config directly. Their interaction with sandbox integrity is via interlock's `check-sandbox` result surfaced through the audit envelope.

## Stage-2-release-blocking

Per `migration/MAIN.md § 11 Stage 2 gate`: `contracts/{audit-envelope,session-stream-jsonl,hook-manifest,sandbox-config,freeze-file,engine-ipc,integrity-inputs}` must be present with semver `1.0.0` tags. This is contract 5 of 7 in that gate enumeration (after `integrity-inputs`, `session-stream-jsonl`, `audit-envelope`, and `hook-manifest`).
