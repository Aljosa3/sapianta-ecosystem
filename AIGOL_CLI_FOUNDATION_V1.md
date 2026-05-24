# AIGOL_CLI_FOUNDATION_V1

## Purpose

This milestone creates the first deterministic AiGOL governance CLI substrate for governed execution continuity.

The CLI is a canonical operational substrate, not an autonomous runtime, orchestrator, browser replacement, retry controller, or hidden execution engine.

## Command Model

Each command performs one deterministic governance step and emits replay-visible evidence:

- `aigol status`
- `aigol ingress generate`
- `aigol governance validate`
- `aigol continuity preview`
- `aigol dispatch authorize`
- `aigol execution handoff`
- `aigol diagnostics runtime`

The implementation lives under:

`aigol/cli`

## CLI Role vs Browser Cockpit

The Browser Companion remains the UX and operator cockpit.

The CLI becomes:

- deterministic governance substrate;
- terminal-visible continuity surface;
- integration backbone;
- explicit operational command shell.

It does not replace the cockpit or create hidden state mutation.

## Replay Continuity Model

The CLI reuses existing AiGOL artifacts and hashes:

- `CHATGPT_INGRESS_ARTIFACT_V1`
- governed task package preview hash;
- human approval hash;
- governed handoff preview hash;
- dispatch authorization hash;
- controlled execution continuity preview hash;
- controlled execution governance hash.

No new replay identity model is introduced.

## Execution Continuity Model

`aigol execution handoff` calls the existing `create_controlled_execution_handoff(...)` path.

It preserves:

- single path;
- single provider;
- fail-closed execution;
- replay-visible result hashes;
- bounded provider continuity;
- no autonomous continuation.

The CLI does not duplicate Native Messaging, Codex provider construction, or execution topology.

## Terminal Rendering Model

Terminal output uses simple deterministic cards:

```text
==================================================
AIGOL STATUS
==================================================
Ingress: READY
Governance: READY
Continuity: READY
Dispatch: READY
Execution: READY_FOR_CONTROLLED_EXECUTION_HANDOFF
Provider: NOT_INVOKED
Replay: NOT_STARTED
==================================================
```

There are no animations, background refreshes, hidden state mutation, or async rendering.

## Fail-Closed Guarantees

Invalid ingress artifacts remain rejected.

Invalid continuity chains block execution.

The CLI does not add:

- orchestration;
- retries;
- alternate providers;
- background workers;
- autonomous continuation;
- governance bypasses.

## Validation

Validation is covered by:

- `tests/test_aigol_cli_foundation_v1.py`
- `tests/test_controlled_execution_handoff_v1.py`
- `tests/test_valid_chatgpt_ingress_artifact_generation_v1.py`

The CLI foundation preserves AiGOL deterministic governance philosophy by wrapping existing governed runtime logic rather than replacing it.
