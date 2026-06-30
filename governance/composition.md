# composition

since: 2026-06-30

Hook-ordering and OR-to-block semantics for the Tidereach layered stack. This document gates Stage 5 (arbiter): arbiter's spec references this file rather than re-documenting the ordering.

## Hook ordering (agent CLI surface)

The following hook types fire in this order for a Claude Code session. The ordering is the same for Copilot; tool names differ.

| Order | Hook type | Layer(s) that respond | Notes |
|---|---|---|---|
| 1 | `UserPromptSubmit` | sieve | Content scan of the user prompt. |
| 2 | `PreToolUse` | sieve, arbiter (optional) | Content scan of tool args; arbiter intent verdict (if engine is running). |
| 3 | `PostToolUse` | sieve | Content scan of tool output. |
| 4 | `Stop` | interlock policy module (BlockAction, v2) | Soft block: flag-file + dedicated Stop-hook script. |

interlock preflight (`verify-integrity`, `check-sandbox`, etc.) runs out-of-band before the session starts, not as a hook.

## OR-to-block rule

**Any layer returning a non-zero exit code or a `block` verdict BLOCKS the operation.** The agent CLI ORs the outputs of all responding hooks; one block is sufficient.

This means:
- sieve returning `block` at `PreToolUse` blocks the tool call regardless of arbiter's verdict.
- arbiter returning `deny` blocks the tool call regardless of sieve's verdict.
- Neither layer needs to know about the other's verdict; the agent CLI is the AND/OR gate.

## Arbiter participation

Arbiter is optional at `PreToolUse`. If the engine socket is absent or the engine times out, the hook must return `allow` (fail-open for arbiter) unless the operator has configured fail-closed mode. The timeout is the `fail_closed_timeout` in the engine-IPC contract.

The hook-ordering example in arbiter's SPEC.md cites this document for the ordering and OR-to-block rule.

## BlockAction (v2 Soft)

The v2 `BlockAction` writes a flag file (`~/.tidereach/block-requested`) and the dedicated Stop-hook script reads it on `Stop`. This is cooperative — the agent CLI must have the Stop hook installed. If the Stop hook is absent, the flag file is written but the session continues (the block is advisory in that configuration). See `layer4_jettison.md` in tidereach/hull for the full BlockAction spec.
