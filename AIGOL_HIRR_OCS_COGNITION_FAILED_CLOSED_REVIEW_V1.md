# AIGOL_HIRR_OCS_COGNITION_FAILED_CLOSED_REVIEW_V1

Status: audit and repair design.

## Objective

Review the remaining failed-closed case from the HIRR workflow target refinement dogfood rerun.

Scope is limited to the downstream `OCS_LLM_COGNITION` path. This does not introduce new governance layers and does not change HIRR target refinement.

## 1. Full Replay Reconstruction

Evidence root:

```text
/tmp/aigol_hirr_workflow_target_refinement_v1/REAL-HIRR-009/runtime/REAL-HIRR-009/TURN-000001
```

Human prompt:

```text
What should be the first step for safer Product 1 decision review?
```

Top-level replay reconstruction:

```text
conversational_cli_routing:
  workflow_id = OCS_LLM_COGNITION
  routing_status = WORKFLOW_SELECTED
  provider_invoked = false
  worker_invoked = false
  execution_requested = false
  replay_artifact_count = 3

universal_intake:
  intake_classification = OCS_COGNITION_INTAKE
  cognition_required = true
  provider_necessity = PROVIDER_REQUIRED_FOR_COGNITION
  source_workflow_id = OCS_LLM_COGNITION
  provider_invoked = false
  worker_invoked = false

ocs_context:
  context_status = OCS_CONTEXT_ASSEMBLED
  accepted_input_count = 3
  rejected_input_count = 0
  provider_invoked = false
  worker_invoked = false

multi_provider_cognition:
  provider_count = 1
  successful_provider_count = 0
  failed_provider_count = 1
  bundle_status = COMPLETED
  failure_isolated = true
  cognition_artifact_hashes = []

cognition_comparison:
  comparison_status = FAILED_CLOSED
  source_cognition_artifacts = []
  comparison_confidence = UNKNOWN
  failure_reason = at least two cognition artifacts are required for comparison

ocs_llm_cognition_end_to_end:
  workflow_status = FAILED_CLOSED
  failure_reason = cognition comparison failed closed: at least two cognition artifacts are required for comparison
  provider_count = 0
  successful_provider_count = 0
  failed_provider_count = 0
```

Replay files present:

```text
conversational_cli_routing/000_conversational_routing_decision_recorded.json
conversational_cli_routing/001_conversational_workflow_selection_recorded.json
conversational_cli_routing/002_conversational_routing_returned.json
universal_intake/000_universal_intake_recorded.json
ocs_llm_cognition_end_to_end/stages/context/000_ocs_context_assembly_recorded.json
ocs_llm_cognition_end_to_end/stages/context/001_ocs_context_assembly_returned.json
ocs_llm_cognition_end_to_end/stages/multi_provider_cognition/000_multi_provider_cognition_request_bundle.json
ocs_llm_cognition_end_to_end/stages/multi_provider_cognition/001_multi_provider_cognition_result_bundle.json
ocs_llm_cognition_end_to_end/stages/cognition_comparison/000_cognition_comparison_artifact.json
ocs_llm_cognition_end_to_end/stages/cognition_comparison/001_cognition_comparison_returned.json
ocs_llm_cognition_end_to_end/000_ocs_llm_cognition_end_to_end_artifact.json
ocs_llm_cognition_end_to_end/001_ocs_llm_cognition_end_to_end_returned.json
```

Provider attachment evidence also exists:

```text
ocs_llm_cognition_end_to_end/real_openai_provider_attachment/openai/000_provider_proposal_created.json
ocs_llm_cognition_end_to_end/real_openai_provider_attachment/openai/001_provider_proposal_returned.json
```

## 2. Failure Point Identification

The request reached the correct workflow:

```text
OCS_LLM_COGNITION
```

The first hard failure that terminates the OCS path is:

```text
COGNITION_COMPARISON_RUNTIME
-> create_cognition_comparison_artifact(...)
-> len(cognition_artifacts) < 2
-> FailClosedRuntimeError("at least two cognition artifacts are required for comparison")
```

However, the causal failure is earlier:

```text
MULTI_PROVIDER_COGNITION
-> provider_count = 1
-> successful_provider_count = 0
-> failed_provider_count = 1
-> cognition_artifact_hashes = []
```

The comparison runtime is behaving correctly for its contract. The OCS end-to-end runtime should not treat an empty cognition bundle as comparison-ready.

## 3. Expected vs Actual Cognition Workflow

Expected OCS workflow for advisory cognition:

