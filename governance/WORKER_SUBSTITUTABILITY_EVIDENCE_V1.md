# Worker Substitutability Evidence V1

Status: Worker substitutability evidence review.

## Substitutability Claim

Attaching an external Worker would demonstrate that Worker substitutability is implementation reality, not only architectural theory.

## Why External Worker Matters

Current execution is internal and read-only. An external Worker would prove that:

- Worker identity can be explicit and replay-visible outside the current internal capability functions.
- AiGOL authorization can remain the only execution gate.
- Worker execution can be swapped behind a deterministic attachment boundary.
- Worker result evidence can remain replay-visible and non-authoritative.
- Worker remains execution-only even when externalized.

## Evidence Already Present

Worker substitutability is supported by:

- `REAL_WORKER_ATTACHMENT_MODEL_V1`
- `WORKER_IDENTITY_MODEL_V1`
- `WORKER_ATTACHMENT_BOUNDARY_V1`
- `WORKER_REPLAY_MAPPING_V1`
- `WORKER_ATTACHMENT_FAIL_CLOSED_RULES_V1`
- read-only capability attachments
- explicit authorization evidence
- replay reconstruction patterns

## What External Worker Would Prove

External Worker implementation would prove:

```text
Worker substitution
=
authorized execution adapter replacement
```

and not:

```text
Worker substitution
=
new governance authority
```

## Constraint For Valid Proof

The proof is valid only if the external Worker:

- receives only authorized execution requests
- cannot self-authorize
- cannot mutate replay
- cannot mutate governance
- cannot expand capability scope
- records deterministic result evidence
- terminates explicitly
- remains read-only for the first attachment

