# IMPROVEMENT_REVIEW_FOUNDATION_V1

IMPROVEMENT_REVIEW_FOUNDATION_STATUS = READY

## Purpose

Define the formal boundary for reviewing improvement proposals.

This is review only. It does not implement Improvement Review Runtime, approval, implementation, reflection, self-improvement, governance mutation, replay mutation, worker dispatch, or worker execution.

## Context

AiGOL now has:

```text
Execution
-> Completion
-> Result
-> Evaluation
-> Improvement Proposal
```

`IMPROVEMENT_PROPOSAL_FOUNDATION_V1` defines how evaluation evidence may become a proposed improvement without approving or implementing it.

The next missing governance boundary is review: a replay-visible assessment of whether an improvement proposal is coherent, bounded, evidence-supported, and ready for a separate approval decision.

## 1. What Is IMPROVEMENT_REVIEW_ARTIFACT_V1?

`IMPROVEMENT_REVIEW_ARTIFACT_V1` is a replay-visible artifact that records review findings for an improvement proposal.

It records:

- which improvement proposal was reviewed;
- which evaluation and result evidence support the proposal;
- which canonical chain the proposal belongs to;
- who or what supplied review observations;
- what review criteria were applied;
- whether the proposal appears review-complete;
- whether approval is recommended;
- what risks, gaps, or constraints remain;
- hashes and references needed for replay reconstruction.

`IMPROVEMENT_REVIEW_ARTIFACT_V1` is not:

- approval;
- rejection;
- implementation;
- execution request;
- worker task;
- result certification;
- reflection runtime;
- self-improvement runtime;
- governance mutation;
- replay repair.

## 2. Who May Review An Improvement Proposal?

Only AiGOL may create `IMPROVEMENT_REVIEW_ARTIFACT_V1`.

AiGOL may use bounded review inputs, such as:

- deterministic local review checks;
- human observations recorded as review evidence;
- read-only worker reports;
- provider-assisted non-authoritative review text;
- governance artifact references used as review context.

Those inputs may inform review findings. They do not directly create the formal review artifact and do not receive approval or implementation authority.

## 3. Who May Never Review An Improvement Proposal?

The following may never directly create `IMPROVEMENT_REVIEW_ARTIFACT_V1`:

- provider;
- LLM;
- worker;
- human directly;
- replay system;
- improvement proposal artifact;
- evaluation artifact;
- result artifact;
- background process;
- external API;
- automatic self-improvement loop.

Humans may later approve or reject through a separate explicit approval boundary. Providers and workers may contribute bounded evidence only.

## 4. Required Proposal Evidence

Review requires:

- valid `IMPROVEMENT_PROPOSAL_ARTIFACT_V1`;
- valid proposal artifact hash;
- valid `RESULT_EVALUATION_ARTIFACT_V1` reference or hash from the proposal;
- valid `RESULT_ARTIFACT_V1` reference or hash from the proposal;
- canonical chain continuity;
- proposal status of `IMPROVEMENT_PROPOSED`;
- `approval_required = true`;
- `implementation_authorized = false`;
- `proposal_approved = false`;
- replay-visible proposal evidence;
- deterministic review criteria and observations;
- replay reference for review creation.

If proposal evidence is missing, corrupt, contradictory, already approved, or implementation-authorized, review must fail closed.

## 5. Separation From Approval

Improvement Review is not approval.

The artifact may recommend approval, recommend rejection, or identify gaps. It may not:

- approve the proposal;
- reject the proposal as a governance transition;
- authorize implementation;
- create approval artifacts;
- change proposal status;
- mark a result as certified;
- mutate governance.

Approval remains a separate explicit human-authorized governance transition.

## 6. Separation From Implementation

Improvement Review is not implementation.

The artifact may assess readiness for approval. It may not:

- write code;
- modify files;
- modify configuration;
- dispatch workers;
- invoke workers;
- execute tasks;
- create execution requests;
- apply remediation;
- perform self-improvement.

Implementation remains a future governed execution path after explicit approval.

## 7. Replay Continuity

Replay continuity requires:

- append-only improvement review replay events;
- immutable review artifact hash;
- proposal reference and proposal hash validation;
- evaluation reference and evaluation hash validation;
- result reference and result hash validation;
- canonical chain continuity validation;
- no replay repair;
- no replay mutation outside improvement review append-only events.

Replay may reconstruct review history. Replay may not infer missing review findings, approve a proposal, or apply an improvement.

## 8. Canonical Chain Continuity

`IMPROVEMENT_REVIEW_ARTIFACT_V1` must contain:

```text
canonical_chain_id
improvement_proposal_reference
improvement_proposal_hash
evaluation_reference
evaluation_hash
result_reference
result_hash
review_status
approval_recommended
approval_authority
implementation_authorized
replay_reference
artifact_hash
```

The canonical chain id must match the improvement proposal, evaluation, and result evidence.

Missing or conflicting chain identity is fail-closed.

## 9. Relationship Between Improvement Proposal, Improvement Review, Improvement Approval, And Implementation

The relationship is:

```text
Improvement Proposal = proposed change derived from evaluation evidence.
Improvement Review = replay-visible assessment of the proposal.
Improvement Approval = explicit human-authorized governance decision.
Implementation = future governed execution of an approved improvement.
```

Ordering:

```text
IMPROVEMENT_PROPOSED
-> IMPROVEMENT_REVIEWED
-> APPROVAL_REQUIRED
-> FUTURE_IMPLEMENTATION_ONLY_IF_APPROVED
```

Review may recommend approval or identify gaps. It may not approve, reject, implement, or self-apply the improvement.

## Decision

Improvement Review Foundation is ready.

AiGOL can define review as a replay-visible assessment boundary over improvement proposals while preserving strict separation from approval, implementation, reflection, self-improvement, and governance mutation.

Final classification:

```text
IMPROVEMENT_REVIEW_FOUNDATION_STATUS = READY
```
