# Tidereach — Interlock

L0 attestation/glue + L4 policy module for the [Tidereach](https://github.com/tidereach/hull) stack. See `README.md` for the layer table; this file is agent orientation.

Stage 2 substance is in progress. Cross-repo stage state lives in **hull's `STATE.md`**, not a local file — read `../hull/STATE.md` (or `tidereach/hull` on GitHub) for the current stage-tracker and recent events.

## Files

- `pyproject.toml` — package metadata; ruff (line-length 100, `E,F,I,UP`) + mypy strict + pytest config.
- `src/tidereach/interlock/` — package code (`cli.py`, `dispatch.py`, `__init__.py`). Namespace package under `src/tidereach/` so sibling layers can co-install into the same `tidereach.*` namespace.
- `tests/` — pytest suite. Currently `test_dispatch.py`; more land as CLI subcommands materialize.
- `contracts/` — cross-repo schemas. **Per-PR file discipline applies — see `contracts/AGENTS.md`.**
- `governance/` — cross-layer governance docs (audit-event ownership, freeze-manager constraint, layer constraints, composition).
- `.github/workflows/ci.yml` — CI; calls hull's reusable workflows via `uses: tidereach/hull/.github/workflows/<file>@main`.
- `.pre-commit-config.yaml` — canonical baseline copied from hull; mypy commented out until `src/` matures.

## Commands

| Command | Purpose |
|---|---|
| `uv sync --frozen` | Install locked deps into `.venv`. |
| `uv run pytest -q` | Run test suite. |
| `uv run mypy src/` | Type-check (strict per `pyproject.toml`). |
| `uv run ruff check .` | Lint. |
| `.venv/bin/pre-commit run --files <paths>` | Hygiene + betterleaks + uv-lock; matches CI parity. |

## Inheritance from hull

Interlock inherits verbatim from hull per hull's bootstrap defaults (see `tidereach/hull/docs/BOOTSTRAP.md`):

- **Branch protection** — three required status checks (`legacy-name-guard / grep-gate`, `betterleaks / scan`, `pr-title-lint / lint`); `required_signatures: false`; `required_approving_review_count: 0`.
- **CI** — `ci.yml` calls hull's reusable workflows remotely.
- **Commit signing** — deferred to v2 per `hull/ROADMAP.md` item 8. `git commit` does NOT require `-S`. Do NOT set `commit.gpgsign=true` locally for this repo.
- **Merge queue** — enabled (2026-06-30). Merge via "Merge when ready".

If any hull-side default changes, the change lands in `hull/AGENTS.md` and this repo tracks it. Do not re-derive defaults locally.

## Project code standards

Layer names (`interlock`, `sieve`, `arbiter`, `airlock`, `jettison`, `hull`, `drydock`) may be renamed by stakeholders. Use layer names in **documentation** only; avoid them in Python identifiers, env vars, and settings keys — a doc rename is search-and-replace; a code rename is a breaking change for consumers.

<!-- legacy-name-allowed -->
The `legacy-name-guard` CI job enforces the same discipline for pre-migration `spektralia` names.
<!-- /legacy-name-allowed -->

## Gotchas

- **Contracts PRs must touch only one contract subdir.** See `contracts/AGENTS.md` for the full rule and rationale. Do NOT edit `contracts/README.md` in a per-contract PR.
- **STATE.md updates ship as dedicated chore-PRs** — same discipline as hull. Never bundle state updates with feature PRs. When several PRs land in a batch, one `chore(state): roll <range>` PR against **hull** covers them.
- **Ember agent** (`ember:Ember`) works well for spec revision. If it fails to spawn with a model-access error, check that the model ID at `~/.claude/plugins/cache/agency/ember/1.0.2/agents/ember.md` uses hyphen notation (`claude-opus-4-7`, not `4.7`).

## Memory vs State

`AGENTS.md` is the north star for stable project decisions. `hull/STATE.md` is the cross-repo session bookmark. Read `hull/STATE.md` at the start of any session touching stage progress; write via a dedicated chore-PR against hull.
