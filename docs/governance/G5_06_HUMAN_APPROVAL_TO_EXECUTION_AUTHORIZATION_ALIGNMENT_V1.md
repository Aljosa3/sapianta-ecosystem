# G5-06 Human Approval To Execution Authorization Alignment V1

Status: certified alignment.

Final verdict: HUMAN_TO_AUTHORIZATION_READY

## 1. Purpose

G5-06 defines the canonical lifecycle from a human approval decision to an execution authorization artifact.

This is an alignment and certification milestone only. It does not introduce runtime changes, provider invocation, worker execution, repository mutation, deployment, retry, fallback, or execution consumption.

The core rule is:

```text
Human approval may permit authorization assessment.
Human approval is not execution authorization.
Execution authorization must be separately derived, scoped, replay-bound, freshness-checked, and revocable.
```

Execution remains out of scope for G5-06.

## 2. Reviewed Baseline

Reviewed certified components:

- G5-00 execution transition readiness review;
- G5-05 OCS proposal to human approval lifecycle alignment;
- G3-02 authorization-readiness bridge;
- execution authorization runtime;
- domain approval-entry to execution-ready bridge;
- worker invocation authorization consumption checks;
- filesystem mutation authorization boundary model.

Existing canonical authorization concepts include:

- approval-to-authorization lineage;
- authorization readiness evidence;
- execution-ready replay binding;
- authorization request artifact;
- authorization decision artifact;
- authorization artifact;
- authorization result artifact;
- expiration checks;
- revocation checks;
- fail-closed replay reconstruction.

## 3. Lifecycle Model

The canonical lifecycle is:

```text
OCS proposal approved
-> approval replay reconstructed
-> governance authorization admissibility checkpoint
-> execution scope derived
-> worker/provider/read-only readiness assessed
-> authorization request recorded
-> authorization decision recorded
-> execution authorization artifact recorded
-> authorization result recorded
-> authorization remains unconsumed until a later execution runtime
```

Approval is prerequisite evidence. Authorization is a separate governed artifact.

## 4. Approval Information Carried Forward

The authorization lifecycle may carry forward the following approval evidence:

| Approval Information | Treatment In Authorization Lifecycle |
| --- | --- |
| Approval decision id | Copied as approval reference. |
| Approval decision hash | Copied as replay-bound evidence. |
| Approval request id | Copied as approval request reference. |
| Approval request hash | Copied as replay-bound evidence. |
| Proposal id | Copied as proposal reference. |
| Proposal version | Copied to bind authorization to exact approved proposal. |
| Proposal hash | Copied and checked against current proposal lineage. |
| Approved scope | Used as upper bound for authorization scope. |
| Human actor id | Copied as actor evidence. |
| Approval timestamp | Used for freshness and expiration evaluation. |
| Approval decision | Must be approved; rejection or clarification blocks authorization. |

Carried-forward approval evidence remains replay evidence. It does not itself authorize execution.

## 5. Authorization Information Derived Independently

The authorization lifecycle must independently derive:

- authorization id;
- authorization status;
- authorization scope;
- authorized operation type;
- authorized target objects;
- authorized permissions;
- execution readiness reference;
- worker readiness reference when worker execution is later requested;
- provider readiness reference when provider execution is later requested;
- authorization expiration;
- single-use or reuse policy;
- revocation status;
- validation checks;
- forbidden operations;
- authorization result hash;
- replay lineage hash.

Authorization scope may not exceed approved scope. If the required execution scope is broader than the approved scope, authorization must fail closed.

## 6. What Remains Replay Evidence Only

The following remain evidence only:

- natural-language intent;
- UHCL confirmation;
- adapter response capture;
- provider cognition output;
- OCS proposal text;
- human review response;
- approval request presentation;
- approval decision text;
- authorization readiness bridge evidence.

None of these can be consumed as executable authorization unless a valid authorization artifact is created and reconstructed.

## 7. What Becomes Executable Authorization

An authorization artifact becomes executable authorization only when all required conditions are satisfied:

- approval replay reconstructs;
- approval decision is approved;
- proposal hash matches approved proposal hash;
- authorization scope is bounded by approved scope;
- execution-ready evidence reconstructs;
- worker/provider readiness evidence is present when applicable;
- governance admissibility checkpoint passes;
- authorization is not expired;
- authorization is not revoked;
- authorization has not been consumed when single-use;
- replay hash continuity is valid;
- forbidden operations remain absent.

