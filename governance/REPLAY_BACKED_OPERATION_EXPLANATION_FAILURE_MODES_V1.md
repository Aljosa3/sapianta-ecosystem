# REPLAY_BACKED_OPERATION_EXPLANATION_FAILURE_MODES_V1

## Fail-Closed Principle

Missing, corrupt, incomplete, or unverifiable replay must not produce a misleading explanation.

## Failure Output

Failure returns:

```text
EXPLANATION_UNAVAILABLE
```

## Failure Modes

| Failure | Required result |
| --- | --- |
| Missing operation replay | `EXPLANATION_UNAVAILABLE` |
| Missing provider evidence | `EXPLANATION_UNAVAILABLE` |
| Missing authorization evidence | `EXPLANATION_UNAVAILABLE` |
| Missing worker evidence | `EXPLANATION_UNAVAILABLE` |
| Corrupt replay JSON | `EXPLANATION_UNAVAILABLE` |
| Broken lineage | `EXPLANATION_UNAVAILABLE` |
| Replay verification failure | `EXPLANATION_UNAVAILABLE` |

## Reasoning Boundary

The system may explain only what replay evidence supports.

If replay evidence does not support a statement, the statement must not be emitted.

## Trust Boundary

When explanation is unavailable, the result must not be presented as trusted.

The correct operator-facing message is that replay-backed explanation could not be generated.
