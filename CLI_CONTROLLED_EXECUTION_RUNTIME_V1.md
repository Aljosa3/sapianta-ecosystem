# CLI_CONTROLLED_EXECUTION_RUNTIME_V1

## Purpose

This milestone proves governed execution continuity through the AiGOL CLI:

Human request -> canonical ingress -> governance continuity -> dispatch authorization -> controlled execution handoff -> bounded provider continuity -> governed return continuity.

It removes browser lifecycle, service worker lifecycle, and Chrome Native Messaging policy instability from this runtime proof while preserving the existing governed execution path.

## CLI Governed Runtime Model

`aigol execution handoff` reuses the existing `create_controlled_execution_handoff(...)` function. The CLI does not create another execution topology, provider abstraction, retry loop, or autonomous continuation path.

## Bounded Provider Continuity

Provider continuity is surfaced from the existing controlled handoff artifact:

- `provider_invoked`
- `provider_result`
- `provider_exit_code`
- provider stdout/stderr
- provider diagnostic evidence

The provider remains the bounded Codex CLI provider path already governed by the runtime.

## Governed Return Continuity

The CLI creates a deterministic return artifact:

`CLI_GOVERNED_RETURN_CONTINUITY_V1`

Required fields include:

- `execution_status`
- `provider_invoked`
- `provider_result`
- `provider_exit_code`
- `governed_return_hash`
- `replay_identity`
- `execution_governance_hash`
- `continuity_verified`
- `fail_closed`
- `diagnostic_evidence`

The return hash is computed with canonical JSON hashing and is replay-visible.

## Replay Continuity

The CLI preserves the existing replay chain:

- ingress artifact hash;
- task package preview hash;
- human approval hash;
- handoff preview hash;
- dispatch authorization hash;
- continuity preview hash;
- execution governance hash;
- governed return hash.

No new replay identity model is introduced.

## Fail-Closed Guarantees

Allowed execution statuses remain:

- `EXECUTION_COMPLETED`
- `EXECUTION_FAILED`
- `EXECUTION_BLOCKED`

Invalid continuity blocks execution. Provider failures remain `EXECUTION_FAILED` and produce fail-closed governed return diagnostics. Successful provider completion produces `EXECUTION_COMPLETED`.

## Terminal Observability Model

The CLI renders deterministic execution result cards:

```text
==================================================
AIGOL EXECUTION RESULT
==================================================
Execution:
  EXECUTION_COMPLETED
Provider:
  INVOKED
Replay:
  <replay_identity>
Governed Return:
  GENERATED
Return Hash:
  <hash>
Exit Code:
  0
Continuity:
  VERIFIED
==================================================
```

There are no animations, background updates, hidden state mutation, retries, or autonomous loops.

## Boundary Confirmation

This milestone does not add:

- orchestration;
- retries;
- alternate providers;
- autonomous continuation;
- hidden execution;
- governance bypass;
- topology redesign.

It stabilizes CLI execution continuity and governed return observability by reusing the existing governed execution runtime.
