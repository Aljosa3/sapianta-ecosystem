# PROVIDER_WORKER_BOUNDARY_MODEL_V1

## Status

Certified boundary model.

## Boundary Principle

Provider output is proposal evidence.

Worker input is authorized execution evidence.

These are not the same artifact and may not be collapsed.

## Boundary Chain

```text
Provider Proposal
-> Governance Review
-> Authorization Decision
-> Worker Execution Request
```

Provider proposal must not become worker request by implication.

## Provider Side

Provider may:

- produce proposal evidence
- identify provider source
- provide replay-visible response
- remain substitutable

Provider may not:

- invoke worker
- dispatch work
- mutate worker state
- authorize execution
- govern admissibility
- create worker authority

## Worker Side

Worker may:

- execute bounded authorized requests
- return worker result evidence
- emit termination evidence

Worker may not:

- trust raw provider proposals
- accept raw provider authority
- accept raw cognition authority
- self-authorize
- bypass governance
- bypass replay

## Compatibility Finding

Provider and worker worlds are compatible because AiGOL places governance and
authorization boundaries between proposal evidence and worker execution.
