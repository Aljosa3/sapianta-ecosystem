# Governed Test Execution Acceptance Criteria V1

Status: finalized acceptance criteria.

Primitive:
`GOVERNED_TEST_EXECUTION_V1`

Certification state:
`CERTIFIED_BOUNDED_TEST_EXECUTION`

## Acceptance Requirements

The primitive is accepted only if:

- allowed command remains `pytest tests/test_governed_preview_runtime.py`;
- command preparation is deterministic;
- helper does not execute tests;
- full test suite is forbidden by default;
- shell chaining is forbidden;
- deployment semantics are forbidden;
- server start semantics are forbidden;
- background execution is forbidden;
- production mutation is forbidden;
- result hash remains stable for equivalent requests.

## Required Test Coverage

Tests must verify:

- allowed targeted pytest command is approved;
- full suite is forbidden by default;
- different test target escalates;
- deployment semantics escalate;
- server start is forbidden;
- shell chaining is forbidden;
- command generation is deterministic;
- scope description is non-executing;
- result hash is stable.

## Forbidden Acceptance Conditions

The primitive is not accepted if it introduces:

- unrestricted pytest execution;
- arbitrary shell execution;
- autonomous execution authority;
- CI/CD orchestration;
- deployment automation;
- daemon orchestration;
- background execution;
- production mutation.

## Current Acceptance State

Acceptance state:
`ACCEPTED_BOUNDED_TEST_EXECUTION`

Reason:
The primitive prepares one targeted pytest command, escalates boundary changes, and remains non-executing.

