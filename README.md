# tidereach/interlock

L0 attestation/glue layer for the [Tidereach](https://github.com/tidereach/hull) stack.

Interlock owns:

- Supply-chain verification (`verify-integrity`, `verify-installed`)
- Runtime preflight (`check-sandbox`, `check-ollama`, `check-engine`, `hook-check`, `verify-hooks`)
- Hash-chained audit log (`audit-verify`, `audit-rotate`, `audit-purge`, `audit-repair`)
- Freeze switch + anomaly counters + heartbeat (`freeze`, `unfreeze`, `stats`)
- Cross-layer contracts (`contracts/`) and governance (`governance/`)
- L4 policy module — session-stream ingestion + deterministic rules + actions (`session-audit`, `session-watch`, `rules-lint`)

Ed25519 attestation (v2) and the Hard action primitives (`KillAgentContainerAction`, `SeverEgressAction`, `FreezeWorkspaceAction`) are v2 stubs in this release.

## Stack context

| Repo | Layer | Role |
|---|---|---|
| [tidereach/hull](https://github.com/tidereach/hull) | meta | Macro docs, hook scripts, CI templates |
| **tidereach/interlock** | L0 + L4 | Attestation/glue + policy module (this repo) |
| tidereach/sieve | L1 | Content scan / sensitivity gate |
| tidereach/arbiter | L2 | Intent policy / control engine integration |
| tidereach/airlock | L3 | Sandbox + session-stream substrate |

## CLI

```
tidereach interlock <subcommand>
```

The `tidereach` binary is the umbrella dispatcher registered by this package.
Subcommands for other layers (`tidereach sieve …`, `tidereach airlock …`) require
those packages to be installed; an `ImportError` prints an install hint.

See `migration/MAIN.md § 7 Decision 16` in hull for the dispatcher design.

## License

Apache-2.0 — see [LICENSE](LICENSE).
