# Memory Based Response Output Model V1

Status: output model for future Memory-Based Response implementation.

## Allowed Output

Constitutional summary: `ALLOWED`

Citation references: `ALLOWED`

Artifact references: `ALLOWED`

Retrieval evidence: `ALLOWED`

Replay reference: `ALLOWED`

Limitation statement: `ALLOWED`

Missing/conflict status: `CONDITIONAL`

## Forbidden Output

Governance recommendation: `FORBIDDEN`

Execution recommendation: `FORBIDDEN`

Authorization recommendation: `FORBIDDEN`

Provider instruction: `FORBIDDEN`

Worker instruction: `FORBIDDEN`

Correction instruction: `FORBIDDEN`

## Required Presentation Boundary

The response may say:

```text
The cited artifacts indicate X.
```

The response must not say:

```text
AiGOL authorizes X.
Execute X.
Worker should do X.
Provider should produce X.
```

Any operational decision must occur through a separate governed path.
