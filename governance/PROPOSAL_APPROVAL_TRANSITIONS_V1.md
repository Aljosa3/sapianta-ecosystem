# Proposal Approval Transitions V1

Status: transition model.

## Transition Principle

Proposal approval transitions are human decision evidence over an already inspected proposal.

Approval transitions do not execute.

Approval transitions do not dispatch workers.

Approval transitions do not mutate governance.

## Approval Transition Table

| From | To | Actor | Requirement |
| --- | --- | --- | --- |
| `INSPECTED` | `PENDING_APPROVAL` | AiGOL | Valid inspection artifact and replay evidence |
| `PENDING_APPROVAL` | `APPROVED` | Human | Explicit human approval decision |
| `PENDING_APPROVAL` | `REJECTED` | Human | Explicit human rejection decision |
| `PENDING_APPROVAL` | `EXPIRED` | AiGOL | Deterministic approval expiry rule |
| `APPROVED` | Proposal Lifecycle `APPROVED` | AiGOL | Valid approval evidence |
| `REJECTED` | Proposal Lifecycle `REJECTED` | AiGOL | Valid rejection evidence |
| `EXPIRED` | Proposal Lifecycle `EXPIRED` | AiGOL | Valid expiry evidence |

## Who May Approve

Only human operator:

```text
Human -> APPROVED
```

## Who May Reject

Human may reject during approval review.

AiGOL may reject earlier during inspection, or may record lifecycle rejection from valid human rejection evidence.

## Who May Expire

AiGOL may expire pending approval using deterministic expiry rules.

Human may choose an explicit expire decision only if the approval model supports `EXPIRE` as an operator disposition.

## Forbidden Transitions

The following transitions are forbidden:

- provider to `APPROVED`;
- provider to `REJECTED`;
- worker to `APPROVED`;
- worker to `REJECTED`;
- replay to any mutating approval state;
- `CREATED` directly to `APPROVED`;
- `PENDING_APPROVAL` directly to execution request;
- `APPROVED` directly to worker execution;
- `REJECTED` to `APPROVED`;
- `EXPIRED` to `APPROVED`;
- approval without inspection evidence;
- approval without proposal hash continuity.

## Required Evidence For `PENDING_APPROVAL`

Before `PENDING_APPROVAL`, replay must contain:

- proposal artifact;
- proposal artifact hash;
- inspection artifact;
- inspection artifact hash;
- inspection result;
- replay lineage;
- non-execution boundary evidence.

## Required Evidence For `APPROVED`

Before `APPROVED`, replay must contain:

- `PENDING_APPROVAL` record;
- explicit human approval decision;
- operator label;
- approval reason;
- proposal hash continuity;
- inspection hash continuity;
- non-execution flags.

## Replay Reconstruction

Replay reconstructs approval transitions in append-only event order.

Replay may prove an approval path valid or invalid.

Replay may not infer missing human approval.

## Fail-Closed Rules

Approval transition must fail closed if:

- proposal was not inspected;
- human decision is missing;
- actor is provider, worker, replay, or unknown;
- proposal hash mismatches;
- inspection hash mismatches;
- proposal expired;
- proposal was rejected;
- execution already occurred;
- approval claims authorization or execution authority.