```text
Routing
-> Universal Intake: OCS_COGNITION_INTAKE
-> OCS Context Assembly
-> Provider Cognition Request
-> At least one successful cognition artifact
-> Single-provider primary cognition result OR multi-provider comparison
-> OCS continuity / clarification
-> Human-facing non-authoritative cognition result
```

Actual workflow:

```text
Routing
-> Universal Intake: OCS_COGNITION_INTAKE
-> OCS Context Assembly: SUCCESS
-> Provider Cognition Request: prepared
-> OpenAI provider unavailable
-> Multi-provider bundle: COMPLETED with 0 successes and 1 isolated failure
-> Comparison runtime invoked with 0 cognition artifacts
-> FAILED_CLOSED
```

Expected behavior for zero successful providers:

```text
Provider availability failure
-> replay-visible OCS provider-unavailable outcome
-> no cognition comparison attempt
-> human-facing failure explanation
-> allowed_next_step = HUMAN_REVIEW_OF_PROVIDER_UNAVAILABILITY
```

## 4. Provider Interaction Analysis

Provider request:

```text
provider_id = openai
provider_role = COGNITION_PROVIDER
provider_count = 1
request_artifact = LLM_COGNITION_PROVIDER_REQUEST_ARTIFACT_V1
```

Provider attachment failure:

```text
event_type = FAILED_CLOSED
failure_reason = OpenAI provider unavailable
failure_stage = openai_http_request
exception_type = URLError
transport_failure_category = URL_ERROR
provider_invoked = false
execution_capable = false
```

Multi-provider cognition normalized this as:

```text
PROVIDER_COGNITION_FAILURE_ARTIFACT_V1
failed_stage = PROVIDER_COGNITION_PROCESSING
failure_reason = provider cognition processing failed closed
provider_status = FAILED_CLOSED
failure_isolated = true
```

Provider output did not become a cognition artifact. No provider response, usage artifact, or cognition hash was produced.

## 5. Comparison / Runtime Analysis

The comparison runtime requires at least two cognition artifacts:

```text
if len(artifacts) < 2:
    raise FailClosedRuntimeError("at least two cognition artifacts are required for comparison")
```

This is correct for normal comparison.

The end-to-end OCS runtime already supports:

```text
single_provider_primary_mode
```

but only when:

```text
len(result_bundle["provider_results"]) == 1
```

That does not apply here because:

```text
provider_results = []
successful_provider_count = 0
```

Current gap:

```text
OCS end-to-end does not branch on zero successful cognition artifacts before invoking comparison.
```

Replay gap:

```text
_failed_end_to_end_artifact(...) loses available stage counts and hashes.
```

The top-level failed artifact reports provider counts as zero even though the stage replay proves:

```text
provider_count = 1
failed_provider_count = 1
provider_failure_hashes = [ ... ]
```

The reconstruction function also skips stage replay reconstruction when `workflow_status = FAILED_CLOSED`, even when stage replay references exist.

## 6. Minimal Deterministic Repair

Repair location:

```text
aigol/runtime/ocs_llm_cognition_end_to_end_runtime.py
```

Minimal repair:

1. After `_validate_result_bundle(...)`, check `successful_provider_count`.
2. If `successful_provider_count == 0`, do not invoke `run_cognition_comparison_runtime(...)`.
3. Create a replay-visible OCS provider-unavailable outcome artifact using the existing end-to-end artifact type.
4. Preserve stage lineage from context and multi-provider cognition.
5. Return `FAILED_CLOSED` with a precise failure reason:

```text
OCS cognition failed closed: no provider cognition artifacts available
```

6. Preserve human-facing result:

```text
summary = "OCS cognition could not produce advisory output because no cognition provider returned a usable result."
allowed_next_step = HUMAN_REVIEW_OF_PROVIDER_UNAVAILABILITY
provider_failures_visible = true
```

Do not relax comparison semantics. Do not synthesize cognition. Do not treat provider failure as advisory output.

This repair changes the first fail-closed stage from:

```text
COGNITION_COMPARISON_RUNTIME
```

to:

```text
OCS_PROVIDER_COGNITION_AVAILABILITY_GATE
```

## 7. Replay-Visible Evidence Additions

Add an internal end-to-end availability gate artifact or equivalent fields in the existing end-to-end artifact.

Preferred minimal artifact:

```text
OCS_PROVIDER_COGNITION_AVAILABILITY_ARTIFACT_V1
```

Fields:

