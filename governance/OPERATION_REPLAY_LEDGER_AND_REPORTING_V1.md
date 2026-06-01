# OPERATION_REPLAY_LEDGER_AND_REPORTING_V1

## Status

`OPERATION_REPLAY_LEDGER_AND_REPORTING_STATUS = READY`

## Purpose

This milestone adds operator visibility across existing operator runtime replay evidence.

It is driven by `FIRST_REAL_WORKFLOW_DISCOVERY_V1`, which identified operation replay ledger and usage reporting as the highest-value future workflow.

This milestone does not introduce:

- new architecture;
- new provider;
- new worker;
- new authority model;
- orchestration;
- planning.

## Implemented Capability

The existing replay CLI now supports:

```text
python -m aigol.cli.aigol_cli replay report \
  --runtime-root .aigol_operator_runtime
```

The report lists operations found under:

```text
<runtime_root>/<operation_id>/
  provider/
  authorization/
  worker/
```

## Operation Ledger Fields

Each operation entry includes:

- operation id;
- status;
- worker;
- operation type;
- timestamp;
- replay status;
- proposal id;
- authorization id;
- replay reference;
- missing evidence;
- verification evidence flags.

## Aggregate Statistics

The report provides:

- total operations;
- successful operations;
- fail-closed operations;
- verification failures;
- success rate;
- fail-closed rate;
- worker usage;
- operation type usage.

## Weekly Usage Summary

The report includes a deterministic human-readable summary.

Example:

```text
1 operations inspected; 1 succeeded; 0 failed closed or failed verification; 0 replay verification failures.
```

## Explanation Model

Every aggregate result is derived from replay-backed operation entries.

Each operation is verified using the existing operator replay verification compatibility path.

The report can explain:

- what happened;
- which worker ran;
- which operation type occurred;
- whether replay verification passed;
- which evidence files support the operation;
- which replay chains failed verification.

## Fail-Closed Behavior

The report fails closed when:

- the operator runtime root is missing;
- the runtime root contains no operation records;
- an operation replay chain cannot be trusted.

Broken operation chains appear as verification failures instead of being silently omitted.

## Observed Smoke Evidence

Command:

```text
python -m aigol.cli.aigol_cli replay report --runtime-root .aigol_operator_runtime
```

Observed result:

```text
status = REPORT_READY
operation_count = 1
successful_operations = 1
verification_failures = 0
operation = AIGOL-RUN-GOVERNED-8852CFA571D1 | SUCCEEDED | FILESYSTEM_CREATE_WORKER | CREATE_FILE | VERIFY_PASSED
```

## Final Classification

```text
OPERATION_REPLAY_LEDGER_AND_REPORTING_STATUS = READY
```
