# hook-manifest v1.0.0

Static integrity record for installed Tidereach hook scripts. Generated once by hull's `integrations/<cli>/` install tooling at hook install time; consumed by interlock's `verify-hooks` (re-hash the live scripts and compare to the recorded digests) and indirectly by `hook-check` (which reads the agent CLI's settings.json + cross-references against the manifest's `integration` field). The manifest's canonical bytes are also the input that `integrity-inputs/v1.0.0`'s currently-TBD `hook_manifest_digest` entry will pin once that schema graduates (see [Cross-contract](#cross-contract) below).

## Fields

| Field | Type | Nullable | Description |
|---|---|---|---|
| `manifest_version` | const `"1.0.0"` | no | Locked to the schema directory version; consumers refuse mismatched values. |
| `integration` | enum (`claude` / `copilot`) | no | Selects the per-integration adapter in hull `integrations/<cli>/`. Adding a new integration (e.g., `cursor`) is a v1.x minor bump. |
| `hashes` | object (path → hex SHA-256) | no | Map of hook-script path (relative to the project root that registered the hook) to lowercase-hex SHA-256 digest of the file's bytes. |
| `pubkey` | hex Ed25519 (64 chars) | yes | Ed25519 public key for verifying `hook_identity` audit-envelope events. Null when no key is configured. |
| `created_at` | float (epoch seconds UTC) | no | When the manifest was generated. Audit-correlation only; not a trust anchor. |

## Schema exhaustiveness

The schema is **exhaustive** (`additionalProperties: false` at the top level). All five fields are required; only `pubkey` is nullable. The `hashes` map itself uses `additionalProperties` to constrain values to lowercase hex SHA-256 strings; the keys (paths) are open by necessity.

## Hash algorithm

Script digests in `hashes` and the `pubkey` field both use SHA-256-compatible hex byte sizes:

- **Script content digests** (`hashes` values): **SHA-256, lowercase hex (64 chars)**. Matches `audit-envelope/v1.0.0` and `integrity-inputs/v1.0.0`'s pattern-table convention.
- **Ed25519 public key** (`pubkey`): raw 32-byte public key encoded as **lowercase hex (64 chars)**. The shared 64-char surface is coincidence — pubkeys are not hashes — but hex is chosen for consistency with the rest of the contract set.

Future v2 (per `migration/layer0_interlock.md § v2 spec`) adds an Ed25519 signature OVER the manifest itself; that signature would also be hex-encoded for the same reason. v1 does not pin that field — see [Versioning](#versioning).

## Canonical serialization

The manifest's bytes-on-disk form (the input to `integrity-inputs`' `hook_manifest_digest` integrity input) is computed under the same canonicalization rules as `audit-envelope/v1.0.0`:

1. Serialize the manifest as a JSON object including all five fields.
2. Sort object keys lexicographically at every nesting level (including inside `hashes`).
3. Use UTF-8 encoding, no insignificant whitespace, no trailing newline.

`integrity-inputs/v1.0.0`'s `pattern_table` entry pins the same discipline; consumers that compute both digests use one canonicalization implementation.

> **Note on file-on-disk vs canonical form.** Operators MAY pretty-print the manifest file on disk for readability. interlock re-serializes through the canonical form before hashing, so on-disk formatting does not affect the digest. The on-disk file remains valid against this schema regardless of formatting.

## Pubkey use

The Ed25519 signing flow lives at runtime, not in this manifest:

1. At hook install time, hull's installer generates an Ed25519 keypair (or reuses the operator's existing keyring entry). The **public** key is recorded in this manifest's `pubkey` field; the **private** key stays in the operator's OS keyring per `migration/MAIN.md § 7 Decision 13` (operator-only signing, CI never holds the key).
2. When a hook fires at agent-CLI runtime, the hook script signs a per-call payload with the private key and includes the signature in the audit record it sends to interlock.
3. interlock emits the audit record as an `audit-envelope/v1.0.0` envelope with `event="hook_identity"` and the signature in `labels`. The pubkey for verification is recovered from THIS manifest, joined on `integration`.
4. `verify-hooks` re-hashes the installed hook scripts against `hashes` and additionally walks the audit log verifying each `hook_identity` envelope's signature against `pubkey`.

When `pubkey` is null, step 4's signature check is skipped; only the script-hash integrity check runs. This is the v1 supported posture under `interlockSettings.hook_integrity_mode = "warn"`.

## What this contract does NOT define

- **`~/.claude/settings.json` (and the project `.claude/settings.json`)**: owned by Anthropic; this contract reads the format but does not redefine it. interlock's `hook-check` parses settings.json directly via Anthropic's documented shape (see `tidereach/hull` `integrations/claude/` reference impl when authored) and asserts the matcher set / tool-name set against per-integration fixtures.
- **Matcher fixtures**: per-integration fixture files live in `tidereach/hull/integrations/<cli>/fixtures/` (when authored; PR #156 deferred this from Stage-1-gating). The fixture format is documented there, not schema-locked here — fixtures evolve on the integration's cadence, not the manifest's.
- **Modes** (`off` / `warn` / `block`): live in `interlockSettings.hook_integrity_mode` per `layer0_interlock.md § Settings`. The manifest is consumed under whatever mode is active; the manifest itself does not carry mode state.
- **Per-call Ed25519 signatures**: emitted to the audit chain as `event="hook_identity"` envelope records (`audit-envelope/v1.0.0`). The manifest carries only the verification pubkey.
- **Manifest signing (v2)**: a future v2 will sign the manifest itself (Ed25519 signature over the canonical bytes). v1 does not pin a `signature` or `signed_at` field; v2 will land as a v1.x minor bump.

## Versioning

- Adding a top-level field (e.g., v2's `signature` + `signed_at`) → **v1.1 minor bump**
- Adding an `integration` enum value (e.g., `cursor`) → **v1.1 minor bump**
- Tightening or loosening any constraint (narrower `pattern`, stricter required set) → **v1.1 minor bump**
- Removing or retyping a field, removing an `integration` value, renaming → **v2 major bump** (breaking; affects `verify-hooks`, `integrity-inputs.hook_manifest_digest`, and every consumer that pinned v1)

See `contracts/README.md` for repo-tag vs inner-schema-version semantics.

## Cross-contract

- **`integrity-inputs/v1.0.0`**: lists `hook_manifest_digest` as TBD with the graduation condition "interlock Stage 2 ships the hook integration manifest format and its canonical serialization." This contract satisfies the condition. The graduation itself (TBD → pinned) is a minor bump on `integrity-inputs` (separate PR; batched with other graduations as their owning contracts land).
- **`audit-envelope/v1.0.0`**: the `hook_identity` event consumes the `pubkey` recorded here. Cross-layer correlation is by `integration` + script path.

## Consumers

- interlock `HookManifest.verify()` and the `verify-hooks` / `hook-check` CLI subcommands (per `layer0_interlock.md § Public API` + `§ CLI`) — in-process, no submodule pin
- hull (meta) `integrations/<cli>/` reference impls — generate the manifest at install time. Reference impls are deferred per PR #156 ("hook-script bullet removed from § 11 Stage 1 prose; § 3 meta-repo deliverable, not Stage-1-gating"); contract ships ahead of them.
- tidereach/sieve / arbiter / airlock — do NOT consume hook-manifest directly. Their interaction with hooks is via interlock's audit-envelope `hook_identity` events.

## Stage-2-release-blocking

Per `migration/MAIN.md § 11 Stage 2 gate`: `contracts/{audit-envelope,session-stream-jsonl,hook-manifest,sandbox-config,freeze-file,engine-ipc,integrity-inputs}` must be present with semver `1.0.0` tags. This is contract 4 of 7 in that gate enumeration.
