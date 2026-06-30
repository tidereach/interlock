"""
tidereach interlock <subcommand> — stub CLI.

All subcommands raise NotImplementedError until Stage 2 implementation lands.
The dispatch contract (argv shape, exit codes, --help) is the stable surface;
implementations are filled in per the Stage 2 gate in migration/MAIN.md § 12.
"""

from __future__ import annotations

import sys

SUBCOMMANDS: dict[str, str] = {
    # L0 verification
    "verify-integrity": "Verify the integrity hash of interlock's own installation",
    "verify-installed": "Verify supply-chain hash pins on installed packages",
    # L0 preflight
    "check-sandbox": "Verify the airlock sandbox image + config hash",
    "check-ollama": "Verify the local Ollama model digest",
    "check-engine": "Check the control engine IPC socket (arbiter)",
    "hook-check": "Validate hook scripts against the integration manifest",
    "verify-hooks": "Verify hook signatures (Ed25519 v2 stub)",
    "install-hooks": "Install hook scripts into the agent CLI config",
    # L0 audit
    "audit-verify": "Verify hash-chain integrity of the audit log",
    "audit-rotate": "Rotate the audit log to a new segment",
    "audit-purge": "Purge audit segments older than the retention window",
    "audit-repair": "Repair a broken hash chain (re-anchors from a checkpoint)",
    # L0 lifecycle
    "self-test": "Run the interlock self-test suite",
    "freeze": "Set the FREEZE flag — blocks sieve gate calls",
    "unfreeze": "Clear the FREEZE flag",
    "stats": "Print anomaly counters, heartbeat state, and audit stats",
    # L4 policy module
    "session-audit": "Audit a session-stream JSONL transcript against the ruleset",
    "session-watch": "Tail the live session-stream volume and emit rule hits",
    "rules-lint": "Validate a YAML ruleset against the rule engine schema",
}


def main() -> None:
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        _print_help()
        return

    sub = args[0]
    if sub not in SUBCOMMANDS:
        print(f"tidereach-interlock: unknown subcommand '{sub}'", file=sys.stderr)
        print(f"Available: {', '.join(sorted(SUBCOMMANDS))}", file=sys.stderr)
        sys.exit(1)

    raise NotImplementedError(
        f"tidereach interlock {sub}: not yet implemented. "
        "Stage 2 implementation is tracked in migration/MAIN.md § 12."
    )


def _print_help() -> None:
    lines = ["tidereach interlock <subcommand>\n", "Subcommands:\n"]
    for name, desc in SUBCOMMANDS.items():
        lines.append(f"  {name:<20} {desc}")
    print("\n".join(lines))
