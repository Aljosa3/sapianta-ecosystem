# Conversation Memory Relationship V1

Status: relationship between Conversation and Constitutional Memory.

## Distinction

Conversation is a human-facing response destination.

Constitutional Memory Consultation is a citation-bound reference retrieval destination.

## When To Use Conversation

Use Conversation when:

- the operator asks for clarification that does not require a cited constitutional artifact
- the response is explanatory, not evidentiary
- no authoritative memory claim is needed
- no execution, proposal, or retrieval is required

## When To Use Constitutional Memory Consultation

Use Memory Consultation when:

- the operator asks what the constitution says
- the response depends on a freeze, certification, lineage, or governance artifact
- citations are required
- replay-visible retrieval evidence is required

## Can Conversation Consult Memory?

Classification: `PARTIALLY_SUPPORTED`

Conversation may be followed by a separate Memory Consultation route, but Conversation itself should not silently retrieve memory.

Constraints:

- memory retrieval must use the Constitutional Memory access path
- returned claims must be citation-bound
- retrieval must be replay-visible
- Conversation must not become memory authority

## Distinction Classification

`CONVERSATION_VS_MEMORY_CONSULTATION`: `PARTIAL`

The distinction is conceptually clear, but no classifier currently enforces it.

