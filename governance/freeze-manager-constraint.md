# freeze-manager-constraint

since: 2026-06-30

Defines the invariants callers must obey when interacting with interlock's `FreezeManager` and the `~/.tidereach/FREEZE` flag file.

## FREEZE flag file invariants

The canonical freeze file is `~/.tidereach/FREEZE`. `FreezeManager` checks and sets the file; all other layers call `FreezeManager.check()` — they never stat or open the file directly.

| Invariant | Requirement |
|---|---|
| File type | `S_ISREG` — a regular file, not a symlink, directory, or special file. |
| Mode | `0o600` — owner read/write, no group/world permissions. |
| Owner | `os.geteuid()` — the effective UID of the running process. |
| Anomalous mode | If mode ≠ 0o600, `FreezeManager` logs an anomaly event and treats the freeze as **set** (fail-closed). |
| Symlink | If the path resolves to a symlink at any point, `FreezeManager` logs an anomaly and treats the freeze as **set** (fail-closed). |

## Caller contract

```
# Correct usage from any layer:
frozen = interlock.FreezeManager.check()  # returns bool
if frozen:
    raise GateFrozenError(...)

# NEVER:
os.path.exists("~/.tidereach/FREEZE")  # bypass — violates ownership
```

## Auto-freeze

`FreezeManager` may set the freeze automatically when a canary drift or anomaly counter threshold is crossed. The resulting audit event is `gate_frozen_auto` (see `audit-event-ownership.md`).

## Unfreeze

Only the operator may unfreeze (`tidereach interlock unfreeze`). No layer may clear the freeze programmatically.
