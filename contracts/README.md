# contracts/

Cross-repo contracts for the Tidereach stack. All consumer repos (sieve, arbiter, airlock, hull) pin this repo as a git submodule at a SHA.

## Two independent version namespaces

Do not conflate these:

1. **Repo tag** (`v0.1.0`, `v1.0.0`, …) — identifies the contracts package as a whole. Bumps whenever any contract or governance file changes.

2. **Inner schema version** (`contracts/<name>/vX.Y.Z/`) — identifies one schema's compat surface. Bumps only when that schema breaks compat.

Example: `interlock-contracts@v0.4.0` might contain `session-stream-jsonl/v1.0.0` + `audit-envelope/v1.2.0` + `integrity-inputs/v0.3.0`.

## Contracts in this repo

Each contract lives under `contracts/<name>/v<X.Y.Z>/`. The presence of a version directory means the contract has been authored at that version; for per-contract status detail, read the contract's `CHANGELOG.md`. For the aggregate cross-repo progress overview, see `STATE.md` in `tidereach/hull`.

The Stage 2 release-blocking set per `migration/MAIN.md § 11 Stage 2 gate` (in `tidereach/hull`):

- `integrity-inputs/`
- `session-stream-jsonl/`
- `audit-envelope/`
- `hook-manifest/`
- `sandbox-config/`
- `freeze-file/`
- `engine-ipc/`

> **Why this list has no per-contract status column.** Tables with one row per contract are a parallel-PR conflict surface: every PR that ships a contract edits a row, and git's line-based merge cannot tell adjacent independent rows apart. The list above is the fixed Stage 2 set and rarely changes; per-contract status lives in each contract's own directory. See `AGENTS.md` in this directory for the per-PR-dir discipline.

## Changelog requirement

Each contract directory carries its own `CHANGELOG.md`. Semver bumps require a changelog entry citing the issue or PR.

## Consumer pinning

Consumers pin via git submodule:

```bash
git submodule add https://github.com/tidereach/interlock contracts/interlock-contracts
git submodule update --init
```

Pin to a specific tag: `git -C contracts/interlock-contracts checkout v0.1.0`. See `migration/MAIN.md § 10` in tidereach/hull for rationale.
