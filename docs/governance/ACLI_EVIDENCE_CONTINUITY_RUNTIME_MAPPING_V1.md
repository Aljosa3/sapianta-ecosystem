# ACLI_EVIDENCE_CONTINUITY_RUNTIME_MAPPING_V1

Status: Defined

Scope: Runtime mapping for ACLI evidence continuity implementation.

Input artifacts:

- ACLI_EVIDENCE_CONTINUITY_REMEDIATION_PLAN_V1
- ACLI_EVIDENCE_CONTINUITY_IMPLEMENTATION_PLAN_V1
- ACLI_EVIDENCE_CONTINUITY_IMPLEMENTATION_BACKLOG_V1
- ACLI_EVIDENCE_CONTINUITY_IMPLEMENTATION_SEQUENCE_V1
- ACLI_EVIDENCE_CONTINUITY_P0_IMPLEMENTATION_V1

Runtime mapping verdict:

```text
RUNTIME_MAPPING_READY
```

Final artifact verdict:

```text
ACLI_EVIDENCE_CONTINUITY_RUNTIME_MAPPING_V1_DEFINED
```

## 1. Purpose

This artifact maps ACLI evidence continuity requirements to actual runtime components.

It is the bridge between governance planning and code implementation. It does not redesign ACLI, governance, replay, certification, or Product 1.

Runtime implementation must preserve:

```text
Human = Authority
Replay = Source Of Truth
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```

No mapped runtime component may infer approval, fabricate replay, bypass fail-closed behavior, or claim `ACLI_GOVERNED_DEVELOPMENT_READY`.

## 2. P0 Requirement Inventory

P0 requirements under this mapping:

| Requirement | Description | Sequence stage |
| --- | --- | --- |
| Evidence root creation | Create deterministic AEC-001 evidence root and lifecycle directories | S0 |
| HIRR evidence persistence | Persist human request intake and resolved intent evidence | S1 |
| Workflow invocation persistence | Persist selected workflow, rejected candidates, rationale, and fail-closed status | S2 |

Out of scope for this mapping tranche:

- approval persistence
- authorization persistence
- mutation persistence
- validation persistence
- full replay package generation
- review-board decision generation

## 3. Runtime Mapping

### 3.1 Evidence Root Creation

Requirement:

```text
Evidence root creation
```

Recommended implementation module:

```text
aigol/runtime/acli_evidence_continuity_p0.py
```

Candidate supporting modules:

- `aigol/runtime/transport/serialization.py`
- `aigol/runtime/replay_certification_runtime.py`
- `aigol/runtime/unified_replay_reconstruction_runtime.py`

Producer:

```text
ACLI evidence continuity P0 runtime
```

Consumer:

```text
HIRR evidence writer
Workflow invocation evidence writer
Future approval, authorization, validation, replay, and review writers
```

Persistence location:

```text
runtime/acli_executable_certification_campaign_v1/EXEC-001/scenarios/AEC-001/
```

Required subdirectories:

- `intent/`
- `workflow/`
- `context/`
- `approval/`
- `authorization/`
- `mutation/`
- `validation/`
- `replay/`
- `review/`

Replay linkage point:

```text
manifest.json
```

The manifest becomes the initial replay-visible anchor for all later lifecycle artifacts.

### 3.2 HIRR Evidence Persistence

Requirement:

```text
HIRR evidence persistence
```

Recommended implementation module:

```text
aigol/runtime/acli_evidence_continuity_p0.py
```

Candidate producer/reference modules:

- `aigol/runtime/human_intent_clarification_intake_runtime.py`
- `aigol/runtime/human_intent_clarification_certification_v1.py`
- `aigol/runtime/intent_classifier.py`
- `sapianta_bridge/nl_envelope/intent_classifier.py`

Producer:

```text
HIRR capture function in ACLI evidence continuity P0 runtime
```

Consumer:

```text
Workflow invocation evidence writer
Future replay package generator
Future evidence completeness matrix
```

Persistence location:

