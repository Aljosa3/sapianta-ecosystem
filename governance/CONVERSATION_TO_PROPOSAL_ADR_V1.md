# Conversation To Proposal ADR V1

Status: accepted with gaps.

## Context

AiGOL has certified conversation, resolution strategy, proposal runtime, and proposal lifecycle foundations.

The missing architectural decision is how a human conversation becomes a proposal candidate without becoming approval, execution, worker dispatch, or provider authority.

## Decision

Adopt a minimal conversation-to-proposal flow:

```text
Human Prompt Evidence
-> Conversational Handling
-> Resolution Strategy Selection
-> Proposal Eligibility Review
-> PROPOSAL_RUNTIME_ARTIFACT_V1.status = CREATED
-> Replay
-> Future Proposal Lifecycle
```

Final foundation status:

```text
CONVERSATION_TO_PROPOSAL_FLOW_STATUS = READY_WITH_GAPS
```

## Rationale

The flow separates human-facing conversation from future governed action.

Conversation may surface an action candidate, but AiGOL alone creates the proposal runtime artifact and only in `CREATED` state.

This preserves replay visibility and prevents provider output, human prompt text, or conversation responses from becoming authority.

## Accepted Claims

AiGOL may claim:

```text
The minimal conversation-to-proposal flow is architecturally defined.
```

AiGOL may also claim:

```text
Conversation can create proposal candidates only through AiGOL-governed, replay-visible proposal creation.
```

## Rejected Claims

AiGOL must not claim:

- runtime implementation of proposal creation;
- direct conversation-to-execution;
- provider-created proposal authority;
- automatic approval;
- worker dispatch from conversation;
- execution request creation from conversation;
- replay mutation authority.

## Consequences

Future implementation must preserve:

- replay-visible prompt evidence;
- replay-visible strategy selection;
- bounded proposal eligibility review;
- `created_by = AIGOL`;
- `status = CREATED`;
- no approval or execution in this flow;
- fail-closed handling for ambiguity.

Any approval, execution request derivation, or worker execution must be handled and certified separately.
