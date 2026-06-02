# IMPROVEMENT_REVIEW_BOUNDARY_GUARANTEES_V1

## Scope

This artifact defines boundary guarantees for future Improvement Review Runtime.

It does not implement runtime behavior.

## Review Boundary

Improvement Review may assess an improvement proposal and record findings.

It may not create improvement proposals, approve proposals, reject proposals as a governance transition, implement changes, create execution requests, dispatch workers, invoke workers, perform reflection, or apply self-improvement.

## Creator Boundary

Only AiGOL may create `IMPROVEMENT_REVIEW_ARTIFACT_V1`.

Providers, workers, humans, and governance artifacts may provide bounded input evidence or context. They may not directly persist formal review artifacts.

## Proposal Boundary

Improvement review requires valid proposal evidence.

Review must fail closed if:

- proposal evidence is missing;
- proposal hash is corrupt;
- proposal status is not `IMPROVEMENT_PROPOSED`;
- approval is already encoded in the proposal;
- implementation is already authorized;
- canonical chain continuity fails;
- proposal contains approval or implementation authority.

## Approval Boundary

Improvement Review is not approval.

It must preserve:

```text
approval_reference = null
proposal_approved = false
proposal_rejected = false
approval_authority = false
```

Any future approval or rejection must pass through an explicit human-authorized governance boundary.

## Implementation Boundary

Improvement Review is not implementation.

It must preserve:

```text
implementation_authorized = false
implementation_reference = null
implementation_applied = false
implementation_authority = false
```

Any future implementation must pass through approved proposal, execution request, readiness, assignment, dispatch, invocation, execution, completion, result, and replay boundaries.

## Provider Boundary

Providers may contribute non-authoritative review text only when explicitly selected by AiGOL.

Providers may not:

- create review artifacts;
- approve proposals;
- reject proposals;
- authorize implementation;
- dispatch or invoke workers;
- mutate governance;
- mutate replay;
- apply self-improvement.

## Worker Boundary

Workers may provide reports or read-only evidence.

Workers may not:

- create review artifacts;
- approve their own proposed improvement;
- reject governance proposals;
- implement improvements without governed execution;
- mutate runtime state;
- mutate governance;
- mutate replay.

## Replay Boundary

Improvement review replay must be append-only and reconstructable.

Review must fail closed if:

- proposal replay is unavailable;
- proposal hash mismatches;
- evaluation hash mismatches;
- result hash mismatches;
- replay wrappers are corrupt;
- canonical chain id mismatches;
- review findings are not deterministic JSON evidence.

Replay may reconstruct review history. Replay may not infer missing review evidence, approve the proposal, or apply the proposal.

## Chain Boundary

Improvement Review must preserve canonical chain continuity across:

- improvement proposal;
- evaluation;
- result;
- execution;
- completion;
- worker identity;
- review artifact;
- replay event.

Missing or conflicting chain identity is fail-closed.

## Constitutional Boundary

Improvement Review preserves:

```text
LLM proposes
AiGOL governs
Worker executes
Replay records
```

Mapping:

- LLM proposes: provider assistance may contribute review text but remains non-authoritative;
- AiGOL governs: AiGOL validates proposal evidence and records the review boundary;
- Worker executes: worker output remains upstream evidence, not review authority;
- Replay records: replay records review evidence without approval or implementation.
