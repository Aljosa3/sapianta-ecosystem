# HUMAN_PROMPT_PROVIDER_SELECTION_MODEL_V1

## Status

`HUMAN_PROMPT_PROVIDER_SELECTION_STATUS = CERTIFIED`

## Purpose

This model reviews who should decide whether provider assistance is needed for a
Human Prompt.

This milestone is review-only.

## Certification

Provider selection must be governed by AiGOL.

A human may express:

- provider preference;
- provider constraint;
- privacy constraint;
- latency or locality preference;
- explicit request to avoid provider assistance.

Human preference is not binding authority.

## Selection Boundary

AiGOL may select provider assistance when:

- self-resolution fails;
- deterministic classification is unresolved;
- prompt meaning requires semantic interpretation;
- a response requires synthesis beyond existing evidence;
- a provider proposal is the correct destination.

AiGOL must avoid provider assistance when:

- replay evidence answers the prompt;
- Constitutional Memory answers the prompt;
- deterministic governance artifacts answer the prompt;
- a direct replay-backed explanation exists;
- provider use would bypass a fail-closed requirement.

## Substitutability

Provider selection must preserve `PROVIDER_SUBSTITUTION_PROOF_V1`.

Selection must not depend on provider-specific constitutional semantics.

Provider-specific formatting belongs inside adapters, while AiGOL consumes a
common proposal or suggestion envelope.

## Replay Requirements

Future provider selection should record:

- self-resolution result;
- provider assistance decision;
- selected provider id and version;
- selection reason;
- provider request;
- provider response;
- validation result;
- final accepted, rejected, or fail-closed outcome.

## Authority Restrictions

Provider selection does not grant:

- execution authority;
- governance authority;
- authorization authority;
- replay authority;
- worker authority.

## Final Classification

```text
HUMAN_PROMPT_PROVIDER_SELECTION_STATUS = CERTIFIED
```

Provider selection belongs to AiGOL governance constraints, not direct human or
provider authority.
