# Governance Primitive Substrate Effectiveness Assessment V1

Status: evidence-only assessment.

Assessment target:
recent governed primitive cycles.

Source artifacts:

- `docs/governance/EXECUTABLE_GOVERNANCE_PRIMITIVE_EVOLUTION_V1.md`
- `docs/governance/GOVERNED_CAPABILITY_MEMORY_FINALIZATION_V1.md`
- `docs/governance/GOVERNED_PREVIEW_RUNTIME_FINALIZATION_V1.md`
- `docs/governance/GOVERNED_TEST_EXECUTION_FINALIZATION_V1.md`
- `runtime/governance/capability_registry.py`
- `runtime/governance/preview_runtime.py`
- `runtime/governance/test_execution.py`
- `tests/test_governed_capability_memory.py`
- `tests/test_governed_preview_runtime.py`
- `tests/test_governed_test_execution.py`

This assessment does not change runtime behavior.

## Assessment Summary

The executable governance primitive substrate is effective for the recent governed capability, preview runtime, and test execution cycles.

It improved:

- prompt compression;
- operational consistency;
- duplicate prevention;
- boundedness;
- replay lineage visibility.

The strongest evidence is that repeated operational instructions were converted into small deterministic primitives:

- `GOVERNED_CAPABILITY_MEMORY_V1`
- `GOVERNED_PREVIEW_RUNTIME_EXECUTION_V1`
- `GOVERNED_TEST_EXECUTION_V1`

These primitives reduce the need to restate long operational constraints in every prompt while preserving governance boundaries.

## Prompt Compression

Before primitive evolution, prompts repeatedly had to restate:

- localhost only;
- no public binding;
- no daemon persistence;
- no deployment;
- no arbitrary shell execution;
- start -> validate -> stop lifecycle;
- targeted test execution only;
- no full test suite by default;
- non-execution by helper.

After primitive evolution, the instructions are represented as structured primitives:

- `LOCALHOST_PREVIEW_RUNTIME_V1` for bounded localhost preview capability;
- `preview_runtime.py` for preview request validation and command preparation;
- `test_execution.py` for targeted pytest command validation and preparation.

Assessment:
prompt compression improved.

The remaining prompt can reference the primitive instead of restating every operational boundary. This supports the goal of keeping `AGENTS.md` constitutional and concise rather than turning it into a procedural encyclopedia.

## Consistency

Consistency improved because repeated operational behavior now has stable code-level checks:

- preview lifecycle is always `start -> validate -> stop`;
- preview host is always `127.0.0.1`;
- preview port is always `8010`;
- preview runtime is always `uvicorn`;
- preview target is always `sapianta_system.sapianta_product.main:app`;
- governed test execution prepares only `pytest tests/test_governed_preview_runtime.py`;
- both helpers expose non-execution status.

The preview and test primitives now share a common replay vocabulary:

- primitive ID;
- request hash;
- command hash;
- scope hash;
- replay lineage references;
- deterministic result hash;
- explicit non-execution field.

Assessment:
consistency improved.

## Duplicate Prevention

Duplicate instruction pressure decreased because operational constraints moved from repeated prompt text into deterministic primitives and finalization artifacts.

Examples:

- Instead of repeatedly defining "localhost preview only", `GOVERNED_PREVIEW_RUNTIME_EXECUTION_V1` locks the preview scope.
- Instead of repeatedly warning against full test suite execution, `GOVERNED_TEST_EXECUTION_V1` encodes full-suite requests as forbidden by default.
- Instead of repeatedly explaining operational approval semantics, `GOVERNED_CAPABILITY_MEMORY_V1` defines capability approval, escalation, and revocation semantics.

Assessment:
duplicate prevention improved, but not complete.

Residual duplicate pressure remains because final reports still repeat explicit limitations for human readability. That repetition is acceptable evidence communication, not governance entropy.

## Boundedness

Boundedness improved materially.

The recent primitives explicitly prevent:

- deployment automation;
- daemon persistence;
- public runtime exposure;
- arbitrary subprocess execution;
- unrestricted shell execution;
- background execution;
- production mutation;
- CI/CD authority;
- autonomous operational authority.

The helpers prepare commands but do not execute them:

- preview result includes `server_started: false`;
- test execution result includes `executed: false`.

Assessment:
boundedness is strong.

The substrate supports operational acceleration without creating autonomous runtime authority.

## Replay Lineage

Replay lineage improved after the recent strengthening pass.

Both preview and test primitives now expose stable lineage fields:

- primitive identity;
- request hash;
- command hash;
- scope hash;
- replay lineage references;
- deterministic result hash.

This makes command preparation evidence replay-comparable without executing commands.

Assessment:
replay lineage improved and is now structurally consistent across the preview and test primitives.

## Effectiveness Matrix

| Dimension | Result | Evidence |
| --- | --- | --- |
| Prompt compression | Improved | Repeated operational rules moved into primitives. |
| Consistency | Improved | Preview and test helpers use deterministic request/result models. |
| Duplicate prevention | Improved | Scope locks and finalization artifacts reduce repeated prompt burden. |
| Boundedness | Strong | Helpers prepare commands only and expose non-execution fields. |
| Replay lineage | Improved | Preview and test results expose request, command, scope, and result hashes. |
| Autonomy containment | Preserved | No daemon, deployment, shell, CI/CD, or production authority introduced. |

## Remaining Limitations

The substrate remains intentionally limited:

- it does not execute commands;
- it does not start preview servers;
- it does not run tests automatically;
- it does not perform browser or screenshot validation;
- it does not choose tests dynamically;
- it does not orchestrate CI/CD;
- it does not deploy software;
- it does not grant persistent operational authority.

These limitations are constitutional boundaries, not defects.

## Conclusion

The recent governed primitive cycles validate the executable governance primitive evolution rule.

SAPIANTA successfully converted repeated operational prompt instructions into bounded, deterministic, replay-visible primitives while preserving constitutional constraints.

The substrate is effective because it improves operational clarity without expanding autonomy.

