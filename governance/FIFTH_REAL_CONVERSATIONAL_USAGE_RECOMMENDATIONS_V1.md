# FIFTH_REAL_CONVERSATIONAL_USAGE_RECOMMENDATIONS_V1

## Recommendation 1: Treat Prompt Continuity Restoration As Materially Effective

The fifth epoch shows that restoring structured `human_prompt` continuity was
the highest-impact improvement since the second epoch baseline.

Evidence:

```text
Fourth epoch success rate = 32%
Fifth epoch success rate = 82%
human_prompt is required failures = 0
```

## Recommendation 2: Next Target Is Ambiguous Classification Evidence

The largest remaining failure class is ambiguous provider-assisted
classification.

Recommended next analysis:

```text
AMBIGUOUS_PROVIDER_CLASSIFICATION_EVIDENCE_ANALYSIS_V1
```

Scope should be evidence-only first:

- inspect provider classification proposals;
- identify why destination evidence remained ambiguous;
- count prompt categories affected;
- preserve fail-closed behavior.

## Recommendation 3: Continue Separating Explanatory Authority Text From Authority Claims

One provider-generated response was rejected for authority-bearing text.

Recommended next analysis:

```text
AUTHORITY_TEXT_VALIDATION_EDGE_CASE_REVIEW_V1
```

The review should distinguish:

- forbidden authority claims;
- safe explanations of authority boundaries;
- unsafe examples that quote or model forbidden claims too directly.

## Recommendation 4: Add Evidence-Grounded State Access As A Future Review Topic

Some accepted answers were valid but evidence-limited for prompts about recent
progress, last result, operation history, and replay ledger.

Recommended review:

```text
CONVERSATIONAL_EVIDENCE_GROUNDING_REVIEW_V1
```

This should remain read-only and replay-safe.

## Recommendation 5: Preserve Current Constitutional Boundaries

No evidence from the fifth epoch supports weakening:

- provider authority boundaries;
- routing authority boundaries;
- worker execution authorization;
- replay visibility;
- fail-closed validation.

The constitutional invariant remains:

```text
LLM proposes. AiGOL governs. Worker executes. Replay records.
```
