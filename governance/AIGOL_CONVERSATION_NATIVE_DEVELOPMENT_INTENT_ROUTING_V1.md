# AIGOL_CONVERSATION_NATIVE_DEVELOPMENT_INTENT_ROUTING_V1

## Status

CERTIFIED

## Purpose

Allow conversation mode to recognize native-development intents before provider-assisted conversation and route them into a replay-visible native-development entry path.

This milestone fixes conversation entry. It does not authorize implementation, dispatch, execution, worker invocation, provider invocation, or governance mutation.

## Root Cause

Conversation mode had two entry defects:

1. Native-development recognition required explicit milestone ids, so normal prompts such as `Create a marketing domain.` or `Add provider Anthropic.` fell through to provider-assisted conversation.
2. Turn ids were precomputed before each turn’s latest resume check, which could produce `turn allocation mismatch` when replay state changed between the initial session resume and later turns.

## Runtime Surface

Runtime:

- `aigol/runtime/conversation_native_development_intent_routing.py`

CLI integration:

- `aigol/cli/aigol_cli.py`

Tests:

- `tests/test_conversation_native_development_intent_routing_v1.py`

## Target Flow

Conversation entry now supports:

```text
Conversation
-> Intent Classification
-> Native Development Routing
-> Native Development Intake
-> Cognition
-> Resource Selection
-> PPP
-> Proposal Production
-> Validation
-> Approval/Handoff
```

This milestone implements the first routing bridge and records the next expected pipeline stage as `NATIVE_DEVELOPMENT_INTAKE`.

## Intent Classification Model

Certified intent classes:

- `CREATE_DOMAIN`
- `CREATE_WORKER`
- `MODIFY_WORKER`
- `ADD_PROVIDER`
- `MODIFY_PROVIDER`
- `IMPROVE_EXISTING_CAPABILITY`
- `GOVERNANCE_CHANGE`
- `REPLAY_DERIVED_IMPROVEMENT`

Certified prompt mappings:

| Prompt | Intent Class | Target |
| --- | --- | --- |
| `Create a marketing domain.` | `CREATE_DOMAIN` | `MARKETING` domain |
| `Create sentiment analysis worker.` | `CREATE_WORKER` | `MARKETING` / `SENTIMENT_ANALYSIS` worker |
| `Add provider Anthropic.` | `ADD_PROVIDER` | `ANTHROPIC` provider |
| `Improve trading strategy.` | `IMPROVE_EXISTING_CAPABILITY` | `TRADING` strategy improvement |
| `Create trading worker.` | `CREATE_WORKER` | `TRADING` worker |
| `Upgrade replay subsystem.` | `MODIFY_WORKER` | AiGOL replay subsystem |
| `Add governance policy.` | `GOVERNANCE_CHANGE` | Governance policy |

## Clarification Rule

Native-development prompts do not require clarification eligibility.

Clarification remains reserved for prompts whose intent remains ambiguous.

Example:

- `Create a workstation.` routes to clarification.
- `Create a marketing domain.` routes to native-development intent routing.

## Turn Allocation Fix

Conversation mode now allocates each turn from the latest `resume_conversation_session(...)` result inside the prompt loop.

The previous loop precomputed `next_turn_number` from initial session state and then compared it with a fresh resume result. That comparison could fail when replay state changed between the initial resume and a later turn.

The new lifecycle is:

1. Read prompt.
2. Resume session.
3. Use `resume_state["next_turn_id"]`.
4. Build `prompt_id`.
5. Persist source router replay.
6. Route intent.

## Replay Model

The runtime persists:

- intent routing evidence;
- routing classification;
- routed intent artifact;
- routing return artifact;
- turn allocation hash;
- turn allocation status;
- canonical chain id;
- authority boundary flags.

Replay reconstruction verifies:

- wrapper ordering;
- wrapper hashes;
- artifact hashes;
- routing evidence lineage;
- classification lineage;
- returned routed-intent lineage.

## Fail-Closed Conditions

Routing fails closed when:

- intent cannot be classified;
- routing lineage breaks;
- replay corruption is detected;
- turn allocation evidence is invalid;
- prompt id does not match allocated turn id;
- append-only replay would collide.

## Authority Boundaries

This runtime must not:

- execute;
- dispatch;
- authorize;
- invoke workers;
- invoke providers;
- mutate governance;
- silently select ambiguous interpretations.

## Final Classification

AIGOL_CONVERSATION_NATIVE_DEVELOPMENT_INTENT_ROUTING_STATUS = CERTIFIED
