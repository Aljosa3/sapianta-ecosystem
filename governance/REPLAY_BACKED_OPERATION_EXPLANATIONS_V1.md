# REPLAY_BACKED_OPERATION_EXPLANATIONS_V1

## Status

`REPLAY_BACKED_OPERATION_EXPLANATIONS_STATUS = READY`

## Purpose

This milestone adds replay-backed human-readable explanations for governed operator operations.

The explanation layer answers:

```text
What happened?
Why did it happen?
Why was it authorized?
Why should the result be trusted?
```

using replay-visible evidence only.

## CLI Surface

The existing replay CLI now supports:

```text
python -m aigol.cli.aigol_cli replay explain \
  --operation-id <operation-id> \
  --runtime-root <runtime-root>
```

This is not a Human Prompt CLI and does not introduce new cognition runtime behavior.

## Evidence Sources

Explanations are derived from:

- provider replay evidence;
- authorization replay evidence;
- worker replay evidence;
- replay verification evidence;
- operation replay summary.

No hidden reasoning or speculative facts are used.

## Successful Explanation Content

For successful operations, the explanation includes:

- what operation occurred;
- what proposal was accepted;
- what authorization was granted;
- which worker executed;
- what result was produced;
- which replay evidence supports the result;
- why replay verification supports trust.

## Failure Behavior

If replay evidence is missing, corrupt, incomplete, or fails verification, the command returns:

```text
EXPLANATION_UNAVAILABLE
```

The unavailable response includes a replay-backed failure reason where available.

## Observed Smoke Evidence

Command:

```text
python -m aigol.cli.aigol_cli replay explain \
  --operation-id AIGOL-RUN-GOVERNED-8852CFA571D1 \
  --runtime-root .aigol_operator_runtime
```

Observed result:

```text
status = EXPLANATION_READY
explanation_type = SUCCESSFUL_OPERATION
replay_backed = True
fail_closed = False
```

The explanation stated:

- the operation completed a governed `CREATE_FILE`;
- proposal `AIGOL-RUN-GOVERNED-8852CFA571D1:PROPOSAL` was returned;
- authorization `AIGOL-RUN-GOVERNED-8852CFA571D1:AUTHORIZATION` was created;
- `FILESYSTEM_CREATE_WORKER` executed;
- replay verification returned `VERIFY_PASSED`.

## Boundary

This milestone does not introduce:

- new provider;
- new worker;
- new authorization model;
- new replay model;
- orchestration;
- planning;
- autonomous dispatch;
- Human Prompt CLI.

## Final Classification

```text
REPLAY_BACKED_OPERATION_EXPLANATIONS_STATUS = READY
```
