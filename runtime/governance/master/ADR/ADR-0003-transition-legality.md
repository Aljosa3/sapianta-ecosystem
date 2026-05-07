# ADR-0003: Transition Legality

## STATUS

Accepted as dormant architectural foundation.

## CONTEXT

Governed systems need explicit reasoning about which state transitions are valid. Without transition legality, governance records can become ambiguous and difficult to replay.

SAPIANTA is not activating transition enforcement in this milestone. It is preserving the concept for future deterministic validation.

ACTIVE has no runtime meaning.

## DECISION

Record transition legality as an architectural concept for future governance reasoning. Transition legality describes why a transition may be considered valid or invalid, but this milestone does not implement runtime checks, enforcement, mutation, or active reads.

Governance remains dormant, replay-safe, and observational only.

## CONSEQUENCES

Future governance work has a deterministic vocabulary for transition review. The current runtime remains unchanged, and the Decision Spine and policy engine remain untouched.

## NON-GOALS

- Runtime transition enforcement
- Decision Spine modification
- Policy engine modification
- Approval validation execution
- Runtime activation
