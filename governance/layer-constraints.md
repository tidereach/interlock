# layer-constraints

since: 2026-06-30

Cross-layer obligations derived from `migration/MAIN.md § 8 Constraints` in tidereach/hull. These constrain every layer repo (interlock, sieve, arbiter, airlock) and drydock.

## Constraint 1 — Greenfield rebuild

**No source from any prior implementation is copied forward.** Every file in every layer repo is authored against the migration specs. Pre-migration code patterns may inform the spec text; no `.py`, `.toml`, `.yaml`, or `.json` file is lifted verbatim from history.

*Gate*: every layer's Reuse table has explicit `Rewrite | Drop | Superseded` per source file. No `Lift verbatim` category.

## Constraint 2 — 100% ready filter

**Only reuse existing code if 100% ready without modification.** In practice, this reinforces Constraint 1: "100% ready" means "authored greenfield against the spec," because the pre-migration codebase is not a source of truth.

## Constraint 3 — Lessons learned required

**Every layer spec must have a `Lessons learned` section** drawn from at least three sources: (a) AGENTS.md Gotchas, (b) `docs/RATIONALE.md` narratives, (c) closed/open issues rolled into the migration. Each lesson is phrased as *what we learned — how it shapes v1*.

## Constraint 4 — Doc currency

**Every layer spec must have a `Doc audit` section** calling out which current docs apply, which are stale, which contradict another doc, and which must be retired. Doc reconciliation tasks are listed in `migration/MAIN.md § 13`.

## Constraint 5 — Spec completeness

**Layer specs are detailed enough for a fresh contributor to start Stage 2/3/4 work from the file alone.** No "see the old SPEC.md §X" hand-offs.

## Constraint 6 — No legacy names in new repos

**Historical `spektralia`, `SPEKTRALIA_`, `src/spektralia/`, `~/.spektralia/` references MUST NEVER appear in new repos** outside an explicitly-flagged `migration/` or `CHANGELOG.md` historical-narrative block. Each repo's CI runs a grep gate (`legacy-name-guard.yml` from tidereach/hull) asserting zero matches. Mark exempt blocks with `<!-- legacy-name-allowed -->`. No exceptions.

*Layer code identifiers*: use descriptive, best-practice naming — no layer names (`interlock`, `sieve`, …) in Python identifiers, env vars, or class names. Layer names are doc-only handles (see `migration/MAIN.md § 7 Decision 5`).
