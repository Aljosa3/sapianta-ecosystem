# AIGOL_CONVERSATION_PROVIDER_UNAVAILABLE_CLARIFICATION_FALLBACK_V1

## Status

CERTIFIED

## Purpose

Prevent provider unavailability from prematurely terminating ambiguous development-style conversation prompts.

The runtime preserves the provider failure evidence, determines whether a deterministic clarification fallback is allowed, and creates a bounded human clarification request when the prompt is eligible.

## Root Cause

Conversation mode attempted provider-assisted conversation before using the certified clarification path.

For prompts such as:

- `Create a workstation.`

the provider failure path returned:

- `FAILED_CLOSED: provider-assisted conversation failed closed: OpenAI provider unavailable`

before AiGOL could ask a deterministic clarification question.

## Runtime Surface

Runtime:

- `aigol/runtime/conversation_provider_unavailable_clarification_fallback.py`

CLI integration:

- `aigol/cli/aigol_cli.py`

Test:

- `tests/test_conversation_provider_unavailable_clarification_fallback_v1.py`

## Fallback Lifecycle

Flow:

1. Conversation receives a human prompt.
2. Provider-assisted conversation fails closed.
3. Conversation detects provider-unavailable evidence.
4. Fallback checks whether the prompt is clarification-eligible.
5. Eligible ambiguous prompts enter deterministic clarification.
6. `HUMAN_CLARIFICATION_REQUEST_ARTIFACT_V1` is created.
7. Operator-facing clarification questions and options are rendered.
8. Conversation remains non-executing and non-dispatching.

## Clarification-Eligible Prompt Class

Certified initial support:

- `Create a workstation.`

Supported ambiguous categories:

- domain ambiguity;
- worker ambiguity;
- capability ambiguity;
- intent ambiguity;
- resource ambiguity.

The runtime also recognizes narrow generic ambiguous phrases such as:

- `Improve trading.`
- `Add analysis.`
- `Create reporting.`

These remain clarification-only and do not create a proposal.

## Expected Operator Output

When fallback is eligible, conversation returns:

```text
HUMAN_CLARIFICATION_REQUIRED

Provider unavailable before safe conversation resolution.
AiGOL will not guess. Choose one interpretation and resubmit with that clarification.

Questions:
- Which domain should this request target?
- Which worker family should this request target?
- Which capability is being requested?
- Which interpretation should AiGOL use?
- Which resource category should this request use?

Options:
- EMPLOYEE_MANAGEMENT_DOMAIN: Create a new employee-management domain.
- OPERATOR_WORKSTATION_TOOL: Create an operator workstation infrastructure artifact.
- WORKER_FOUNDATION: Create a new governed worker foundation.
```

## Replay Model

The fallback persists:

- provider failure reason;
- provider failure hash;
- fallback eligibility status;
- fallback status;
- clarification request reference;
- clarification request hash;
- clarification replay reference;
- authority boundary flags.

Fallback replay path:

- `<turn_root>/provider_unavailable_clarification_fallback/`

Clarification replay path:

- `<turn_root>/provider_unavailable_clarification_fallback/clarification_dialog/`

## Fail-Closed Conditions

Fallback fails closed when:

- provider unavailable evidence is missing;
- prompt is not clarification-eligible;
- deterministic ambiguity classification is unavailable;
- clarification artifact cannot be created;
- append-only replay already exists;
- replay hash continuity is corrupt.

## Authority Boundaries

The fallback must not:

- authorize;
- dispatch;
- execute;
- invoke workers;
- mutate governance;
- mutate replay outside append-only fallback evidence;
- silently choose an interpretation.

Provider remains unavailable evidence only.

Human remains final authority.

## Final Classification

AIGOL_CONVERSATION_PROVIDER_UNAVAILABLE_CLARIFICATION_FALLBACK_STATUS = CERTIFIED
