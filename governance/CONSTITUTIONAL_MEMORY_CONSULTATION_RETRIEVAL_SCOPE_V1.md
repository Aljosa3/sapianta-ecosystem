# Constitutional Memory Consultation Retrieval Scope V1

Status: retrieval scope model for consultation activation.

## Allowed Retrieval

Allowed:

- constitutional specifications
- canonical invariants
- authority invariants
- freeze documents
- baseline guarantees
- acceptance evidence
- certification evidence
- position reviews
- governance reviews
- canonical replay and authority language

Classification: `ALLOWED`

## Conditional Retrieval

Conditional:

- operational replay evidence
- runtime reconstruction outputs
- derived summaries

Allowed only when explicitly requested, replay-visible, and treated as derived evidence.

Classification: `CONDITIONAL`

## Forbidden Retrieval

Forbidden:

- hidden memory
- vector memory
- semantic memory
- provider-private context
- worker-private state
- uncited constitutional claims
- inferred missing rules
- authorization decisions
- execution requests
- worker instructions

Classification: `FORBIDDEN`

## Scope Boundary

Consultation activation must map routing evidence to an explicit retrieval scope compatible with the existing Constitutional Memory access catalog.

Unsupported or ambiguous scopes fail closed.

