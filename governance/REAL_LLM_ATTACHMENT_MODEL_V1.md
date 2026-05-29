# Real LLM Attachment Model V1

Status: model-only real external LLM attachment definition.

This milestone defines how a real external LLM may connect to AiGOL while preserving the frozen invariant:

```text
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```

This milestone does not implement provider integration, OpenAI integration, Claude integration, Codex integration, API calls, orchestration, memory, capability expansion, execution expansion, or runtime mutation.

## Attachment Role

A real LLM attachment is a proposal source boundary.

It may produce externally generated proposal evidence, but it may not:

- authorize execution
- execute work
- bypass AiGOL validation
- bypass replay
- mutate governance
- create hidden continuation
- introduce orchestration

## Attachment Flow

The model-only flow is:

```text
Human request
-> Provider identity envelope
-> Raw LLM response capture
-> Replay-visible raw response evidence
-> Proposal normalization
-> PROPOSAL_ARTIFACT
-> AiGOL validation
-> AiGOL authorization or rejection
-> Worker execution only if authorized
-> Replay-visible governed result
```

## Boundary Definition

The LLM attachment boundary ends at `PROPOSAL_ARTIFACT`.

The proposal artifact is untrusted input to AiGOL governance. It is not execution authority, authorization evidence, worker instruction authority, or governance mutation authority.

## Required Model Components

The real LLM attachment model requires:

- provider identity model
- raw response capture
- deterministic response hash
- proposal normalization
- fail-closed malformed and ambiguous response handling
- replay linkage from raw response to proposal artifact
- explicit non-authority certification

## Integration Constraint

Future implementation must bind the real LLM attachment into the frozen `FIRST_USEFUL_AIGOL_V1` operator path without weakening:

- proposal-only cognition
- AiGOL governance authority
- authorization-before-execution
- worker execution-only role
- replay centrality
- read-only capability discipline
- fail-closed behavior

## Success Definition

Success for the model is a clear attachment contract for future real provider work.

Success is not a live provider call.
