# Active ChatGPT Bridge v1

`ACTIVE_CHATGPT_BRIDGE_V1` defines the first bounded interaction-runtime bridge between ChatGPT-facing input and governed execution session output.

The bridge connects existing bounded components:

```text
ChatGPT input
-> ingress request
-> NL-to-envelope proposal
-> active provider invocation
-> result return loop
-> governed execution session
-> ChatGPT-facing response payload
```

The bridge is single-session, single-provider, and single-invocation. It does not route, retry, fallback, schedule, create follow-up tasks, mutate governance state, or autonomously interpret results.

## Invariants

- `ACTIVE_CHATGPT_BRIDGE != ORCHESTRATION`
- `BRIDGE_RESPONSE != AUTONOMOUS INTERPRETATION`
- `CHATGPT_INPUT != EXECUTION AUTHORITY`
