# GOVERNED_DOWNSTREAM_EXECUTION_GATE_V1

This milestone introduces the first constitutional downstream execution
authorization model.

## Scope

- explicit human approval
- replay-visible temporary authority tokens
- deterministic 300-second authorization windows
- revocation receipts
- authority receipts for `AUTHORIZED`, `REVOKED`, `EXPIRED`, and `REJECTED`

## Boundary

Execution authorization is not execution itself. AiGOL remains governance
authority; downstream AI systems receive only separately granted, bounded,
revocable eligibility.
