# IMPROVEMENT_IMPLEMENTATION_BOUNDARY_GUARANTEES_V1

## Scope

This artifact defines boundary guarantees for future Improvement Implementation Planning Runtime.

It does not implement runtime behavior.

## Planning Boundary

Implementation planning may create a bounded plan from an approved improvement.

It may not create execution requests, implement code, modify configuration, dispatch workers, invoke workers, execute tasks, perform reflection, perform self-modification, or apply self-improvement.

## Creator Boundary

Only AiGOL may create `IMPROVEMENT_IMPLEMENTATION_PLAN_ARTIFACT_V1`.

Humans may authorize the improvement through prior approval. Providers and workers may contribute bounded planning evidence only when recorded as non-authoritative context.

## Approval Boundary

Implementation planning requires valid approval evidence.

Planning must fail closed if:

- approval evidence is missing;
- approval hash is corrupt;
- approval decision is not `APPROVED`;
- approval status is not `APPROVED`;
- human authorization reference is missing;
- review, proposal, evaluation, or result references mismatch;
- canonical chain continuity fails;
- approval contains performed implementation or execution request creation.

## Execution Request Boundary

Implementation planning is not execution request creation.

It must preserve:

```text
execution_request_created = false
execution_request_reference = null
```

Any future execution request must be created by a separate governed runtime boundary.

## Implementation Boundary

Implementation planning is not implementation.

It must preserve:

```text
implementation_performed = false
code_mutated = false
configuration_mutated = false
self_modification_performed = false
self_improvement_performed = false
```

Actual code change must occur only through future governed execution and replay evidence.

## Governance Mutation Boundary

Implementation planning may not mutate governance.

It may not:

- rewrite governance artifacts;
- alter constitutional rules;
- modify approval, review, proposal, evaluation, result, execution, or completion artifacts;
- repair replay;
- silently alter planning semantics;
- create self-modifying governance paths.

## Provider Boundary

Providers may contribute non-authoritative plan text only when explicitly selected by AiGOL.

Providers may not:

- create implementation plan artifacts;
- create execution requests;
- authorize implementation;
- mutate code;
- dispatch or invoke workers;
- mutate governance;
- mutate replay;
- apply self-improvement.

## Worker Boundary

Workers may provide reports or read-only planning evidence.

Workers may not:

- create implementation plan artifacts;
- create execution requests;
- implement improvements without governed execution;
- mutate runtime state;
- mutate governance;
- mutate replay.

## Replay Boundary

Implementation planning replay must be append-only and reconstructable.

Planning must fail closed if:

- approval replay is unavailable;
- approval hash mismatches;
- review hash mismatches;
- proposal hash mismatches;
- evaluation hash mismatches;
- result hash mismatches;
- replay wrappers are corrupt;
- canonical chain id mismatches.

Replay may reconstruct planning history. Replay may not infer approval, create execution requests, or apply code changes.

## Chain Boundary

Implementation planning must preserve canonical chain continuity across:

- improvement approval;
- improvement review;
- improvement proposal;
- evaluation;
- result;
- execution;
- completion;
- worker identity;
- implementation plan artifact;
- replay event.

Missing or conflicting chain identity is fail-closed.

## Constitutional Boundary

Improvement Implementation Planning preserves:

```text
LLM proposes
AiGOL governs
Worker executes
Replay records
```

Mapping:

- LLM proposes: provider assistance may contribute plan text but remains non-authoritative;
- AiGOL governs: AiGOL validates approved evidence and records the planning boundary;
- Worker executes: worker output remains upstream evidence, not planning or implementation authority;
- Replay records: replay records plan evidence without execution request creation or mutation.
