# Governed Preview Runtime Finalization V1

Status: constitutional finalization of bounded preview runtime lifecycle.

Finalized primitive:
`GOVERNED_PREVIEW_RUNTIME_EXECUTION_V1`

Finalized capability:
`LOCALHOST_PREVIEW_RUNTIME_V1`

Certification state:
`CERTIFIED_BOUNDED_PREVIEW_RUNTIME`

## Purpose

This document finalizes the first bounded preview runtime lifecycle primitive for SAPIANTA.

The finalized primitive provides deterministic preparation and validation for a temporary localhost preview lifecycle:

start -> validate -> stop

It does not provide deployment orchestration, autonomous runtime management, daemon lifecycle automation, unrestricted shell execution, or production runtime governance.

## Lifecycle Semantics

The finalized lifecycle is:

1. start: prepare the bounded localhost preview command.
2. validate: use the approved preview for bounded visual and runtime verification.
3. stop: terminate the temporary preview process after validation.

The helper prepares and validates the lifecycle. It does not silently execute it.

## Capability Scope Lock

The finalized scope is locked to:

- capability: `LOCALHOST_PREVIEW_RUNTIME_V1`
- host: `127.0.0.1`
- port: `8010`
- runtime: `uvicorn`
- target: `sapianta_system.sapianta_product.main:app`
- lifecycle: `start -> validate -> stop`
- temporary local preview only

Any deviation requires escalation.

## Replay-Safe Preview Semantics

Preview runtime validation produces deterministic evidence:

- primitive ID;
- capability ID;
- decision;
- approved, rejected, or escalation state;
- prepared command when approved;
- lifecycle;
- forbidden boundary checks;
- reason;
- request hash;
- command hash;
- scope hash;
- replay lineage references;
- deterministic hash;
- `server_started: false`.

The evidence is replay-visible and does not mutate runtime state.

## Deterministic Command Preparation

The only approved prepared command is:

```bash
uvicorn sapianta_system.sapianta_product.main:app --host 127.0.0.1 --port 8010
```

This command is returned as bounded operational evidence. The helper does not execute it.

## Escalation Boundaries

Escalation is required for:

- host changes;
- port changes;
- target changes;
- lifecycle changes;
- persistence semantics;
- deployment semantics;
- background execution;
- public network exposure;
- mutation scope expansion;
- runtime engine changes.

The primitive favors explicit escalation over silent operational expansion.

## Non-Deployment Semantics

This finalization explicitly confirms:

- no server auto-start introduced;
- no deployment automation introduced;
- no daemon persistence introduced;
- no public runtime exposure introduced;
- no unrestricted subprocess execution introduced;
- no autonomous orchestration introduced;
- no production runtime lifecycle introduced.

## Constitutional Position

This primitive is an executable governance primitive under `EXECUTABLE_GOVERNANCE_PRIMITIVE_EVOLUTION_V1`.

It converts repeated operational instructions about localhost preview execution into a bounded, deterministic, replay-visible helper without expanding runtime authority.
