# Governed Test Execution Evidence V1

Status: replay-safe test execution primitive evidence.

Primitive:
`GOVERNED_TEST_EXECUTION_V1`

## Evidence Summary

The governed test execution primitive provides deterministic validation and command preparation for one bounded targeted pytest command.

Prepared command:

```bash
pytest tests/test_governed_preview_runtime.py
```

The helper does not execute the command.

## Replay Visibility Evidence

The result model includes:

- primitive ID;
- request hash;
- command hash;
- scope hash;
- replay lineage references;
- deterministic result hash;
- `executed: false`.

These fields make repeated equivalent command-preparation evaluations
replay-comparable without granting execution authority.

## Implementation Evidence

Runtime helper:

- `runtime/governance/test_execution.py`

Tests:

- `tests/test_governed_test_execution.py`

Governance specification:

- `docs/governance/GOVERNED_TEST_EXECUTION_V1.md`

## Forbidden Boundary Evidence

The primitive escalates requests involving:

- full test suite by default;
- deployment;
- server start;
- shell chaining;
- arbitrary subprocess execution;
- destructive commands;
- background execution;
- production mutation.

## Validation Evidence

Required validation:

- `pytest tests/test_governed_test_execution.py`
- `python -m py_compile runtime/governance/test_execution.py`
- `git diff --check`

## Explicit Non-Execution Evidence

The result model includes:

- `executed: false`

No test command is run by the helper.
