# Operator Result Presentation Model V1

Status: operator-facing presentation model.

## Presentation Contract

The governed result summary presents existing evidence using stable field names:

| Field | Meaning |
| --- | --- |
| Status | `ACCEPTED` or `REJECTED` |
| Reason | why the result was accepted or rejected |
| Capability Used | bounded capability target |
| Replay Reference | path or identifier for replay evidence |
| Replay Verification Status | `VERIFIED` or `UNVERIFIED` |
| Authority Boundary Reminder | invariant reminder |
| Evidence Summary | concise replay-derived evidence sentence |
| Recommended Next Action | bounded next operator action |

## Determinism

The presentation must be deterministic:

- stable field names
- stable ordering in rendered output
- replay-derived source metadata
- summary hash

## Human Readability

The presentation must be understandable without opening raw replay artifacts. Raw replay remains available and authoritative.

## Non-Authority

The presentation model must not:

- authorize execution
- validate execution
- execute capability work
- replace replay evidence
- hide failure details
- infer new capability scope

## Recommended Next Action Rules

Recommended next action must remain bounded:

- accepted result: use the governed result and retain replay reference
- unverified replay: inspect replay evidence before relying on result
- unsupported capability: choose a supported read-only capability
- missing authorization: request explicit authorization
- hidden continuation: remove continuation language
- other rejection: review reason and retry only if still needed
