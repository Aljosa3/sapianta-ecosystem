# AGOL Convergence-Aware Refinement Acceptance Criteria V1

Status: finalized acceptance criteria.

Primitive:
`AGOL_CONVERGENCE_AWARE_REFINEMENT_V1`

Certification target:
`CERTIFIED_BOUNDED_CONVERGENCE_AWARE_REFINEMENT`

## Required Capabilities

The primitive is accepted only if it supports:

- deterministic convergence detection;
- convergence confidence reporting;
- stabilized region detection;
- freeze-zone recommendation;
- continuity protection recommendation;
- mutation pressure risk detection;
- recommended refinement scope reduction;
- `preserve_existing_direction` guidance;
- `local_refinement_only` guidance;
- replay lineage continuity.

## Required Governance Boundaries

The primitive must preserve:

- no autonomous redesign authority;
- no automatic UI freezing;
- no automatic mutation blocking;
- no runtime authority;
- no orchestration authority;
- no deployment authority;
- no user intent override;
- no autonomous execution;
- no automatic Product 1 mutation.

## Required Replay Guarantees

The primitive must expose:

- `primitive_id`;
- `request_hash`;
- `command_hash`;
- `scope_hash`;
- `deterministic_hash`;
- `replay_lineage`.

The command hash must remain tied to an empty command payload because the
primitive is non-executing.

## Required Acceptance Assertions

Acceptance requires validation that:

- convergence detection remains deterministic;
- replay visibility is preserved;
- stabilization guidance remains proposal-only;
- continuity protection does not become execution authority;
- `local_refinement_only` remains advisory;
- `preserve_existing_direction` remains non-binding;
- user final authority is preserved;
- no runtime or orchestration authority exists.

## Required Validation

Acceptance requires targeted validation of:

```bash
pytest tests/test_agol_convergence_aware_refinement.py
```

and compilation of:

```bash
python -m py_compile runtime/governance/agol_convergence_aware_refinement.py
```

Generated JSON finalize artifacts must pass `python -m json.tool`.

## Acceptance Result

Acceptance state:
`ACCEPTED_BOUNDED_CONVERGENCE_AWARE_REFINEMENT`

The primitive is accepted as a bounded, deterministic, replay-safe,
proposal-only convergence stabilization layer for Product 1 refinement.
