# Conversation To Proposal Flow Model V1

Status: flow model.

## Model Purpose

This model defines the minimum evidence and decision flow required before a conversation can create a proposal runtime artifact.

It bridges:

```text
Human Prompt
-> Conversation
-> Resolution Strategy
-> Proposal Runtime
-> Proposal Lifecycle
```

## Canonical Flow

```text
Human Prompt Evidence
-> Conversational Handling
-> Resolution Strategy Selection
-> Proposal Eligibility Review
-> Proposal Runtime Artifact Created
-> Replay
-> Future Proposal Lifecycle
```

## Flow Inputs

Required:

- `source_prompt_id`;
- replay-visible prompt evidence;
- resolution strategy selection;
- proposal lifecycle requirement;
- proposal candidate text;
- source evidence references.

Optional:

- `source_conversation_id`;
- `source_provider_event_id`;
- governance evidence reference;
- replay evidence reference;
- Constitutional Memory citation reference.

## Flow Output

The only valid foundation output is:

```text
PROPOSAL_RUNTIME_ARTIFACT_V1
```

with:

```text
status = CREATED
created_by = AIGOL
```

## Proposal Eligibility

A prompt is proposal-eligible when it contains a bounded future action candidate that cannot be satisfied as a conversation response alone.

Examples of proposal-eligible intents:

- request to perform future bounded work;
- request to prepare future worker execution;
- request to inspect or remediate a bounded artifact;
- request to create a candidate action for later approval;
- request whose strategy result is `WORKER`;
- request whose strategy result is `COMBINED` with explicit action candidate.

## Non-Eligible Conversation Outcomes

Do not create a proposal when the outcome is:

- explanatory conversation response;
- replay answer;
- governance answer;
- Constitutional Memory citation answer;
- provider-assisted wording only;
- fail-closed termination;
- direct execution request;
- governance bypass request.

## Proposal Source Mapping

| Flow evidence | Proposal source |
| --- | --- |
| Conversation action candidate | `CONVERSATION` |
| Strategy-selected action candidate | `RESOLUTION_STRATEGY` |
| Provider contribution evidence | `PROVIDER_EVIDENCE` |
| Replay follow-up evidence | `REPLAY_EVIDENCE` |
| Governance remediation candidate | `GOVERNANCE_EVIDENCE` |
| Human prompt action request | `HUMAN_PROMPT` |
| Multiple bounded sources | `COMBINED` |

## Required Artifact Fields

Conversation-to-proposal creation must produce:

```text
proposal_id
proposal_type
proposal_source
proposal_text
created_at
created_by
status
replay_reference
source_prompt_id
source_conversation_id optional
source_strategy_id
source_provider_event_id optional
artifact_hash
```

## Fail-Closed Rules

The flow must fail closed if:

- prompt lineage is missing;
- strategy selection is missing;
- `proposal_lifecycle_required` is not true;
- action candidate is unbounded;
- provider output implies authority;
- source evidence is not replay-visible;
- proposal source is unsupported;
- artifact hash cannot be reconstructed;
- execution or approval is implied.

## Non-Authority Rule

Proposal creation is not approval, authorization, execution, dispatch, or governance mutation.

It creates only a candidate artifact for future lifecycle inspection.
