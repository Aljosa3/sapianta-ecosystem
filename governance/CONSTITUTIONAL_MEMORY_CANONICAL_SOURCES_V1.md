# Constitutional Memory Canonical Sources V1

Status: canonical source classification for Constitutional Memory.

## CANONICAL Sources

Canonical sources are the first read targets.

- `docs/governance/CONSTITUTIONAL_ARCHITECTURE_SPEC_V1.md`
- `docs/governance/CANONICAL_LAYER_MODEL.md`
- `docs/governance/CONSTITUTIONAL_INVARIANTS.md`
- `docs/governance/GOVERNANCE_ENFORCEMENT_HIERARCHY.md`
- `docs/governance/GOVERNANCE_LINEAGE_MODEL.md`
- `governance/FIRST_CONSTITUTIONAL_BASELINE_FREEZE_V1.md`
- `governance/CONSTITUTIONAL_BASELINE_FREEZE_GUARANTEES_V1.md`
- `governance/REPLAY_BASELINE_FREEZE_V1.md`
- `governance/CANONICAL_REPLAY_LANGUAGE_V1.md`
- `governance/CANONICAL_AUTHORITY_MODEL_V1.md`
- `governance/FIRST_USEFUL_AIGOL_V1_FREEZE.md`
- `governance/FIRST_USEFUL_AIGOL_V1_BASELINE.md`
- `governance/FIRST_USEFUL_AIGOL_V1_GUARANTEES.md`

## SUPPORTING Sources

Supporting sources provide certification, review, readiness, and boundary evidence.

- acceptance JSON artifacts
- certification JSON artifacts
- manifest JSON artifacts
- boundary guarantee markdown artifacts
- position reviews
- readiness reviews
- pressure validation reports
- stability reports
- operational epoch artifacts
- provider, worker, and human request reviews

## DERIVED Sources

Derived sources provide runtime or replay observations.

- `.runtime/` evidence artifacts
- replay summaries
- governed result summaries
- runtime reconstruction outputs
- lineage reconstruction outputs
- hash chain verification outputs

## Conflict Rule

If sources conflict, interpret in this order:

1. replay safety
2. constitutional specs and invariants
3. canonical layer and enforcement hierarchy
4. frozen baselines and guarantees
5. canonical replay and authority language
6. certifications and acceptance evidence
7. operational replay and runtime evidence
8. derived summaries

Derived evidence may reveal a gap or failure, but it does not silently rewrite the canonical source.

