# Governed Test Execution Scope Lock V1

Status: finalized scope lock declaration.

Primitive:
`GOVERNED_TEST_EXECUTION_V1`

## Locked Prepared Command

The only approved prepared command is:

```bash
pytest tests/test_governed_preview_runtime.py
```

The command is prepared only. It is not executed by the primitive.

## Locked Scope

Locked semantics:

- runner: `pytest`
- target: `tests/test_governed_preview_runtime.py`
- execution state: non-executing helper
- purpose: bounded targeted validation preparation
- output: deterministic approval or escalation result

## Controlled Changes

The following require governed review and renewed approval:

- changing the test target;
- allowing full suite execution by default;
- changing the test runner;
- adding command execution behavior;
- adding CI/CD behavior;
- adding server start behavior;
- adding shell features;
- adding background execution.

## Escalation Boundary

Escalation is mandatory for:

- full test suite request;
- deployment semantics;
- server start semantics;
- shell chaining;
- arbitrary subprocess semantics;
- destructive commands;
- background execution;
- production mutation.

## Non-Inheritance Rule

Approval of this primitive does not authorize:

- other pytest targets;
- full test suites;
- deployment;
- CI/CD orchestration;
- shell command execution;
- runtime orchestration.

