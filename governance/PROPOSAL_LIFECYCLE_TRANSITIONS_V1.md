# Proposal Lifecycle Transitions V1

Status: transition model.

## Transition Principle

Proposal lifecycle transitions are governed state changes recorded as replay-visible evidence.

Providers cannot transition proposals.

Workers cannot approve proposals.

Replay cannot mutate proposals.

## Transition Table

| From | To | Actor | Human approval required | Rule |
| --- | --- | --- | --- | --- |
| Conversation evidence | `CREATED` | AiGOL | No | AiGOL records bounded proposal candidate |
| Provider suggestion | `CREATED` | AiGOL | No | Provider contributes evidence only |
| `CREATED` | `INSPECTED` | AiGOL | No | AiGOL validates structure, lineage, scope, and authority |
| `CREATED` | `REJECTED` | AiGOL | No | Malformed, unsupported, or boundary-violating proposal |
| `CREATED` | `EXPIRED` | AiGOL | No | Deterministic expiry rule applies |
| `INSPECTED` | `APPROVED` | Human | Yes | Human explicitly approves inspected proposal |
| `INSPECTED` | `REJECTED` | AiGOL | No | Inspection fails |
| `INSPECTED` | `REJECTED` | Human | No | Human declines |
| `INSPECTED` | `EXPIRED` | AiGOL | No | Deterministic expiry rule applies |
| `APPROVED` | execution request candidate | AiGOL | Approval already required | AiGOL derives governed execution request if valid |
| execution request candidate | `EXECUTED` | Worker | Approval evidence required | Worker executes only authorized bounded request |
| Any recorded lifecycle | `REPLAY_RECONSTRUCTED` | Replay | No | Replay reconstructs read-only history |

## Explicit Human Approval Transitions

Explicit human approval is required for:

```text
INSPECTED -> APPROVED
```

Explicit human approval must also be present before any future execution request can be derived for:

- write or mutation actions;
- external effects;
- worker execution;
- governance-sensitive actions;
- uncertain or elevated risk classifications.

## AiGOL-Only Transitions

AiGOL is the only actor that may:

- create a proposal artifact;
- inspect a proposal;
- reject a proposal due to governance or boundary failure;
- expire a proposal;
- derive a governed execution request from an approved proposal.

## Human Transitions

Human may:

- approve an inspected proposal;
- reject an inspected proposal.

Human may not:

- bypass AiGOL inspection;
- directly create execution authority;
- directly dispatch a worker;
- mutate replay history.

## Provider Transitions

Provider may contribute proposal evidence.

Provider may not:

- create lifecycle state;
- inspect;
- approve;
- reject;
- expire;
- execute;
- reconstruct;
- derive execution requests.

## Worker Transitions

Worker may only contribute the execution result that allows an approved proposal lineage to be marked `EXECUTED`.

Worker may not:

- approve proposals;
- infer missing approval;
- expand proposal scope;
- derive its own work;
- mutate governance;
- bypass replay.

## Replay Transitions

Replay may reconstruct lifecycle history as:

```text
REPLAY_RECONSTRUCTED
```

Replay reconstruction is read-only. It is evidence reconstruction, not lifecycle mutation.

## Fail-Closed Rules

Transitions must fail closed if:

- source state is missing;
- actor authority is invalid;
- human approval is required but missing;
- provider authority is implied;
- worker authority is implied before execution request authorization;
- replay lineage is missing;
- proposal hash cannot be reconstructed;
- state order is invalid;
- expiry has occurred;
- proposal content is malformed or unsupported.
