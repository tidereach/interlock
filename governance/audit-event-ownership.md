# audit-event-ownership

since: 2026-06-30

Defines which layer emits which audit event and where ownership lives. interlock owns the audit chain and defines the event envelope; layers that emit events call into interlock's `AuditChain.append()`.

## Two-tier model

**Layer-exclusive events** — emitted only by interlock's own code (including the in-process policy module):

| Event | Emitter | Notes |
|---|---|---|
| `integrity_verified` | interlock `IntegrityHasher` | |
| `integrity_failed` | interlock `IntegrityHasher` | |
| `freeze_set` | interlock `FreezeManager` | |
| `freeze_cleared` | interlock `FreezeManager` | |
| `anomaly_counter_incremented` | interlock anomaly module | |
| `heartbeat` | interlock heartbeat | |
| `audit_rotated` | interlock audit module | |
| `audit_repaired` | interlock audit module | |
| `session_event_seen` | interlock policy module | |
| `rule_hit` | interlock policy module | |
| `action_logged` | interlock policy module | |
| `egress_decision` | interlock `SquidAccessReader` | Parsed from host-bound Squid access log; one envelope per line. Fields: `{domain, action, client, http_status}`. |

**Cross-layer shared-namespace events** — defined by interlock, emitted by named layer via `AuditChain.append()` call:

| Event | Defined by | Emitter | Notes |
|---|---|---|---|
| `gate_frozen` | interlock | sieve (at gate-call time) | Emitted when sieve calls `FreezeManager.check()` and freeze is set. Replaces the pre-migration `gate_frozen{_auto}` events that incorrectly emitted from `gate.py` (L1). |
| `gate_frozen_auto` | interlock | sieve (at gate-call time) | Emitted when auto-freeze triggers at the gate. Same fix as `gate_frozen`. |
| `scan_completed` | interlock (envelope only) | sieve | Per-scan summary event. |
| `verdict_issued` | interlock (envelope only) | arbiter adapter | Engine verdict; carries `context_id` for correlation. |

## Ownership rule

- interlock defines the envelope schema (in `contracts/audit-envelope/`).
- Any layer calling `AuditChain.append()` does so with a pre-built envelope; it does not construct the hash chain itself.
- The `gate_frozen` / `gate_frozen_auto` reassignment from sieve to the interlock-managed cross-layer namespace is the canonical example of this rule: L1 `gate.py` calls `interlock.FreezeManager.check()`; interlock emits the event.
