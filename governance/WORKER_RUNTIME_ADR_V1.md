# Worker Runtime ADR V1

Status: accepted foundation decision.

## Decision

AiGOL will define Worker Runtime as a downstream, capability-bound, replay-visible execution layer that can operate only after AiGOL validates a dispatch-ready execution request.

Worker Runtime will not be implemented in this foundation step.

## Context

AiGOL now has:

- proposal creation;
- proposal approval disposition;
- execution request creation.

Execution Request Runtime currently creates:

```text
EXECUTION_REQUEST_ARTIFACT_V1
status = CREATED
```

Worker Runtime requires a stronger future state:

```text
status = READY_FOR_DISPATCH
```

This ADR prevents `CREATED` execution requests from being treated as worker-dispatchable.

## Rationale

Worker Runtime must be explicit because execution is the first layer where real external effects may occur.

Without a distinct Worker boundary, AiGOL could accidentally conflate:

- proposal approval;
- execution request creation;
- dispatch authorization;
- worker assignment;
- execution;
- result evidence.

The Worker boundary preserves these as separate replay-visible steps.

## Decision Rules

1. A Worker is execution-only.
2. A Worker is not a provider, LLM, human, replay system, or governance artifact.
3. Workers may receive only replay-valid `READY_FOR_DISPATCH` execution requests.
4. Current `CREATED` execution requests may not reach workers.
5. AiGOL records worker assignment.
6. Workers may not self-assign.
7. Workers may not approve proposals or execution requests.
8. Workers may not expand scope.
9. Providers may not command workers.
10. Replay records and reconstructs worker evidence only.

## Consequences

Future Worker Runtime must implement:

- worker identity envelope;
- capability binding;
- assignment artifact;
- execution result artifact;
- termination artifact;
- fail-closed replay reconstruction.

Future dispatch work must first implement or certify:

```text
EXECUTION_REQUEST.CREATED -> READY_FOR_DISPATCH
```

## Non-Goals

This ADR does not implement:

- worker execution;
- dispatch;
- worker adapters;
- provider authority;
- worker result persistence;
- execution completion;
- deployment behavior.

## Known Gaps

- Worker Runtime is not implemented.
- Dispatch is not implemented.
- Execution request readiness is not implemented.
- Worker identity envelope is not implemented.
- Capability binding runtime is not implemented.
- Worker result and termination replay are not implemented.

## Final Decision

Worker Runtime foundation is accepted as a boundary model and remains ready with gaps until dispatch readiness and worker execution are separately implemented and certified.

```text
WORKER_RUNTIME_FOUNDATION_STATUS = READY_WITH_GAPS
```
