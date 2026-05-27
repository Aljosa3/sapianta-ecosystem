# REAL_OPERATOR_RUNTIME_EXPERIMENTS_V1

## Purpose

`REAL_OPERATOR_RUNTIME_EXPERIMENTS_V1` validates repeated readonly operational usage through the existing operator CLI and governed cognition runtime.

This milestone is experimentation and evidence only. It does not introduce orchestration, autonomous execution, retries, async runtime behavior, write execution, shell execution, subprocess execution, workflow planning, provider mutation, runtime mutation, or capability expansion.

## Scope

The experiment runner executes a bounded sequential set of operator prompts through:

1. existing operator CLI invocation logic;
2. existing real OpenAI API invocation boundary;
3. existing governed cognition flow;
4. existing readonly execution providers;
5. existing replay-visible governed return flow.

Allowed readonly capability surfaces remain:

- runtime metadata inspection;
- readonly filesystem inspection;
- readonly HTTP GET.

No new provider is added.

## Implementation

The implementation adds:

- `RealOperatorRuntimeExperimentsEvidence`;
- `run_real_operator_runtime_experiments`;
- `reconstruct_real_operator_runtime_experiments_lineage`.

The runner records:

- scenario count;
- completed count;
- rejected count;
- replay continuity validation;
- governed return consistency validation;
- immutable evidence hash;
- append-only experiment lineage.

## Fail-Closed Behavior

The experiment fails closed when:

- operator prompts are malformed;
- cognition output is malformed;
- unauthorized capability escalation is proposed;
- CLI invocation evidence is rejected;
- replay lineage ordering is invalid;
- duplicate experiment identifiers are detected;
- governed return consistency is not preserved.

Rejected scenarios remain replay-visible in the CLI records and experiment evidence.

## Validation

Targeted validation for this milestone:

```bash
python -m pytest \
tests/test_runtime_operator_cli_v1.py \
tests/test_real_operator_runtime_experiments_v1.py

python -m py_compile \
aigol/runtime/operator_cli.py \
aigol/runtime/real_operator_runtime_experiments.py \
aigol/runtime/__init__.py

git diff --check
```
