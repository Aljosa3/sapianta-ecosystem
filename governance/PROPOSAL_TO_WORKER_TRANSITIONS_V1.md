# PROPOSAL_TO_WORKER_TRANSITIONS_V1

## Status

Certified transition model.

## Valid Transition Model

```text
PROVIDER_PROPOSAL
-> PROPOSAL_NORMALIZATION
-> GOVERNANCE_REVIEW
-> AUTHORIZATION_DECISION
-> AUTHORIZED_EXECUTION_REQUEST
-> WORKER_EXECUTION_REQUEST
-> WORKER_RESULT
-> REPLAYED_GOVERNED_RESULT
```

## Forbidden Transitions

```text
PROVIDER_PROPOSAL -> WORKER_EXECUTION_REQUEST
PROVIDER_PROPOSAL -> WORKER_INVOCATION
PROVIDER_PROPOSAL -> AUTHORIZATION_DECISION
PROVIDER_PROPOSAL -> GOVERNANCE_DECISION
PROVIDER_PROPOSAL -> DISPATCH
PROVIDER_PROPOSAL -> WORKER_STATE_MUTATION
```

## Transition Requirements

Every transition toward worker execution requires:

- replay-visible proposal lineage
- governance admissibility review
- explicit authorization evidence
- capability binding
- worker identity
- fail-closed boundary validation

## Where Interpretation Ends

Proposal interpretation ends at normalized proposal evidence and admissibility
candidate status.

It does not create permission.

## Where Governance Begins

Governance begins when AiGOL evaluates admissibility, authority separation,
capability boundaries, replay continuity, and constitutional compatibility.

## Where Worker Execution Begins

Worker execution begins only after an authorized execution request is bound to a
specific worker capability.
