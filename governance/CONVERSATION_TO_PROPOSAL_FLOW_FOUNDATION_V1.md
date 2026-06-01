# Conversation To Proposal Flow Foundation V1

Status: foundation review.

Final classification:

```text
CONVERSATION_TO_PROPOSAL_FLOW_STATUS = READY_WITH_GAPS
```

## Scope

This review defines the minimal replay-safe flow from human conversation to proposal creation.

It does not implement runtime, execution, workers, routing, provider behavior, approval, governance mutation, or deployment behavior.

## Context

AiGOL now has:

- certified Conversational Runtime;
- Resolution Strategy Foundation;
- Proposal Runtime Foundation;
- Proposal Lifecycle Foundation.

The missing foundation is the explicit transition path:

```text
Human Prompt
-> Conversation
-> Resolution Strategy
-> Proposal Creation
```

## 1. Conditions For Conversation To Create A Proposal

A conversation may create a proposal only when AiGOL determines that the prompt contains a bounded future action candidate rather than only an answer request.

Required conditions:

- a replay-visible human prompt exists;
- conversational handling is complete enough to identify intent or ambiguity;
- a resolution strategy record determines `proposal_lifecycle_required = true`;
- source evidence is replay-visible;
- AiGOL can create a `PROPOSAL_RUNTIME_ARTIFACT_V1` with `created_by = AIGOL`;
- initial proposal status is `CREATED`;
- no provider, worker, replay, or conversation artifact claims authority;
- no execution, approval, or worker dispatch occurs.

If any condition is missing or ambiguous, proposal creation must fail closed.

## 2. Resolution Strategies That May Create Proposals

The following strategies may lead to proposal creation, through AiGOL only:

| Strategy | Proposal creation eligibility |
| --- | --- |
| `PROVIDER` | May contribute proposal evidence after AiGOL validation |
| `WORKER` | May require proposal lifecycle when future worker result is needed |
| `COMBINED` | May create proposal when source precedence is explicit and action candidate is bounded |
| `SELF_RESOLUTION` | May create proposal only when deterministic AiGOL analysis identifies a bounded action candidate |
| `REPLAY` | May create proposal only when replay evidence identifies a follow-up bounded action candidate |
| `GOVERNANCE` | May create proposal only when governance evidence identifies a permitted bounded remediation candidate |

All creation remains AiGOL-created proposal runtime artifact creation.

## 3. Resolution Strategies That May Never Create Proposals

No strategy may create a proposal when the strategy result is only:

- explanatory answer;
- replay truth answer;
- governance truth answer;
- Constitutional Memory citation answer;
- fail-closed termination;
- provider explanation without bounded future action;
- request to bypass governance;
- request to execute directly;
- request to mutate constitutional artifacts.

`CONSTITUTIONAL_MEMORY` may not create proposals from citation evidence alone. It may only provide evidence that another AiGOL-governed strategy uses to identify a bounded action candidate.

## 4. Conversation Response Versus Proposal

| Object | Purpose | Authority |
| --- | --- | --- |
| Conversation response | Human-readable answer returned to operator | No execution authority |
| Proposal | Candidate future governed action | No execution authority |

A conversation response may explain, summarize, or answer.

A proposal records a bounded action candidate for future inspection, approval, and possible governed execution request derivation.

Returning a conversation response does not imply proposal creation.

Creating a proposal does not imply approval or execution.

## 5. Replay Evidence Before Proposal Creation

Before proposal creation, replay must contain:

- human prompt artifact or equivalent prompt evidence;
- conversation handling reference when conversation participated;
- resolution strategy selection reference;
- source evidence references;
- provider contribution reference when provider evidence was used;
- fail-closed absence of direct execution;
- non-authority boundary evidence.

If provider evidence is used, replay must also show AiGOL validation of provider contribution before proposal creation.

## 6. Proposal Creation Recording

Proposal creation is recorded as:

```text
PROPOSAL_RUNTIME_CREATED
PROPOSAL_RUNTIME_RETURNED
```

The created proposal must be:

```text
artifact_type = PROPOSAL_RUNTIME_ARTIFACT_V1
created_by = AIGOL
status = CREATED
```

The creation record must preserve:

- `proposal_id`;
- `proposal_type`;
- `proposal_source`;
- `proposal_text`;
- `source_prompt_id`;
- `source_conversation_id` when present;
- `source_strategy_id`;
- `source_provider_event_id` when present;
- `replay_reference`;
- `artifact_hash`.

## 7. Constitutional Preservation

Conversation-to-proposal flow preserves:

```text
LLM proposes
AiGOL governs
Worker executes
Replay records
```

Mapping:

| Role | Flow meaning |
| --- | --- |
| LLM proposes | Provider output may contribute proposal evidence only |
| AiGOL governs | AiGOL selects strategy, validates evidence, and creates proposal artifact |
| Worker executes | No worker execution occurs in this flow |
| Replay records | Replay records prompt, strategy, source evidence, and proposal creation |

## 8. Future Approval And Execution Integration

Conversation-to-proposal flow ends at:

```text
PROPOSAL_RUNTIME_ARTIFACT_V1.status = CREATED
```

Future approval and execution require separate Proposal Lifecycle handling:

```text
CREATED
-> INSPECTED
-> APPROVED or REJECTED
-> future governed execution request
-> future worker execution
```

The conversation-to-proposal flow may not skip inspection, human approval where required, execution request derivation, authorization, or replay reconstruction.

## Foundation Result

The minimal conversation-to-proposal flow is ready as a review artifact.

It remains ready with gaps because no runtime implementation, routing integration, proposal creation code, schema enforcement, approval surface, worker integration, or tests are introduced by this review.

```text
CONVERSATION_TO_PROPOSAL_FLOW_STATUS = READY_WITH_GAPS
```
