# G5-05 OCS Proposal To Human Approval Lifecycle Alignment V1

Status: certified alignment.

Final verdict: OCS_TO_HUMAN_APPROVAL_READY

## 1. Purpose

G5-05 defines the canonical lifecycle between an OCS-owned decision proposal and human approval evidence.

This is an alignment and certification milestone only. It does not introduce runtime changes, execution authorization, provider invocation, worker execution, repository mutation, deployment, retry, fallback, or approval activation.

The core rule is:

```text
An OCS proposal may become eligible for a human approval lifecycle.
An OCS proposal does not become approved by presentation, confirmation, or continuation alone.
```

Human approval must be explicit, replay-visible, proposal-hash-bound, scoped, and separate from authorization.

## 2. Reviewed Baseline

Reviewed certified components:

- G4-02 OCS advisory proposal artifact;
- G4-03 and G4-04 UHCL proposal presentation and human response model;
- G5-00 approval activation readiness review;
- G5-04 provider cognition to OCS proposal alignment;
- G3-02 proposal approval bridge lifecycle;
- approval request infrastructure;
- universal domain proposal interface.

Existing canonical states include:

- `PROPOSAL_DRAFTED`;
- `PROPOSAL_REVISED`;
- `APPROVAL_REQUESTED`;
- `APPROVAL_RECORDED`;
- `PROPOSAL_REJECTED`;
- `CLARIFICATION_RETURNED`;
- `FAILED_CLOSED`.

Existing approval decisions include:

- `APPROVED`;
- `REJECTED`;
- `CLARIFICATION_REQUESTED`.

## 3. Lifecycle Model

The canonical lifecycle is:

```text
OCS proposal drafted
-> governance pre-approval checkpoint
-> UHCL proposal presentation
-> human review response captured
-> proposal lifecycle transition
-> optional proposal revision
-> explicit approval request
-> human approval decision recorded
-> governance post-decision checkpoint
-> execution authorization readiness assessment
```

Execution remains inactive after G5-05. Approval evidence may establish readiness for a later authorization lifecycle, but it does not itself authorize execution.

## 4. Lifecycle States

| State | Meaning | Execution Impact |
| --- | --- | --- |
| `OCS_PROPOSAL_DRAFTED` | OCS has produced a proposal artifact. | None |
| `OCS_PROPOSAL_PRESENTED` | UHCL has presented the proposal for human review. | None |
| `HUMAN_REVIEW_CAPTURED` | A canonical human response class was captured. | None |
| `PROPOSAL_MODIFICATION_REQUESTED` | Human requested changes or clarification. | None |
| `OCS_PROPOSAL_REVISED` | OCS produced an append-only proposal revision. | None |
| `APPROVAL_REQUEST_ELIGIBLE` | Governance allows an explicit approval request to be generated. | None |
| `APPROVAL_REQUESTED` | Approval-request evidence exists and binds to proposal hash. | None |
| `APPROVAL_RECORDED` | Human approval decision was recorded as evidence. | No execution authority |
| `PROPOSAL_REJECTED` | Human rejected the proposal. | Execution blocked |
| `CLARIFICATION_RETURNED` | Human requested clarification. | Execution blocked pending response |
| `FAILED_CLOSED` | Lifecycle evidence is invalid or incomplete. | Execution blocked |

## 5. Human Review States

UHCL and PGSP may capture human review responses before approval activation.

Review states:

- `CONFIRMATION`: human confirms review or wants to continue;
- `CONTINUATION`: human permits the session to continue to the next governed step;
- `CLARIFICATION`: human requests explanation or missing context;
- `MODIFICATION`: human requests proposal changes;
- `REJECTION`: human rejects the current proposal.

These are review states, not approval states.

Review responses may lead to:

- additional UHCL explanation;
- OCS proposal revision;
- approval request eligibility;
- rejection closure;
- failed-closed recovery guidance.

They may not directly create approval, authorization, execution, mutation, or deployment authority.

## 6. Human Approval States

Approval states are entered only after an explicit approval request is generated.

Canonical approval states:

| Approval State | Meaning | Required Evidence |
| --- | --- | --- |
| `APPROVAL_NOT_REQUESTED` | Proposal has no approval request. | OCS proposal hash, UHCL presentation hash |
| `APPROVAL_REQUESTED` | Approval request exists. | Approval request id, proposal id, proposal version, proposal hash, risk class |
| `APPROVED` | Human approved the exact proposal hash. | Human decision artifact, actor identity, timestamp, approval request hash |
| `REJECTED` | Human rejected the proposal. | Rejection decision artifact, proposal hash, reason when provided |
| `CLARIFICATION_REQUESTED` | Human requested clarification instead of approval. | Clarification decision artifact and return reference |
| `FAILED_CLOSED` | Approval evidence is missing, stale, mismatched, or invalid. | Failure reason and replay evidence |

Approval is valid only for the bound proposal hash and scope. Any proposal revision invalidates earlier approval eligibility and requires a new approval request.

## 7. Modification And Rejection Handling

Modification handling:

- records the human modification response;
- preserves the prior proposal hash;
- creates a new OCS proposal version if OCS accepts the modification;
- invalidates prior approval request eligibility;
- requires a new UHCL presentation and approval request.

Clarification handling:

- records the clarification decision;
- returns to UHCL explanation or OCS proposal clarification;
- preserves replay lineage;
- blocks execution readiness until a new review or approval path is completed.

Rejection handling:

- records rejection evidence;
- marks the proposal lifecycle as rejected;
- preserves proposal and decision hashes;
- blocks authorization readiness;
- may produce UHCL recovery guidance.

## 8. Ownership Matrix

