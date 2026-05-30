# Constitutional Memory Authority Guarantees V1

Status: authority guarantees for Constitutional Memory retrieval.

## Core Guarantee

Retrieval is reference-only.

Retrieval does not create:

- authorization authority
- governance authority
- execution authority
- proposal authority
- replay authority
- mutation authority

## Boundary Rules

1. Retrieval output must be labeled `REFERENCE_RESULT`.
2. Retrieval output must include citations.
3. Retrieval output must be replay-visible.
4. Retrieval output must not be accepted as authorization.
5. Retrieval output must not be accepted as execution request.
6. Retrieval output must not mutate governance artifacts.
7. Retrieval output must not mutate replay artifacts.
8. Retrieval output must not silently resolve conflicts.
9. Provider-triggered retrieval is forbidden.
10. Worker-triggered retrieval is forbidden.

## Invariant Preservation

Retrieval preserves:

```text
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```

Constitutional Memory retrieves and cites. It does not propose, govern, execute, or record in place of replay.

