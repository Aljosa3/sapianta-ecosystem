# G5-07 Execution Authorization To Worker Handoff Alignment V1

Status: certified alignment.

Final verdict: AUTHORIZATION_TO_WORKER_READY

## 1. Purpose

G5-07 defines the canonical handoff from an execution authorization artifact to Worker Services.

This is an alignment and certification milestone only. It does not introduce runtime changes, worker assignment, worker dispatch, worker invocation, repository mutation, deployment, retry, fallback, or execution consumption.

The core rule is:

```text
Execution authorization may permit creation of a Worker handoff package.
Execution authorization does not itself assign, dispatch, invoke, or execute a Worker.
```

Execution remains out of scope for G5-07.

## 2. Reviewed Baseline

Reviewed certified components:

- G5-06 human approval to execution authorization alignment;
- execution authorization runtime;
- worker invocation request runtime;
- worker assignment runtime;
- OCS execution readiness runtime;
- domain execution-ready bridge;
- human intent worker invocation certification;
- worker invocation authorization consumption checks.

Existing canonical concepts include:

- execution authorization replay reconstruction;
- revoked authorization rejection;
- expired authorization rejection;
- execution-ready packet lineage;
- worker request scope classification;
- allowed outputs preservation;
- forbidden operations preservation;
- validation requirements preservation;
- worker role and target worker family selection constraints;
- non-authoritative Worker invocation request creation.

## 3. Handoff Model

The canonical handoff is:

```text
execution authorization artifact
-> authorization replay reconstruction
-> revocation and expiration checks
-> execution-ready packet reconstruction
-> approval and authorization lineage validation
-> Worker request evidence
-> Worker request classification
-> Worker handoff/request artifact
-> governance handoff checkpoint
-> UHCL handoff summary
-> replay reconstruction
```

The handoff creates a Worker-facing request package. It does not select a concrete Worker, dispatch the request, invoke Worker code, mutate repositories, deploy software, retry, or fallback.

## 4. What Worker Services Receive

Worker Services may receive a bounded handoff package containing:

- worker handoff id or invocation request id;
- execution authorization reference and hash;
- execution authorization replay reference;
- authorization status;
- execution-ready reference and hash;
- execution candidate reference and hash;
- execution packet reference and hash;
- OCS handoff reference and hash when present;
- approval reference and hash;
- target domain or target resource;
- worker role;
- target worker family;
- worker capability requirements;
- worker registry requirements;
- allowed outputs;
- forbidden operations;
- validation requirements;
- requested by;
- requested at;
- replay references;
- non-authority flags.

The package must be sufficient for Worker Services to validate scope before any later assignment, dispatch, or invocation.

## 5. What Worker Services Must Validate

Worker Services must validate:

- authorization artifact type;
- authorization status is authorized;
- authorization replay reconstructs;
- authorization is not revoked;
- authorization is not expired;
- authorization has not already been consumed when single-use;
- authorization scope permits Worker handoff;
- execution-ready packet reconstructs;
- execution packet hash matches authorization lineage;
- execution candidate hash matches authorization lineage;
- approval hash matches the approved execution candidate;
- chain id is continuous;
- allowed outputs are preserved;
- forbidden operations are preserved;
- validation requirements are preserved;
- worker role is compatible with the requested work;
- target worker family is compatible with the request;
- Worker identity/capability evidence exists before later assignment;
- no worker assignment, dispatch, invocation, mutation, deployment, retry, or fallback has occurred during handoff.

If any validation fails, the handoff must fail closed.

## 6. What Remains Replay Evidence Only

The following remain replay evidence only:

- OCS proposal text;
- provider cognition evidence;
- UHCL review and confirmation;
- human approval decision;
- authorization request and decision narrative;
- authorization readiness bridge evidence;
- execution-ready packet evidence;
- Worker handoff package;
- Worker request classification.

None of these are Worker execution. They become actionable only when a later certified Worker assignment, dispatch, and invocation path consumes them.

## 7. What Becomes Executable Work

Executable work begins only after later certified milestones perform all required downstream transitions:

```text
Worker handoff package
-> Worker assignment
-> Worker dispatch authorization
-> Worker dispatch
-> Worker invocation
-> result capture
-> post-execution replay review
```

G5-07 certifies only the first handoff boundary into Worker Services.

The handoff package is executable work intent, not execution.

