# COGNITION_RUNTIME_COVERAGE_GAP_ANALYSIS_V1

## Status

Review-only coverage gap analysis.

## Gap 1: Unified Context Assembly

Affected prompt classes:

- current status;
- recent progress;
- replay explanation;
- governance explanation;
- domain-related prompt;
- trading-domain prompt.

Current behavior:

Provider-assisted responses can be produced, but they are not preceded by a canonical context assembly artifact.

Required future capability:

```text
CONTEXT_ASSEMBLY_ARTIFACT_MODEL_V1
```

## Gap 2: Domain Selection Registry

Affected prompt classes:

- domain-related prompt;
- trading-domain prompt;
- ambiguous prompt.

Current behavior:

Trading-related prompts can be answered with provider assistance, but no canonical domain selector routes them to `TRADING`.

Required future capability:

```text
DOMAIN_SELECTION_REGISTRY_V1
```

## Gap 3: Unified Provider Necessity Policy

Affected prompt classes:

- current status;
- recent progress;
- replay explanation;
- governance explanation;
- domain-related prompt;
- ambiguous prompt.

Current behavior:

Provider need is inferred through source routing, deterministic classification failure, and self-resolution failure.

Required future capability:

```text
PROVIDER_NECESSITY_POLICY_V1
```

## Gap 4: Conversation Integration With Evidence-Bound Sources

Affected prompt classes:

- constitutional memory consultation;
- current status;
- recent progress.

Current behavior:

Source router can select evidence-bound sources, but prompt-to-conversation does not yet unify all evidence-bound selections into direct governed response generation.

Required future capability:

```text
EVIDENCE_BOUND_CONVERSATION_RESPONSE_V1
```

## Gap 5: Unsafe Prompt Classification

Affected prompt classes:

- unsafe execution request;
- ambiguous provider/execution prompt.

Current behavior:

Unsafe request fails closed without execution, which is correct. Source routing can still select provider before the conversation path rejects the request.

Required future capability:

```text
UNSAFE_PROMPT_REJECTION_CLASSIFIER_V1
```

## Gap 6: Replay Visibility Rollup

Affected prompt classes:

- all prompt classes.

Current behavior:

Replay artifacts exist, but top-level coverage results need clearer replay visibility rollup.

Required future capability:

```text
COGNITION_REPLAY_VISIBILITY_ROLLUP_V1
```

## Coverage Impact

Current coverage:

```text
representative_prompt_class_coverage = 100%
successful_response_coverage = 75%
healthy_fail_closed_coverage = 25%
```

Coverage blockers for certification:

- context assembly gaps;
- domain selection gaps;
- provider necessity ambiguity;
- evidence-bound conversation integration gap;
- broad replay visibility rollup gap.

## Trading Impact

These gaps do not block explicit-input, evidence-only Trading Worker development.

They do block claims that cognition coverage is fully certified.
