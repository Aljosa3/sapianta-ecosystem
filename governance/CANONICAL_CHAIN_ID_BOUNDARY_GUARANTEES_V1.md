# CANONICAL_CHAIN_ID_BOUNDARY_GUARANTEES_V1

## Purpose

Record the boundary guarantees for canonical chain identity.

## AiGOL Boundary

AiGOL is the only actor that may create canonical chain identity.

AiGOL must:

- create the chain id at chain opening;
- bind it to human prompt and source routing evidence;
- propagate it to chain-aware artifacts;
- verify it at every downstream boundary;
- fail closed on mismatches;
- record chain identity in replay.

## Provider Boundary

Providers may never:

- create chain ids;
- mutate chain ids;
- supersede chain ids;
- merge chain ids;
- split chain ids;
- authorize chain propagation;
- repair missing chain evidence.

Provider output may be linked to a chain as evidence, but it is not identity authority.

## Worker Boundary

Workers may never:

- create chain ids;
- mutate chain ids;
- claim chain membership without assignment evidence;
- self-assign to a chain;
- self-dispatch because a chain id exists;
- self-invoke because a chain id exists;
- execute without governed assignment, dispatch, and invocation evidence.

Workers may receive chain-scoped work only after AiGOL governance boundaries.

## Human Boundary

The human prompt may initiate a chain.

Human action alone may not:

- create canonical identity outside AiGOL governance;
- mutate chain id;
- bypass proposal approval;
- bypass readiness;
- bypass worker assignment;
- bypass dispatch or invocation.

## Replay Boundary

Replay records chain identity and reconstructs chain history.

Replay may not:

- create chain ids;
- repair missing chain ids;
- infer chain membership without evidence;
- ignore hash mismatches;
- authorize execution.

## Fail-Closed Guarantees

Future chain-aware runtimes must fail closed on:

- missing chain id;
- malformed chain id;
- mismatched chain id;
- duplicate unrelated chain id;
- child artifact referencing a different chain;
- parent artifact missing required chain id;
- corrupt chain identity artifact;
- corrupt replay wrapper;
- provider-created chain id;
- worker-created chain id;
- replay-created chain id;
- chain mutation;
- hidden chain supersession;
- chain reconstruction mismatch.

## Authority Preservation

The chain id is identity only.

It does not grant:

- proposal authority;
- approval authority;
- execution request authority;
- readiness authority;
- worker assignment authority;
- dispatch authority;
- invocation authority;
- execution authority;
- completion authority.

Each stage still requires its own governed artifact and fail-closed validation.

## Constitutional Invariant

Canonical chain identity preserves:

```text
LLM proposes
AiGOL governs
Worker executes
Replay records
```

The chain id makes governance lineage visible. It does not collapse governance boundaries or create authority.

## Boundary Classification

The boundary guarantees are ready as a foundation. Runtime enforcement remains future work.
