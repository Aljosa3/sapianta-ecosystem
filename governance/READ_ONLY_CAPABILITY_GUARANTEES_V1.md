# Read-Only Capability Guarantees V1

Status: read-only capability guarantees.

## Guarantee 1: Read-Only Behavior

The capability may inspect bounded runtime metadata only.

It must not write, delete, move, mutate, dispatch, invoke network actions, execute shell commands, or call APIs.

## Guarantee 2: Authorization Required

The capability may execute only after explicit authorization evidence exists.

Missing authorization fails closed.

## Guarantee 3: Replay Visibility

Capability request, validation, authorization, execution evidence, and termination must be replay-visible and append-only.

## Guarantee 4: Boundary Preservation

The capability must preserve:

- replay centrality
- constitutional freeze
- authority separation
- boundedness
- execution boundaries

## Guarantee 5: Fail-Closed Ambiguity

Capability ambiguity must stop the lifecycle.

No automatic retry, hidden recovery, inferred continuation, or mutation fallback is permitted.

