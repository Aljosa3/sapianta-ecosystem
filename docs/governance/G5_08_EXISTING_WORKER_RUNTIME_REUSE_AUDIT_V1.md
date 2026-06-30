# G5-08 Existing Worker Runtime Reuse Audit V1

Status: reuse audit complete.

Final verdict: WORKER_RUNTIME_REUSE_CONFIRMED

## 1. Purpose

G5-08 audits the existing Worker runtime stack against the certified Generation 5 execution pipeline.

This is a reuse audit only. It does not introduce runtime changes, worker execution inside PGSP, repository mutation, deployment, retry, fallback, approval creation, or authorization creation.

The core finding is:

```text
Existing Worker runtime components already implement the required Worker Services architecture.
PGSP needs governed wiring into those components, not a duplicate Worker runtime.
```

## 2. Reviewed Runtime Inventory

Reviewed Worker and execution-chain components:

| Runtime | Existing Capability | Reuse Assessment |
| --- | --- | --- |
| `aigol/runtime/worker_runtime.py` | Worker registration and legacy assignment identity model. | Reuse for Worker identity and non-authority boundaries. |
| `aigol/runtime/worker_invocation_request_runtime.py` | Creates bounded Worker invocation request from execution authorization. | Reuse as authorization-to-Worker handoff surface. |
| `aigol/runtime/worker_assignment_runtime.py` | Assigns compatible Worker without dispatch or invocation. | Reuse as Worker identity/capability matching surface. |
| `aigol/runtime/worker_dispatch_runtime.py` | Dispatches assigned Worker without invocation or result production. | Reuse as dispatch boundary. |
| `aigol/runtime/worker_invocation_runtime.py` | Invokes dispatched Worker and records invocation evidence. | Reuse as invocation boundary. |
| `aigol/runtime/worker_result_capture_runtime.py` | Captures Worker output with forbidden-output filtering. | Reuse as completion capture surface. |
| `aigol/runtime/worker_result_validation_runtime.py` | Validates captured Worker result. | Reuse as result validation surface. |
| `aigol/runtime/post_execution_replay_review_runtime.py` | Reviews validated execution replay and output realization. | Reuse as post-execution review surface. |
| `aigol/runtime/execution_authorization_runtime.py` | Creates scoped execution authorization with replay reconstruction. | Reuse as authorization input to Worker handoff. |
| `aigol/runtime/ocs_execution_readiness_runtime.py` | Produces execution-ready packet and Worker constraints from OCS handoff. | Reuse as pre-Worker execution packet source. |

## 3. Capability Matrix

| Required G5 Capability | Existing Support | Assessment |
| --- | --- | --- |
| Worker identity model | Worker artifacts include id, type, version, capabilities, supported request types, trust boundary, state, and non-authority flags. | Exists. |
| Worker authorization validation | Worker invocation request reconstructs execution authorization, verifies status, artifact type, revocation, expiration, approval lineage, packet lineage, and authority continuity. | Exists. |
| Worker execution lifecycle | Existing chain separates request, assignment, dispatch, invocation, result capture, result validation, and post-execution review. | Exists. |
| Worker replay model | Each phase writes ordered replay wrappers, artifact hashes, lineage hashes, and reconstruction functions. | Exists. |
| Worker governance model | Runtime boundaries preserve non-authority flags and fail closed on invalid scope, state, lineage, or replay. | Exists. |
| Worker failure handling | Each Worker phase records `FAILED_CLOSED` result artifacts with failure reason. | Exists. |
| Worker completion evidence | Result capture and result validation artifacts record completion evidence and validation status. | Exists. |
| Worker rollback support | Rollback/recovery is represented through replay lineage, failure reasons, recovery guidance patterns, and downstream audit surfaces; executable rollback remains operation-specific. | Partial, but not a blocker for Worker runtime reuse. |
| Post-execution review | Post-execution replay review validates result lineage, output binding, domain bundle, executable bundle, replay continuity, and authority continuity. | Exists. |
| PGSP invocation path | PGSP-specific lifecycle wiring from G5-07 handoff into existing Worker request runtime is not yet implemented. | Wiring required, not new Worker runtime. |

## 4. Reuse Assessment

The existing Worker runtime stack already implements the architectural decomposition required by Generation 5:

```text
Execution Authorization
-> Worker invocation request
-> Worker assignment
-> Worker dispatch
-> Worker invocation
-> Worker result capture
-> Worker result validation
-> Post-execution replay review
```

This decomposition matches the certified G5-07 boundary. It preserves the distinction between:

- authorization;
- handoff/request creation;
- Worker identity matching;
- dispatch;
- invocation;
- output capture;
- validation;
- post-execution review.

Creating a new PGSP-specific Worker runtime would duplicate existing Worker Services and risk violating the certified platform ownership model.

## 5. Ownership Validation

| Concern | Existing Owner | Audit Result |
| --- | --- | --- |
| Session lifecycle | PGSP | PGSP should call Worker Services but not own Worker execution. |
| Execution authorization | Authorization service / Governance | Existing authorization runtime supplies scoped authorization evidence. |
| Worker request package | Worker Services | Existing Worker invocation request runtime owns request creation. |
| Worker identity and assignment | Worker Services | Existing Worker assignment runtime validates capability and compatibility. |
| Worker dispatch | Worker Services / dispatch governance | Existing dispatch runtime owns dispatch boundary. |
| Worker invocation | Worker Services | Existing invocation runtime owns invocation boundary. |
| Result capture | Worker Services / Replay | Existing result capture runtime owns output capture evidence. |
| Result validation | Worker Services / Governance | Existing validation runtime owns result validation evidence. |
| Post-execution review | Replay / Governance | Existing post-execution review runtime owns review reconstruction. |
| Communication | UHCL | Existing render summaries are local; PGSP should add UHCL-facing summaries rather than move ownership to adapters. |

