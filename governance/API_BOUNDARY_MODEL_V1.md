# API Boundary Model V1

Status: API boundary classification only.

## Purpose

This artifact classifies API interaction surfaces for future governed execution implementations. It does not implement API execution.

## API Capability Classification

### QUERY

State: `RESTRICTED`.

API query may be considered only under explicit authorization, bounded endpoint scope, replay-visible request and response capture, and deterministic lineage.

Query is not automatically allowed.

### CREATE

State: `DENIED`.

API create is denied because it can create persistent external state.

### UPDATE

State: `DENIED`.

API update is denied because it can mutate external state and create replay divergence.

### DELETE

State: `DENIED`.

API delete is denied because it can destroy external state or evidence.

## API Fail-Closed Conditions

API interaction must fail closed on:

- ambiguous method
- unbounded endpoint
- missing replay capture
- mutation pressure
- hidden persistence
- authorization mismatch
- response lineage ambiguity

## Boundary Rule

No API capability may bypass authorization, replay lineage, or bounded classification.

