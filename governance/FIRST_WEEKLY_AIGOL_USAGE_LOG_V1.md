# FIRST_WEEKLY_AIGOL_USAGE_LOG_V1

## Summary

Weekly usage evidence was collected on 2026-05-31 through the hardened existing operator CLI.

## Successful Operations

| # | Target | Replay id | Status |
| ---: | --- | --- | --- |
| 1 | `weekly_aigol_usage_01.txt` | `AIGOL-RUN-GOVERNED-BE27CB9FA018` | `SUCCEEDED` |
| 2 | `weekly_aigol_usage_02.txt` | `AIGOL-RUN-GOVERNED-B657303B5D72` | `SUCCEEDED` |
| 3 | `weekly_aigol_usage_03.txt` | `AIGOL-RUN-GOVERNED-8BE76D93201F` | `SUCCEEDED` |
| 4 | `weekly_aigol_usage_04.txt` | `AIGOL-RUN-GOVERNED-B333C485FF1E` | `SUCCEEDED` |
| 5 | `weekly_aigol_usage_05.txt` | `AIGOL-RUN-GOVERNED-30845BA8A745` | `SUCCEEDED` |
| 6 | `weekly_aigol_usage_06.txt` | `AIGOL-RUN-GOVERNED-70805A4C0968` | `SUCCEEDED` |
| 7 | `weekly_aigol_usage_07.txt` | `AIGOL-RUN-GOVERNED-B1596635798C` | `SUCCEEDED` |
| 8 | `weekly_aigol_usage_08.txt` | `AIGOL-RUN-GOVERNED-09D25E8DE097` | `SUCCEEDED` |
| 9 | `weekly_aigol_usage_09.txt` | `AIGOL-RUN-GOVERNED-F95D0930FDA8` | `SUCCEEDED` |
| 10 | `weekly_aigol_usage_10.txt` | `AIGOL-RUN-GOVERNED-57372DCDE2AE` | `SUCCEEDED` |
| 11 | `weekly_aigol_usage_11.txt` | `AIGOL-RUN-GOVERNED-AD1C5D06BC70` | `SUCCEEDED` |
| 12 | `weekly_aigol_usage_12.txt` | `AIGOL-RUN-GOVERNED-9BDF5F0BBC9B` | `SUCCEEDED` |

## Fail-Closed Attempts

| # | Input | Result | Failure reason |
| ---: | --- | --- | --- |
| 13 | `worker=unknown` | `FAILED_CLOSED` | `unknown worker` |
| 14 | `operation=delete-file` | `FAILED_CLOSED` | `unknown operation` |
| 15 | missing workspace | `FAILED_CLOSED` | `workspace is invalid` |

## Replay Count Evidence

Successful operations produced:

```text
12 operation replay directories
72 replay files
6 replay files per successful operation
```

Fail-closed invalid inputs did not create worker output and did not create invalid target files.

## Replay Lookup Evidence

The operation replay lookup command:

```text
python -m aigol.cli.aigol_cli replay operation \
  --operation-id AIGOL-RUN-GOVERNED-BE27CB9FA018 \
  --runtime-root /tmp/aigol_weekly_usage_runtime
```

returned:

```text
status = SUCCEEDED
operator_status = READY
execution_status = SUCCEEDED
replay_summary.event_count = 6
```
