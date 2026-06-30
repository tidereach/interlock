# contracts/ — agent notes

Cross-repo schemas and their consumer contracts. Each contract lives in its own subdirectory with three files: `schema.json`, `README.md`, `CHANGELOG.md`. See `README.md` in this directory for the namespace + pinning explanation.

## Per-PR file discipline (the parallel-PR rule)

**A PR authoring or amending one contract MUST only touch files inside that contract's own subdirectory.** Do not edit `contracts/README.md`, do not edit other contracts' files, do not edit aggregate status anywhere.

Why: parallel PRs that touch shared aggregate files (a per-contract status table, a registry list, a tracker doc) conflict at merge time because git's line-based merge cannot tell adjacent independent rows apart. The conflict isn't semantic — both PRs are correct — but the resolution is manual. Single-PR-at-a-time serializes the work; stacking PRs propagates rebase pain. The durable fix is to keep per-PR work in per-PR directories.

What this means in practice:

| Want to | Do |
|---|---|
| Author a new contract | Create `contracts/<name>/v1.0.0/{schema.json, README.md, CHANGELOG.md}` in your PR. Touch nothing else under `contracts/`. |
| Bump an existing contract | Create `contracts/<name>/v<new-version>/`. Update only that contract's `CHANGELOG.md`. |
| Add cross-contract status / overview content | Update `STATE.md` in `tidereach/hull` (the aggregate cross-repo progress home), not files in this repo. |
| Add a new contract to the Stage 2 release set | This IS a multi-contract change — touch `contracts/README.md`'s Stage 2 list once, document why, accept that this PR will not parallelize with other contract PRs. |

## Why `contracts/README.md` carries no per-contract status

Removed 2026-06-30 after PR #4 hit the conflict for the third time in one session. The status had three duplicate homes (per-contract CHANGELOG, hull STATE.md, and this file's table); compressing to two (CHANGELOG + STATE.md) eliminates the conflict surface without losing information.

A new contract added to the Stage 2 set still requires editing the fixed list in `contracts/README.md`, but that's a once-per-release event, not a per-PR event.

## Canonical serialization (cross-contract convention)

All v1 contracts share one canonicalization discipline so consumers can use a single implementation across `audit-envelope`, `hook-manifest`, and `sandbox-config`:

- Sorted-keys JSON at every nesting level
- UTF-8 encoding
- No insignificant whitespace
- No trailing newline
- SHA-256 lowercase hex for all hash outputs (script digests, content digests, combined hashes, integrity-input bytes)

When you author a new contract that needs canonical bytes (for an integrity-input or for a chain-hash), match these rules. The README of each contract restates the discipline explicitly to keep the contract self-contained.

## Cross-contract dependencies

- `integrity-inputs/v1.0.0` lists four TBD entries whose graduation conditions are met by other contracts. Graduating an entry from TBD → pinned is a minor bump on `integrity-inputs` (creates `integrity-inputs/v1.x.0/`); batch graduations rather than bumping per contract.
- `audit-envelope/v1.0.0` `event` field is governed by `governance/audit-event-ownership.md` (open string in the schema; semantically-locked by governance). New audit events go through governance, not through schema bumps.
