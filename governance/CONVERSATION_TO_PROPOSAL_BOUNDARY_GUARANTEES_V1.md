# Conversation To Proposal Boundary Guarantees V1

Status: boundary guarantees.

## Certified Guarantees

The conversation-to-proposal foundation preserves authority separation while allowing conversational evidence to become a proposal candidate.

## Conversation Boundary

Conversation may:

- answer the human;
- identify an action candidate;
- provide replay-visible source context;
- feed Resolution Strategy.

Conversation may not:

- approve proposals;
- authorize execution;
- dispatch workers;
- bypass Proposal Lifecycle;
- mutate governance.

## Proposal Boundary

Proposal creation creates only:

```text
PROPOSAL_RUNTIME_ARTIFACT_V1.status = CREATED
```

It does not create:

- approval;
- authorization;
- execution request;
- worker task;
- governance decision;
- replay mutation authority.

## Resolution Strategy Boundary

Resolution Strategy may determine that proposal lifecycle is required.

It may not:

- create approved proposal state;
- create execution requests;
- dispatch workers;
- use provider output as authority;
- bypass replay evidence.

## Provider Boundary

Provider output may contribute proposal evidence.

Provider output may not:

- create proposals;
- approve proposals;
- inspect proposals;
- authorize execution;
- dispatch workers;
- mutate replay;
- decide governance truth.

## Replay Boundary

Replay records:

- prompt evidence;
- conversation evidence;
- strategy selection evidence;
- provider contribution evidence when present;
- proposal creation evidence.

Replay may not:

- create proposals;
- approve proposals;
- infer missing strategy selection;
- repair invalid lineage;
- mutate proposal state.

## Worker Boundary

Workers are not invoked by conversation-to-proposal flow.

Future worker execution requires:

- proposal lifecycle inspection;
- approval when required;
- governed execution request;
- authorization evidence;
- replay-visible execution result.

## Fail-Closed Boundary

The flow must fail closed if:

- proposal eligibility is ambiguous;
- strategy selection is missing;
- replay evidence is missing;
- provider authority is implied;
- worker execution is implied;
- approval is implied;
- proposal source is unsupported;
- artifact hash cannot be reconstructed;
- governance bypass is requested.

## Constitutional Invariant

The flow preserves:

```text
LLM proposes
AiGOL governs
Worker executes
Replay records
```

Mapping:

```text
LLM proposes = provider contribution may be evidence only
AiGOL governs = AiGOL selects strategy, validates source evidence, and creates CREATED proposal
Worker executes = no worker execution in this flow
Replay records = replay records prompt, strategy, evidence, and proposal creation
```

## Boundary Result

```text
CONVERSATION_TO_PROPOSAL_BOUNDARY_STATUS = PRESERVED
```
