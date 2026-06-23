# ACLI_EVIDENCE_CONTINUITY_P0_IMPLEMENTATION_V1

Status: Defined

Scope: First P0 implementation tranche for ACLI execution-to-evidence continuity.

Source artifacts:

- ACLI_EVIDENCE_CONTINUITY_IMPLEMENTATION_BACKLOG_V1
- ACLI_EVIDENCE_CONTINUITY_IMPLEMENTATION_SEQUENCE_V1
- ACLI_CERTIFICATION_EXECUTION_001_EVIDENCE_V1

Tranche focus:

```text
S0 Evidence Root
S1 HIRR Evidence Persistence
S2 Workflow Invocation Persistence
```

Implementation verdict:

```text
P0_IMPLEMENTATION_READY
```

Final artifact verdict:

```text
ACLI_EVIDENCE_CONTINUITY_P0_IMPLEMENTATION_V1_DEFINED
```

## 1. Scope

This artifact defines the first implementation execution tranche for evidence continuity.

Included P0/P1 sequence work:

- certification evidence root creation
- HIRR evidence persistence
- workflow invocation evidence persistence
- fail-closed missing-evidence behavior for these stages

Out of scope for this tranche:

- approval persistence
- authorization persistence
- repository mutation execution
- validation execution
- replay package generation beyond root/link fields
- review-board decision artifacts
- AEC-001 rerun

This artifact prepares and records the implementation execution boundary. It does not claim that runtime implementation has already produced certifiable AEC-001 evidence.

## 2. Implementation Targets

Primary runtime target:

```text
aigol/runtime/acli_evidence_continuity_p0.py
```

Primary test target:

```text
tests/test_acli_evidence_continuity_p0.py
```

Primary evidence root target:

```text
runtime/acli_executable_certification_campaign_v1/EXEC-001/scenarios/AEC-001/
```

Adjacent runtime surfaces to preserve and integrate carefully:

- `aigol/runtime/human_intent_clarification_intake_runtime.py`
- `aigol/runtime/human_intent_clarification_certification_v1.py`
- `aigol/runtime/intent_classifier.py`
- `sapianta_bridge/nl_envelope/intent_classifier.py`
- `aigol/runtime/replay_certification_runtime.py`
- `aigol/runtime/unified_replay_reconstruction_runtime.py`
- `aigol/cli/commands/replay.py`

Targeting rule:

This tranche should add evidence continuity primitives or a narrow harness. It should not change existing certified runtime semantics unless a future implementation task explicitly approves that change.

## 3. Implementation Tasks

### Task P0-T001 Evidence Root Builder

Implement a deterministic evidence root builder for AEC-001.

Required behavior:

- create or reference the AEC-001 execution evidence root
- create lifecycle directories for intent, workflow, context, approval, authorization, mutation, validation, replay, and review
- write a root manifest
- include execution id and scenario id
- preserve existing artifacts if root already exists
- fail closed when root cannot be created or is unsafe to use

Expected output:

```text
EVIDENCE_ROOT_CREATED
```

or:

```text
EVIDENCE_ROOT_FAILED_CLOSED
```

### Task P0-T002 HIRR Evidence Model

Implement a persisted HIRR evidence model for certification execution.

Required fields:

- artifact type
- schema version
- execution id
- scenario id
- original human request reference
- resolved intent
- clarification status
- ambiguity status
- fail-closed status
- workflow input reference
- replay reference placeholder

Expected output:

```text
HIRR_INTENT_RESOLUTION_ARTIFACT
```

### Task P0-T003 HIRR Evidence Writer

Implement a writer that persists HIRR evidence under the evidence root.

Required behavior:

- write evidence as deterministic JSON
- include stable artifact path
- include hash or integrity reference when existing local patterns support it
- reject unresolved ambiguity unless explicitly recorded as fail-closed
- never infer approval or authorization

Expected output:

```text
HIRR_EVIDENCE_PERSISTED
```

or:

```text
HIRR_EVIDENCE_FAILED_CLOSED
```

### Task P0-T004 Workflow Invocation Evidence Model

Implement a persisted workflow invocation evidence model.

Required fields:

- artifact type
- schema version
- execution id
- scenario id
- HIRR artifact reference
- candidate workflows
- selected workflow
- rejected workflows
- selection rationale
- ambiguity status
- escalation status
- invocation verdict
- replay reference placeholder

Expected selected workflow for AEC-001:

```text
GOVERNANCE_ARTIFACT_CREATION
```

### Task P0-T005 Workflow Invocation Evidence Writer

Implement a writer that persists workflow invocation evidence under the evidence root.

Required behavior:

- refuse workflow persistence without HIRR evidence reference
- record selected and rejected candidates
- fail closed on no-match or multi-match ambiguity
- block mutation readiness when workflow evidence is missing
- write deterministic JSON evidence

Expected output:

```text
WORKFLOW_INVOCATION_EVIDENCE_PERSISTED
```

or:

```text
WORKFLOW_INVOCATION_FAILED_CLOSED
```

### Task P0-T006 Tranche Verification Harness

Implement a narrow verification harness for this tranche.

Required checks:

