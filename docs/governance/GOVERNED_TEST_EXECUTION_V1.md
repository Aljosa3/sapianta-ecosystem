# Governed Test Execution V1

Status: bounded executable governance primitive.

Purpose: deterministic preparation and validation of targeted pytest commands.

This primitive exists under the SAPIANTA constitutional governance substrate. It formalizes a narrow test execution preparation model without introducing unrestricted shell execution, autonomous test orchestration, server start, deployment, or production mutation.

## Allowed Scope

Initial allowed command:

```bash
pytest tests/test_governed_preview_runtime.py
```

Allowed behavior:

- targeted pytest command preparation;
- deterministic request validation;
- deterministic result hashing;
- forbidden boundary reporting;
- explicit non-execution by the helper.

## Forbidden Boundaries

The primitive must not allow:

- full test suite by default;
- deployment;
- server start;
- shell chaining;
- arbitrary subprocess execution;
- destructive commands;
- background execution;
- production mutation.

Any request crossing these boundaries must escalate instead of silently expanding trust.

## Execution Semantics

The helper prepares a command. It does not execute tests silently.

Execution remains a separate user/tooling action requiring explicit approval or direct user instruction.

## Deterministic Output

Validation output includes:

- approved/escalation state;
- prepared command when approved;
- reason;
- forbidden boundary checks;
- deterministic hash;
- `executed: false`.

## Relation to Governance Substrate

This primitive aligns with:

- `AGENTS.md`;
- `CODEX_TASK_EXECUTION_PROTOCOL_V1.md`;
- `GOVERNED_CAPABILITY_MEMORY_V1.md`;
- `GOVERNED_PREVIEW_RUNTIME_EXECUTION_V1.md`;
- `EXECUTABLE_GOVERNANCE_PRIMITIVE_EVOLUTION_V1.md`.

It converts repeated targeted validation instructions into a small deterministic governance primitive instead of expanding textual prompt requirements.

## Known Limitations

This primitive does not:

- run tests;
- select tests dynamically;
- run full suites by default;
- start preview servers;
- execute arbitrary shell commands;
- manage background jobs;
- mutate production runtime state.