```text
artifact_type
runtime_version
availability_gate_id
multi_provider_result_bundle_reference
multi_provider_result_bundle_hash
provider_count
successful_provider_count
failed_provider_count
provider_failure_hashes
cognition_artifact_hashes
availability_status
failure_reason
comparison_allowed
selected_next_stage
created_at
provider_invoked = false
worker_invoked = false
authorization_created = false
execution_requested = false
governance_modified = false
replay_modified = false
artifact_hash
```

Replay insertion:

```text
stages/provider_cognition_availability/000_ocs_provider_cognition_availability_recorded.json
```

End-to-end artifact should preserve:

```text
context_artifact_hash
context_hash
multi_provider_result_bundle_hash
multi_provider_result_bundle_result_hash
provider_count
successful_provider_count
failed_provider_count
provider_failure_hashes
cognition_artifact_hashes
availability_gate_artifact_hash
first_failed_stage = OCS_PROVIDER_COGNITION_AVAILABILITY_GATE
comparison_attempted = false
comparison_artifact_hash = null
```

Replay reconstruction should include failed-stage reconstruction:

```text
stage_replay.context
stage_replay.multi_provider_cognition
stage_replay.provider_cognition_availability
stage_replay.cognition_comparison = {}
stage_replay.continuity_and_clarification = {}
```

## 8. Acceptance Criteria

Functional acceptance:

- ACLI routes advisory prompt to `OCS_LLM_COGNITION`.
- Universal Intake records `OCS_COGNITION_INTAKE`.
- Context assembly succeeds.
- Provider request is replay-visible.
- Provider unavailability is replay-visible.
- Zero successful provider results do not invoke comparison.
- OCS returns a clear failed-closed provider-availability outcome.
- No provider output is treated as authoritative.
- No worker is invoked.
- No authorization is created.
- No execution is requested.

Replay acceptance:

- provider availability gate artifact is present;
- end-to-end failed artifact preserves context and multi-provider lineage;
- provider failure hashes are visible at top level;
- reconstruction includes available failed-stage replay;
- comparison replay is absent or not attempted when no cognition artifacts exist;
- returned artifact hash verifies.

Operator acceptance:

- operator sees provider unavailability, not an unrelated comparison-count error;
- allowed next step is human review of provider availability;
- failure remains fail-closed.

## 9. Certification Criteria

Tests:

- OCS end-to-end with all providers unavailable fails at provider availability gate.
- OCS end-to-end with one successful provider and `single_provider_primary_mode=True` still completes.
- OCS end-to-end with one success and comparison-required mode still fails at comparison count.
- OCS end-to-end with two successes and one failure still completes comparison.
- Failed OCS replay reconstruction includes context and multi-provider stage replay.
- Availability gate artifact rejects authority flags and preserves replay hashes.
- ACLI real-world dogfood prompt `REAL-HIRR-009` reports provider availability failure instead of comparison failure.

Validation commands:

```text
python -m pytest tests/test_ocs_llm_cognition_end_to_end_runtime_v1.py
python -m pytest tests/test_conversational_cli_runtime_v1.py
git diff --check
```

Certification fields:

```text
OCS_TARGET_SELECTION_CORRECT = YES
PROVIDER_FAILURE_IDENTIFIED = YES
FIRST_FAIL_CLOSED_STAGE_BEFORE = COGNITION_COMPARISON_RUNTIME
FIRST_FAIL_CLOSED_STAGE_AFTER = OCS_PROVIDER_COGNITION_AVAILABILITY_GATE
COMPARISON_SKIPPED_WHEN_ZERO_COGNITION_ARTIFACTS = YES
PROVIDER_FAILURE_REPLAY_VISIBLE = YES
FAILED_STAGE_RECONSTRUCTION_SUPPORTED = YES
GOVERNANCE_LAYER_ADDED = NO
FAIL_CLOSED_PRESERVED = YES
```

## 10. Final Fields

```text
FULL_REPLAY_RECONSTRUCTED = YES
FAILURE_POINT_IDENTIFIED = YES
EXPECTED_VS_ACTUAL_DEFINED = YES
PROVIDER_INTERACTION_ANALYZED = YES
COMPARISON_RUNTIME_ANALYZED = YES
MINIMAL_REPAIR_DEFINED = YES
REPLAY_EVIDENCE_ADDITIONS_DEFINED = YES
ACCEPTANCE_CRITERIA_DEFINED = YES
CERTIFICATION_CRITERIA_DEFINED = YES
NEXT_REPAIR = Implement OCS provider cognition availability gate
```
