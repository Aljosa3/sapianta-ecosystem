# Governed Capability Scope Lock V1

Status: finalized scope lock declaration.

Capability:
`LOCALHOST_PREVIEW_RUNTIME_V1`

## Locked Scope

The locked capability scope is:

- capability ID: `LOCALHOST_PREVIEW_RUNTIME_V1`
- host: `127.0.0.1`
- runtime: `uvicorn`
- lifecycle: `start -> validate -> stop`
- temporary: `true`
- visual validation: `true`

## Locked Philosophy

The capability is a bounded operational affordance.

It is not:

- deployment authority;
- daemon authority;
- shell authority;
- orchestration authority;
- production runtime authority;
- self-modifying permission authority.

## Controlled Elements

The following may evolve only through governed review:

- port value;
- approved preview runtime;
- lifecycle stages;
- visual validation semantics;
- capability metadata;
- registry evidence format;
- test coverage.

## Escalation Boundary

Any request outside the locked scope requires renewed approval.

Escalation is mandatory for:

- host changes;
- port changes;
- runtime engine changes;
- lifecycle mutation;
- persistent process behavior;
- background execution;
- deployment;
- public exposure;
- expanded mutation scope.

## Revocation Boundary

Revocation must reject future capability requests.

Revocation must remain visible and must not rewrite historical capability evidence.

## Non-Inheritance Rule

Approval of `LOCALHOST_PREVIEW_RUNTIME_V1` does not authorize any other capability.

No capability may inherit operational authority implicitly from this scope lock.

