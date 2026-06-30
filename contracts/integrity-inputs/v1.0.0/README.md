# integrity-inputs v1.0.0

Canonical `HashInput` names and serialization specs for interlock's `IntegrityHasher`. Each entry names one input to the integrity hash; layer repos implement the `HashInput` protocol against this list.

## Pinned entries (spec locked)

| Name | Owner | Serialization |
|---|---|---|
| `pattern_table` | tidereach/sieve | Sorted-keys JSON of the pattern registry, UTF-8 encoded. |
| `model_digest` | tidereach/sieve | Raw model manifest bytes as returned by the Ollama API manifest endpoint. |
| `prompt_template` | tidereach/sieve | UTF-8 encoded template string, NFC-normalised. |

## TBD entries (pending layer spec locks)

These entries are expected but their serialization spec depends on the owning layer's spec locking. Each will be pinned in a minor-version bump to this schema once the named condition is met.

| Name | Owner | Graduation condition |
|---|---|---|
| `sandbox_config_hash` | tidereach/airlock | Airlock Stage 4 spec locks the set of files hashed (Containerfile + compose + proxy lists + landlock + seccomp). |
| `hook_manifest_digest` | tidereach/interlock | interlock Stage 2 ships the hook integration manifest format and its canonical serialization. |
| `ruleset_hash` | tidereach/interlock (policy module) | interlock Stage 2 ships the YAML rule engine; the ruleset hash input is defined alongside the rule DSL. |
| `engine_ipc_version` | tidereach/arbiter | arbiter Stage 5 locks the engine IPC contract version string format. |

## Versioning

- Adding a `tbd` → `pinned` entry → **v1.x minor bump**
- Changing serialization of a pinned entry → **v2 major bump** (breaking; affects all IntegrityHasher consumers)

## Protocol

Each layer implements:

```python
class HashInput(Protocol):
    name: str
    def serialize(self) -> bytes: ...
```

interlock's `IntegrityHasher` collects all registered `HashInput` instances, calls `serialize()` on each in deterministic `name`-sorted order, and hashes the concatenation.