- evidence root exists
- HIRR artifact exists
- workflow invocation artifact exists
- workflow artifact references HIRR artifact
- missing HIRR blocks workflow evidence
- missing or ambiguous workflow fails closed
- no mutation, approval, authorization, validation, or replay package is claimed by this tranche

Expected output:

```text
P0_TRANCHE_VERIFICATION_PASS
```

or:

```text
P0_TRANCHE_VERIFICATION_FAIL_CLOSED
```

## 4. Validation Strategy

Minimum validation for documentation-only creation of this artifact:

```bash
git diff --check
```

Required validation after implementation code is added:

```bash
python -m pytest tests/test_acli_evidence_continuity_p0.py
git diff --check
```

Implementation validation must prove:

- positive evidence root creation
- positive HIRR persistence
- positive workflow invocation persistence
- negative missing-HIRR fail-closed behavior
- negative ambiguous-workflow fail-closed behavior
- no readiness claim emitted by P0 tranche

## 5. Expected Evidence

Expected evidence after successful P0 tranche implementation:

```text
runtime/acli_executable_certification_campaign_v1/EXEC-001/scenarios/AEC-001/manifest.json
runtime/acli_executable_certification_campaign_v1/EXEC-001/scenarios/AEC-001/intent/hirr_intent_resolution.json
runtime/acli_executable_certification_campaign_v1/EXEC-001/scenarios/AEC-001/workflow/workflow_invocation_decision.json
runtime/acli_executable_certification_campaign_v1/EXEC-001/scenarios/AEC-001/workflow/workflow_candidate_selection.json
```

Expected negative evidence fixtures:

- missing HIRR blocks workflow invocation
- unresolved ambiguity blocks workflow invocation
- workflow no-match fails closed
- workflow multi-match fails closed unless clarification is required

Evidence status after this tranche:

```text
PARTIAL_EVIDENCE_CONTINUITY
```

This tranche does not produce complete certification evidence.

## 6. Replay Impact

Replay impact:

```text
REPLAY_LINKAGE_PREPARED
```

This tranche prepares replay linkage by adding replay reference fields and deterministic evidence paths.

It does not yet generate:

- development replay package
- replay artifact index
- replay reconstruction report
- secret-free evidence assessment
- review-board decision artifact

Replay boundary:

```text
Replay remains Source Of Truth.
P0 evidence is not certification replay until replay package generation is implemented.
```

## 7. Risks

### 7.1 Evidence Root Collision Risk

Risk:

Existing or partial evidence roots may be overwritten.

Required handling:

Preserve existing artifacts. Use deterministic versioning or fail closed when root reuse is unsafe.

### 7.2 Chat-Only Evidence Risk

Risk:

Implementation may treat the active conversation as sufficient certification evidence.

Required handling:

Persist formal artifacts. Conversation may be referenced only as source context, not as standalone certification evidence.

### 7.3 Workflow Over-Inference Risk

Risk:

Implementation may infer workflow selection without recording candidates and rationale.

Required handling:

Persist selected workflow, rejected candidates, and selection rationale.

### 7.4 Premature Readiness Risk

Risk:

Partial P0 evidence may be mistaken for AEC-001 readiness.

Required handling:

Emit only partial readiness status and preserve `ACLI_GOVERNED_DEVELOPMENT_READY_NOT_CLAIMED`.

## 8. Completion Criteria

P0 tranche implementation is complete when:

1. Evidence root builder exists.
2. Evidence root manifest can be persisted.
3. HIRR evidence model exists.
4. HIRR evidence can be persisted under the evidence root.
5. Workflow invocation evidence model exists.
6. Workflow invocation evidence can be persisted under the evidence root.
7. Workflow evidence links to HIRR evidence.
8. Missing HIRR fails closed.
9. Missing or ambiguous workflow selection fails closed.
10. Tests or verification artifacts prove positive and negative paths.
11. No approval, authorization, mutation, replay package, review, or readiness claim is emitted.

Completion status when criteria pass:

```text
P0_TRANCHE_COMPLETE
```

## 9. Re-Execution Impact

Impact on AEC-001 rerun readiness:

```text
AEC_001_RE_EXECUTION_NOT_READY
```

Rationale:

This tranche closes only the first continuity stages:

```text
Evidence Root
-> HIRR
-> Workflow Invocation
```

AEC-001 rerun remains blocked until later tranches implement:

- repository context persistence
- approval persistence
- authorization persistence
- mutation and validation persistence
- replay package generation
- review evidence generation

Re-execution impact after successful tranche:

```text
AEC_001_RE_EXECUTION_PROGRESS_INCREASED
```

but:

```text
AEC_001_RE_EXECUTION_READY_NOT_CLAIMED
```

## 10. Final Verdict

Final P0 implementation verdict:

```text
P0_IMPLEMENTATION_READY
```

Rationale:

The first implementation tranche is scoped, ordered, and ready to execute. It targets evidence root creation, HIRR evidence persistence, and workflow invocation evidence persistence without redesigning ACLI or governance and without claiming complete certification evidence.

Readiness boundary:

```text
ACLI_GOVERNED_DEVELOPMENT_READY_NOT_CLAIMED
AEC_001_RE_EXECUTION_READY_NOT_CLAIMED
```

Final artifact verdict:

```text
ACLI_EVIDENCE_CONTINUITY_P0_IMPLEMENTATION_V1_DEFINED
```
