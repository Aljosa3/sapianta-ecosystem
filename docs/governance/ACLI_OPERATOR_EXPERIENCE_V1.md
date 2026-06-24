# ACLI_OPERATOR_EXPERIENCE_V1

## 1. Purpose

ACLI_OPERATOR_EXPERIENCE_V1 records the operator-facing improvements required after the first real ACLI development pilot.

The runtime path is already certified for governed development execution. This artifact addresses presentation friction only.

It does not redesign ACLI, HIRR, workflow routing, approval governance, repository mutation, validation, or replay.

## 2. UX Review

The verified pilot flow is:

Human
-> ACLI
-> DEVELOPMENT_INTENT
-> GOVERNED_DEVELOPMENT_WORKFLOW
-> Proposal
-> APPROVE
-> Execution
-> Repository Mutation
-> Validation
-> Replay

The primary operator friction was misleading routing visibility on the approval turn. When the operator entered `APPROVE`, ACLI correctly executed the pending governed development proposal, but the routing visibility block displayed `ROUTING FAILED CLOSED`.

That message was misleading because the approval turn is a stateful continuation of a pending proposal. It does not require fresh workflow selection.

## 3. Exact Message Changes

The approval turn now renders stateful routing visibility as:

```text
ROUTING DECISION
workflow: GOVERNED_DEVELOPMENT_WORKFLOW
confidence: HIGH
matched:
- governed-development-pending-approval
- APPROVE
reason:
Stateful governed development approval decision detected; continuing the pending proposal without rerouting.
```

The proposal summary now makes the approval boundary explicit:

```text
approval_boundary: explicit human APPROVE required before mutation
mutation_performed: false
worker_invoked: false
validation_executed: false
replay_lineage_preserved: true
```

The execution summary now surfaces approval and safety evidence:

```text
approval_decision: APPROVED
proposal_hash: sha256:...
approval_hash: sha256:...
worker_protections_preserved: true
validation_allowlists_preserved: true
replay_lineage_preserved: true
```

## 4. Implementation Plan

The implementation is intentionally narrow:

1. Detect pending governed development approval decisions in interactive routing visibility.
2. Record `GOVERNED_DEVELOPMENT_WORKFLOW` as the selected workflow for the stateful approval turn.
3. Preserve the existing approval and execution bridge behavior.
4. Surface proposal and execution evidence already present in bridge captures.
5. Add regression coverage preventing `ROUTING FAILED CLOSED` from appearing on successful governed development approval turns.

## 5. Regression Tests

Required regression coverage:

- A governed development proposal still requires explicit approval.
- `APPROVE` executes the pending proposal.
- Approval turns render `ROUTING_SELECTED`.
- Approval turns identify `GOVERNED_DEVELOPMENT_WORKFLOW`.
- Universal intake records `GOVERNED_DEVELOPMENT_WORKFLOW` as the source workflow.
- Successful approval turns do not render `ROUTING FAILED CLOSED`.
- Proposal and execution summaries expose replay, proposal, approval, worker, and validation evidence.

## 6. Governance Preservation

The change preserves:

- fail-closed behavior;
- explicit approval boundaries;
- proposal hash binding;
- repository mutation worker protections;
- validation allowlists;
- replay lineage;
- Human = Authority;
- Replay = Source Of Truth;
- LLM proposes. AiGOL governs. Worker executes. Replay records.

## 7. Final Verdict

ACLI_OPERATOR_EXPERIENCE_READY
