# IMPROVEMENT_APPROVAL_FOUNDATION_V1

IMPROVEMENT_APPROVAL_FOUNDATION_STATUS = READY

## Purpose

Define the formal approval boundary for reviewed improvement proposals.

This is review only. It does not implement Improvement Approval Runtime, implementation, self-modification, reflection, self-improvement, governance mutation, replay mutation, worker dispatch, or worker execution.

## Context

AiGOL now has:

```text
Result
-> Evaluation
-> Improvement Proposal
-> Improvement Review
```

`IMPROVEMENT_REVIEW_FOUNDATION_V1` defines how improvement proposals may be reviewed without approving, rejecting, implementing, or mutating them.

The next missing governance boundary is approval: an explicit human-authorized decision that may approve or reject a reviewed improvement proposal without implementing it.

## 1. What Is IMPROVEMENT_APPROVAL_ARTIFACT_V1?

`IMPROVEMENT_APPROVAL_ARTIFACT_V1` is a replay-visible artifact that records an approval decision for a reviewed improvement proposal.

It records:

- which improvement proposal was reviewed;
- which improvement review supports the decision;
- which evaluation and result evidence are linked to the proposal;
- which canonical chain the approval belongs to;
- who authorized the decision;
- whether the proposal was approved or rejected;
- why the decision was made;
- whether implementation remains separate and unperformed;
- hashes and references required for replay reconstruction.

`IMPROVEMENT_APPROVAL_ARTIFACT_V1` is not:

- implementation;
- execution request;
- worker task;
- dispatch;
- invocation;
- result certification;
- reflection runtime;
- self-improvement runtime;
- governance mutation;
- replay repair.

## 2. Who May Approve An Improvement Proposal?

Only an explicit human authority may approve or reject an improvement proposal.

AiGOL may record the approval artifact after validating:

- reviewed proposal evidence;
- human authorization evidence;
- replay continuity;
- canonical chain continuity.

Allowed decision authority:

```text
decision_authority = HUMAN
recorded_by = AIGOL
```

AiGOL records the decision. AiGOL does not autonomously approve.

## 3. Who May Never Approve An Improvement Proposal?

The following may never approve or reject an improvement proposal:

- provider;
- LLM;
- worker;
- replay system;
- improvement proposal artifact;
- improvement review artifact;
- evaluation artifact;
- result artifact;
- completion artifact;
- execution artifact;
- background process;
- external API;
- automatic self-improvement loop.

Providers may propose language. Workers may produce evidence. AiGOL may validate and record. None of those actors may supply approval authority.

## 4. Required Review Evidence

Approval requires:

- valid `IMPROVEMENT_REVIEW_ARTIFACT_V1`;
- valid review artifact hash;
- valid `IMPROVEMENT_PROPOSAL_ARTIFACT_V1` reference and hash from the review;
- valid evaluation reference and hash;
- valid result reference and hash;
- canonical chain continuity;
- review status of `IMPROVEMENT_REVIEWED`;
- `implementation_authorized = false` in the review evidence;
- `approval_authority = false` in the review evidence;
- explicit human decision evidence;
- deterministic approval reason;
- replay reference for approval creation.

If review evidence is missing, corrupt, contradictory, not reviewed, or implementation-authorized, approval must fail closed.

## 5. Separation From Implementation

Improvement Approval is not implementation.

Approval may authorize a future implementation path. It may not:

- write code;
- modify files;
- modify configuration;
- create execution requests;
- dispatch workers;
- invoke workers;
- execute tasks;
- apply remediation;
- perform self-modification;
- perform self-improvement.

Implementation remains a separate future governed lifecycle after approval.

## 6. Separation From Governance Mutation

Improvement Approval is a governance decision record. It is not governance mutation.

It may not:

- rewrite constitutional artifacts;
- change governance hierarchy;
- mutate existing governance evidence;
- repair replay;
- redefine approval semantics;
- silently alter proposal, review, result, evaluation, execution, or completion artifacts.

Any future governance artifact change must pass through its own explicit governed mutation path.

## 7. Replay Continuity

Replay continuity requires:

- append-only improvement approval replay events;
- immutable approval artifact hash;
- review reference and review hash validation;
- proposal reference and proposal hash validation;
- evaluation reference and evaluation hash validation;
- result reference and result hash validation;
- human decision evidence reference validation;
- canonical chain continuity validation;
- no replay repair;
- no replay mutation outside improvement approval append-only events.

Replay may reconstruct approval history. Replay may not infer missing human authorization, change decision outcomes, or implement the approval.

## 8. Canonical Chain Continuity

`IMPROVEMENT_APPROVAL_ARTIFACT_V1` must contain:

```text
canonical_chain_id
improvement_review_reference
improvement_review_hash
improvement_proposal_reference
improvement_proposal_hash
evaluation_reference
evaluation_hash
result_reference
result_hash
decision
decision_authority
implementation_authorized
implementation_reference
replay_reference
artifact_hash
```

The canonical chain id must match the review, proposal, evaluation, and result evidence.

Missing or conflicting chain identity is fail-closed.

## 9. Relationship Between Improvement Proposal, Improvement Review, Improvement Approval, And Implementation

The relationship is:

```text
Improvement Proposal = proposed change derived from evaluation evidence.
Improvement Review = replay-visible assessment of the proposal.
Improvement Approval = explicit human-authorized approve or reject decision.
Implementation = future governed execution of an approved improvement.
```

Ordering:

```text
IMPROVEMENT_PROPOSED
-> IMPROVEMENT_REVIEWED
-> APPROVED or REJECTED
-> FUTURE_IMPLEMENTATION_ONLY_IF_APPROVED
```

Approval may permit a future implementation path if the decision is approved. It may not perform implementation.

## Decision

Improvement Approval Foundation is ready.

AiGOL can define approval as an explicit human-authorized, replay-visible decision boundary over reviewed improvement proposals while preserving strict separation from implementation, self-modification, self-improvement, governance mutation, and replay mutation.

Final classification:

```text
IMPROVEMENT_APPROVAL_FOUNDATION_STATUS = READY
```
