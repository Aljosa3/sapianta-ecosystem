# Conversation To Proposal Transitions V1

Status: transition model.

## Transition Principle

Conversation-to-proposal transition is a bounded creation transition.

It can create only:

```text
PROPOSAL_RUNTIME_ARTIFACT_V1.status = CREATED
```

It cannot inspect, approve, reject, expire, execute, dispatch, or authorize.

## Transition Table

| From | To | Actor | Requirement |
| --- | --- | --- | --- |
| Human prompt evidence | Conversational handling | AiGOL | Prompt lineage and replay evidence |
| Conversational handling | Resolution strategy selection | AiGOL | Strategy selection evidence |
| Resolution strategy selection | Proposal eligibility review | AiGOL | `proposal_lifecycle_required = true` or bounded action candidate |
| Provider contribution evidence | Proposal eligibility review | AiGOL | Provider validation and replay reference |
| Proposal eligibility review | `PROPOSAL_RUNTIME_ARTIFACT_V1.CREATED` | AiGOL | Valid proposal fields and artifact hash |
| `PROPOSAL_RUNTIME_ARTIFACT_V1.CREATED` | Proposal Lifecycle | AiGOL | Future lifecycle implementation required |

## Strategies That May Transition To Proposal Eligibility

The following may transition to proposal eligibility:

```text
SELF_RESOLUTION
PROVIDER
WORKER
COMBINED
REPLAY
GOVERNANCE
```

They may do so only when a bounded future action candidate is present and AiGOL creates the artifact.

## Strategies That Do Not Transition By Themselves

The following do not transition to proposal by themselves:

```text
CONSTITUTIONAL_MEMORY
```

Constitutional Memory citation evidence may support proposal eligibility only through another AiGOL-governed strategy.

## Never-Allowed Transitions

The following transitions are forbidden:

- conversation response directly to worker execution;
- provider contribution directly to proposal state;
- provider contribution directly to approval;
- strategy selection directly to execution request;
- proposal creation directly to `APPROVED`;
- proposal creation directly to `EXECUTED`;
- replay reconstruction directly to proposal mutation;
- human prompt directly to execution authority.

## Required Human Approval

Conversation-to-proposal creation does not require human approval when it creates only `CREATED` candidate state.

Human approval is required later for:

```text
INSPECTED -> APPROVED
```

and for future execution-sensitive transitions as defined by Proposal Lifecycle.

## Transition Evidence

Every transition must record:

- actor;
- source artifact;
- target artifact;
- transition reason;
- replay reference;
- artifact hash;
- non-authority status;
- fail-closed reason when blocked.

## Illegal Transition Prevention

Illegal transitions are prevented by:

- accepting only AiGOL-created proposal artifacts;
- requiring replay-visible strategy evidence;
- requiring bounded proposal source;
- rejecting provider-created authority;
- rejecting execution or approval state in this flow;
- failing closed on missing lineage or unsupported transition.