| Capability | Canonical Owner | Boundary |
| --- | --- | --- |
| Proposal synthesis | OCS | Proposal content and version lineage. |
| Proposal presentation | UHCL | Human-readable explanation and approval prompt semantics. |
| Adapter rendering | Interface adapter | Display and response capture only. |
| Human review response | PGSP / UHCL | Review-class evidence only. |
| Approval request | Approval service / Governance | Explicit request evidence; no execution authority. |
| Approval decision | Human authority recorded through Governance | Human decision evidence only. |
| Proposal hash binding | Replay / Governance | Evidence continuity and fail-closed validation. |
| Governance checkpoints | Governance | Authority separation and lifecycle admissibility. |
| Authorization readiness | Governance / Authorization service | Future transition only, separate from approval. |
| Provider evidence | Provider Services / Replay | Non-authoritative source evidence only. |
| Worker execution | Worker Services | Out of scope for G5-05. |
| Repository mutation | Governed mutation runtime | Out of scope for G5-05. |

## 9. Replay Implications

Required replay bindings:

- OCS proposal artifact reference and hash;
- proposal version hash;
- source evidence references and hashes;
- UHCL proposal presentation reference and hash;
- human review response reference and hash;
- approval request id and hash when requested;
- approval decision id and hash when recorded;
- rejection or clarification reference when applicable;
- governance checkpoint hash before approval request;
- governance checkpoint hash after approval decision;
- authorization readiness assessment hash when produced.

Replay reconstruction must fail closed if:

- approval decision is recorded before approval request;
- approval request does not bind the current proposal hash;
- approval decision binds a stale proposal hash;
- proposal revision occurs after approval without a new request;
- UHCL confirmation is treated as approval;
- adapter response capture is treated as approval;
- provider evidence is treated as approval;
- approval is treated as authorization;
- execution, worker invocation, mutation, deployment, retry, or fallback appears in this lifecycle.

## 10. Governance Implications

Governance must enforce:

- OCS proposal ownership;
- UHCL communication ownership;
- adapter rendering boundary;
- explicit approval request before approval decision;
- proposal hash binding;
- approval freshness;
- approval scope;
- denial and clarification handling;
- revision invalidation;
- approval-authority separation from authorization authority;
- execution remains blocked after approval until authorization is separately certified.

The governance checkpoint should record:

```text
ocs_proposal_owner = OCS
proposal_presented_by = UHCL
human_review_is_approval = false
approval_request_required = true
approval_request_hash_bound = true
approval_decision_recorded = true | false
approval_created = false
authorization_created = false
execution_authorized = false
worker_invoked = false
repository_mutated = false
deployment_performed = false
```

In this document, `approval_created = false` means G5-05 does not activate a runtime approval creation path. Future runtime milestones may certify approval creation as an explicit lifecycle transition.

## 11. Transition Readiness For Authorization

After a valid approval decision is recorded, the proposal may become eligible for future authorization assessment.

Authorization readiness requires:

- approved proposal hash;
- approval request hash;
- approval decision hash;
- actor identity evidence;
- scope evidence;
- freshness evidence;
- expiration or reuse policy;
- denial and revocation handling;
- governance checkpoint;
- replay reconstruction.

Approval does not create authorization. Authorization must remain a separate governed transition before any execution path consumes it.

## 12. Certification Criteria

OCS-to-human-approval alignment is certified only if:

- OCS proposal artifact exists and is OCS-owned;
- UHCL presentation exists and is replay-visible;
- human review response is captured as review evidence only;
- approval request is explicit and proposal-hash-bound;
- approval decision occurs only after approval request;
- approval decision records actor, timestamp, proposal id, proposal version, proposal hash, and decision hash;
- modification creates append-only proposal revision and invalidates prior request eligibility;
- rejection blocks authorization readiness;
- clarification returns to UHCL/OCS without execution;
- approval remains separate from authorization;
- execution, provider invocation, worker invocation, mutation, deployment, retry, and fallback remain absent.

## 13. Implementation Recommendation

The next implementation batch should add a deterministic OCS proposal approval lifecycle runtime that consumes an OCS proposal artifact and emits replay-visible approval lifecycle evidence.

Recommended scope:

1. Input:
   - OCS proposal artifact;
   - UHCL proposal presentation artifact;
   - human review response;
   - optional approval request command.

2. Output:
   - proposal lifecycle transition artifact;
   - explicit approval request artifact;
   - approval decision artifact;
   - governance checkpoint artifact;
   - UHCL approval outcome summary;
   - replay reconstruction summary.

3. Required exclusions:
   - no authorization creation;
   - no execution authorization;
   - no provider invocation;
   - no worker invocation;
   - no repository mutation;
   - no deployment;
   - no retry;
   - no fallback.

The implementation should reuse existing approval request and proposal lifecycle concepts where possible, while normalizing ownership around PGSP, OCS, Governance, UHCL, and Replay.

## 14. Compatibility Impact

This alignment preserves existing runtime behavior.

Compatibility impact:

- no runtime behavior changes;
- no schema changes to G5-02, G5-03, or G5-04 artifacts;
- OCS proposal semantics remain proposal-only until explicit approval lifecycle activation;
- existing approval bridge concepts remain reusable;
- future adapters continue to render UHCL and capture responses;
- authorization remains separate and future-scoped.

## 15. Final Determination

The OCS proposal to human approval lifecycle is architecturally ready as a governed, replay-visible, non-executing lifecycle.

OCS owns proposal content. UHCL owns presentation. Human authority owns approval decisions. Governance owns lifecycle admissibility. Replay owns reconstruction. Authorization and execution remain separate future transitions.

Final verdict: OCS_TO_HUMAN_APPROVAL_READY
