# REPLAY_INSPECTOR_WORKER_FOUNDATION_V1

REPLAY_INSPECTOR_WORKER_FOUNDATION_STATUS = READY

## Purpose

Define `REPLAY_INSPECTOR_WORKER_V1` as AiGOL's first real worker candidate.

This is foundation review only. It does not implement a worker, dispatch adapter, execution body, result runtime, mutation path, or provider authority.

## Context

AiGOL now has replay-visible lifecycle coverage from proposal through completion:

```text
Proposal
-> Approval
-> Execution Request
-> Ready For Dispatch
-> Worker Assignment
-> Dispatch
-> Invocation
-> Execution
-> Completion
```

The first real worker should be read-only, deterministic, low-risk, and useful for validating replay continuity.

## Worker Definition

`REPLAY_INSPECTOR_WORKER_V1` is a bounded read-only worker that inspects approved replay artifacts and produces a deterministic inspection summary.

It may read replay evidence.

It may not modify replay evidence.

It may not create governance decisions.

It may not approve, dispatch, invoke, execute, complete, certify, repair, or mutate any lifecycle artifact.

## 1. Replay Artifacts The Worker May Read

The worker may read replay artifacts that are explicitly referenced by its execution request, invocation parameters, or canonical chain id.

Allowed read scope:

- proposal runtime replay artifacts;
- proposal approval replay artifacts;
- execution request replay artifacts;
- ready-for-dispatch replay artifacts;
- worker registration replay artifacts;
- worker assignment replay artifacts;
- dispatch replay artifacts;
- worker invocation replay artifacts;
- execution runtime replay artifacts;
- completion runtime replay artifacts;
- source-of-truth router replay artifacts, if referenced;
- conversational prompt replay artifacts, if referenced.

The worker may read only immutable artifact files or their replay wrappers. It may not scan unrelated filesystem paths unless a future execution request explicitly authorizes a bounded replay root.

## 2. What The Worker Must Never Modify

The worker must never modify:

- replay artifacts;
- governance artifacts;
- proposal artifacts;
- approval artifacts;
- execution request artifacts;
- readiness artifacts;
- worker artifacts;
- dispatch artifacts;
- invocation artifacts;
- execution artifacts;
- completion artifacts;
- provider artifacts;
- source-of-truth router artifacts;
- prompt replay artifacts;
- runtime source files;
- repository governance files;
- working tree files outside a future explicitly declared output location.

The worker must not repair corrupt replay. Corruption must produce fail-closed output.

## 3. Worker Output

The worker produces a deterministic read-only inspection summary.

Minimum output fields:

```text
worker_id
worker_type
canonical_chain_id
inspection_id
inspected_replay_references
artifact_count
artifact_types
chain_continuity_status
missing_references
corrupt_references
authority_leak_detected
mutation_detected
inspection_status
failure_reason
created_at
```

Allowed `inspection_status` values:

```text
INSPECTION_COMPLETED
FAILED_CLOSED
```

This output is an observation artifact only. It is not result certification, governance approval, failure analysis, or mutation authority.

## 4. Worker Identity Verification

The worker identity must be verified through the existing worker lifecycle:

- registered worker artifact exists;
- worker id matches the assignment artifact;
- worker type is `REPLAY_INSPECTOR_WORKER_V1`;
- declared capability includes replay inspection;
- assigned request type is supported;
- assignment, dispatch, invocation, execution, and completion chain references are continuous;
- canonical chain id matches all applicable lifecycle artifacts;
- worker cannot self-assign, self-dispatch, self-invoke, self-start, or self-complete.

## 5. Replay Integrity Preservation

Replay integrity is preserved by:

- read-only access;
- no writes to replay roots;
- no artifact repair;
- no hash recalculation that replaces existing evidence;
- no replay wrapper mutation;
- explicit input reference lists;
- deterministic output;
- fail-closed behavior on missing or corrupt references.

The worker may compute hashes for inspection, but computed hashes are observations only. They do not mutate or repair replay.

## 6. Fail-Closed Behavior

The worker fails closed when:

- referenced replay is missing;
- referenced replay is corrupt;
- artifact hash validation fails;
- wrapper hash validation fails;
- chain references diverge;
- canonical chain id is absent or mismatched;
- worker identity does not match assignment;
- unauthorized path access is requested;
- mutation is attempted;
- provider authority is implied;
- output cannot be serialized deterministically.

Fail-closed output must preserve:

```text
inspection_status = FAILED_CLOSED
mutation_performed = false
provider_authority = false
governance_authority = false
```

## 7. Lifecycle Integration

`REPLAY_INSPECTOR_WORKER_V1` integrates with the existing worker lifecycle as a normal worker:

```text
Proposal
-> Approval
-> Execution Request
-> Ready For Dispatch
-> Worker Assignment
-> Dispatch
-> Invocation
-> Execution
-> Completion
```

The execution request payload must identify the replay references to inspect and must bind the inspection to a canonical chain id.

Completion records that the inspection operation completed. Completion does not certify the inspection result. A future result runtime may persist and classify inspection output separately.

## Constitutional Preservation

`REPLAY_INSPECTOR_WORKER_V1` preserves:

```text
LLM proposes
AiGOL governs
Worker executes
Replay records
```

Mapping:

- LLM proposes: provider evidence may exist upstream only and has no worker authority;
- AiGOL governs: AiGOL approves, validates, assigns, dispatches, invokes, starts, and completes the worker lifecycle;
- Worker executes: the worker performs bounded read-only inspection;
- Replay records: replay records lifecycle evidence and future inspection output evidence.

## Decision

`REPLAY_INSPECTOR_WORKER_V1` is suitable as the first real worker foundation because it is:

- read-only;
- local;
- deterministic;
- replay-native;
- low-risk;
- directly useful for validating lifecycle continuity;
- compatible with existing worker lifecycle boundaries.

Final classification:

```text
REPLAY_INSPECTOR_WORKER_FOUNDATION_STATUS = READY
```
