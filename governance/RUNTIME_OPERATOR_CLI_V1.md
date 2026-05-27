# RUNTIME_OPERATOR_CLI_V1

## Purpose

`RUNTIME_OPERATOR_CLI_V1` exposes the completed governed cognition runtime through a minimal operator-facing command line interface.

This milestone is a bounded usability surface only. It does not introduce orchestration, autonomous execution, retries, async runtime behavior, provider mutation, write execution, shell execution, subprocess execution, workflow planning, or capability expansion.

## Operator Surface

Example:

```bash
python -m aigol.runtime.operator_cli "inspect runtime status"
```

The CLI accepts one operator prompt, invokes the existing readonly governed operator path, and renders:

- governed return status;
- normalized governed return summary;
- CLI invocation identifier;
- CLI evidence hash;
- operator usage identifier;
- operator usage evidence hash;
- activation evidence hash when the governed path reaches activation evidence.

## Implementation Boundary

The CLI reuses:

- `run_first_real_operator_usage`;
- the real OpenAI API invocation boundary;
- existing governed cognition flow;
- existing readonly execution providers;
- existing replay-visible activation and operator usage evidence.

The CLI adds only:

- `RuntimeOperatorCLIEvidence`;
- `run_runtime_operator_cli`;
- `reconstruct_runtime_operator_cli_lineage`;
- `main`.

No new provider, governance layer, execution authority, orchestration path, or autonomous runtime behavior is introduced.

## Evidence Model

Each CLI invocation emits immutable replay-visible evidence containing:

- `cli_invocation_id`;
- `operator_id`;
- `operator_prompt`;
- `cli_mode`;
- `operator_usage_id`;
- `operator_usage_evidence_hash`;
- `rendered_return`;
- `cli_status`;
- `cli_reason`;
- `created_at`;
- `evidence_hash`.

Allowed CLI statuses are:

- `COMPLETED`;
- `REJECTED`.

## Fail-Closed Behavior

The CLI fails closed when:

- prompt structure is malformed;
- cognition output is malformed;
- an unauthorized capability is requested;
- underlying governed runtime evidence is rejected;
- evidence reconstruction detects duplicate invocation identifiers;
- deterministic ordering is violated.

Rejected invocations remain replay-visible.

## Validation

Targeted validation for this milestone:

```bash
python -m pytest \
tests/test_operator_interaction_loop_v1.py \
tests/test_runtime_operator_cli_v1.py

python -m py_compile \
aigol/runtime/operator_interaction_loop.py \
aigol/runtime/operator_cli.py \
aigol/runtime/__init__.py

git diff --check
```