```text
runtime/acli_executable_certification_campaign_v1/EXEC-001/scenarios/AEC-001/intent/hirr_intent_resolution.json
```

Replay linkage point:

```text
HIRR artifact hash or path recorded in evidence root manifest and workflow invocation artifact
```

Mapping rule:

Existing intent and clarification runtimes may provide classification semantics, but the AEC-001 certification path still needs a persisted HIRR evidence artifact with execution id, scenario id, resolved intent, ambiguity status, and fail-closed state.

### 3.3 Workflow Invocation Persistence

Requirement:

```text
Workflow invocation persistence
```

Recommended implementation module:

```text
aigol/runtime/acli_evidence_continuity_p0.py
```

Candidate reference artifacts:

- `docs/governance/ACLI_WORKFLOW_INVOCATION_RUNTIME_V1.md`
- `docs/governance/ACLI_CERTIFICATION_SCENARIO_001_V1.md`
- `docs/governance/ACLI_EVIDENCE_CONTINUITY_IMPLEMENTATION_BACKLOG_V1.md`

Producer:

```text
Workflow invocation capture function in ACLI evidence continuity P0 runtime
```

Consumer:

```text
Repository context evidence writer
Future approval proposal generator
Future replay package generator
Future scenario review artifact
```

Persistence locations:

```text
runtime/acli_executable_certification_campaign_v1/EXEC-001/scenarios/AEC-001/workflow/workflow_invocation_decision.json
runtime/acli_executable_certification_campaign_v1/EXEC-001/scenarios/AEC-001/workflow/workflow_candidate_selection.json
```

Replay linkage point:

```text
Workflow artifact references HIRR artifact and is referenced by later context, approval, replay, and review artifacts.
```

Mapping rule:

Workflow invocation must be deterministic and persisted before any mutation-relevant stage. For AEC-001 the expected selected workflow is:

```text
GOVERNANCE_ARTIFACT_CREATION
```

No-match or multi-match states must produce fail-closed evidence.

## 4. Evidence Flow Mapping

Canonical evidence flow:

```text
Intent
-> HIRR
-> Workflow
-> Approval
-> Validation
-> Replay
```

Mapped runtime locations:

| Flow stage | Current candidate runtime location | P0 mapping status | Notes |
| --- | --- | --- | --- |
| Intent | `aigol/runtime/intent_classifier.py`, `aigol/runtime/human_intent_clarification_intake_runtime.py` | PARTIAL | Existing classifiers can inform HIRR evidence but do not by themselves emit AEC-001 evidence package artifacts |
| HIRR | `aigol/runtime/human_intent_clarification_intake_runtime.py`, new `aigol/runtime/acli_evidence_continuity_p0.py` | MAPPED | New continuity runtime should persist certification-specific HIRR evidence |
| Workflow | new `aigol/runtime/acli_evidence_continuity_p0.py` | MAPPED | No current certification-specific workflow evidence writer was identified for AEC-001 |
| Approval | `aigol/runtime/proposal_approval_runtime.py`, `aigol/runtime/approval/*`, `aigol/cli/commands/approval.py` | FUTURE_MAPPING_REQUIRED | Out of P0 tranche, but candidate components exist |
| Authorization | `aigol/runtime/execution_authorization_runtime.py`, `aigol/authorization/*` | FUTURE_MAPPING_REQUIRED | Out of P0 tranche, but candidate components exist |
| Validation | future AEC-001 validation binding, `git diff --check` execution harness | FUTURE_MAPPING_REQUIRED | Out of P0 tranche |
| Replay | `aigol/runtime/replay_certification_runtime.py`, `aigol/runtime/unified_replay_reconstruction_runtime.py`, `aigol/cli/commands/replay.py` | PARTIAL | Existing replay runtimes provide patterns; P0 only prepares replay linkage |

Flow implication:

The smallest safe implementation is a narrow P0 continuity runtime that writes certification-specific evidence while preserving existing runtimes as sources, validators, or later integration points.

## 5. Gap Mapping

