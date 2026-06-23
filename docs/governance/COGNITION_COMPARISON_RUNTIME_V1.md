# COGNITION_COMPARISON_RUNTIME_V1

Status: Runtime Ready

Scope: Multi-provider cognition comparison for OCS.

Target flow:

```text
Human
-> OCS
-> Provider A / Provider B / Provider C
-> Cognition Artifacts
-> Comparison Runtime
-> Agreement Analysis
-> Disagreement Analysis
-> Confidence Synthesis
-> Human Review
-> Replay
```

## 1. Architecture Review

The cognition comparison capability is implemented through the existing runtime stack:

- `aigol/runtime/multi_provider_cognition_runtime.py`
- `aigol/runtime/cognition_comparison_runtime.py`
- `aigol/runtime/ocs_llm_cognition_end_to_end_runtime.py`

The multi-provider runtime invokes approved cognition providers under a replay-visible OCS context and produces a `MULTI_PROVIDER_COGNITION_RESULT_BUNDLE_V1`.

The comparison runtime consumes the result bundle, extracts completed `LLM_COGNITION_ARTIFACT_V1` artifacts, compares provider outputs, synthesizes confidence, and emits a `COGNITION_COMPARISON_ARTIFACT_V1`.

The OCS end-to-end runtime integrates comparison as a governed stage after provider cognition and before continuity and clarification.

## 2. Runtime Design

The runtime design is intentionally non-authoritative.

Providers may produce cognition artifacts, but they do not approve, authorize, execute, mutate governance, invoke workers, or mutate replay.

The comparison runtime may compare, summarize, identify agreement, identify disagreement, and lower confidence when conflicts or missing information exist.

The comparison runtime may not:

- approve decisions
- authorize execution
- invoke workers
- dispatch tasks
- create domains
- mutate governance
- mutate replay history
- replace human review

Human review remains the authority boundary after comparison.

## 3. Artifact Contract

Required source input:

```text
MULTI_PROVIDER_COGNITION_RESULT_BUNDLE_V1
```

Required cognition sources:

```text
LLM_COGNITION_ARTIFACT_V1
```

Required comparison output:

```text
COGNITION_COMPARISON_ARTIFACT_V1
```

Required returned artifact:

```text
COGNITION_COMPARISON_RETURNED_V1
```

The comparison artifact must include:

- source bundle hash
- source result bundle hash
- context hash
- source cognition artifact summaries
- provider identities
- agreement
- disagreement
- conflicting assumptions
- conflicting risks
- conflicting alternatives
- uncertainty
- missing information
- comparison confidence
- lineage references
- authority flags
- human review requirement
- replay visibility

The comparison artifact must set all authority flags to false.

## 4. Agreement Analysis

Agreement analysis uses deterministic normalized text overlap across provider findings.

An item is agreement only when the normalized finding appears across all compared provider cognition artifacts.

Agreement is evidence for human review, not an approval.

## 5. Disagreement Analysis

Disagreement analysis identifies provider-specific findings that do not appear across all compared providers.

The runtime also identifies provider-specific conflicts in:

- assumptions
- risks
- alternatives

Disagreement lowers confidence but does not itself authorize clarification, rejection, approval, or execution.

## 6. Confidence Synthesis

Confidence synthesis uses bounded provider confidence and applies penalties for:

- provider failures
- missing information
- conflicting findings
- conflicting assumptions
- conflicting risks
- conflicting alternatives

The comparison confidence is a review signal only.

## 7. Replay Model

Comparison replay consists of:

```text
000_cognition_comparison_artifact.json
001_cognition_comparison_returned.json
```

Replay reconstruction verifies:

- replay ordering
- wrapper hash
- artifact hash
- returned comparison hash
- comparison hash
- append-only replay behavior

Replay remains the source of truth.

## 8. Fail-Closed Requirements

The comparison runtime must fail closed when:

- source result bundle is malformed
- source result bundle is not completed
- source result bundle already contains comparison
- fewer than two cognition artifacts are available
- cognition artifact type is invalid
- cognition artifact hash is invalid
- cognition artifact is authoritative
- cognition artifact requests approval, execution, worker invocation, governance mutation, or replay mutation
- replay artifacts are missing, reordered, or tampered

Failure output must remain replay-visible and non-authoritative.

## 9. Implementation Plan

Current runtime implementation exists.

Required implementation posture:

- preserve existing `cognition_comparison_runtime.py`
- preserve existing `multi_provider_cognition_runtime.py`
- preserve OCS end-to-end integration
- avoid introducing new workflow families
- harden only where tests expose concrete gaps
- maintain deterministic replay reconstruction
- expand tests only around observed runtime risk

No architecture redesign is required.

## 10. Validation Strategy

Required validation:

```bash
python -m pytest tests/test_cognition_comparison_runtime_v1.py
python -m pytest tests/test_cognition_comparison_certification_v1.py
python -m pytest tests/test_ocs_llm_cognition_end_to_end_runtime_v1.py -k "comparison or provider_failure"
git diff --check
```

Validation must prove:

- agreement detection
- disagreement detection
- confidence synthesis
- provider failure isolation
- non-authoritative comparison boundary
- fail-closed malformed source handling
- replay reconstruction
- replay tamper detection
- OCS end-to-end integration

## 11. Final Verdict

```text
COGNITION_COMPARISON_RUNTIME_READY
```
