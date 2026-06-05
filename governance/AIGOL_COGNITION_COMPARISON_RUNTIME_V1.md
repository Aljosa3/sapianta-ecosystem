# AIGOL_COGNITION_COMPARISON_RUNTIME_V1

## Status

Certified cognition comparison runtime.

This milestone compares multiple `LLM_COGNITION_ARTIFACT_V1` outputs and produces one governed, non-authoritative comparison artifact:

```text
COGNITION_COMPARISON_ARTIFACT_V1
```

## Scope

Runtime:

- `aigol/runtime/cognition_comparison_runtime.py`

Input:

- `MULTI_PROVIDER_COGNITION_RESULT_BUNDLE_V1`
- multiple `LLM_COGNITION_ARTIFACT_V1` outputs inside the result bundle

Output:

- `COGNITION_COMPARISON_ARTIFACT_V1`

Classification:

```text
CERTIFIED_COGNITION_COMPARISON_RUNTIME
```

## Implemented Flow

```text
Human Question
-> OCS Context
-> Multiple Cognition Providers
-> Multiple Cognition Artifacts
-> COGNITION_COMPARISON_ARTIFACT_V1
```

## Comparison Model

The runtime detects:

- agreement;
- disagreement;
- conflicting assumptions;
- conflicting risks;
- conflicting alternatives;
- uncertainty;
- missing information.

The comparison method is deterministic:

- exact normalized text overlap identifies shared agreement;
- provider-specific normalized findings identify disagreement;
- provider-specific assumptions, risks, and alternatives identify conflicts;
- source uncertainties and provider failures become uncertainty evidence;
- empty cognition fields and failed providers become missing information evidence.

## Comparison Confidence

The runtime produces:

```text
comparison_confidence
```

Confidence is derived from:

- source cognition artifact confidence values;
- detected disagreements;
- conflicting assumptions, risks, and alternatives;
- missing information;
- provider failures.

Confidence remains a bounded comparison assessment. It is not approval, execution authority, or governance authority.

## Replay Requirements

The comparison artifact includes:

- source result bundle hash;
- source cognition artifact hashes;
- source cognition hashes;
- provider identities;
- provider identity hashes;
- context hash;
- comparison hash;
- replay lineage.

Replay reconstructs:

- comparison artifact;
- returned comparison reference;
- replay wrapper hashes;
- artifact hashes;
- comparison hash;
- lineage references.

## Boundary Preservation

The comparison remains non-authoritative.

The runtime does not create:

- approval;
- execution;
- worker invocation;
- dispatch;
- domain creation;
- governance mutation;
- replay mutation.

## Explicit Non-Goals Preserved

This milestone does not implement:

- continuity integration;
- memory integration;
- clarification integration;
- worker invocation;
- execution;
- approval creation.

Those remain later governed milestones.

## Certification Statement

`AIGOL_COGNITION_COMPARISON_RUNTIME_V1` certifies deterministic comparison of multiple provider-assisted cognition artifacts into one replay-visible, non-authoritative `COGNITION_COMPARISON_ARTIFACT_V1`.
