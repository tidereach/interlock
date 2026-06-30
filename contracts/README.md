# contracts/

Cross-repo contracts for the Tidereach stack. All consumer repos (sieve, arbiter, airlock, hull) pin this repo as a git submodule at a SHA.

## Two independent version namespaces

Do not conflate these:

1. **Repo tag** (`v0.1.0`, `v1.0.0`, …) — identifies the contracts package as a whole. Bumps whenever any contract or governance file changes.

2. **Inner schema version** (`contracts/<name>/vX.Y.Z/`) — identifies one schema's compat surface. Bumps only when that schema breaks compat.

Example: `interlock-contracts@v0.4.0` might contain `session-stream-jsonl/v1.0.0` + `audit-envelope/v1.2.0` + `integrity-inputs/v0.3.0`.

## Contracts in this repo

| Contract | Status | Notes |
|---|---|---|
| `integrity-inputs/v1.0.0/` | **Shipped (Stage 2 pre-parallel)** | 3 pinned + 4 TBD entries |
| `session-stream-jsonl/v1.0.0/` | **Shipped (Stage 2 pre-parallel, release-blocking)** | 7-field exhaustive schema |
| `audit-envelope/v1.0.0/` | **Shipped (Stage 2)** | 13-field hash-chained record envelope; SHA-256 lowercase hex; `emitter` enum locks cross-layer ownership |
| `hook-manifest/v1.0.0/` | **Shipped (Stage 2)** | 5-field static integrity record for installed hook scripts; SHA-256 lowercase hex; Ed25519 pubkey for `hook_identity` audit-envelope events |
| `sandbox-config/` | Pending Stage 2 implementation | |
| `freeze-file/` | Pending Stage 2 implementation | |
| `engine-ipc/` | Pending Stage 2 implementation | |

## Changelog requirement

Each contract directory carries its own `CHANGELOG.md`. Semver bumps require a changelog entry citing the issue or PR.

## Consumer pinning

Consumers pin via git submodule:

```bash
git submodule add https://github.com/tidereach/interlock contracts/interlock-contracts
git submodule update --init
```

Pin to a specific tag: `git -C contracts/interlock-contracts checkout v0.1.0`. See `migration/MAIN.md § 10` in tidereach/hull for rationale.
