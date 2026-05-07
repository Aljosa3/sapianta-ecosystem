# ADR-0004: Governance Replay

## STATUS

Accepted as dormant architectural foundation.

## CONTEXT

Long-horizon governance needs replayability so decisions, milestones, constraints, and validation reasoning can be inspected after the fact. Replay must be deterministic and safe, especially when future AI sessions reconstruct architecture from persisted memory.

Replay must not imply live enforcement.

ACTIVE has no runtime meaning.

## DECISION

Define governance replay as deterministic inspection of historical architectural memory and decision lineage. Governance replay is observational only and does not execute runtime code, mutate state, activate policies, or enforce approvals.

Governance remains dormant, replay-safe, and observational only.

## CONSEQUENCES

SAPIANTA can preserve and inspect lineage without risking runtime side effects. Future replay UI or artifact lineage integration must be introduced through later ADRs and milestones.

## NON-GOALS

- Runtime replay execution
- Active governance reads
- Automated remediation
- Policy enforcement
- Runtime mutation
