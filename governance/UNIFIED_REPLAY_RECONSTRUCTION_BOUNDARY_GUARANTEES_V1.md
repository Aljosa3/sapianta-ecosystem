# UNIFIED_REPLAY_RECONSTRUCTION_BOUNDARY_GUARANTEES_V1

## Guarantee Summary

Unified replay reconstruction is read-only inspection.

It may:

- locate replay evidence;
- validate artifact hashes;
- validate wrapper hashes;
- validate references;
- validate stage order;
- report missing evidence;
- report corruption;
- report authority boundary failures;
- summarize chain lineage.

It may not:

- create artifacts;
- approve artifacts;
- repair replay;
- mutate governance;
- mutate runtime state;
- create execution requests;
- mark readiness;
- assign workers;
- dispatch workers;
- invoke workers;
- execute workers;
- complete work;
- evaluate quality as authority;
- self-apply improvements.

## Provider Boundary

Provider evidence may be reconstructed only as non-authoritative evidence.

Providers may not:

- create reconstruction reports directly;
- repair missing replay;
- infer missing approvals;
- infer authorization;
- merge chains;
- mutate lineage;
- decide safe next action.

## Worker Boundary

Worker evidence may be reconstructed as execution or inspection output.

Workers may not:

- repair replay;
- approve improvements;
- authorize execution requests;
- create canonical chain ids;
- merge chains;
- mutate governance;
- mutate runtime state.

## Human Boundary

Human operators may request inspection views.

Inspection requests do not create approval, authorization, execution request, dispatch, invocation, or execution authority.

## AiGOL Boundary

AiGOL may:

- perform deterministic reconstruction;
- classify reconstruction status;
- report safe next actions;
- fail closed on ambiguity or corruption.

AiGOL may not:

- invent missing evidence;
- mutate artifacts;
- infer human authorization;
- silently merge ambiguous chains;
- reinterpret provider or worker evidence as authority.

## Replay Boundary

Replay records and reconstructs.

Replay may not:

- repair itself;
- create canonical identity;
- change event order;
- authorize decisions;
- create execution requests;
- dispatch workers;
- execute changes.

## Chain Boundary

Each lifecycle boundary remains separate.

Unified reconstruction may show adjacency between stages. It must not collapse stages into one authority event.

Forbidden collapses:

```text
conversation response = proposal approval
proposal approval = execution
implementation plan = execution request authorization
replay reconstruction = authorization
worker output = improvement approval
provider response = governance decision
```

## Fail-Closed Guarantees

Unified reconstruction fails closed on:

- missing mandatory evidence for a requested `VALID` view;
- corrupt artifact hash;
- corrupt replay wrapper hash;
- reference mismatch;
- chain id mismatch;
- ambiguous chain candidates;
- invalid lifecycle order;
- unauthorized authority flags;
- replay mutation evidence;
- governance mutation evidence;
- hidden execution state changes.

## Constitutional Invariant

Unified reconstruction preserves:

```text
LLM proposes
AiGOL governs
Human authorizes
Worker executes
Replay records
```

Meaning:

- LLM/provider output is evidence only;
- AiGOL validates and reports;
- human authorization remains explicit evidence;
- worker execution remains separate from governance authority;
- replay records without mutation.
