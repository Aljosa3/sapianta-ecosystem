# Constitutional Memory Consultation Boundary Guarantees V1

Status: boundary guarantees for the first consultation activation path.

## Reference-Only Boundary

Constitutional Memory Consultation returns evidence only:

- artifact references
- constitutional references
- citation references
- reconstruction metadata

It does not return:

- execution requests
- authorization decisions
- governance decisions
- provider requests
- worker requests
- worker instructions
- conversation responses

## Activation Boundary

Activation may begin only from a valid `INTENT_ROUTING_ATTACHMENT_RECORD` selecting `CONSTITUTIONAL_MEMORY_CONSULTATION`.

The activation must not be triggered directly by:

- provider output
- worker output
- unauthenticated runtime state
- execution result
- replay mutation

## Authority Preservation

Constitutional Memory remains:

```text
REFERENCE_ONLY
```

It does not gain:

- authorization authority
- governance authority
- execution authority
- proposal authority
- worker authority
- provider authority

## Bounded Retrieval

Retrieval is limited to the existing Constitutional Memory access path and its indexed artifact catalog.

The activation must not introduce unrestricted search, semantic lookup, vector retrieval, memory learning, or automatic memory updates.
