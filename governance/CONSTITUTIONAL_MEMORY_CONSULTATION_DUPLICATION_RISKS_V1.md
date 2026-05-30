# Constitutional Memory Consultation Duplication Risks V1

Status: duplication risk analysis for consultation activation.

## Constitutional Memory Access Path

Risk:

- activation could duplicate `retrieve_constitutional_memory`.

Boundary:

- activation should call or wrap the existing access path, not reimplement retrieval.

## Retrieval Model

Risk:

- activation could redefine retrieval semantics.

Boundary:

- activation must inherit citation, replay, and reference-only requirements.

## Intent Routing

Risk:

- activation could become routing.

Boundary:

- activation consumes routing evidence after routing attachment has selected consultation.

## Governance

Risk:

- consultation evidence could be mistaken for governance decision.

Boundary:

- consultation remains reference evidence only.

## Replay

Risk:

- activation could create parallel replay semantics.

Boundary:

- activation replay must link routing evidence to memory access replay.

## Anti-Duplication Rule

The safe shape is:

```text
Routing Evidence
-> Consultation Activation Record
-> Existing Memory Access Path
-> Citation Bundle
-> Replay Linkage
```

