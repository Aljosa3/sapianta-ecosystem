# AIGOL_HUMAN_CLARIFICATION_REPLAY_MODEL_V1

## Status

Human clarification and approval replay model.

## Replay Purpose

Replay must allow an operator to reconstruct:

- why clarification was required;
- what ambiguity category was detected;
- what human response resolved or failed to resolve the ambiguity;
- why approval was required;
- what human approval decision was recorded;
- how workflow resumed;
- whether provider and AiGOL authority boundaries were preserved.

## Required Clarification Replay Chain

Minimum clarification replay chain:

```text
human_clarification_required
human_clarification_prompt_presented
human_clarification_response_recorded
human_clarification_validated
workflow_resume_instruction_recorded
```

## Required Approval Replay Chain

Minimum approval replay chain:

```text
human_approval_required
human_approval_prompt_presented
human_approval_decision_recorded
human_approval_validated
workflow_resume_instruction_recorded
```

## Required Replay Fields

Replay must preserve:

- `canonical_chain_id`;
- `clarification_request_reference`;
- `clarification_request_hash`;
- `clarification_response_reference`;
- `clarification_response_hash`;
- `approval_request_reference`;
- `approval_request_hash`;
- `approval_decision_reference`;
- `approval_decision_hash`;
- `source_artifact_reference`;
- `source_artifact_hash`;
- `context_reference`;
- `context_hash`;
- `proposal_reference`;
- `proposal_hash`;
- `resume_stage`;
- `resume_input_hash`;
- `replay_visible`;
- `artifact_hash`.

## Hash Requirements

Replay must validate:

- wrapper hashes;
- clarification request hash;
- clarification response hash;
- approval request hash;
- approval decision hash;
- source proposal hash;
- context hash;
- resume instruction hash.

Any mismatch requires:

```text
FAILED_CLOSED
```

## Continuity Requirements

Clarification and approval artifacts must share:

- canonical chain id;
- source artifact lineage;
- context reference;
- replay visibility;
- resume stage reference.

Continuity failure requires:

```text
FAILED_CLOSED
```

## Resume Replay

Resume replay must show:

- previous blocked stage;
- clarification or approval decision;
- selected resume stage;
- resume input references;
- resume input hashes;
- authority boundaries preserved.

## Forbidden Replay States

Replay must fail closed if any clarification or approval artifact records:

```text
provider_authority = true
aigol_execution_authority = true
dispatch_requested = true
execution_requested = true
worker_invoked = true
governance_mutated = true
replay_mutated = true
```

## Non-Goals

This replay model does not implement:

- clarification runtime;
- approval runtime;
- provider invocation;
- dispatch;
- execution;
- governance mutation.

