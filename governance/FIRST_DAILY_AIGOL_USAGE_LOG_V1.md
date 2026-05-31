# FIRST_DAILY_AIGOL_USAGE_LOG_V1

## Summary

Daily-use evidence was collected on 2026-05-31 using the existing `run-governed` operator command.

## Operation Counts

| Metric | Count |
| --- | ---: |
| Governed operations attempted | 2 |
| Successful operations | 1 |
| Failed operations | 1 |
| Fail-closed operations | 1 |
| Unexpected failures | 0 |
| Provider invocations requiring external network | 0 |
| Worker executions | 1 |
| Replay-visible successful operations | 1 |

## Operation 001

| Field | Value |
| --- | --- |
| Operation id | `FIRST_DAILY_AIGOL_USAGE_V1_OPERATION_001` |
| Worker | `filesystem` |
| Operation | `create-file` |
| Target | `/tmp/first_daily_aigol_usage_v1.txt` |
| Status | `SUCCEEDED` |
| Execution status | `SUCCEEDED` |
| Proposal id | `FIRST_DAILY_AIGOL_USAGE_V1_OPERATION_001:PROPOSAL` |
| Authorization id | `FIRST_DAILY_AIGOL_USAGE_V1_OPERATION_001:AUTHORIZATION` |
| Replay reference | `.aigol_daily_usage_runtime/FIRST_DAILY_AIGOL_USAGE_V1_OPERATION_001` |

Replay files observed:

```text
.aigol_daily_usage_runtime/FIRST_DAILY_AIGOL_USAGE_V1_OPERATION_001/provider/000_provider_proposal_created.json
.aigol_daily_usage_runtime/FIRST_DAILY_AIGOL_USAGE_V1_OPERATION_001/provider/001_provider_proposal_returned.json
.aigol_daily_usage_runtime/FIRST_DAILY_AIGOL_USAGE_V1_OPERATION_001/authorization/000_authorization_created.json
.aigol_daily_usage_runtime/FIRST_DAILY_AIGOL_USAGE_V1_OPERATION_001/authorization/001_authorization_returned.json
.aigol_daily_usage_runtime/FIRST_DAILY_AIGOL_USAGE_V1_OPERATION_001/worker/000_authorized_worker_request.json
.aigol_daily_usage_runtime/FIRST_DAILY_AIGOL_USAGE_V1_OPERATION_001/worker/001_filesystem_worker_execution.json
```

## Operation 002

| Field | Value |
| --- | --- |
| Operation id | `FIRST_DAILY_AIGOL_USAGE_V1_OPERATION_002` |
| Worker | `unknown` |
| Operation | `create-file` |
| Target | `should_not_exist_daily_usage.txt` |
| Status | `FAILED_CLOSED` |
| Execution status | `FAILED_CLOSED` |
| Failure reason | `unknown worker` |

## Operator Notes

The command is usable for a narrow filesystem operation.

The operator must provide several low-level fields manually:

- worker;
- operation;
- target;
- content;
- operation id;
- runtime root;
- workspace.

This is acceptable for first daily use, but it is friction for repeated daily operation.
