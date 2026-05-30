# Intent Classifier Output Model V1

Status: output model for Intent Classifier.

## Allowed Outputs

The classifier may output exactly one candidate destination:

- `CONVERSATION`
- `CONSTITUTIONAL_MEMORY_CONSULTATION`
- `PROVIDER_PROPOSAL`
- `EXECUTION_REQUEST`

or a fail-closed classification status.

## Multiple Destinations

Multiple destination outputs are not allowed as a successful classification.

If more than one destination is valid, the classifier must emit `FAILED_CLOSED` or `REJECTED` with ambiguity evidence.

## Output Must Not Contain

The classifier output must not contain:

- authorization decision
- governance decision
- execution request
- provider command
- worker command
- memory retrieval result
- proposal artifact
- correction instruction

## Routing Relationship

Classifier output may feed the future routing artifact.

It is not itself routing execution.

## Output Boundary

The classifier output is:

```text
classification evidence
```

not:

```text
destination action
```

