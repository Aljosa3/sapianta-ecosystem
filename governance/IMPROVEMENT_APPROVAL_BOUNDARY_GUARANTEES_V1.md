# IMPROVEMENT_APPROVAL_BOUNDARY_GUARANTEES_V1

## Scope

This artifact defines boundary guarantees for future Improvement Approval Runtime.

It does not implement runtime behavior.

## Approval Boundary

Improvement Approval may record an explicit human-authorized approve or reject decision for a reviewed improvement proposal.

It may not create improvement proposals, review proposals, implement changes, create execution requests, dispatch workers, invoke workers, perform reflection, perform self-modification, or apply self-improvement.

## Human Authority Boundary

Only explicit human authority may approve or reject.

AiGOL may validate evidence and record the decision. AiGOL may not autonomously approve or reject.

The approval artifact must preserve:

```text
decision_authority = HUMAN
recorded_by = AIGOL
aigol_autonomous_approval = false
```

## Review Boundary

Approval requires valid review evidence.

Approval must fail closed if:

- review evidence is missing;
- review hash is corrupt;
- review status is not `IMPROVEMENT_REVIEWED`;
- proposal reference mismatches;
- evaluation reference mismatches;
- result reference mismatches;
- canonical chain continuity fails;
- review contains implementation authority.

## Implementation Boundary

Approval is not implementation.

Approval must preserve:

```text
implementation_reference = null
implementation_performed = false
execution_requested = false
worker_dispatched = false
worker_invoked = false
```

An approved decision may authorize future implementation, but implementation requires separate governed lifecycle artifacts.

## Governance Mutation Boundary

Approval records a decision. It does not mutate governance.

Approval may not:

- rewrite governance artifacts;
- alter constitutional rules;
- modify proposal, review, evaluation, result, execution, or completion artifacts;
- repair replay;
- silently alter approval semantics;
- create self-modifying governance paths.

## Provider Boundary

Providers may not approve or reject improvement proposals.

Providers may not:

- create approval artifacts;
- supply decision authority;
- authorize implementation;
- create execution requests;
- dispatch or invoke workers;
- mutate governance;
- mutate replay;
- apply self-improvement.

## Worker Boundary

Workers may not approve or reject improvement proposals.

Workers may not:

- create approval artifacts;
- approve their own proposed improvement;
- authorize implementation;
- mutate runtime state;
- mutate governance;
- mutate replay.

## Replay Boundary

Improvement approval replay must be append-only and reconstructable.

Approval must fail closed if:

- human authorization evidence is missing;
- review replay is unavailable;
- review hash mismatches;
- proposal hash mismatches;
- evaluation hash mismatches;
- result hash mismatches;
- replay wrappers are corrupt;
- canonical chain id mismatches.

Replay may reconstruct approval history. Replay may not infer authorization, alter decision outcome, or implement a decision.

## Chain Boundary

Improvement Approval must preserve canonical chain continuity across:

- improvement review;
- improvement proposal;
- evaluation;
- result;
- execution;
- completion;
- worker identity;
- approval artifact;
- replay event.

Missing or conflicting chain identity is fail-closed.

## Constitutional Boundary

Improvement Approval preserves:

```text
LLM proposes
AiGOL governs
Worker executes
Replay records
```

Mapping:

- LLM proposes: provider assistance remains non-authoritative and cannot approve;
- AiGOL governs: AiGOL validates evidence and records the human-authorized decision;
- Worker executes: worker output remains upstream evidence, not approval authority;
- Replay records: replay records approval evidence without implementation or mutation.
