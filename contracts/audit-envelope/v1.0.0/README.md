# audit-envelope v1.0.0

Hash-chained audit record envelope written by interlock's `AuditChain.append()`. Every audit record persisted by interlock or any layer calling into interlock matches this schema. Consumers (`audit-verify`, external auditors, GDPR rotation/purge tooling) read records by this schema.

## Fields

| Field | Type | Nullable | Description |
|---|---|---|---|
| `seq` | integer (≥ 0) | no | Monotonic chain sequence; `chain_genesis` is `seq=0`. |
| `prev_hash` | hex SHA-256 (64 chars) | no | Lowercase hex digest of the previous record's `record_hash`. See [Chain genesis](#chain-genesis). |
| `record_hash` | hex SHA-256 (64 chars) | no | Lowercase hex digest of this record's canonical serialization. See [Canonical serialization](#canonical-serialization). |
| `wall_time` | float (epoch seconds, UTC) | no | Wall-clock at `append()` time. Not monotonic across reboots; correlate with `monotonic_ns` per-process. |
| `monotonic_ns` | integer (≥ 0) | no | Python `time.monotonic_ns()` at `append()` time. Only ordered within a single process lifetime. |
| `event` | string (non-empty) | no | Event name. Namespace governed by `governance/audit-event-ownership.md`. |
| `emitter` | enum (`interlock` / `sieve` / `arbiter` / `airlock`) | no | Layer that called `AuditChain.append()`. Required so `audit-verify` can check cross-layer ownership. |
| `labels` | object | no | Event-specific payload. Open object: per-event shape lives alongside the event entry in governance. |
| `categories` | array of string | yes | Sieve classifier categories for verdict-carrying events; null otherwise. |
| `confidence` | float in [0, 1] | yes | Sieve classifier confidence for verdict-carrying events; null otherwise. |
| `pattern_hash` | hex SHA-256 | yes | `pattern_table` HashInput digest active at emission; null when not applicable. |
| `model_digest` | string | yes | `model_digest` HashInput value active at emission; null when not applicable. Format is whatever the Ollama manifest endpoint returns. |
| `prompt_hash` | hex SHA-256 | yes | `prompt_template` HashInput digest active at emission; null when not applicable. |

## Schema exhaustiveness

The schema is **exhaustive** (`additionalProperties: false` at the envelope level). Any field a consumer needs to act on must be named here. Per-event detail rides inside `labels`, which is itself an open object — its per-event shape is documented in governance, not schema-enforced.

## Hash algorithm

v1.0.0 pins **SHA-256, lowercase hex** for `prev_hash`, `record_hash`, `pattern_hash`, and `prompt_hash`. Rationale: Python stdlib, broadly available cross-language, output size adequate for chain integrity. v2 could revisit (BLAKE2b for speed) but v1 stays SHA-256 for cross-tool compatibility.

`model_digest` is **not** SHA-256 — it carries the raw bytes returned by Ollama's manifest endpoint, formatted as whatever string Ollama uses (typically `sha256:<hex>` or similar). The schema does not constrain it because the format belongs to Ollama, not interlock. See `integrity-inputs/v1.0.0/README.md` for the serialization spec.

## Canonical serialization

`record_hash` is computed over the canonical JSON serialization of all envelope fields **except** `record_hash` itself. Rules:

1. Serialize the envelope as a JSON object excluding the `record_hash` key.
2. Sort object keys lexicographically (including inside nested `labels`).
3. Use UTF-8 encoding, no insignificant whitespace, no trailing newline.
4. Encode the resulting bytes through SHA-256; format as lowercase hex.

This matches `integrity-inputs/v1.0.0`'s `pattern_table` serialization convention (sorted-keys JSON, UTF-8) so the chain hash and the HashInput digests use the same canonicalization discipline.

## Chain genesis

The first record on a fresh chain has:

- `seq = 0`
- `event = "chain_genesis"`
- `prev_hash = "0000000000000000000000000000000000000000000000000000000000000000"` (64 zero hex characters)
- `emitter = "interlock"`

Subsequent re-anchor events (`chain_anchor_after_rotate`, `chain_anchor_after_purge`, `chain_anchor_after_repair`) reset `prev_hash` to the same all-zero value and bump `seq` from the prior record. `audit-verify` recognises the all-zero sentinel as the genesis / re-anchor signal.

## Event namespace

Event names are **governed**, not enum-locked in this schema. The canonical list lives in `governance/audit-event-ownership.md`. Adding an event is a governance change (and a contracts-repo tag bump per the two-namespace rule in `contracts/README.md`), not a schema bump. Removing or renaming an event still requires a v2 major bump because consumers query on `event` values.

Two-tier ownership model (from governance):

- **Layer-exclusive events** — only `emitter="interlock"` is valid (e.g., `heartbeat`, `chain_genesis`, `freeze_set`).
- **Cross-layer events** — interlock defines the envelope but a named layer emits (e.g., `gate_frozen` with `emitter="sieve"`; `ollama_socket_untrusted` with `emitter="sieve"`).

`audit-verify` enforces the mapping. Mismatched `emitter` is a contract violation.

> **Known gap (2026-06-30):** `governance/audit-event-ownership.md` and `migration/layer0_interlock.md § Audit events owned` list non-overlapping v1 event sets. Reconciliation is a separate governance PR; this schema sidesteps it by not enum-locking `event`.

## Example: egress_decision

```json
{
  "seq": 42,
  "prev_hash": "8b1a9953c4611296a827abf8c47804d7bb2c4b3a5e6f1234567890abcdef1234",
  "record_hash": "9c2bff64d5722307b938b0c81b5ee6f8c45d6e3f8a1b2c3d4e5f6789012345ab",
  "wall_time": 1751301600.123,
  "monotonic_ns": 458291837465,
  "event": "egress_decision",
  "emitter": "interlock",
  "labels": {
    "domain": "registry.example.com",
    "action": "deny",
    "client": "172.18.0.4",
    "http_status": 403
  },
  "categories": null,
  "confidence": null,
  "pattern_hash": null,
  "model_digest": null,
  "prompt_hash": null
}
```

## Versioning

- Adding a top-level field → **v1.1 minor bump**
- Adding a value to the `emitter` enum (new layer) → **v1.1 minor bump**
- Tightening a constraint (narrower `pattern`, lower max, etc.) → **v1.1 minor bump** (consumers fail closed, producers must update)
- Loosening a constraint → **v1.1 minor bump**
- Removing or retyping a field, removing an `emitter` value, renaming → **v2 major bump** (breaking; affects all consumers and the audit-verify tool)

See `contracts/README.md` for repo-tag vs inner-schema-version semantics.

## Consumers

- interlock `AuditChain.append()` (producer) and `audit-verify` CLI (consumer) — in-process, no submodule pin
- tidereach/sieve — pins via `interlock-contracts` git submodule; produces cross-layer events (`gate_frozen`, `gate_frozen_auto`, `ollama_*`)
- tidereach/arbiter — pins via `interlock-contracts` git submodule; produces `verdict_issued`
- tidereach/airlock — pins via `interlock-contracts` git submodule; provides Squid access log consumed by interlock's `SquidAccessReader` (no direct AuditChain calls in v1)

## Stage-2-release-blocking

Per `migration/MAIN.md § 10`, the audit envelope is the cross-plane visibility surface. Stage 3+ layers cannot ship without a pinned envelope schema — their `AuditChain.append()` call sites are written against this contract. v1.0.0 is the Stage 2 release pin.
