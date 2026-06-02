# IMPROVEMENT_IMPLEMENTATION_FOUNDATION_V1

IMPROVEMENT_IMPLEMENTATION_FOUNDATION_STATUS = READY

## Purpose

Define the formal boundary where an approved improvement may become an implementation plan.

This is review only. It does not implement Improvement Implementation Runtime, execution request creation, code mutation, self-application, self-modification, reflection, self-improvement, governance mutation, replay mutation, worker dispatch, or worker execution.

## Context

AiGOL now has:

```text
Result
-> Evaluation
-> Improvement Proposal
-> Improvement Review
-> Improvement Approval
```

`IMPROVEMENT_APPROVAL_FOUNDATION_V1` defines an explicit human-authorized approval or rejection decision over a reviewed improvement proposal.

The next missing boundary is implementation planning: a replay-visible artifact that translates an approved improvement into a bounded plan without performing implementation.

## 1. What Is IMPROVEMENT_IMPLEMENTATION_PLAN_ARTIFACT_V1?

`IMPROVEMENT_IMPLEMENTATION_PLAN_ARTIFACT_V1` is a replay-visible planning artifact for an approved improvement.

It records:

- which approved improvement is being planned;
- which approval, review, proposal, evaluation, and result evidence support the plan;
- which canonical chain the plan belongs to;
- what implementation steps are proposed;
- what files, modules, or artifact classes are expected to be in scope;
- what constraints and non-goals apply;
- what validation would be required after implementation;
- whether execution request creation remains separate;
- hashes and references required for replay reconstruction.

`IMPROVEMENT_IMPLEMENTATION_PLAN_ARTIFACT_V1` is not:

- code change;
- execution request;
- worker task;
- dispatch;
- invocation;
- implementation completion;
- result certification;
- reflection runtime;
- self-improvement runtime;
- governance mutation;
- replay repair.

## 2. Who May Create It?

Only AiGOL may create `IMPROVEMENT_IMPLEMENTATION_PLAN_ARTIFACT_V1`.

AiGOL may create the plan only after validating an approved `IMPROVEMENT_APPROVAL_ARTIFACT_V1`.

Allowed creator:

```text
created_by = AIGOL
```

Human approval authorizes planning eligibility. It does not directly write the plan. Providers and workers may contribute bounded planning input only if explicitly recorded as non-authoritative evidence.

## 3. Required Approval Evidence

Implementation planning requires:

- valid `IMPROVEMENT_APPROVAL_ARTIFACT_V1`;
- approval decision of `APPROVED`;
- approval status of `APPROVED`;
- valid approval artifact hash;
- valid human authorization reference;
- valid improvement review reference and hash;
- valid improvement proposal reference and hash;
- valid evaluation reference and hash;
- valid result reference and hash;
- canonical chain continuity;
- replay-visible approval evidence;
- no implementation already performed;
- no execution request already created by approval;
- deterministic plan text and scope.

Rejected approvals may never create implementation plans.

If approval evidence is missing, corrupt, rejected, contradictory, or already implementation-bearing, planning must fail closed.

## 4. Separation From Implementation

Implementation planning is not implementation.

The plan may describe future steps. It may not:

- write code;
- modify files;
- modify configuration;
- create execution requests;
- dispatch workers;
- invoke workers;
- execute tasks;
- apply remediation;
- mutate existing lifecycle artifacts;
- perform self-application.

Implementation remains a separate future governed runtime path.

## 5. Replay Continuity

Replay continuity requires:

- append-only implementation plan replay events;
- immutable implementation plan artifact hash;
- approval reference and approval hash validation;
- review, proposal, evaluation, and result reference validation;
- human authorization reference preservation;
- canonical chain continuity validation;
- no replay repair;
- no replay mutation outside implementation plan append-only events.

Replay may reconstruct implementation planning history. Replay may not infer missing approval, create execution requests, or apply code changes.

## 6. Canonical Chain Continuity

`IMPROVEMENT_IMPLEMENTATION_PLAN_ARTIFACT_V1` must contain:

```text
canonical_chain_id
improvement_approval_reference
improvement_approval_hash
improvement_review_reference
improvement_review_hash
improvement_proposal_reference
improvement_proposal_hash
evaluation_reference
evaluation_hash
result_reference
result_hash
plan_status
execution_request_created
implementation_performed
replay_reference
artifact_hash
```

The canonical chain id must match the approval, review, proposal, evaluation, and result evidence.

Missing or conflicting chain identity is fail-closed.

## 7. Relationship Between Approval, Implementation Plan, Execution Request, And Actual Code Change

The relationship is:

```text
Approval = explicit human-authorized decision that permits future implementation planning.
Implementation Plan = replay-visible bounded plan for a future change.
Execution Request = future governed request to perform approved implementation work.
Actual Code Change = future implementation output produced only after governed execution.
```

Ordering:

```text
APPROVED
-> IMPLEMENTATION_PLAN_CREATED
-> FUTURE_EXECUTION_REQUEST
-> FUTURE_GOVERNED_IMPLEMENTATION
-> FUTURE_RESULT_AND_REPLAY
```

The implementation plan bridges approval to future execution request creation. It may not create the execution request or change code.

## Decision

Improvement Implementation Foundation is ready.

AiGOL can define implementation planning as a replay-visible, chain-bound boundary after human-approved improvement approval while preserving strict separation from execution requests, actual code mutation, self-application, self-improvement, governance mutation, and replay mutation.

Final classification:

```text
IMPROVEMENT_IMPLEMENTATION_FOUNDATION_STATUS = READY
```
