# REPLAY_INSPECTOR_WORKER_MODEL_V1

## Worker Type

```text
REPLAY_INSPECTOR_WORKER_V1
```

## Worker Class

```text
READ_ONLY_REPLAY_INSPECTION_WORKER
```

## Capability

```text
REPLAY_INSPECTION_READ_ONLY
```

## Supported Request Type

```text
CAPABILITY_EXECUTION_REQUEST
```

## Input Model

The execution request payload must provide:

```text
canonical_chain_id
inspection_scope
replay_references
expected_artifact_types
max_artifact_count
created_by
created_at
```

`inspection_scope` must be one of:

```text
CHAIN_SUMMARY
ARTIFACT_VALIDATION
REFERENCE_CONTINUITY
RECENT_ACTIVITY_SUMMARY
```

## Allowed Replay Reference Types

Allowed reference categories:

```text
SOURCE_ROUTER_REPLAY
PROMPT_REPLAY
PROPOSAL_REPLAY
APPROVAL_REPLAY
EXECUTION_REQUEST_REPLAY
READY_FOR_DISPATCH_REPLAY
WORKER_REGISTRATION_REPLAY
WORKER_ASSIGNMENT_REPLAY
DISPATCH_REPLAY
WORKER_INVOCATION_REPLAY
EXECUTION_REPLAY
COMPLETION_REPLAY
```

## Output Model

The worker output must be deterministic JSON with:

```text
artifact_type = REPLAY_INSPECTION_RESULT_V1
worker_type = REPLAY_INSPECTOR_WORKER_V1
worker_id
inspection_id
canonical_chain_id
inspection_scope
inspection_status
inspected_replay_references
artifact_count
artifact_types
chain_continuity_status
missing_references
corrupt_references
authority_leak_detected
mutation_detected
provider_authority = false
governance_authority = false
worker_authority = false
mutation_performed = false
failure_reason
created_at
artifact_hash
```

## Status Values

```text
INSPECTION_COMPLETED
FAILED_CLOSED
```

## Chain Continuity Values

```text
CONTINUOUS
BROKEN
NOT_EVALUATED
```

## Authority Fields

The output must always assert:

```text
provider_authority = false
governance_authority = false
worker_authority = false
mutation_performed = false
```

Any attempt to set these differently is invalid and must fail closed.

## Non-Result Classification

The worker output is not:

- approval;
- certification;
- result quality assessment;
- governance decision;
- replay repair;
- failure analysis;
- execution completion.

It is an inspection observation that future result runtime may persist.
