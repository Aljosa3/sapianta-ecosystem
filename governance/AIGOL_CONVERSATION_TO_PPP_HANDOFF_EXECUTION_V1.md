# AIGOL_CONVERSATION_TO_PPP_HANDOFF_EXECUTION_V1

## Status

CERTIFIED

## Purpose

Continue successfully routed conversation native-development intents through the certified Resource Selection and PPP handoff pipeline until a governed terminal state is reached.

Despite the milestone name, this runtime is non-executing. It does not authorize, dispatch, invoke workers, execute proposals, or mutate governance.

## Root Cause

Conversation entry could classify prompts such as `Create a marketing domain.` and route them as native-development intents, but the live CLI path stopped at `NATIVE_DEVELOPMENT_INTAKE`.

The certified downstream PPP components already existed, but conversation mode did not continue from routed intent into:

- Resource Selection;
- Resource Selection PPP Integration;
- Provider Proposal Production evidence;
- Proposal Contract Validation;
- Approval Evaluation;
- Implementation Handoff.

## Runtime Surface

Runtime:

- `aigol/runtime/conversation_to_ppp_handoff_execution.py`

CLI integration:

- `aigol/cli/aigol_cli.py`

Tests:

- `tests/test_conversation_to_ppp_handoff_execution_v1.py`
- `tests/test_conversation_native_development_intent_routing_v1.py`

## Target Flow

```text
Conversation
-> Intent Classification
-> Native Development Routing
-> Resource Selection
-> PPP Integration
-> Provider Proposal Production Evidence
-> Proposal Validation
-> Approval Evaluation
-> Implementation Handoff
```

## Terminal States

The bridge may return:

- `IMPLEMENTATION_HANDOFF_CREATED`
- `HUMAN_APPROVAL_REQUIRED`
- `HUMAN_CLARIFICATION_REQUIRED`
- `FAILED_CLOSED`

For V1, `HUMAN_CLARIFICATION_REQUIRED` remains a reserved terminal state for future unresolved downstream ambiguity. Existing clarification entry behavior remains handled by the clarification dialog runtimes.

## Acceptance Scenarios

| Prompt | Result |
| --- | --- |
| `Create a marketing domain.` | `IMPLEMENTATION_HANDOFF_CREATED` |
| `Add provider Anthropic.` | `IMPLEMENTATION_HANDOFF_CREATED` |
| `Create sentiment analysis worker.` | `IMPLEMENTATION_HANDOFF_CREATED` |
| `Improve trading strategy.` | `HUMAN_APPROVAL_REQUIRED` |

Trading is treated as high risk and stops before implementation handoff.

## Proposal Production Model

The runtime creates deterministic provider proposal production evidence for conversation continuation.

This evidence is proposal-only and replay-visible. It does not grant provider authority, worker authority, execution authority, dispatch authority, governance authority, or replay mutation authority.

## Replay Model

The runtime persists:

- conversation request lineage;
- native-development routing reference and hash;
- resource selection status and hash;
- PPP integration status and hash;
- proposal production evidence and hash;
- proposal validation status and hash;
- approval evidence and hash;
- implementation handoff evidence when created.

Replay reconstruction verifies:

- append-only wrapper ordering;
- wrapper hashes;
- artifact hashes;
- routed intent lineage;
- returned execution reference;
- returned execution hash;
- implementation handoff replay lineage when a handoff exists.

## Authority Boundaries

Conversation may only advance to PPP-certified terminal states.

The runtime must not:

- execute workers;
- dispatch workers;
- authorize execution;
- mutate governance;
- bypass approval;
- grant provider authority;
- create domain or worker artifacts directly.

## Fail-Closed Conditions

The runtime fails closed when:

- routed intent is invalid;
- resource selection fails;
- PPP integration fails;
- proposal validation fails;
- implementation handoff creation fails;
- replay append-only continuity is broken;
- artifact hashes mismatch;
- authority boundary evidence is violated.

## CLI Before And After

Before:

```text
Create a marketing domain.
-> CREATE_DOMAIN
-> NATIVE_DEVELOPMENT_INTENT_ROUTED
-> NATIVE_DEVELOPMENT_INTAKE
```

After:

```text
Create a marketing domain.
-> CREATE_DOMAIN
-> RESOURCE_SELECTION_SUCCEEDED
-> RESOURCE_PPP_INTEGRATED
-> PROVIDER_PROPOSAL_PRODUCED
-> DEVELOPMENT_PROPOSAL_CONTRACT_VALIDATED
-> IMPLEMENTATION_HANDOFF_CREATED
```

## Remaining Blockers Before Full Conversation-Driven Domain Creation

- Dedicated native-development task-intake artifacts must replace the deterministic context shell used by this bridge.
- Domain-specific context assembly must provide richer artifact references for implementation planning.
- Human approval resume behavior after `HUMAN_APPROVAL_REQUIRED` remains a follow-on milestone.
- Provider live invocation remains governed by provider availability and approval policy.
- Actual domain creation remains outside conversation mode and requires human-authorized implementation work.

## Final Classification

AIGOL_CONVERSATION_TO_PPP_HANDOFF_EXECUTION_STATUS = CERTIFIED
