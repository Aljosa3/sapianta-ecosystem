# Worker Execution Only Invariant V1

Status: permanent worker authority boundary.

## Invariant

Worker / deterministic execution runtime executes only bounded authorized work.

The worker is not a governance authority. It is not a cognition authority. It is not an authorization authority.

## Worker May

A worker may:

- receive a governed execution request
- verify required authorization evidence is present
- execute the bounded authorized task
- emit replay-visible execution evidence
- terminate deterministically
- fail closed on invalid request, authorization, lineage, or boundary state

## Worker Must Not

A worker must not:

- self-authorize
- infer missing authorization
- expand capability scope
- choose forbidden capabilities
- bypass replay lineage
- mutate constitutional substrate
- create hidden continuation
- persist unauthorized state
- continue after fail-closed termination

## Execution Preconditions

Worker execution requires:

- normalized proposal-derived execution request
- AiGOL constitutional validation
- AiGOL authorization evidence
- capability boundary validation
- replay lineage continuity
- deterministic lifecycle state

Absent any precondition, worker execution must fail closed.

## Certification

This invariant certifies:

- worker executes only after AiGOL authorization
- worker cannot self-authorize
- worker cannot mutate governance authority
- worker cannot create autonomous execution
- worker execution remains replay-visible
