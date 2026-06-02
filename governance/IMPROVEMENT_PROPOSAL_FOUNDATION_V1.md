# IMPROVEMENT_PROPOSAL_FOUNDATION_V1

IMPROVEMENT_PROPOSAL_FOUNDATION_STATUS = READY

## Purpose

Define the formal boundary for improvement proposals generated from result evaluation evidence.

This is review only. It does not implement Improvement Proposal Runtime, approval, implementation, reflection, self-improvement, governance mutation, replay mutation, worker dispatch, or worker execution.

## Context

AiGOL now has:

```text
Execution
-> Completion
-> Result
-> Evaluation
```

`RESULT_EVALUATION_FOUNDATION_V1` defines how captured results may be evaluated without approving, certifying, mutating, or improving them.

The next missing concept is the boundary where evaluation evidence may become a proposed improvement while still preserving explicit approval and implementation separation.

## 1. What Is IMPROVEMENT_PROPOSAL_ARTIFACT_V1?

`IMPROVEMENT_PROPOSAL_ARTIFACT_V1` is a replay-visible proposal artifact that records a proposed improvement derived from evaluation evidence.

It records:

- which evaluation produced the improvement recommendation;
- which result the evaluation examined;
- which canonical chain produced the result;
- what improvement is proposed;
- why the improvement is proposed;
- what scope and constraints apply;
- which approval boundary is required before implementation;
- hashes and references for evaluation, result, execution, completion, and replay evidence.

`IMPROVEMENT_PROPOSAL_ARTIFACT_V1` is not:

- approval;
- implementation;
- execution request;
- worker task;
- result certification;
- reflection runtime;
- self-improvement runtime;
- governance mutation;
- replay repair.

## 2. Who May Create An Improvement Proposal?

Only AiGOL may create `IMPROVEMENT_PROPOSAL_ARTIFACT_V1`.

AiGOL may create an improvement proposal only after validating replay-visible evaluation evidence that recommends improvement.

Allowed creator:

```text
created_by = AIGOL
```

Human observations, worker reports, and provider-assisted evaluation may inform the evaluation evidence. They may not directly create the formal improvement proposal artifact.

## 3. Who May Never Create An Improvement Proposal?

The following may never directly create `IMPROVEMENT_PROPOSAL_ARTIFACT_V1`:

- provider;
- LLM;
- worker;
- human directly;
- replay system;
- result artifact;
- evaluation artifact;
- completion artifact;
- execution artifact;
- background process;
- external API;
- automatic self-improvement loop.

Humans may approve or reject a future approval boundary. Workers may produce evidence. Providers may propose language. None of those actors may directly persist formal improvement proposals.

## 4. Required Evaluation Evidence

Improvement proposal creation requires:

- valid `RESULT_EVALUATION_ARTIFACT_V1`;
- `improvement_recommended = true`;
- valid `RESULT_ARTIFACT_V1` reference or hash from the evaluation;
- valid canonical chain id continuity;
- valid result, execution, completion, and worker references;
- replay-visible evaluation evidence;
- deterministic improvement proposal text;
- explicit scope boundaries;
- explicit non-implementation status;
- replay reference for proposal creation.

If evaluation evidence is missing, corrupt, contradictory, or does not recommend improvement, proposal creation must fail closed.

## 5. Separation From Approval

An improvement proposal is not approval.

The artifact may state that an improvement is proposed. It may not:

- approve the improvement;
- authorize implementation;
- create an execution request;
- change runtime state;
- mutate governance;
- mutate replay;
- mark any result as accepted or certified.

Approval remains a separate explicit human-authorized governance transition.

## 6. Separation From Implementation

An improvement proposal is not implementation.

The artifact may describe a possible change. It may not:

- write code;
- modify configuration;
- dispatch a worker;
- invoke a worker;
- execute a task;
- apply a remediation;
- change result or evaluation history;
- perform self-improvement.

Implementation, if ever allowed, must follow future governed approval, execution request, dispatch, invocation, execution, completion, result, and replay boundaries.

## 7. Replay Continuity

Replay continuity requires:

- append-only improvement proposal replay events;
- immutable improvement proposal artifact hash;
- evaluation reference and evaluation hash validation;
- result reference and result hash validation;
- upstream execution and completion reference validation;
- canonical chain continuity validation;
- no replay repair;
- no replay mutation outside improvement proposal append-only events.

Replay may reconstruct the proposal history. Replay may not infer missing evaluation evidence, approve a proposal, or apply an improvement.

## 8. Canonical Chain Continuity

`IMPROVEMENT_PROPOSAL_ARTIFACT_V1` must contain:

```text
canonical_chain_id
evaluation_reference
evaluation_hash
result_reference
result_hash
execution_reference
completion_reference
worker_reference
proposal_status
approval_required
implementation_authorized
replay_reference
artifact_hash
```

The canonical chain id must match the evaluation and result evidence.

Missing or conflicting chain identity is fail-closed.

## 9. Relationship Between Result, Evaluation, Improvement Proposal, Approval, And Implementation

The relationship is:

```text
Result = captured worker output.
Evaluation = replay-visible observations about the captured result.
Improvement Proposal = proposed change derived from evaluation evidence.
Approval = explicit human-authorized governance decision.
Implementation = future governed execution of an approved improvement.
```

Ordering:

```text
RESULT_CAPTURED
-> EVALUATED
-> IMPROVEMENT_PROPOSED
-> APPROVAL_REQUIRED
-> FUTURE_IMPLEMENTATION_ONLY_IF_APPROVED
```

An improvement proposal may bridge evaluation to future approval. It may not skip approval or perform implementation.

## Decision

Improvement Proposal Foundation is ready.

AiGOL can define improvement proposals as replay-visible, chain-bound artifacts derived from evaluation evidence while preserving strict separation from approval, implementation, reflection, self-improvement, and governance mutation.

Final classification:

```text
IMPROVEMENT_PROPOSAL_FOUNDATION_STATUS = READY
```
