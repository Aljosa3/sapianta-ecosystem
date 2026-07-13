# G27-11 — Validation Completion to Replay Certification Handoff

Status: IMPLEMENTED AND DETERMINISTICALLY VERIFIED

Date: 2026-07-13

## Purpose

G27-11 implements one bounded Platform Core transition:

`completed governed validation evidence -> RESULT_VALIDATION_ARTIFACT_V1`

The resulting artifact is the existing input contract accepted by Replay
Certification. This milestone does not invoke Replay Certification and does not
interpret a validation outcome as certification.

## Runtime

- `aigol/runtime/validation_completion_replay_certification_handoff_runtime.py`
- handoff evidence:
  `VALIDATION_COMPLETION_REPLAY_CERTIFICATION_HANDOFF_ARTIFACT_V1`
- registry capability:
  `VALIDATION_COMPLETION_REPLAY_CERTIFICATION_HANDOFF`

The runtime exposes bounded composition, handoff-artifact validation, and
Replay reconstruction operations.

## Accepted Sources

Exactly two validation evidence types are accepted:

- `VALIDATION_RESULT_ARTIFACT_V1` from the single-command governed validation
  lifecycle;
- `VALIDATION_SUITE_SUMMARY_ARTIFACT_V1` from the governed validation-suite
  lifecycle.

The supplied artifact must be byte-for-byte equivalent at the canonical JSON
level to the corresponding artifact stored in its source Replay. Artifact type,
artifact hash, validation status, candidate binding, and lifecycle completion
are verified.

A failed validation command or failed validation suite is still admissible when
the governed lifecycle itself completed normally and preserved the failure as
evidence. A failed-closed or incomplete lifecycle is not admissible.

## Replay Lineage

For single-command evidence, the runtime delegates reconstruction to
`reconstruct_governed_validation_replay(...)` and binds:

- candidate identity and hash;
- Worker result hash;
- validation result identity and hash;
- governed validation completion identity and hash;
- source Replay reference and deterministic Replay hash.

For suite evidence, it delegates reconstruction to
`reconstruct_governed_validation_suite_replay(...)` and binds:

- suite candidate identity and hash;
- ordered command-execution evidence hash;
- suite summary identity and hash;
- suite completion identity and hash;
- source Replay reference and deterministic Replay hash.

## Plan Lineage

When the source candidate contains the G27-09 `associated_reference`, the
handoff preserves the validation plan identifier, plan artifact hash, plan hash,
impact lineage, requirement lineage, and command-mapping lineage. The complete
plan lineage is included in both validation evidence and the composed Result
Validation artifact and is therefore covered by their deterministic hashes.

Legacy validation candidates without plan lineage remain supported. Their
handoff records `plan_lineage_preserved: false` rather than synthesizing plan
lineage.

## Existing Contract Reuse

The handoff emits the existing `RESULT_VALIDATION_ARTIFACT_V1` contract with:

- `validation_status: RESULT_VALIDATION_COMPLETED`;
- hash-bound `RESULT_VALIDATION_EVIDENCE_ARTIFACT_V1`;
- `replay_lineage_preserved: true`;
- `fail_closed_preserved: true`;
- `deterministic_validation_preserved: true`;
- `ready_for_replay_certification: true`;
- `requires_replay_certification: true`;
- `improvement_loop_entry_allowed: false`.

Compatibility is verified against the existing
`certify_validated_replay(...)` entrypoint without modifying Replay
Certification or Result Validation runtimes.

## Handoff Replay

One immutable handoff artifact is persisted under
`validation_completion_replay_certification_handoff_recorded`. Reconstruction
verifies the wrapper hash, handoff hash, non-authority flags, embedded Result
Validation artifact, validation evidence hash, readiness fields, and failure
state.

## Constitutional Boundary

G27-11 only composes certification input. It does not:

- execute validation;
- invoke Workers or Providers;
- create human approval or Governance authorization;
- mutate the repository;
- invoke Replay Certification;
- certify validation results;
- create a new Replay or Certification runtime;
- transfer orchestration to AiCLI or another Human Interface.

Replay Certification remains the sole downstream owner of certification.

## Known Limitation

The handoff requires the complete canonical source validation Replay. A detached
result or suite summary, even with a valid self-hash, fails closed because
lifecycle completion and Replay continuity cannot be established.
