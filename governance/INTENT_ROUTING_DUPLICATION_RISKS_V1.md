# Intent Routing Duplication Risks V1

Status: duplication risk analysis for intent routing.

## Human Request Processing

Risk:

- routing could duplicate request normalization

Boundary:

- routing should consume Human Prompt evidence and emit route evidence
- it should not rewrite prompts

## Constitutional Memory Retrieval

Risk:

- routing could duplicate memory retrieval, citation generation, or source selection

Boundary:

- routing may select `CONSTITUTIONAL_MEMORY_CONSULTATION`
- memory access must perform retrieval

## Provider Attachment

Risk:

- routing could duplicate provider formatting, invocation, or proposal normalization

Boundary:

- routing may select `PROVIDER_PROPOSAL`
- provider adapter and attachment remain responsible for provider interaction

## Execution Authorization

Risk:

- routing to `EXECUTION_REQUEST` could be mistaken for authorization

Boundary:

- routing stops before authorization
- authorization remains separate and mandatory

## Governance

Risk:

- routing could become hidden governance if its destination choice is treated as a decision authority

Boundary:

- routing is evidence and lineage only
- governance remains separate
- replay visibility is mandatory

## Anti-Duplication Rule

Routing must be a narrow boundary:

```text
prompt evidence
-> route evidence
-> destination boundary
```

Nothing more.

