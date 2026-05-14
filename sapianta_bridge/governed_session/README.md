# Governed Execution Session v1

`GOVERNED_EXECUTION_SESSION_V1` defines the first canonical governed execution session layer for SAPIANTA / AiGOL.

The session binds existing bounded artifacts:

```text
ChatGPT ingress
-> natural language to envelope
-> execution envelope
-> active provider invocation
-> result return loop
-> session evidence
```

The session layer links references and validates completeness. It does not orchestrate, retry, route providers, schedule work, create follow-up tasks, invoke multiple providers, or mutate governance decisions.

## Invariant

`SESSION != ORCHESTRATION`

A session may bind lifecycle steps. It may not become an autonomous executor.
