# Governed Preview Runtime Acceptance Criteria V1

Status: finalized acceptance criteria.

Primitive:
`GOVERNED_PREVIEW_RUNTIME_EXECUTION_V1`

Capability:
`LOCALHOST_PREVIEW_RUNTIME_V1`

## Acceptance Requirements

The primitive is accepted only if:

- lifecycle remains `start -> validate -> stop`;
- host remains `127.0.0.1`;
- port remains `8010`;
- runtime remains `uvicorn`;
- target remains `sapianta_system.sapianta_product.main:app`;
- command preparation is deterministic;
- helper does not start the server;
- helper does not execute subprocesses;
- forbidden boundaries are reported;
- escalation occurs for scope changes;
- result hash remains stable across equivalent evaluation.

## Required Validation Coverage

Tests must verify:

- valid localhost preview request accepted;
- host `0.0.0.0` escalated;
- different port escalated;
- persistent runtime escalated;
- deployment semantics escalated;
- command generation deterministic;
- lifecycle must be `start -> validate -> stop`;
- lifecycle description remains non-executing;
- result hash remains stable.

## Forbidden Acceptance Conditions

The primitive is not accepted if it introduces:

- server auto-start;
- deployment automation;
- daemon persistence;
- public runtime exposure;
- unrestricted subprocess execution;
- autonomous orchestration;
- production runtime lifecycle;
- arbitrary command execution;
- unbounded runtime authority.

## Current Acceptance State

Acceptance state:
`ACCEPTED_BOUNDED_PREVIEW_RUNTIME`

Reason:
The helper prepares and validates a bounded preview command, preserves lifecycle scope, escalates boundary changes, and remains non-executing.

