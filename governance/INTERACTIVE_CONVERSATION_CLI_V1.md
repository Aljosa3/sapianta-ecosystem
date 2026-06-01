# INTERACTIVE_CONVERSATION_CLI_V1

INTERACTIVE_CONVERSATION_CLI_STATUS = CERTIFIED

## Purpose

`INTERACTIVE_CONVERSATION_CLI_V1` adds a human-facing conversational loop:

```bash
python -m aigol.cli.aigol_cli conversation
```

The interface accepts repeated human prompts, exits gracefully on `exit` or `quit`, and delegates each non-empty prompt to the existing conversational runtime.

## Runtime Boundary

The interactive CLI is a shell over existing runtime capabilities:

- source-of-truth routing is recorded through `SOURCE_OF_TRUTH_ROUTER_RUNTIME_V1`;
- prompt ingress and conversation response are recorded through `PROMPT_TO_CONVERSATION_INTEGRATION_V1`;
- conversation events remain replay-visible under the interactive session runtime root;
- runtime failures are returned as fail-closed turn summaries.

The CLI does not create proposals, approvals, execution requests, dispatch records, worker assignments, worker invocations, or worker completions.

## Human Entry Capability

The supported entry point is:

```bash
python -m aigol.cli.aigol_cli conversation
```

The command presents:

```text
AiGOL >
```

Each prompt is assigned a deterministic turn-scoped prompt id:

```text
{session_id}:TURN-000001
```

## Replay Evidence

For every completed turn, AiGOL persists:

- a source-of-truth router replay record;
- a human prompt replay record;
- a provider-assisted conversation runtime replay record;
- a turn summary containing replay references.

Replay remains append-only at the underlying runtime artifact layer.

## Fail-Closed Behavior

If routing or conversation runtime handling raises an error, the interactive CLI:

- emits `FAILED_CLOSED: <reason>` to the human;
- records the turn as `FAILED_CLOSED` in the session summary;
- does not invoke workers;
- does not request execution;
- does not dispatch;
- does not invoke a worker.

## Constitutional Invariant

The interactive CLI preserves:

```text
LLM proposes
AiGOL governs
Worker executes
Replay records
```

In this version, only the conversation and replay portions are active. Workers remain outside the boundary and receive no authority from conversation.

## Validation

Focused validation passed:

```bash
python -m pytest tests/test_interactive_conversation_cli_v1.py
```

Result:

```text
6 passed
```

Integration validation passed:

```bash
python -m pytest tests/test_interactive_conversation_cli_v1.py tests/test_prompt_to_conversation_integration_v1.py tests/test_source_of_truth_router_runtime_v1.py
```

Result:

```text
38 passed
```

CLI smoke validation passed:

```bash
printf 'What is AiGOL?\nexit\n' | python -m aigol.cli.aigol_cli conversation --runtime-root /tmp/aigol_interactive_cli_smoke --session-id INTERACTIVE-SMOKE-000001
```

Result: the prompt loop accepted the question, returned the deterministic AiGOL response, and exited on `exit`.

## Certification

AiGOL CLI can now be certified as supporting an interactive conversational entry point for the current runtime.

Final classification:

```text
INTERACTIVE_CONVERSATION_CLI_STATUS = CERTIFIED
```
