# Proposal Runtime State Model V1

Status: state model.

## State Purpose

The proposal runtime state model defines which proposal states are valid and which actor may cause state movement.

This artifact is design-only. It does not implement state mutation.

## Runtime-Valid States

```text
CREATED
INSPECTED
APPROVED
REJECTED
EXPIRED
EXECUTED
```

## Foundation Runtime Scope

The minimal runtime foundation may create:

```text
CREATED
```

All other states are lifecycle-compatible future states.

## State Meanings

| State | Meaning |
| --- | --- |
| `CREATED` | AiGOL recorded a proposal candidate |
| `INSPECTED` | AiGOL inspected the proposal structure, lineage, and boundaries |
| `APPROVED` | Explicit human approval was recorded after inspection |
| `REJECTED` | AiGOL or human rejected the proposal |
| `EXPIRED` | Proposal is no longer valid for future use |
| `EXECUTED` | A downstream governed execution request was executed by a worker |

## Allowed Transition Model

| From | To | Actor | Requirement |
| --- | --- | --- | --- |
| none | `CREATED` | AiGOL | Valid source evidence and replay reference |
| `CREATED` | `INSPECTED` | AiGOL | Inspection artifact |
| `CREATED` | `REJECTED` | AiGOL | Invalid source, structure, or boundary |
| `CREATED` | `EXPIRED` | AiGOL | Deterministic expiry rule |
| `INSPECTED` | `APPROVED` | Human | Explicit approval evidence |
| `INSPECTED` | `REJECTED` | AiGOL or Human | Inspection failure or human rejection |
| `INSPECTED` | `EXPIRED` | AiGOL | Deterministic expiry rule |
| `APPROVED` | `EXECUTED` | Worker | Governed execution request and worker result evidence |

## Illegal Transitions

The following transitions are illegal:

- provider to any status;
- replay to any mutating status;
- worker to `APPROVED`;
- worker to `INSPECTED`;
- conversation directly to `EXECUTED`;
- provider evidence directly to `APPROVED`;
- `CREATED` directly to `EXECUTED`;
- `REJECTED` to `APPROVED`;
- `EXPIRED` to `APPROVED`;
- `EXECUTED` to any earlier status.

## Transition Prevention Rules

Illegal transitions are prevented by requiring:

- actor identity;
- source state;
- target state;
- transition reason;
- replay reference;
- artifact hash;
- required approval evidence;
- required inspection evidence;
- required execution request reference for `EXECUTED`;
- deterministic fail-closed handling when any requirement is missing.

## Runtime Fail-Closed Conditions

State handling must fail closed if:

- source status is missing;
- target status is unsupported;
- actor is unauthorized;
- replay reference is missing;
- proposal hash cannot be reconstructed;
- provider authority is implied;
- human approval is missing for `APPROVED`;
- governed execution request reference is missing for `EXECUTED`;
- transition order is invalid.

## Replay Reconstruction

Replay may reconstruct state history from append-only events.

Replay reconstruction does not create state mutation authority.

Replay-derived views must preserve the original event order and artifact hashes.
