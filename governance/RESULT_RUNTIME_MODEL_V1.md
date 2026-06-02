# RESULT_RUNTIME_MODEL_V1

## Artifact

```text
RESULT_ARTIFACT_V1
```

## Required Fields

```text
artifact_type
result_runtime_version
result_id
canonical_chain_id
execution_reference
execution_hash
completion_reference
completion_hash
worker_reference
worker_hash
worker_assignment_reference
dispatch_reference
worker_invocation_reference
execution_request_reference
worker_output_reference
worker_output_hash
result_status
result_payload
result_payload_hash
captured_by
captured_at
replay_reference
replay_visible
artifact_hash
```

## Valid Result Status

```text
RESULT_CAPTURED
FAILED_CLOSED
```

## Required False Authority Flags

```text
provider_authority = false
governance_authority = false
worker_authority = false
worker_self_certified = false
result_quality_evaluated = false
result_certified = false
failure_analysis_performed = false
governance_mutated = false
replay_mutated = false
execution_history_modified = false
```

## Creation Preconditions

Result capture requires:

- valid `EXECUTION_ARTIFACT_V1`;
- valid `COMPLETION_ARTIFACT_V1`;
- valid worker output evidence;
- matching worker identity;
- matching execution request reference;
- matching worker assignment reference;
- matching dispatch reference;
- matching worker invocation reference;
- canonical chain continuity;
- replay-visible output evidence.

## Worker Output Model

Worker output may be:

- embedded deterministic JSON payload;
- reference to a replay-visible worker output artifact;
- hash-bound externalized JSON artifact inside a governed result-output boundary.

Worker output may not be:

- mutable filesystem path without hash;
- provider-only text without AiGOL capture;
- hidden process stdout;
- unbounded binary payload;
- governance mutation;
- certification decision.

## Result Payload Requirements

The result payload must be:

- deterministic;
- JSON-serializable;
- hash-bound;
- chain-bound;
- authority-free;
- replay-visible.

## Replay Events

Future Result Runtime should persist:

```text
000_result_captured.json
001_result_returned.json
```

Replay reconstruction should return:

```text
result_id
canonical_chain_id
result_status
worker_reference
execution_reference
completion_reference
worker_output_hash
result_payload_hash
captured_at
replay_hash
```

## Non-Goals

`RESULT_ARTIFACT_V1` does not encode:

- quality score;
- correctness judgment;
- compliance certification;
- failure cause;
- remediation proposal;
- worker self-assessment;
- provider judgment;
- governance decision.
