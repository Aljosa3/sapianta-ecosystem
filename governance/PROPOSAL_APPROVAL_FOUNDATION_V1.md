# Proposal Approval Foundation V1

Status: foundation review.

Final classification:

```text
PROPOSAL_APPROVAL_FOUNDATION_STATUS = READY_WITH_GAPS
```

## Scope

This artifact defines the minimal approval architecture between proposal creation and future execution.

It does not implement runtime, execution, workers, approval UI, routing, provider behavior, governance mutation, or deployment behavior.

## Context

AiGOL now has:

- Conversational Runtime;
- Resolution Strategy Foundation;
- Proposal Runtime Foundation;
- Proposal Lifecycle Foundation;
- Conversation-to-Proposal Flow Foundation.

The remaining major boundary is:

```text
Proposal Creation
-> Approval
-> Future Execution
```

## 1. Who Can Approve A Proposal?

Only a human operator can approve a proposal.

Approval applies only after AiGOL inspection has produced replay-visible inspection evidence.

The approval transition is:

```text
INSPECTED -> APPROVED
```

Human approval does not replace AiGOL governance validation, execution request derivation, authorization, worker boundary checks, or replay requirements.

## 2. Who Can Never Approve A Proposal?

The following can never approve proposals:

- provider;
- worker;
- replay;
- conversation response;
- resolution strategy selection;
- proposal artifact itself;
- Constitutional Memory citation;
- execution request;
- automated fallback path.

## 3. Can Providers Approve Proposals?

No.

Provider output may contribute proposal evidence only. Provider output may not approve, reject, inspect, authorize, execute, dispatch, or mutate proposal state.

## 4. Can Workers Approve Proposals?

No.

Workers may execute only future authorized governed execution requests. A worker may not approve proposals, infer missing approval, expand scope, or self-authorize work.

## 5. Replay Evidence Required Before Approval

Before approval, replay must contain:

- proposal runtime artifact;
- proposal status `CREATED`;
- proposal source evidence;
- prompt lineage;
- conversation lineage when present;
- resolution strategy lineage when present;
- provider contribution lineage when present;
- AiGOL inspection artifact;
- inspection result permitting approval consideration;
- proposal artifact hash;
- non-authority boundary evidence;
- absence of execution.

If inspection evidence is missing, approval must fail closed.

## 6. Approval Recording

Approval is recorded as a replay-visible approval artifact:

```text
PROPOSAL_APPROVAL_ARTIFACT_V1
```

Required approval events:

```text
PROPOSAL_APPROVAL_PENDING
PROPOSAL_APPROVED
PROPOSAL_REJECTED
PROPOSAL_APPROVAL_EXPIRED
```

The approval artifact must include:

- approval id;
- proposal id;
- proposal artifact hash;
- inspection artifact reference;
- human decision;
- approval status;
- approval reason;
- operator label;
- created at;
- replay reference;
- non-execution flags;
- approval artifact hash.

## 7. Approval Reconstruction

Replay reconstructs approval decisions by reading append-only proposal and approval events in deterministic order:

```text
PROPOSAL_RUNTIME_CREATED
PROPOSAL_INSPECTED
PROPOSAL_APPROVAL_PENDING
PROPOSAL_APPROVED or PROPOSAL_REJECTED or PROPOSAL_APPROVAL_EXPIRED
```

Replay reconstruction may prove:

- approval existed;
- rejection existed;
- approval expired;
- inspection preceded approval;
- human operator made the approval decision;
- no execution occurred as part of approval.

Replay reconstruction may not create, repair, or infer approval.

## 8. Constitutional Preservation

Approval preserves:

```text
LLM proposes
AiGOL governs
Worker executes
Replay records
```

Mapping:

| Role | Approval meaning |
| --- | --- |
| LLM proposes | Provider evidence remains non-authoritative |
| AiGOL governs | AiGOL inspects proposal and validates approval prerequisites |
| Worker executes | Worker remains dormant until future authorized execution request |
| Replay records | Replay records inspection, human decision, and approval result |

## 9. Approval States

The minimal approval states are:

```text
PENDING_APPROVAL
APPROVED
REJECTED
EXPIRED
```

These states describe approval disposition. They do not replace proposal lifecycle states.

## 10. Proposal Lifecycle Integration

Approval integrates with Proposal Lifecycle as:

```text
CREATED
-> INSPECTED
-> PENDING_APPROVAL
-> APPROVED or REJECTED or EXPIRED
```

When approval is granted, proposal lifecycle may transition:

```text
INSPECTED -> APPROVED
```

Future execution still requires separate governed execution request derivation and worker execution certification.

## Foundation Result

The minimal proposal approval foundation is ready as a review artifact.

It remains ready with gaps because no runtime implementation, approval UI, schema enforcement, execution request derivation, worker integration, or tests are introduced by this review.

```text
PROPOSAL_APPROVAL_FOUNDATION_STATUS = READY_WITH_GAPS
```
