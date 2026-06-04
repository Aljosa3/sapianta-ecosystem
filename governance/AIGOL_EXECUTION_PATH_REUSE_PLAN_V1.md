# AIGOL_EXECUTION_PATH_REUSE_PLAN_V1

## Status

Review-only reuse plan.

## Reuse Principle

```text
Reuse implementation logic.
Do not reuse authority by implication.
```

Every reused runtime must explicitly bind the new execution authorization,
execution packet, canonical chain, Worker role, and replay lineage before it can
participate in the new path.

## Reuse Plan

| Existing Component | Reuse | Required Adaptation |
| --- | --- | --- |
| Execution authorization runtime | Direct | Treat as the only canonical downstream authority source |
| Authorized Worker request model | Design precedent | Align terminology and fields with `WORKER_INVOCATION_REQUEST_ARTIFACT_V1` |
| Ready-for-dispatch runtime | Adapt | Validate authorization, packet, invocation request, and scope continuity |
| Worker runtime | Adapt | Bind assignment to role, capability, trust, authority, packet, and authorization |
| Dispatch runtime | Adapt | Bind dispatch to the same Worker, invocation request, authorization, and packet |
| Worker invocation runtime | Adapt | Consume invocation request and prove exact parameter/scope continuity |
| Execution and completion runtimes | Adapt | Propagate authorization and packet lineage without claiming result validity |
| Result runtime | Adapt | Separate Worker result evidence from generic result capture |
| Result evaluation runtime | Adapt | Preserve observation-only behavior behind a new result validation boundary |
| Unified replay reconstruction | Extend | Recognize and verify the complete new artifact vocabulary |
| External runtime inspection Worker | Reference | Use as a low-risk Worker identity, result, termination, and replay example |
| Filesystem Worker proof path | Reference | Reuse narrow mutation safeguards only after new authority binding |
| Bounded Codex execution | Reference and adapt | Expose only through explicit hybrid `WORKER_ROLE`, never Provider role |
| Workspace boundary validation | Adapt | Bind containment checks to allowed outputs and forbidden operations |
| Provider result return loop | Pattern reuse | Reuse deterministic binding and hash checks for Worker result validation |
| Governed return interpretation | Pattern reuse | Reuse human-readable result summary patterns after validation |

## Recommended Runtime Sequence

### 1. AIGOL_WORKER_INVOCATION_REQUEST_RUNTIME_V1

Consume replay-valid `EXECUTION_AUTHORIZATION_ARTIFACT_V1` and produce a
non-authoritative `WORKER_INVOCATION_REQUEST_ARTIFACT_V1`.

This runtime must not assign, dispatch, invoke, or execute a Worker.

### 2. Authorization-Aware Readiness And Assignment Upgrade

Upgrade readiness and Worker assignment contracts to consume the invocation
request and verify:

- authorization status and expiry;
- packet, candidate, handoff, and approval lineage;
- requested Worker role and capability;
- allowed outputs and forbidden operations;
- chain and replay continuity.

### 3. Authorization-Bound Dispatch And Invocation Upgrade

Require dispatch and invocation artifacts to carry the same authorization,
packet, request, Worker, role, capability, parameter, and scope hashes.

### 4. Governed Worker Execution Adapter

Introduce one narrowly bounded Worker execution adapter only after invocation
continuity is certified.

The safest first real execution should be a read-only Worker or similarly
bounded validation Worker. A mutation-capable implementation Worker should
follow only after workspace and allowed-output enforcement are certified.

### 5. Worker Result Validation Runtime

Create `WORKER_RESULT_ARTIFACT_V1` and `RESULT_VALIDATION_ARTIFACT_V1` contracts
that verify:

- execution authorization continuity;
- invocation and Worker identity;
- allowed outputs;
- forbidden-operation absence;
- required validations;
- result and evidence hashes;
- explicit termination state.

### 6. Post-Execution Replay Review Runtime

Produce `POST_EXECUTION_REPLAY_REVIEW_ARTIFACT_V1` and fail closed on missing,
corrupt, duplicated, reordered, or inferred evidence.

### 7. End-To-End Dry Run Before Real Execution

Validate the complete chain without Worker execution:

```text
EXECUTION_AUTHORIZED
-> WORKER_INVOCATION_REQUEST
-> WORKER_ASSIGNMENT
-> DISPATCH
-> WORKER_INVOCATION
-> WORKER_RESULT
-> RESULT_VALIDATION
-> POST_EXECUTION_REPLAY_REVIEW
-> TERMINATION
```

Only after this dry run is certified should AiGOL attempt the first real
governed Worker execution.

## First Real Execution Recommendation

Use an existing read-only Worker pattern as the first real execution target.
This maximizes reuse of:

- external Worker identity evidence;
- bounded execution request validation;
- replay-visible Worker result evidence;
- explicit termination;
- fail-closed reconstruction.

Do not begin with a file-writing implementation Worker or Codex implementation
role. Those require additional workspace, artifact-plan, output-scope, and
result-validation guarantees.

## Reuse Answer

First real governed Worker execution can reuse substantial existing runtime
pieces, but it cannot reuse them unchanged. The repository has enough proven
logic to avoid rebuilding the lifecycle from scratch; it does not yet have a
constitutionally continuous path from `EXECUTION_AUTHORIZED` to execution.

