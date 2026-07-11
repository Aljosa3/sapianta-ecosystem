# G18-09 Deterministic Root Cause Trace Binding Implementation

## Executive Summary

G18-09 implements the smallest reusable Platform Core binding for deterministic backward root-cause tracing.

The new binding accepts an observed runtime result, projected field, failure reason, artifact reference, replay reference, runtime result, or user-visible result and composes existing replay-backed capabilities to produce a deterministic causal trace.

Implementation:

- `aigol/runtime/platform_core_root_cause_trace.py`
- `trace_platform_core_root_cause(...)`

The binding is read-only. It does not mutate replay, invoke providers, execute workers, create improvement intent, create governance authority, or move diagnostic logic into a Human Interface.

Final verdict: `DETERMINISTIC_ROOT_CAUSE_TRACE_BINDING_IMPLEMENTED`.

## Reused Capabilities

The implementation reuses existing certified foundations instead of creating a parallel replay engine:

- Replay loading and hashing:
  - `aigol.runtime.transport.serialization.load_json`
  - `aigol.runtime.transport.serialization.replay_hash`
- Replay Observation Layer:
  - `aigol.runtime.replay_observation_layer.replay_observation_artifact`
- Runtime projection evidence:
  - `runtime_status_projection_evidence`
  - current-turn replay root evidence from G18-07
- Replay certification evidence:
  - existing replay certification artifact shape and expected replay location
- Governance evidence:
  - execution authorization artifacts
  - source router artifacts
- Originating request evidence:
  - multiline prompt capture artifacts
  - universal intake artifacts
  - source router prompt references
- Capability registry:
  - `DETERMINISTIC_ROOT_CAUSE_TRACE_BINDING`
  - owner: `PLATFORM_CORE_REPLAY`
  - implementation owner: `aigol.runtime.platform_core_root_cause_trace`

No observation, reconstruction, governance, Provider, Worker, or Human Interface subsystem was duplicated.

## Platform Core Ownership

The binding belongs to Platform Core.

The service returns:

- `platform_core_authority = true`
- `human_interface_authority = false`
- `human_interface_owns_replay_traversal = false`
- `provider_invoked = false`
- `worker_invoked = false`
- `governance_modified = false`
- `replay_modified = false`
- `improvement_intent_created = false`

Human Interfaces may later render this result, but they do not own trace logic, replay traversal, governance interpretation, runtime-stage resolution, or root-cause classification.

## Trace Input Contract

`trace_platform_core_root_cause(...)` accepts:

- `observed_field`;
- `observed_value`;
- `failure_reason`;
- `artifact_reference`;
- `replay_reference`;
- `runtime_result`;
- `user_visible_result`;
- `created_at`.

The service can start from:

- a runtime status;
- a projected Boolean field;
- a failure reason;
- an artifact reference;
- a replay reference;
- a user-visible result.

If no observed result or replay source can be resolved, the service returns `ROOT_CAUSE_TRACE_FAILED_CLOSED`.

## Backward Traversal Model

The trace walks backward through:

```text
Observed Result
-> Source Projection or Producing Artifact
-> Runtime Stage
-> Governance Decision
-> Originating Request
```

The implementation resolves:

- the replay root from replay, artifact, runtime result, or user-visible result references;
- all JSON replay sources beneath the replay root;
- a primary source artifact or projection;
- a runtime stage using Replay Observation Layer classification when possible;
- governance evidence from authorization and source-router replay;
- originating request evidence from prompt capture, universal intake, or source-router replay;
- causal predecessors for relevant projected fields;
- missing and contradictory evidence.

## Evidence Resolution

The returned trace includes:

- `observed_result`;
- `replay_reference`;
- `producing_component`;
- `source_artifact`;
- `source_projection`;
- `runtime_stage`;
- `governance_decision`;
- `originating_request`;
- `causal_predecessors`;
- `replay_sources_inspected`;
- `replay_source_count`;
- `missing_evidence`;
- `contradictory_evidence`;
- `root_cause_explanation`;
- `trace_hash`.

