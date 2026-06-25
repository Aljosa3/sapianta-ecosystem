# GOVERNANCE_TO_HUMAN_TRANSLATION_RUNTIME_V1

Status: IMPLEMENTED

## 1. Runtime Purpose

GOVERNANCE_TO_HUMAN_TRANSLATION_RUNTIME_V1 implements the deterministic Governance -> Human translation runtime for Universal ACLI.

The runtime converts authoritative governance state and evidence references into a human-readable Universal Translation Artifact.

It exists to help an operator understand what the governance system currently knows, what requires approval, whether execution occurred, what validation reported, where replay evidence exists, and whether ERR evidence is present.

## 2. Runtime Module

Runtime module:

`aigol/runtime/governance_to_human_translation_runtime.py`

Primary entrypoints:

- `translate_governance_to_human`
- `reconstruct_governance_to_human_translation_replay`

The runtime uses:

- `aigol/runtime/universal_translation_artifact_schema.py`
- `aigol/runtime/transport/serialization.py`
- `aigol/runtime/models.py`

## 3. Inputs

Required inputs:

- governance state
- replay evidence
- translation request identifier
- creation timestamp
- replay directory

Optional evidence inputs:

- proposal state
- approval state
- worker results
- validation results
- ERR evidence
- operator context

Governance state and replay evidence must be non-empty JSON objects. Optional evidence may be omitted, but if supplied it must be a JSON object.

## 4. Outputs

The runtime outputs a Universal Translation Artifact with:

- `source_direction`: `GOVERNANCE_TO_HUMAN`
- normalized workflow state
- deterministic human-readable payload
- authoritative source-state references
- ambiguity flags
- governance-only confidence
- deterministic fallback status
- replay reference
- authority-denial flags

The runtime also writes a deterministic replay wrapper:

`000_governance_to_human_translation_recorded.json`

## 5. Human-Readable Payload

The human-readable payload includes:

- governance decision summary
- proposal summary
- approval explanation
- worker execution status
- validation summary
- replay summary
- ERR summary
- operator action required
- authoritative state references
- ambiguity explanation
- rendered explanation
- non-authoritative notice

The rendered explanation is deterministic and generated from fixed sections:

- SUMMARY
- APPROVAL
- EXECUTION
- VALIDATION
- REPLAY
- ERR
- WHAT TO DO NEXT

## 6. Authoritative State References

The runtime preserves references to authoritative state by recording deterministic hashes for:

- governance state
- replay evidence
- proposal state
- approval state
- worker results
- validation results
- ERR evidence

It also preserves stable reference fields when present:

- replay reference
- proposal reference
- approval reference
- ERR reference

These references allow the explanation to be audited without allowing the explanation to become authority.

## 7. Approval Runtime Integration

The runtime explains approval requirements and approval state.

It does not:

- grant approval
- infer approval
- repair missing approval evidence
- convert explanation into approval

If governance state requires approval but approval state is unavailable, the runtime marks material ambiguity and asks for evidence review.

## 8. Replay And ERR Integration

Replay is the source of truth for translation evidence.

Replay records:

- authoritative governance state snapshot
- replay evidence snapshot
- optional proposal, approval, worker, validation, and ERR evidence snapshots
- source-state hashes
- rendered human-readable explanation
- artifact hash
- wrapper replay hash

Replay reconstruction verifies:

- replay ordering
- wrapper hash
- Universal Translation Artifact validity
- artifact hash
- source direction

Tampered replay fails closed.

ERR evidence is summarized when supplied. Missing ERR evidence is explicitly visible rather than inferred.

## 9. Authority Boundaries

The runtime cannot:

- invoke providers
- approve execution
- execute workflows
- mutate governance state
- mutate repository state
- mutate replay after persistence
- grant worker authority

All authority flags are false.

The explanation is advisory and non-authoritative. ACLI and governance state remain authoritative.

## 10. Fail-Closed Requirements

The runtime fails closed when:

- governance state is missing or empty
- replay evidence is missing or empty
- optional evidence inputs are malformed
- translation metadata is malformed
- replay evidence is missing during reconstruction
- replay ordering is invalid
- replay hash verification fails
- Universal Translation Artifact validation fails
- replay source direction is not `GOVERNANCE_TO_HUMAN`

Fail-closed translation never proceeds to approval or execution.

## 11. Validation Evidence

Focused validation covers:

- deterministic translation
- human-readable payload generation
- approval requirement explanation
- worker result explanation
- validation result explanation
- replay evidence explanation
- ERR evidence explanation
- authoritative reference hashing
- stable artifact hashes
- replay reconstruction
- malformed input failure
- replay tamper detection
- Universal Translation Artifact compatibility

Validation commands:

```bash
python -m pytest tests/test_governance_to_human_translation_runtime_v1.py tests/test_universal_translation_artifact_schema_v1.py -q
python -m py_compile aigol/runtime/governance_to_human_translation_runtime.py aigol/runtime/universal_translation_artifact_schema.py
git diff --check
```

## 12. Final Verdict

GOVERNANCE_TO_HUMAN_TRANSLATION_RUNTIME_READY
