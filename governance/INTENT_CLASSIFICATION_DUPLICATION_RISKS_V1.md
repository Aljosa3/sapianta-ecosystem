# Intent Classification Duplication Risks V1

Status: duplication and overengineering risk analysis.

## Core Risk

Future intent classification could duplicate existing bounded surfaces if it attempts to become a routing engine, provider adapter, memory retriever, execution normalizer, or governance authorizer.

## Duplication Risks

### Human Request Processing

Risk: duplicating operator entrypoint normalization.

Mitigation: classifier should consume normalized Human Prompt evidence rather than create a second request-processing layer.

### Constitutional Memory Retrieval

Risk: duplicating retrieval scope selection, citation generation, or replay visibility.

Mitigation: classifier may choose `MEMORY_CONSULTATION` but must let the memory access path perform retrieval.

### Provider Attachment

Risk: duplicating provider request formatting or proposal normalization.

Mitigation: classifier may choose `PROVIDER_PROPOSAL` but must not become provider adapter logic.

### Execution Authorization

Risk: treating execution intent classification as authorization.

Mitigation: classifier output must remain pre-authorization evidence.

### Governance

Risk: classifier becomes hidden governance.

Mitigation: classifier must be replay-visible, fail-closed, and explicitly non-authoritative.

## Anti-Overengineering Rule

Do not introduce:

- intent engine
- autonomous routing
- provider auto-selection
- worker auto-selection
- correction loops
- semantic planner

until a specific downstream gap proves they are required.

## Safe Future Shape

The smallest future model should be:

```text
Human Prompt
-> Intent Classification Artifact
-> Governed Destination Boundary
```

The classifier should stop at classification.