Executable authorization does not perform execution. It is a consumable gate for a later runtime.

## 8. Authorization Prerequisites

Required prerequisites:

- OCS proposal artifact;
- UHCL proposal presentation artifact;
- approval request artifact;
- human approval decision artifact;
- proposal hash binding;
- approval request hash binding;
- approval decision hash binding;
- actor identity evidence;
- approved scope evidence;
- execution-ready package or equivalent bounded execution candidate;
- validation evidence for the requested execution class;
- replay reconstruction of all source evidence;
- governance checkpoint;
- expiration policy;
- revocation policy;
- consumption policy.

Worker-specific authorization additionally requires:

- worker capability declaration;
- worker assignment readiness;
- worker request scope;
- worker dispatch constraints;
- side-effect boundary declaration.

Provider-specific authorization additionally requires:

- provider identity artifact;
- credential reference boundary;
- provider role and capability scope;
- read-only or execution mode declaration;
- cost/rate/attempt limit where applicable.

Repository mutation authorization additionally requires:

- exact target paths;
- operation mode;
- content hashes;
- validation result hashes;
- rollback or recovery guidance;
- protected path policy.

## 9. Ownership Matrix

| Capability | Canonical Owner | Boundary |
| --- | --- | --- |
| Approval decision | Human authority recorded through Governance | Approval evidence only. |
| Approval request | Approval service / Governance | Explicit proposal-bound request. |
| Authorization admissibility | Governance | Determines if authorization may be created. |
| Authorization artifact | Authorization service / Governance | Scoped execution gate only. |
| Execution-ready package | OCS / execution readiness runtime | Candidate evidence only. |
| Worker readiness | Worker Services under governance | Capability and dispatch readiness only. |
| Provider readiness | Provider Services under OCS governance | Identity, credential, and scope readiness only. |
| Human communication | UHCL | Explanation and review only. |
| Interface rendering | Adapter | Display and response capture only. |
| Replay reconstruction | Replay | Evidence continuity and fail-closed validation. |
| Execution consumption | Future execution runtime | Out of scope for G5-06. |

## 10. Replay Implications

Required replay bindings:

- OCS proposal reference and hash;
- approval request reference and hash;
- approval decision reference and hash;
- human actor identity reference;
- approved scope hash;
- execution-ready replay reference and hash;
- authorization request artifact hash;
- authorization decision artifact hash;
- authorization artifact hash;
- authorization result artifact hash;
- governance checkpoint hash;
- expiration policy hash;
- revocation policy hash;
- consumption policy hash.

Replay reconstruction must fail closed if:

- approval decision is missing;
- approval decision is not approved;
- approval decision precedes approval request;
- approval request is not bound to the proposal hash;
- authorization scope exceeds approval scope;
- execution-ready evidence is missing;
- worker readiness is missing for worker authorization;
- provider readiness is missing for provider authorization;
- authorization has expired;
- authorization is revoked;
- single-use authorization has already been consumed;
- authorization lineage is modified;
- execution, worker invocation, provider invocation, mutation, deployment, retry, or fallback occurs during authorization creation.

## 11. Governance Implications

Governance must enforce:

- approval is prerequisite evidence only;
- authorization is a separate lifecycle transition;
- authorization scope is bounded by approved scope;
- authorization cannot be inferred from UHCL confirmation, adapter response, provider cognition, OCS proposal, or worker readiness;
- authorization must be replay-bound;
- authorization must be fresh;
- authorization must be revocable;
- authorization consumption must be tracked by later execution runtimes;
- authorization failure states must be visible to UHCL;
- execution remains blocked until a later runtime consumes valid authorization.

The governance checkpoint should record:

```text
approval_reconstructed = true
approval_decision = APPROVED
approval_hash_bound = true
authorization_scope_within_approval_scope = true
execution_ready_replay_bound = true
authorization_created = true
execution_started = false
provider_invoked = false
worker_invoked = false
repository_mutated = false
deployment_performed = false
authorization_consumed = false
authorization_revoked = false
authorization_expired = false
```

In this document, `authorization_created = true` describes the future lifecycle artifact certified by this alignment. G5-06 does not implement or activate that runtime.

