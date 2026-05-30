# Conversation Duplication Risks V1

Status: duplication and boundary risk analysis.

## Constitutional Memory Consultation

Risk:

- Conversation could duplicate Constitutional Memory retrieval by answering constitutional questions without citations.

Boundary:

- cited constitutional claims should route to Memory Consultation.

## Provider Proposal

Risk:

- Conversation could become hidden provider interaction.

Boundary:

- provider use must route through Provider Proposal or a future governed provider-backed conversation model.

## Execution Request

Risk:

- Conversation could answer as if it authorized or performed work.

Boundary:

- execution intent must route to Execution Request and authorization.

## Human Request Processing

Risk:

- Conversation could duplicate prompt normalization or routing.

Boundary:

- Conversation should consume routed prompt evidence, not create a parallel request layer.

## Governance

Risk:

- Conversation could sound like governance authority.

Boundary:

- Conversation is explanation only unless a separate governance boundary produces a decision.

## Anti-Duplication Rule

Conversation must remain:

```text
routed prompt evidence
-> bounded non-authoritative response
-> replay-visible termination
```