Ownership is compatible with certified Platform Core boundaries.

## 6. Replay Assessment

The existing Worker chain is replay-native.

Existing replay guarantees include:

- ordered replay steps per phase;
- wrapper hash verification;
- artifact hash verification;
- chain id continuity;
- authorization lineage verification;
- approval lineage verification;
- execution packet lineage verification;
- worker assignment lineage verification;
- worker dispatch lineage verification;
- worker invocation lineage verification;
- result capture lineage verification;
- result validation lineage verification;
- post-execution review reconstruction.

PGSP integration should bind to these replay references rather than creating parallel PGSP-local replay schemas for Worker execution.

## 7. Governance Assessment

Existing Worker runtimes already fail closed on:

- missing execution authorization;
- invalid authorization artifact;
- non-authorized authorization status;
- revoked authorization;
- expired authorization;
- reused authorization or duplicate downstream phase;
- missing execution-ready packet;
- packet/candidate/validation lineage mismatch;
- broken approval lineage;
- unsupported worker role;
- incompatible worker capability;
- changed allowed outputs;
- changed forbidden operations;
- changed validation requirements;
- replay corruption.

The existing model preserves:

- no Worker self-authorization;
- no provider authority;
- no approval authority;
- no governance authority;
- no hidden repository mutation in request, assignment, dispatch, or invocation phases;
- explicit result capture and validation before post-execution review.

## 8. Failure Handling

Failure handling already exists across the Worker stack:

- `FAILED_CLOSED` result artifacts;
- failure reason preservation;
- replay-visible failed result records;
- duplicate phase detection;
- corrupted replay rejection;
- invalid lineage rejection;
- missing prerequisite rejection.

PGSP should reuse these failure surfaces and add UHCL recovery summaries for PGSP sessions where needed.

## 9. Completion Evidence

Completion evidence is not a single Worker artifact. It is a chain:

```text
Worker invocation evidence
-> Worker result capture
-> Worker result validation
-> Post-execution replay review
```

This is architecturally preferable because invocation, raw output, validation, and review remain separable and replayable.

PGSP should treat post-execution review as the canonical completion review surface, not invent a separate PGSP completion artifact that duplicates Worker result validation.

## 10. Rollback Assessment

The existing Worker stack supports rollback and recovery indirectly through:

- replay reconstruction;
- chain lineage;
- failure reasons;
- immutable evidence references;
- output binding review;
- post-execution review;
- rollback/recovery guidance in surrounding governance documentation.

Executable rollback remains domain-specific and operation-specific. That is not a Worker runtime reuse blocker, because rollback should be governed by the affected execution domain, mutation model, and output realization type.

PGSP Worker execution should require rollback or recovery guidance before mutating execution classes are enabled.

## 11. Duplication Risk

New Worker runtime components would create high duplication risk if they reimplement:

- Worker identity;
- Worker request creation;
- assignment;
- dispatch;
- invocation;
- result capture;
- result validation;
- post-execution replay review;
- authorization replay validation;
- failure handling.

Allowed additions are limited to:

- PGSP-to-existing-Worker wiring;
- UHCL Worker execution summaries;
- PGSP replay binding artifacts;
- PGSP governance checkpoints over existing Worker runtime outputs;
- domain-specific Worker adapters where a genuinely new worker capability is needed.

## 12. Required Wiring

PGSP Worker execution should wire into the existing stack in this order:

1. Consume G5-07 authorization-to-Worker handoff evidence.
2. Call the existing Worker invocation request runtime.
3. Call existing Worker assignment runtime.
4. Call existing Worker dispatch runtime.
5. Call existing Worker invocation runtime only after dispatch is replay-valid.
6. Call result capture runtime.
7. Call result validation runtime.
8. Call post-execution replay review runtime.
9. Emit UHCL Worker execution summary and recovery guidance.
10. Bind all replay references into PGSP session replay.

No PGSP-local Worker lifecycle should be created.

## 13. Implementation Recommendation

The next implementation batch should implement a PGSP Worker execution orchestration wrapper that composes existing Worker runtimes without changing them.

Recommended scope:

- input: PGSP session id, G5-07 Worker handoff evidence, execution authorization replay reference, created_at;
- orchestration: invoke existing Worker request, assignment, dispatch, invocation, capture, validation, and review runtimes in order;
- output: PGSP Worker execution capture, governance checkpoint, UHCL summary, replay binding;
- validation: targeted PGSP Worker orchestration tests plus full pytest;
- cleanup: generated `.runtime` artifacts.

Required exclusions:

- no duplicate Worker runtime;
- no bypass of existing authorization checks;
- no direct repository mutation outside certified Worker path;
- no provider execution unless separately authorized;
- no retry or fallback;
- no deployment.

## 14. Certification Impact

The existing Worker runtime satisfies the Generation 5 architecture sufficiently for reuse.

Certification impact:

- Worker Services remain reusable Platform Services;
- PGSP remains session/orchestration boundary, not Worker owner;
- Governance remains authority owner;
- Replay remains reconstruction owner;
- UHCL remains communication owner;
- adapters remain renderers and response capture surfaces.

## 15. Final Determination

No new Worker runtime architecture is required before PGSP Worker execution.

The correct next step is governed PGSP wiring over the existing Worker runtime stack.

Final verdict: WORKER_RUNTIME_REUSE_CONFIRMED
