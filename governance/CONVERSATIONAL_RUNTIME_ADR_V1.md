# Conversational Runtime ADR V1

Status: accepted with gaps.

## Context

AiGOL conversational usage improved across four real conversational usage epochs:

| Epoch | Responses | Rate |
| --- | ---: | ---: |
| Second real conversational usage epoch | 6 / 50 | 12% |
| Third real conversational usage epoch | 6 / 50 | 12% |
| Fourth real conversational usage epoch | 16 / 50 | 32% |
| Fifth real conversational usage epoch | 41 / 50 | 82% |

The current question is whether AiGOL CLI can now be certified as an operational human entry point into AiGOL for conversational operation.

## Decision

Certify AiGOL CLI as:

```text
Operational Human Conversational Entry Point
```

with final classification:

```text
CONVERSATIONAL_RUNTIME_STATUS = CERTIFIED_WITH_GAPS
```

## Basis

The decision is based on:

- human prompt ingress through the CLI prompt submission path;
- fifth epoch majority conversational response coverage;
- provider-assisted intent classification;
- provider-assisted conversation responses;
- replay-visible evidence;
- fail-closed unsuccessful outcomes;
- preserved provider authority isolation;
- preserved worker boundary;
- preserved governance boundary.

## Accepted Claim

AiGOL may claim:

```text
AiGOL CLI is an operational human conversational entry point for the current AiGOL runtime.
```

## Rejected Claims

AiGOL must not claim:

- full conversational coverage;
- unrestricted autonomous operation;
- provider execution authority;
- provider governance authority;
- worker execution through this conversational certification;
- guaranteed OpenAI availability;
- perfect response reliability;
- hidden or automatic remediation of failed classifications.

## Consequences

Conversational operation can now be treated as operationally available for governed human ingress.

The certification remains bounded:

- one current runtime certification;
- one reviewed fifth epoch evidence set;
- 41 / 50 observed success coverage;
- provider remains proposal-only;
- AiGOL remains governing authority;
- worker execution remains outside this certification scope;
- replay evidence remains required for certification continuity.

## Future Work Boundary

Any future work to improve the remaining gaps must be handled as separate governed evolution.

This ADR does not authorize runtime fixes, provider fixes, governance mutation, worker changes, or execution expansion.