Missing runtime components for P0:

| Gap | Missing runtime component | Required closure |
| --- | --- | --- |
| Evidence root not emitted | AEC-001 evidence root builder | Create root, directories, and manifest |
| HIRR evidence not persisted | Certification HIRR evidence writer | Write HIRR artifact under `intent/` |
| Workflow evidence not persisted | Certification workflow invocation writer | Write workflow decision and candidate selection artifacts |
| HIRR-to-workflow trace absent | Evidence linkage validation | Workflow artifact must reference HIRR artifact |
| Fail-closed path not persisted | Negative evidence writer | Missing or ambiguous evidence must be recorded |

Not mapped as P0 implementation gaps:

- approval persistence
- authorization persistence
- validation binding
- replay package generator
- review-board decision artifact

Those are later sequence stages.

## 6. Implementation Boundaries

Smallest implementation footprint:

```text
aigol/runtime/acli_evidence_continuity_p0.py
tests/test_acli_evidence_continuity_p0.py
```

Allowed implementation behavior:

- create evidence root
- create deterministic JSON evidence artifacts
- compute artifact hashes using existing serialization/hash helpers where applicable
- persist HIRR evidence
- persist workflow invocation evidence
- persist fail-closed evidence for missing or ambiguous inputs
- expose pure functions suitable for tests

Forbidden implementation behavior:

- redesign HIRR
- redesign workflow invocation governance
- mutate approval or authorization runtimes
- perform repository mutation
- run validation as a certification claim
- generate full replay certification
- claim AEC-001 rerun readiness
- claim `ACLI_GOVERNED_DEVELOPMENT_READY`

Integration posture:

```text
Add a narrow evidence continuity harness first.
Integrate with broader ACLI runtime only after P0 evidence persistence is verified.
```

## 7. Verification Strategy

Runtime modifications should be verified with:

```bash
python -m pytest tests/test_acli_evidence_continuity_p0.py
git diff --check
```

Required positive verification:

- evidence root is created
- manifest is persisted
- HIRR artifact is persisted
- workflow invocation artifact is persisted
- workflow candidate selection artifact is persisted
- workflow artifact references HIRR artifact
- selected AEC-001 workflow is `GOVERNANCE_ARTIFACT_CREATION`

Required negative verification:

- missing evidence root fails closed
- unresolved HIRR ambiguity fails closed
- missing HIRR artifact blocks workflow invocation evidence
- no workflow match fails closed
- multiple workflow matches fail closed or requires clarification
- P0 runtime does not emit readiness claim

Expected test artifact coverage:

- positive AEC-001 P0 fixture
- missing HIRR fixture
- ambiguous workflow fixture
- no-match workflow fixture
- manifest/path integrity fixture

## 8. Re-Execution Impact

After this runtime mapping is implemented, AEC-001 status should become:

```text
AEC_001_RE_EXECUTION_PROGRESS_INCREASED
```

but remain:

```text
AEC_001_RE_EXECUTION_READY_NOT_CLAIMED
```

Reason:

P0 mapping covers only evidence root, HIRR evidence, and workflow invocation evidence. AEC-001 rerun readiness still requires later implementation of:

- repository context persistence
- approval persistence
- authorization persistence
- mutation and validation evidence
- replay package generation
- review evidence generation

## 9. Final Verdict

Final runtime mapping verdict:

```text
RUNTIME_MAPPING_READY
```

Rationale:

P0 evidence continuity requirements have been mapped to existing runtime surfaces and a smallest-footprint implementation target. The mapping identifies producers, consumers, persistence locations, replay linkage points, missing components, implementation boundaries, and verification requirements.

Readiness boundary:

```text
ACLI_GOVERNED_DEVELOPMENT_READY_NOT_CLAIMED
AEC_001_RE_EXECUTION_READY_NOT_CLAIMED
```

Final artifact verdict:

```text
ACLI_EVIDENCE_CONTINUITY_RUNTIME_MAPPING_V1_DEFINED
```
