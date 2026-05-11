# AGOL Refinement Guidance Acceptance Criteria V1

Status: finalized acceptance criteria.

Workflow:
`AGOL_REFINEMENT_GUIDANCE_WORKFLOW_V1`

Certification target:
`CERTIFIED_BOUNDED_REFINEMENT_GUIDANCE`

## Required Capabilities

The workflow is accepted only if it supports:

- stagnation-triggered refinement guidance;
- bounded restructuring recommendation behavior;
- perceptual-impact escalation guidance;
- prompt augmentation generation;
- deterministic replay hashes;
- replay lineage continuity;
- proposal-only preservation;
- user authority preservation.

## Required Governance Boundaries

The workflow must preserve:

- no autonomous redesign authority;
- no automatic file mutation;
- no runtime behavior authority;
- no orchestration authority;
- no deployment authority;
- no user authority override;
- no governance semantic mutation.

## Required Replay Guarantees

The workflow must expose:

- `primitive_id`;
- `request_hash`;
- `command_hash`;
- `scope_hash`;
- `deterministic_hash`;
- `replay_lineage`.

The command hash must remain tied to an empty command payload because the
workflow is non-executing.

## Required Validation

Acceptance requires targeted validation of:

```bash
pytest tests/test_agol_adaptive_intent.py tests/test_agol_refinement_guidance.py
```

and compilation of:

```bash
python -m py_compile runtime/governance/agol_adaptive_intent.py runtime/governance/agol_refinement_guidance.py
```

Generated JSON finalize artifacts must pass `python -m json.tool`.

## Acceptance Result

Acceptance state:
`ACCEPTED_BOUNDED_REFINEMENT_GUIDANCE`

The workflow is accepted as a bounded, deterministic, replay-safe,
proposal-only guidance layer for Product 1 refinement collaboration.
