# AIGOL_FIRST_REAL_EXECUTION_REUSE_PLAN_V1

## Status

Reuse plan for first real governed Worker execution.

## Classification

```text
AIGOL_FIRST_REAL_EXECUTION_READINESS_STATUS = PARTIAL
```

## Principle

Reuse existing execution infrastructure as substrate, but certify new bindings
where the current execution chain changes artifact contracts or authority
semantics.

## Stage Reuse Plan

| Stage | Reuse Decision | Required Work |
| --- | --- | --- |
| `WORKER_DISPATCHED -> WORKER_INVOKED` | Reuse older invocation pattern and bounded Codex substrate | New current-chain invocation binding |
| `WORKER_INVOKED -> WORKER_RESULT_CAPTURED` | Reuse bounded capture and older result-capture pattern | New Worker result artifact binding |
| `WORKER_RESULT_CAPTURED -> RESULT_VALIDATED` | Reuse result evaluation pattern | New validation runtime with fail-closed scope checks |
| `RESULT_VALIDATED -> POST_EXECUTION_REPLAY_REVIEW` | Reuse unified replay reconstruction framework | Extend artifact vocabulary and produce post-execution review artifact |
| `POST_EXECUTION_REPLAY_REVIEW -> TERMINATED` | Reuse completion and external inspection termination patterns | New governed termination runtime |

## Components To Reuse Unchanged

- deterministic serialization;
- replay hashing;
- append-only replay write semantics;
- bounded execution workspace validation;
- bounded timeout and stdin controls;
- bounded command execution restrictions;
- bounded execution capture model;
- bounded execution evidence model.

## Components To Reuse With Binding

- `aigol/runtime/worker_invocation_runtime.py`;
- `aigol/runtime/execution_runtime.py`;
- `aigol/runtime/completion_runtime.py`;
- `aigol/runtime/result_runtime.py`;
- `aigol/runtime/result_evaluation_runtime.py`;
- `aigol/runtime/unified_replay_reconstruction_runtime.py`;
- `aigol/runtime/external_runtime_inspection_worker.py`;
- `aigol/runtime/governed_return_interpretation.py`.

## New Runtime Milestones

### 1. Current-Chain Worker Invocation Runtime

Input:

- `WORKER_DISPATCH_ARTIFACT_V1`.

Output:

- current-chain `WORKER_INVOCATION_ARTIFACT_V1`.

Required verification:

- dispatch lineage;
- assignment lineage;
- invocation request lineage;
- authorization lineage;
- execution packet lineage;
- Worker identity continuity;
- allowed-output scope;
- forbidden-operation scope;
- replay continuity;
- authority continuity.

### 2. Worker Result Capture Runtime

Input:

- Worker invocation artifact;
- bounded execution capture evidence.

Output:

- `WORKER_RESULT_ARTIFACT_V1`.

Required verification:

- Worker identity continuity;
- execution packet continuity;
- output scope continuity;
- capture hash continuity;
- no provider authority escalation.

### 3. Result Validation Runtime

Input:

- `WORKER_RESULT_ARTIFACT_V1`.

Output:

- `RESULT_VALIDATION_ARTIFACT_V1`.

Required verification:

- result satisfies validation requirements;
- allowed outputs are preserved;
- forbidden operations are absent;
- no approval or governance mutation is created.

### 4. Post-Execution Replay Review Runtime

Input:

- result validation artifact;
- full replay chain.

Output:

- `POST_EXECUTION_REPLAY_REVIEW_ARTIFACT_V1`.

Required verification:

- lineage continuity;
- authority continuity;
- replay continuity;
- hash continuity.

### 5. Governed Termination Runtime

Input:

- post-execution replay review artifact.

Output:

- termination artifact.

Required verification:

- terminal state is deterministic;
- no retry, fallback, background execution, or hidden mutation remains active.

## CLI Before And After

Current CLI after dispatch:

```text
Worker Dispatch
Dispatch Status: WORKER_DISPATCHED
No Worker has been invoked, executed, or produced results.
```

Required CLI after first invocation binding:

```text
Worker Invocation
Invocation Status: WORKER_INVOKED
Execution Status: bounded execution requested or completed according to runtime result
No result is validated until RESULT_VALIDATED is recorded.
```

## Earliest Invocation Point

The earliest valid invocation point is after replay reconstruction verifies
`WORKER_DISPATCHED`.

Invocation must not begin directly from assignment, invocation request, or
authorization. It must be bound to the dispatch artifact.

## Remaining Blockers

- current-chain Worker invocation binding;
- Worker result artifact contract;
- result validation contract;
- post-execution replay review contract;
- governed termination contract;
- unified replay vocabulary update for the new execution chain;
- output-scope enforcement during real bounded execution.
