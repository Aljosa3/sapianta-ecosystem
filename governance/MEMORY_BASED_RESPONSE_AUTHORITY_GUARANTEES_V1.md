# Memory Based Response Authority Guarantees V1

Status: authority preservation guarantees for Memory-Based Response.

## Authority Status

`MEMORY_BASED_RESPONSE_AUTHORITY_STATUS`: `PRESERVED`

The response is non-authoritative.

It must never become:

- governance authority
- authorization authority
- execution authority
- provider authority
- worker authority
- replay authority
- memory mutation authority

## Required Labels

Every response must declare:

```text
authority_status = REFERENCE_ONLY
```

and:

```text
decision_status = NOT_A_DECISION
```

## Separation Rule

Memory-Based Response may explain cited evidence.

It may not decide what should happen next except to state that a separate governed path is required for decisions, execution, provider use, or worker use.
