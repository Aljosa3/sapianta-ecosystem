# Resolution Strategy Boundary Guarantees V1

Status: boundary guarantees.

## Certified Guarantees

Resolution Strategy preserves source-of-truth boundaries without granting authority to providers, workers, or replay.

## Strategy Boundary

A strategy selection is source selection evidence.

It is not:

- final answer authority;
- routing authority;
- execution authority;
- authorization authority;
- governance mutation;
- worker dispatch;
- proposal approval.

## Provider Boundary

Provider may assist only when AiGOL selects a provider-eligible strategy.

Provider may not determine:

- replay truth;
- governance truth;
- constitutional authority;
- authorization;
- approval;
- worker execution permission;
- fail-closed termination.

Provider output remains proposal or semantic suggestion evidence only.

## Governance Boundary

AiGOL remains responsible for:

- selecting the strategy;
- validating evidence source categories;
- preserving source precedence;
- accepting or rejecting provider output;
- deciding whether Proposal Lifecycle is required;
- failing closed on ambiguity.

Strategy selection does not mutate governance.

## Replay Boundary

Replay records strategy selection and source evidence.

Replay may not:

- choose a strategy;
- approve a strategy;
- repair missing evidence;
- infer missing provider validation;
- mutate source truth.

## Worker Boundary

Worker is never selected as direct conversational execution.

`WORKER` means future worker result evidence is required. It must pass through Proposal Lifecycle and governed execution request handling before any worker can execute.

Worker may not self-authorize from a selected strategy.

## Constitutional Memory Boundary

Constitutional Memory may provide citation evidence.

It may not:

- authorize execution;
- approve proposals;
- replace governance validation;
- silently resolve citation conflicts;
- mutate itself through strategy selection.

## Combined Strategy Boundary

`COMBINED` is valid only when source precedence is explicit.

It must not allow:

- provider override of governance evidence;
- provider override of replay evidence;
- worker execution without proposal lifecycle;
- memory citations without citation references;
- hidden source blending.

## Proposal Lifecycle Boundary

Resolution Strategy may determine that Proposal Lifecycle is required.

It may not:

- create approved proposal state;
- approve proposals;
- create execution requests;
- dispatch workers.

AiGOL proposal lifecycle logic must handle those transitions separately.

## Fail-Closed Boundary

Strategy selection must fail closed on:

- missing evidence;
- source conflict without precedence;
- provider authority language;
- governance truth delegated to provider;
- replay discontinuity;
- worker execution request without proposal lifecycle;
- unsupported strategy;
- ambiguous source-of-truth claim.

## Constitutional Invariant

The strategy model preserves:

```text
LLM proposes
AiGOL governs
Worker executes
Replay records
```

Mapping:

```text
LLM proposes = provider semantic assistance remains suggestion evidence
AiGOL governs = AiGOL selects and validates source strategy
Worker executes = worker evidence only after authorized future execution
Replay records = replay records strategy selection and source evidence
```

## Boundary Result

```text
RESOLUTION_STRATEGY_BOUNDARY_STATUS = PRESERVED
```
