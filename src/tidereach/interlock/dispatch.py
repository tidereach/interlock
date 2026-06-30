"""
tidereach umbrella dispatcher (Decision 16).

Parses argv[1] as the layer name, imports tidereach.<layer>.cli, and
calls its main(). On ImportError prints an install hint and exits 1.

Pattern: kubectl plugin / git <subcommand> / cargo subcommands.
"""

from __future__ import annotations

import importlib
import sys


LAYERS = ("interlock", "sieve", "arbiter", "airlock")


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        _print_help()
        return

    layer = sys.argv[1]
    if layer not in LAYERS:
        print(f"tidereach: unknown layer '{layer}'. Available: {', '.join(LAYERS)}", file=sys.stderr)
        print("Run 'tidereach --help' for usage.", file=sys.stderr)
        sys.exit(1)

    try:
        mod = importlib.import_module(f"tidereach.{layer}.cli")
    except ImportError:
        print(
            f"tidereach: layer '{layer}' is not installed.\n"
            f"  Run: pip install tidereach-{layer}",
            file=sys.stderr,
        )
        sys.exit(1)

    # Shift argv so the layer CLI sees `tidereach-<layer> <subcommand> ...`
    sys.argv = [f"tidereach-{layer}"] + sys.argv[2:]
    mod.main()


def _print_help() -> None:
    print(
        "tidereach — Tidereach stack CLI\n"
        "\n"
        "Usage: tidereach <layer> <subcommand> [args...]\n"
        "\n"
        "Layers:\n"
        "  interlock   L0 attestation/glue + L4 policy module\n"
        "  sieve       L1 content scan / sensitivity gate\n"
        "  arbiter     L2 intent policy / control engine integration\n"
        "  airlock     L3 sandbox + session-stream substrate\n"
        "\n"
        "Examples:\n"
        "  tidereach interlock verify-integrity\n"
        "  tidereach interlock session-audit <transcript>\n"
        "  tidereach sieve scan --explain\n"
    )