Source artifacts include replay path, event type, replay index, replay step, replay hash, artifact type, artifact hash, runtime version, status, and failure reason.

Runtime stage metadata is derived through `replay_observation_artifact(...)` where possible and falls back to deterministic artifact/path classification when an artifact family is outside the observation layer's current recognizer surface.

## Missing Evidence Handling

Missing evidence is explicit and fail-closed.

For `replay_certification_reached = false`, the trace checks the expected current-turn certification artifact:

```text
governed_bridge_certified_development_continuation/
  worker_lifecycle_continuation/
    replay_certification/
      000_replay_certification_artifact_recorded.json
```

If absent, the trace records:

- expected path;
- missing status;
- whether certification was attempted;
- whether runtime projection evidence was supplied;
- nearest causal predecessors.

If the replay root itself cannot be resolved, the trace returns `ROOT_CAUSE_TRACE_FAILED_CLOSED`.

## Initial TURN-000024 Validation

Initial validation target:

```text
.runtime/aicli/AICLI-REFERENCE-SESSION/TURN-000024
```

Observed result:

```text
replay_certification_reached = false
```

The trace determines:

- producing component: `HUMAN_INTERFACE_RUNTIME_STATUS_PROJECTION`;
- replay certification attempted: `false`;
- replay certification artifact exists: `false`;
- replay certification status: `REPLAY_CERTIFICATION_NOT_REACHED`;
- missing evidence: replay certification artifact absent from the current turn replay tree;
- causal predecessor: `UNIVERSAL_PROVIDER_WORKER_RESULT_ARTIFACT_V1`;
- predecessor status: `FAILED_CLOSED`;
- predecessor failure reason: `OpenAI provider unavailable`.

The trace does not speculate beyond replay evidence. It reports that no completed replay certification artifact exists and identifies the nearest replay-backed predecessor result.

## Human Interface Boundary

No `./aicli` command or Human Interface diagnostic logic was added.

The new service is reusable by future renderers such as:

- `/trace replay_certification_reached`;
- `/explain last-result`;
- Web;
- REST;
- Mobile;
- Voice;
- future autonomous services.

Those renderers remain adapters over the Platform Core trace result.

## Validation Results

Focused tests added:

```text
tests/test_g18_09_platform_core_root_cause_trace.py
```

Coverage:

- trace from projected Boolean result;
- trace from failure reason;
- trace from replay reference;
- missing evidence fail-closed behavior;
- TURN-000024 replay certification trace;
- Human Interface neutrality;
- Platform Core capability registry visibility.

Focused validation:

```bash
python -m pytest tests/test_g18_09_platform_core_root_cause_trace.py
```

Result:

```text
6 passed
```

Scoped regression validation:

```bash
python -m pytest tests/test_g18_09_platform_core_root_cause_trace.py tests/test_g15_01_replay_observation_layer_v1.py tests/test_replay_certification_runtime_v1.py tests/test_g14_30_canonical_human_interface_runtime_entry_service_v1.py tests/test_replay_backed_operation_explanations_v1.py
```

Result:

```text
31 passed
```

## Architectural Impact Assessment

The implementation preserves existing architecture:

- Platform Core owns trace composition.
- Replay remains the source of truth.
- Replay Observation Layer remains the observation primitive.
- Replay Certification remains unchanged.
- Governance remains unchanged.
- Provider Platform remains unchanged.
- Worker Platform remains unchanged.
- Human Interfaces remain thin adapters.
- Improvement Analysis remains downstream and non-authoritative.

The binding adds a reusable composition point, not a new subsystem.

## Remaining Observations

The service currently includes explicit current-turn handling for `replay_certification_reached = false`, which was the initial validation target.

Other observed fields are supported through generic artifact matching, failure-reason matching, artifact-reference tracing, replay-reference tracing, and runtime projection evidence. Future refinements can add additional field-specific expected-artifact mappings while continuing to reuse the same Platform Core binding.

## Final Verdict

`DETERMINISTIC_ROOT_CAUSE_TRACE_BINDING_IMPLEMENTED`
