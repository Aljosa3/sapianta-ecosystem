# Source Of Truth Router Boundary Guarantees V1

Status: boundary guarantee foundation.

## Boundary Summary

Source Of Truth Router selects evidence source.

It does not execute source resolution by itself in this foundation.

It does not authorize providers, workers, proposals, approvals, execution requests, or dispatch.

## Provider Boundary

Provider may be selected only as the lowest-priority fallback source.

Provider may not:

- select source of truth;
- override replay evidence;
- override governance artifacts;
- replace constitutional citations;
- create approval;
- create execution request;
- dispatch workers;
- mutate replay.

Required flags:

```text
provider_authority = false
provider_used = false at selection time
```

Provider use can occur only in a later provider response path after router selection.

## Replay Boundary

Replay is preferred for recorded operational truth.

Replay may not:

- select a source;
- repair missing source evidence;
- mutate router selection;
- invoke providers;
- infer absent events.

If replay evidence is required but unavailable, routing fails closed.

## Governance Boundary

Governance artifacts are preferred for governance truth.

Provider output may not determine:

- certifications;
- ADR meaning;
- milestone status;
- governance guarantees;
- authority boundaries.

If governance evidence is missing, routing fails closed.

## Constitutional Memory Boundary

Constitutional Memory is preferred for constitutional and architectural truth.

Provider output may not replace:

- citations;
- constitutional memory retrieval;
- boundary guarantees;
- canonical definitions.

If constitutional evidence is missing, routing fails closed.

## Self-Resolution Boundary

Self-resolution is allowed only when deterministic runtime knowledge is sufficient.

Self-resolution may not:

- invent governance facts;
- infer replay events;
- replace citations;
- claim provider output;
- create execution authority.

## Worker Boundary

Worker Runtime is outside source-of-truth routing V1.

Router may not:

- dispatch workers;
- invoke workers;
- mark worker evidence required as execution authority;
- create worker tasks.

If worker evidence is needed, the router must defer to future Proposal Lifecycle and execution request handling.

## Proposal And Execution Boundary

Router may not create:

- proposal artifacts;
- approval artifacts;
- execution requests;
- dispatch requests;
- execution completion records.

Router selection is conversational source governance only.

## Replay Guarantees

Router selection must be:

- replay-visible;
- append-only;
- hash-verifiable;
- prompt-linked;
- source-priority-linked;
- evidence-linked;
- fail-closed when invalid.

## Constitutional Invariant

Router preserves:

```text
LLM proposes
AiGOL governs
Worker executes
Replay records
```

Meaning:

- LLM/provider may propose only after AiGOL selects provider source;
- AiGOL governs source selection;
- Worker execution is absent;
- Replay records source selection evidence.
