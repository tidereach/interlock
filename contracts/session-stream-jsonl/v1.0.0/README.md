# session-stream-jsonl v1.0.0

JSONL record schema for the session-stream substrate written by the agent CLI into the airlock volume and consumed by interlock's policy module.

## Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `ts` | float (epoch seconds, UTC) | yes | Wall-clock timestamp at which the agent CLI emitted the record. |
| `session_id` | string | yes | Agent CLI session identifier; opaque to interlock. |
| `source` | string (`claude` \| `copilot`) | yes | Which agent CLI emitted the record; selects the per-CLI adapter. |
| `event_type` | string | yes | Normalised event type: `user`, `assistant`, `tool_call`, `tool_result`, `system`, … |
| `transcript_path` | string \| null | no | Source transcript file path when the adapter parsed an on-disk record; null for synthesised entries. |
| `assistant_text` | string \| null | no | Assistant turn text the adapter extracted; null on non-assistant records. |
| `correlation_id` | string \| null | no | Arbiter `context_id` propagated through interlock's in-process verdict map; null when no verdict precedes the record. |

## Schema exhaustiveness

The schema is **exhaustive** (`additionalProperties: false`). Any field the policy module needs to act on must be named here. Adapters keep scratch state adapter-local; it does not survive into a v1 record.

## Versioning

- Adding a field → **v1.1 minor bump**
- Removing or retyping a field → **v2 major bump** (breaking)

See the root `contracts/` README for repo-tag vs inner-schema-version semantics.

## Consumers

- interlock policy module (`src/tidereach/interlock/policy/`) — in-process, no submodule pin
- tidereach/sieve — pins via `interlock-contracts` git submodule
- tidereach/airlock — pins via `interlock-contracts` git submodule
- tidereach/arbiter — pins via `interlock-contracts` git submodule

## Stage-2-release-blocking

Per the 2026-06-29 layer-4 ember review (Pivot 3), this schema must be pinned at v1.0.0 in the Stage 2 release. Without it, Stage 3+ layer development desyncs on the policy-module surface. See `migration/MAIN.md § 12 Stage 2 gate` in hull.
