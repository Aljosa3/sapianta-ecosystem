# Governed Execution Session v1

`GOVERNED_EXECUTION_SESSION_V1` creates the first canonical governed execution session substrate for SAPIANTA / AiGOL.

The session binds existing bounded components into one deterministic lifecycle:

```text
ChatGPT ingress
-> natural language to envelope
-> bounded envelope
-> active provider invocation
-> result return loop
-> replay-safe session evidence
```

The session is single-session, single-provider, and single-invocation. It does not choose providers, retry failed execution, fallback to another provider, schedule future tasks, create follow-up tasks, mutate governance decisions, or bypass validation.

## Invariants

- `SESSION != ORCHESTRATION`
- `SESSION != AUTONOMOUS EXECUTION`
- `ONE SESSION == ONE PROVIDER INVOCATION`
- `SESSION EVIDENCE MUST BE REPLAY SAFE`
