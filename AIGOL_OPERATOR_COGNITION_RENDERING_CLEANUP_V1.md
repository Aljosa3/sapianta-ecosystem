# AIGOL_OPERATOR_COGNITION_RENDERING_CLEANUP_V1

## Status

Implemented operator cognition rendering cleanup.

## Goal

Human operators should see structured cognition content, not raw provider payloads, JSON fragments, artifact structures, or implementation details.

## Runtime Trace

The active rendering path is:

```text
Provider Response
-> LLM_COGNITION_ARTIFACT_V1
-> OCS_LLM_COGNITION_END_TO_END_ARTIFACT_V1.human_facing_cognition_result
-> render_operator_visible_ocs_llm_cognition(...)
-> CLI Output
```

The technical summary remains separate:

```text
render_ocs_llm_cognition_end_to_end_summary(...)
```

## Root Cause

The prior operator-visible projection used comparison artifact content for operator findings.

In single-provider primary mode, comparison findings include runtime statements such as:

```text
Single-provider primary cognition completed.
Comparison was not performed in default conversational OCS mode.
Provider cognition confidence: ...
```

If normalized cognition contained a JSON-looking string inside a finding, that string could also be rendered directly.

This exposed internal representation too close to the operator surface.

## Canonical Operator Sources

The canonical source for operator cognition sections is now:

```text
LLM_COGNITION_ARTIFACT_V1
```

Mapped fields:

- Findings -> `llm_cognition_artifact.findings`
- Assumptions -> `llm_cognition_artifact.assumptions`
- Risks -> `llm_cognition_artifact.risks`
- Uncertainties -> `llm_cognition_artifact.uncertainties`
- Clarification Questions -> clarification artifact candidate questions
- Recommended Next Milestone -> deterministic human-review milestone text

Comparison artifacts remain replay-visible evidence, but they are not the source for operator cognition content.

## Rendering Cleanup

The operator renderer now:

- renders only normalized text items;
- unwraps JSON-looking strings only to extract the relevant operator field;
- drops JSON-looking strings that cannot be safely mapped to an operator section;
- suppresses raw provider payloads;
- suppresses artifact schemas and runtime fields;
- suppresses replay implementation details;
- suppresses provider implementation details;
- suppresses authority flags from the operator cognition section.

The technical summary still preserves replay references and runtime metadata after the operator section.

## Governance Boundary

This change does not alter:

- provider invocation;
- cognition artifact creation;
- replay persistence;
- routing;
- dispatch;
- provider non-authority;
- approval behavior;
- worker invocation behavior;
- governance mutation behavior.

Provider cognition remains non-authoritative and human-review-bound.

## Regression Coverage

Regression tests cover:

- structured cognition payloads;
- partial cognition payloads;
- missing optional fields;
- large cognition payloads;
- embedded JSON-looking finding strings;
- preservation of the existing technical summary.