## 8. Worker Prerequisites

Worker handoff prerequisites:

- valid execution authorization artifact;
- authorization replay reference and hash;
- authorization not expired;
- authorization not revoked;
- authorization not consumed;
- execution-ready packet reference and hash;
- approval lineage continuity;
- OCS handoff lineage continuity when present;
- worker role requirements;
- worker capability requirements;
- candidate worker constraints;
- worker registry requirements;
- allowed outputs;
- forbidden operations;
- validation requirements;
- replay reconstruction;
- governance checkpoint.

Worker identity prerequisites for later assignment:

- Worker identity artifact;
- Worker role;
- Worker capability declarations;
- Worker availability status;
- Worker scope compatibility;
- Worker exclusion-rule compliance;
- Worker registry selection evidence.

These identity prerequisites may be referenced by G5-07, but assignment remains out of scope.

## 9. Ownership Matrix

| Capability | Canonical Owner | Boundary |
| --- | --- | --- |
| Execution authorization artifact | Authorization service / Governance | Scoped gate only. |
| Authorization admissibility | Governance | Validates scope, freshness, revocation, and lineage. |
| Execution-ready packet | OCS / execution readiness runtime | Candidate work definition. |
| Worker handoff package | Worker Services under Governance | Request package only. |
| Worker identity | Worker Services | Capability and availability evidence. |
| Worker assignment | Worker Services | Out of scope for G5-07. |
| Worker dispatch | Worker Services / dispatch governance | Out of scope for G5-07. |
| Worker invocation | Worker Services / execution runtime | Out of scope for G5-07. |
| Human communication | UHCL | Handoff explanation and recovery guidance only. |
| Replay reconstruction | Replay | Evidence continuity and fail-closed validation. |
| Interface rendering | Adapter | Display and response capture only. |

## 10. Replay Implications

Required replay bindings:

- execution authorization replay reference;
- authorization request hash;
- authorization decision hash;
- authorization artifact hash;
- authorization result hash;
- authorization expiration evidence;
- authorization revocation evidence;
- execution-ready replay reference and hash;
- execution candidate hash;
- execution packet hash;
- execution validation hash;
- OCS handoff hash when present;
- approval hash;
- Worker handoff evidence hash;
- Worker request classification hash;
- Worker request artifact hash;
- governance checkpoint hash;
- UHCL handoff summary hash.

Replay reconstruction must fail closed if:

- authorization replay does not reconstruct;
- authorization status is not authorized;
- authorization artifact type is invalid;
- authorization is expired;
- authorization is revoked;
- authorization was already consumed;
- execution-ready packet does not reconstruct;
- candidate, packet, validation, and ready hashes do not align;
- approval lineage is broken;
- OCS handoff lineage is broken when required;
- Worker scope exceeds authorized scope;
- allowed outputs change;
- forbidden operations change;
- validation requirements change;
- worker assignment, dispatch, invocation, mutation, deployment, retry, or fallback appears during handoff.

## 11. Governance Implications

Governance must enforce:

- authorization is a prerequisite, not a Worker execution trigger;
- Worker handoff cannot infer authority from approval, UHCL confirmation, provider cognition, OCS proposal, or adapter state;
- Worker handoff scope cannot exceed authorization scope;
- Worker handoff must preserve execution packet scope;
- Worker handoff must preserve forbidden operations;
- Worker handoff must preserve validation requirements;
- revoked authorization blocks handoff;
- expired authorization blocks handoff;
- consumed authorization blocks handoff when single-use;
- Worker identity and capability evidence must exist before later assignment;
- handoff failures produce UHCL recovery guidance;
- no Worker execution occurs during handoff.

The governance checkpoint should record:

```text
authorization_reconstructed = true
authorization_status = EXECUTION_AUTHORIZED
authorization_revoked = false
authorization_expired = false
authorization_consumed = false
execution_ready_replay_bound = true
worker_handoff_created = true
worker_assigned = false
worker_dispatched = false
worker_invoked = false
repository_mutated = false
deployment_performed = false
retry_performed = false
fallback_performed = false
```

In this document, `worker_handoff_created = true` describes the future lifecycle artifact certified by this alignment. G5-07 does not implement or activate that runtime.

## 12. Revocation And Expiration Handling

Revocation handling:

