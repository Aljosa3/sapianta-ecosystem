# AGOL Refinement Guidance Workflow Evidence V1

## Evidence Status

Status: CREATED

This evidence records the first practical integration of AGOL adaptive
intent-awareness into Product 1 refinement guidance.

## Created Artifacts

- `docs/governance/AGOL_REFINEMENT_GUIDANCE_WORKFLOW_V1.md`
- `runtime/governance/agol_refinement_guidance.py`
- `tests/test_agol_refinement_guidance.py`
- `.github/governance/evidence/AGOL_REFINEMENT_GUIDANCE_WORKFLOW_EVIDENCE_V1.md`

## Governance Meaning

The workflow turns bounded adaptive intent signals into human-facing refinement
guidance. It helps AGOL propose more effective refinement strategies without
granting autonomous redesign authority.

The workflow is:

- bounded
- deterministic
- replay-visible
- proposal-only
- user-authority preserving
- Product 1 refinement oriented

## Recommendation Semantics

The workflow can produce:

- suggested refinement mode
- recommendation reason
- suggested direction
- prompt augmentation text
- bounded escalation guidance

If stagnation or mismatch is detected, the workflow may recommend
`bounded_restructuring` or `perceptual_impact`. This is a strategy suggestion,
not a mutation permission.

## Prompt Augmentation Semantics

Prompt augmentation helps users express:

- refinement magnitude
- composition tolerance
- perceptual impact expectations
- governance continuity requirements
- runtime and autonomy boundaries

The augmentation is guidance only. It does not execute changes.

## Preserved Boundaries

The workflow explicitly preserves:

- no autonomous redesign
- no automatic file mutation
- no runtime behavior change
- no governance semantic change
- no deployment automation
- no orchestration authority
- no user authority override

## Replay-Safe Evidence

Guidance outputs preserve:

- primitive id: `AGOL_REFINEMENT_GUIDANCE_WORKFLOW_V1`
- adaptive primitive reference: `AGOL_ADAPTIVE_INTENT_AWARENESS_V1`
- deterministic request hash
- deterministic empty command hash
- deterministic scope hash
- deterministic result hash
- replay lineage references

## Validation Expectations

Targeted tests validate:

- stagnation-triggered refinement suggestions
- refinement mode recommendation behavior
- bounded escalation guidance
- prompt augmentation suggestions
- proposal-only behavior
- preservation of user authority
- deterministic replay visibility

## Known Limitations

This layer does not inspect the live UI, redesign Product 1, execute tooling, or
autonomously choose a new visual direction. It only improves the guidance layer
around human-directed AGOL refinement work.
