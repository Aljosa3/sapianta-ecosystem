# Intent Classifier Duplication Risks V1

Status: duplication risk analysis for Intent Classifier.

## Intent Routing

Risk:

- classifier could duplicate routing.

Boundary:

- classifier emits candidate destination evidence
- routing creates the routing artifact and enters the destination boundary

## Governance

Risk:

- classifier output could be mistaken for governance decision.

Boundary:

- classifier has no governance authority

## Authorization

Risk:

- `EXECUTION_REQUEST` classification could be mistaken for authorization.

Boundary:

- authorization remains separate and mandatory

## Provider Layer

Risk:

- classifier could become hidden provider invocation.

Boundary:

- classifier may classify provider proposal intent, but provider attachment invokes providers

## Worker Layer

Risk:

- classifier could become hidden worker dispatch.

Boundary:

- classifier may classify execution intent, but worker execution requires authorization

## Constitutional Memory Retrieval

Risk:

- classifier could duplicate memory retrieval.

Boundary:

- memory access retrieves citations; classifier may only consume cited replay-visible memory context

## Anti-Duplication Rule

Classifier scope must remain:

```text
input evidence
-> destination classification evidence
```

Nothing more.

