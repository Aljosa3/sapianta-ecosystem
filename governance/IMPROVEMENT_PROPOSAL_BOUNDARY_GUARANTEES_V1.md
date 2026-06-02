# IMPROVEMENT_PROPOSAL_BOUNDARY_GUARANTEES_V1

## Scope

This artifact defines boundary guarantees for future Improvement Proposal Runtime.

It does not implement runtime behavior.

## Proposal Boundary

Improvement Proposal may translate evaluation evidence into a proposed change.

It may not evaluate results, approve changes, implement changes, create execution requests, dispatch workers, invoke workers, perform reflection, or apply self-improvement.

## Creator Boundary

Only AiGOL may create `IMPROVEMENT_PROPOSAL_ARTIFACT_V1`.

Providers, workers, humans, and evaluation artifacts may provide input evidence or observations. They may not directly persist formal improvement proposal artifacts.

## Evaluation Boundary

Improvement proposal creation requires valid evaluation evidence.

The proposal may not be created if:

- evaluation evidence is missing;
- evaluation hash is corrupt;
- `improvement_recommended` is not true;
- result evidence is missing;
- canonical chain continuity fails;
- evaluation contains approval or implementation authority.

## Approval Boundary

Improvement Proposal is not approval.

It must preserve:

```text
approval_required = true
approval_reference = null
proposal_approved = false
approval_authority = false
```

Any future approval must pass through an explicit human-authorized governance boundary.

## Implementation Boundary

Improvement Proposal is not implementation.

It must preserve:

```text
implementation_authorized = false
implementation_reference = null
implementation_applied = false
implementation_authority = false
```

Any future implementation must pass through approved proposal, execution request, readiness, assignment, dispatch, invocation, execution, completion, result, and replay boundaries.

## Provider Boundary

Providers may propose language or observations only when explicitly selected by AiGOL.

Providers may not:

- create improvement proposal artifacts;
- approve proposals;
- authorize implementation;
- dispatch or invoke workers;
- mutate governance;
- mutate replay;
- apply self-improvement.

## Worker Boundary

Workers may provide reports or output evidence.

Workers may not:

- create improvement proposal artifacts;
- approve their own improvement;
- implement improvements without governed execution;
- mutate runtime state;
- mutate governance;
- mutate replay.

## Replay Boundary

Improvement proposal replay must be append-only and reconstructable.

Improvement proposal creation must fail closed if:

- evaluation replay is unavailable;
- evaluation hash mismatches;
- result hash mismatches;
- replay wrappers are corrupt;
- canonical chain id mismatches;
- proposal text is not deterministic JSON evidence.

Replay may reconstruct proposal history. Replay may not infer missing evaluation evidence, approve the proposal, or apply the proposal.

## Chain Boundary

Improvement Proposal must preserve canonical chain continuity across:

- evaluation;
- result;
- execution;
- completion;
- worker identity;
- proposal artifact;
- replay event.

Missing or conflicting chain identity is fail-closed.

## Constitutional Boundary

Improvement Proposal preserves:

```text
LLM proposes
AiGOL governs
Worker executes
Replay records
```

Mapping:

- LLM proposes: provider assistance may propose language but remains non-authoritative;
- AiGOL governs: AiGOL validates evaluation evidence and records the proposal boundary;
- Worker executes: worker output remains upstream evidence, not improvement authority;
- Replay records: replay records proposal evidence without approval or implementation.
