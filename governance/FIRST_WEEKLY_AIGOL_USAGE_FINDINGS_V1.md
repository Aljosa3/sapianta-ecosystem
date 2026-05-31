# FIRST_WEEKLY_AIGOL_USAGE_FINDINGS_V1

## Findings Summary

Repeated usage confirms that AiGOL can operate as a real governed system for a narrow bounded filesystem use case.

The strongest evidence-based next priority is replay/operator UX hardening, not a new provider, new worker, or new authorization model.

## Operation Count

Status: `ADEQUATE_FOR_FIRST_WEEKLY_SAMPLE`

15 attempts were performed, within the requested 10-50 operation target.

## Success Rate

Status: `STABLE_FOR_SUPPORTED_SCOPE`

12 of 12 supported create-file requests succeeded.

Overall success rate across all attempts was 80%.

The 20% fail-closed rate was expected because three invalid cases were intentionally submitted.

## Replay Usefulness

Status: `HIGH_FOR_SUCCESSFUL_OPERATIONS`

For successful operations, replay lookup by operation id reconstructed:

- proposal id;
- authorization id;
- worker id;
- worker result;
- replay event count;
- replay event names.

The six-event replay summary was useful and reduced manual navigation.

## Authorization Friction

Status: `LOW`

Authorization remained visible without requiring manual operator steps.

No weekly evidence suggests changing the authorization model.

## Worker Usefulness

Status: `USEFUL_BUT_NARROW`

The filesystem create-file worker was reliable for repeated marker/file creation.

Observed demand only supports the current create-file path. The weekly sample does not yet justify new worker classes.

## Operator Usability

Status: `IMPROVED`

Default operation ids removed a major daily-use friction point.

Remaining friction:

- no aggregate weekly operation history command;
- successful replay summaries exist, but summary counts still required manual shell inspection;
- early fail-closed attempts are visible in command output but do not produce full operation replay chains.

## Provider Reliability

Status: `NOT_MEASURED_FOR_EXTERNAL_PROVIDERS`

The weekly run used the deterministic local operator provider.

No evidence was collected about remote OpenAI, Claude, Gemini, Codex, or local LLM reliability.

## Error Recovery

Status: `FAIL_CLOSED`

Invalid worker, invalid operation, and invalid workspace all failed closed.

No fallback execution occurred.

## Most Requested Worker Features

Observed requests used only:

```text
filesystem create-file
```

There is not enough usage evidence to claim demand for additional worker features.

## Key Finding

The next major development priority should be:

```text
Replay and operator usage visibility
```

before provider expansion, worker expansion, or authorization expansion.
