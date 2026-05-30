# Intent Classification Artifact Routing Relationship V1

Status: canonical relationship between classifier, artifact, and routing.

## Canonical Sequence

```text
Human Prompt Evidence
-> Intent Classifier
-> Intent Classification Artifact
-> Intent Routing Artifact
-> Destination Boundary
```

## Intent Classifier

The classifier evaluates prompt evidence and emits a classification artifact.

The classifier does not route.

## Intent Classification Artifact

The artifact records:

- candidate destination
- classification reason
- ambiguity status
- replay lineage
- authority guarantees

The artifact is evidence for routing.

## Intent Routing

Routing consumes the classification artifact and determines whether a valid route artifact may be emitted.

Routing remains separate and must also be replay-visible and fail-closed.

## Relationship Rule

The classification artifact is necessary input evidence for routing, but it is not routing authority by itself.

## Constitutional Memory Relationship

The artifact may reference Constitutional Memory only when:

- citations came from the memory access path
- memory references are replay-visible
- memory remains `REFERENCE_ONLY`
- references support classification reason only

Classification: `PARTIALLY_SUPPORTED`

