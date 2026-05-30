# Memory Based Response Inputs V1

Status: input analysis for `MEMORY_BASED_RESPONSE`.

## Input Classification

Citation bundle: `ALLOWED`

Constitutional references: `ALLOWED`

Acceptance evidence: `ALLOWED`

Certification evidence: `ALLOWED`

Position reviews: `ALLOWED`

Provider output: `FORBIDDEN`

Worker output: `FORBIDDEN`

Execution result: `FORBIDDEN`

Uncited memory: `FORBIDDEN`

## Required Input Properties

Inputs must be:

- citation-bound
- replay-visible
- reference-only
- reconstructable
- hash-verifiable where runtime artifacts exist

## Input Boundary

Provider and worker outputs remain outside V1 response construction because they belong to separate proposal and execution paths.

Using them would blur:

```text
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```
