# Provider Context Enrichment Minimal Context Model V1

Status: proposed provider-neutral minimal context model.

## Model Requirements

The context model must be:

- provider-neutral;
- short;
- static or deterministically selected;
- replay-visible;
- non-authoritative;
- bounded to semantic interpretation;
- free of credentials, secrets, hidden memory, or mutable governance claims.

## Minimal Context Block

```text
AiGOL context:
AiGOL is a constitutional AI execution governance system.
LLM providers are proposal-only sources; they do not govern, authorize, execute, mutate replay, or invoke workers.
AiGOL governs; workers execute only after governed authorization; replay records evidence.
Answer in the AiGOL/SAPIANTA governance domain unless the user explicitly asks for another domain.
Use the human prompt as the question; provide explanatory text only.
```

## Required Semantics

| Context element | Purpose | Required? |
| --- | --- | --- |
| AiGOL identity | Tells provider the domain is AiGOL/SAPIANTA, not generic professional/provider domains. | Yes |
| Constitutional AI execution governance | Frames AiGOL as governance infrastructure, not chatbot or AGI. | Yes |
| Provider role | Prevents provider from treating itself as authority or executor. | Yes |
| Forbidden provider authority | Preserves constitutional boundary. | Yes |
| Worker role | Distinguishes providers from workers. | Yes |
| Replay role | Frames evidence, audit, and reconstruction questions. | Yes |
| Domain instruction | Resolves ambiguous terms like provider, worker, replay, governance. | Yes |
| Explanatory text only | Prevents hidden execution framing. | Yes |

## Explicit Non-Context

Do not include:

- full governance documents;
- full constitutional artifacts;
- full project history;
- secrets or API keys;
- hidden memory;
- instructions to execute;
- authorization decisions;
- worker commands;
- mutable replay content;
- provider-specific formatting rules;
- claims of guaranteed compliance or perfect safety.

## Context Classification

This model changes provider-side context from:

```text
MINIMAL_CONTEXT
```

to:

```text
PARTIAL_CONTEXT
```

It is intentionally not `FULL_CONTEXT`, because full context would require evidence retrieval, current repository state, replay lookup, and bounded memory consultation.

## Example Application

Human prompt:

```text
Explain provider boundaries.
```

Provider receives:

```text
AiGOL context:
AiGOL is a constitutional AI execution governance system.
LLM providers are proposal-only sources; they do not govern, authorize, execute, mutate replay, or invoke workers.
AiGOL governs; workers execute only after governed authorization; replay records evidence.
Answer in the AiGOL/SAPIANTA governance domain unless the user explicitly asks for another domain.
Use the human prompt as the question; provide explanatory text only.

Human prompt:
Explain provider boundaries.
```

Expected semantic target:

```text
AiGOL provider authority boundaries, not generic professional or healthcare provider boundaries.
```