## 12. Revocation Model

Authorization revocation must be explicit and replay-visible.

Revocation states:

| State | Meaning |
| --- | --- |
| `AUTHORIZATION_ACTIVE` | Authorization is valid and unconsumed. |
| `AUTHORIZATION_EXPIRED` | Authorization is beyond its expiration boundary. |
| `AUTHORIZATION_REVOKED` | Human or governance revoked authorization. |
| `AUTHORIZATION_CONSUMED` | Single-use authorization was consumed by a later execution runtime. |
| `AUTHORIZATION_FAILED_CLOSED` | Authorization evidence is invalid or incomplete. |

Revocation evidence must include:

- authorization id;
- authorization hash;
- revocation actor or governance trigger;
- revocation timestamp;
- revocation reason;
- replay hash;
- affected execution scopes;
- recovery guidance.

Revoked, expired, or consumed authorization must fail closed before execution.

## 13. Failure States

Canonical failure states:

- `MISSING_APPROVAL`;
- `APPROVAL_NOT_APPROVED`;
- `STALE_APPROVAL_HASH`;
- `APPROVAL_SCOPE_EXCEEDED`;
- `MISSING_EXECUTION_READY_REPLAY`;
- `WORKER_READINESS_MISSING`;
- `PROVIDER_READINESS_MISSING`;
- `AUTHORIZATION_SCOPE_INVALID`;
- `AUTHORIZATION_EXPIRED`;
- `AUTHORIZATION_REVOKED`;
- `AUTHORIZATION_ALREADY_CONSUMED`;
- `REPLAY_LINEAGE_MISMATCH`;
- `FORBIDDEN_OPERATION_PRESENT`.

Each failure state must produce UHCL recovery guidance without granting authority.

## 14. Certification Criteria

Human approval to execution authorization alignment is certified only if:

- approval evidence reconstructs;
- approval decision is approved;
- authorization is separately created;
- authorization records proposal, approval request, approval decision, actor, scope, expiration, revocation, and replay lineage;
- authorization scope does not exceed approval scope;
- execution-ready evidence reconstructs;
- worker/provider/mutation readiness prerequisites are checked according to requested authorization class;
- authorization can expire;
- authorization can be revoked;
- authorization can be consumed by a later runtime only once when single-use;
- failure states fail closed;
- UHCL can explain missing or failed prerequisites;
- no execution occurs during authorization creation.

## 15. Implementation Recommendation

The next implementation batch should add a deterministic PGSP authorization lifecycle runtime that consumes approved OCS proposal lifecycle evidence and emits a scoped authorization artifact without executing it.

Recommended scope:

1. Input:
   - approved OCS proposal lifecycle replay;
   - approval request artifact;
   - approval decision artifact;
   - execution-ready candidate evidence;
   - requested authorization scope;
   - expiration policy;
   - revocation policy.

2. Output:
   - authorization request artifact;
   - authorization decision artifact;
   - execution authorization artifact;
   - authorization result artifact;
   - governance checkpoint artifact;
   - UHCL authorization readiness summary;
   - replay reconstruction summary.

3. Required exclusions:
   - no provider invocation;
   - no worker invocation;
   - no repository mutation;
   - no deployment;
   - no execution consumption;
   - no retry;
   - no fallback.

The implementation should reuse the existing execution authorization runtime concepts while normalizing ownership around PGSP, OCS, Governance, UHCL, Replay, Provider Services, and Worker Services.

## 16. Compatibility Impact

This alignment preserves existing runtime behavior.

Compatibility impact:

- no runtime behavior changes;
- no schema changes to G5-02 through G5-05 artifacts;
- existing authorization bridge concepts remain reusable;
- existing execution authorization replay shape remains a strong implementation reference;
- future execution runtimes must consume authorization rather than infer it;
- repository mutation remains out of scope until separately certified.

## 17. Final Determination

The human approval to execution authorization lifecycle is architecturally ready as a governed, replay-visible, non-executing transition.

Human approval remains prerequisite evidence. Authorization becomes the scoped execution gate. Governance owns admissibility. Replay owns reconstruction. UHCL owns explanation and recovery guidance. Execution remains a separate future milestone.

Final verdict: HUMAN_TO_AUTHORIZATION_READY
