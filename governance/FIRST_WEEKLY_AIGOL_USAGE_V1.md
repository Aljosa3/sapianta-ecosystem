# FIRST_WEEKLY_AIGOL_USAGE_V1

## Status

`FIRST_WEEKLY_AIGOL_USAGE_STATUS = READY`

## Purpose

This milestone records repeated AiGOL operation after `OPERATOR_EXPERIENCE_HARDENING_V1`.

The purpose is evidence collection, not architecture expansion.

## Scope

The weekly usage pass executed 15 operator attempts through the existing CLI:

- 12 successful governed filesystem operations;
- 3 fail-closed invalid operations;
- 0 new workers;
- 0 new providers;
- 0 new governance models;
- 0 orchestration, planning, reflection, or autonomous behavior.

## Command Shape Used

Successful operations used:

```text
python -m aigol.cli.aigol_cli run-governed \
  --worker filesystem \
  --operation create-file \
  --target weekly_aigol_usage_<NN>.txt \
  --content FIRST_WEEKLY_AIGOL_USAGE_V1_<NN> \
  --runtime-root /tmp/aigol_weekly_usage_runtime \
  --workspace /tmp/aigol_weekly_usage_workspace
```

The operator omitted `--operation-id`, exercising the hardened default operation id behavior.

## Results

| Metric | Value |
| --- | ---: |
| Operator attempts | 15 |
| Successful governed operations | 12 |
| Fail-closed attempts | 3 |
| Unexpected failures | 0 |
| Success rate | 80% |
| Fail-closed rate | 20% |
| Successful replay chains | 12 |
| Successful replay files | 72 |
| Files created | 12 |
| Invalid fail-case files created | 0 |

## Observed Replay Example

Operation:

```text
AIGOL-RUN-GOVERNED-BE27CB9FA018
```

Replay lookup returned:

```text
status = SUCCEEDED
operator_status = READY
execution_status = SUCCEEDED
proposal_id = AIGOL-RUN-GOVERNED-BE27CB9FA018:PROPOSAL
authorization_id = AIGOL-RUN-GOVERNED-BE27CB9FA018:AUTHORIZATION
replay_summary.event_count = 6
```

## Weekly Finding

AiGOL is operationally useful for repeated bounded file creation.

The most important next priority is not provider expansion or worker expansion. The evidence points first to replay and operator UX hardening:

- persist early fail-closed operation records;
- provide aggregate operation history;
- provide weekly usage summaries without manual counting.

## Final Classification

```text
FIRST_WEEKLY_AIGOL_USAGE_STATUS = READY
```
