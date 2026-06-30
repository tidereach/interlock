# CHANGELOG — session-stream-jsonl

## v1.0.0 (2026-06-30)

Initial schema commitment. Seven fields: `ts`, `session_id`, `source`, `event_type`, `transcript_path`, `assistant_text`, `correlation_id`. No `extra`/`raw_payload` catch-all. Schema is exhaustive (`additionalProperties: false`).

Locked as Stage-2-release-blocking per Pivot 3 of the 2026-06-29 layer-4 ember review. See `migration/MAIN.md § 12 Stage 2 gate` in tidereach/hull.
