# SAPIANTA Launcher Authority Model v1

## Document Role

This document formalizes future launcher semantics for the SAPIANTA ecosystem.

It is documentation-only. It does not implement a launcher, add entrypoints, activate domains, or introduce runtime orchestration.

## Future Launcher Shape

Potential future commands:
- `./sapianta validator`
- `./sapianta trading`
- `./sapianta governance`
- `./sapianta factory`

These commands are governance-aware entrypoint concepts. They are not currently implemented by this document.

## Routing Semantics

Future launcher routing must resolve:
- requested subsystem
- canonical repository root
- authority boundary
- activation status
- replay lineage requirements
- approval requirements

Routing must be deterministic and must fail closed when authority is ambiguous.

## Authority Checks

Before any future launcher executes a subsystem, it must verify:
- workspace root identity
- target repository authority
- subsystem activation status
- approved contract lineage
- replay lineage availability
- governance approval status when required

Architectural memory alone must never satisfy activation authority.

## Dormant Domain Behavior

Dormant domain commands must not execute production behavior.

For dormant domains such as Trading, future launcher behavior may only expose approved non-mutating views, validation plans, or replay-safe simulations after explicit implementation and review.

Dormant domain routing must clearly distinguish:
- contract inspection
- deterministic simulation
- validation-only execution
- production activation

Production activation requires separate approval lineage.

## Governance Command Behavior

`./sapianta governance` is a future concept for governance-aware inspection and validation.

It must not imply:
- runtime enforcement
- policy execution
- Decision Spine mutation
- autonomous governance evolution
- automatic approval execution

## Factory Command Behavior

`./sapianta factory` is a future concept for sandboxed proposal generation.

Factory routing must remain isolated from runtime authority. Factory proposals must not mutate runtime, governance memory, or domain repositories without explicit human-reviewed promotion.

## Future Orchestration Semantics

Any future launcher must be:
- deterministic
- bounded
- governance-aware
- replay-lineage aware
- authority-checking
- fail-closed

This model does not implement launcher execution.