- load authorization artifact;
- verify authorization hash;
- inspect revocation status;
- reject revoked authorization before Worker handoff creation;
- record revocation reason and recovery guidance;
- preserve replay evidence.

Expiration handling:

- load authorization expiration boundary;
- compare requested handoff time to expiration;
- reject expired authorization before Worker handoff creation;
- record expiration reason and recovery guidance;
- require a new authorization lifecycle if execution remains desired.

Consumed authorization handling:

- check prior handoff, request, assignment, dispatch, or invocation records;
- reject reused single-use authorization;
- record reuse failure and recovery guidance.

## 13. Failure States

Canonical failure states:

- `MISSING_EXECUTION_AUTHORIZATION`;
- `INVALID_AUTHORIZATION_ARTIFACT`;
- `AUTHORIZATION_NOT_AUTHORIZED`;
- `AUTHORIZATION_REVOKED`;
- `AUTHORIZATION_EXPIRED`;
- `AUTHORIZATION_ALREADY_CONSUMED`;
- `EXECUTION_READY_REPLAY_MISSING`;
- `EXECUTION_PACKET_LINEAGE_MISMATCH`;
- `APPROVAL_LINEAGE_MISMATCH`;
- `OCS_HANDOFF_LINEAGE_MISMATCH`;
- `WORKER_SCOPE_EXCEEDS_AUTHORIZATION`;
- `WORKER_ROLE_UNSUPPORTED`;
- `WORKER_CAPABILITY_REQUIREMENT_MISSING`;
- `FORBIDDEN_OPERATION_PRESENT`;
- `VALIDATION_REQUIREMENTS_MISMATCH`;
- `REPLAY_LINEAGE_MISMATCH`.

Each failure state must fail closed and produce UHCL recovery guidance without granting authority.

## 14. Certification Criteria

Authorization-to-Worker handoff alignment is certified only if:

- execution authorization replay reconstructs;
- authorization status is authorized;
- authorization is not revoked;
- authorization is not expired;
- authorization is not already consumed when single-use;
- execution-ready packet reconstructs;
- approval and authorization lineage remain continuous;
- Worker handoff scope is bounded by authorization scope;
- worker role, target family, capability requirements, allowed outputs, forbidden operations, and validation requirements are preserved;
- handoff package is replay-visible;
- governance checkpoint records non-execution;
- UHCL can explain handoff status and failures;
- no worker assignment, dispatch, invocation, mutation, deployment, retry, or fallback occurs.

## 15. Implementation Recommendation

The next implementation batch should add a deterministic PGSP Worker handoff runtime that consumes an execution authorization artifact and emits a Worker invocation request package without assigning or invoking a Worker.

Recommended scope:

1. Input:
   - execution authorization replay reference;
   - authorization artifact;
   - execution-ready replay reference;
   - requested handoff id;
   - requested by;
   - requested at.

2. Output:
   - Worker handoff evidence artifact;
   - Worker scope classification artifact;
   - Worker invocation request artifact;
   - governance handoff checkpoint artifact;
   - UHCL Worker handoff summary;
   - replay reconstruction summary.

3. Required exclusions:
   - no Worker assignment;
   - no Worker dispatch;
   - no Worker invocation;
   - no repository mutation;
   - no deployment;
   - no provider invocation;
   - no retry;
   - no fallback.

The implementation should reuse the existing Worker invocation request runtime concepts while normalizing ownership around PGSP, OCS, Governance, UHCL, Replay, Authorization Services, and Worker Services.

## 16. Compatibility Impact

This alignment preserves existing runtime behavior.

Compatibility impact:

- no runtime behavior changes;
- no schema changes to G5-02 through G5-06 artifacts;
- existing Worker invocation request semantics remain reusable;
- existing authorization replay shape remains a strong implementation reference;
- future Worker runtimes must consume handoff packages rather than infer work from authorization alone;
- repository mutation remains out of scope until separately certified.

## 17. Final Determination

The execution authorization to Worker Services handoff is architecturally ready as a governed, replay-visible, non-executing transition.

Authorization remains the scoped gate. Worker Services receive a bounded handoff package. Governance owns admissibility. Replay owns reconstruction. UHCL owns explanation and recovery guidance. Worker assignment, dispatch, invocation, and execution remain separate future milestones.

Final verdict: AUTHORIZATION_TO_WORKER_READY
