# COGNITION_RUNTIME_END_TO_END_COVERAGE_V1

## Status

Review-only end-to-end cognition coverage report.

No runtime implementation, governance mutation, execution behavior change, worker creation, or domain modification is introduced by this coverage review.

## Final Classification

```text
COGNITION_RUNTIME_COVERAGE_STATUS = READY_WITH_GAPS
```

## Purpose

Run and document broad end-to-end cognition coverage across representative prompt classes.

This report evaluates prompt intake, source routing, intent classification, provider-assisted fallback, conversation response validation, fail-closed behavior, replay visibility, and authority boundaries.

## Coverage Method

A 16-case local coverage sweep was run against existing cognition runtimes using temporary replay output under:

```text
/tmp/aigol_cognition_coverage_v1
```

The sweep used existing runtime APIs:

- `route_source_of_truth(...)`;
- `submit_prompt_to_conversation(...)`;
- provider proposal envelope validation;
- provider registry metadata boundaries.

The provider used for the sweep was a local proposal-only coverage adapter. It did not call a real provider, execute work, dispatch workers, or mutate governance.

## Coverage Summary

```text
representative_prompt_class_coverage = 100%
successful_response_coverage = 75%
healthy_fail_closed_coverage = 25%
worker_invoked_count = 0
execution_requested_count = 0
```

Coverage status:

```text
READY_WITH_GAPS
```

## Prompt Classes Covered

Tested prompt classes:

- simple conversation;
- Slovenian conversation;
- AiGOL explanation;
- replay explanation;
- governance explanation;
- current status;
- recent progress;
- constitutional memory consultation;
- provider-needed prompt;
- self-resolution prompt;
- unsupported prompt;
- unsafe execution request;
- domain-related prompt;
- trading-domain prompt;
- ambiguous prompt;
- malformed prompt.

## Direct Answers

### 1. Which prompt classes are handled deterministically?

Deterministically handled as self-resolution:

- AiGOL explanation;
- self-resolution prompt.

Source routing deterministically selected evidence-bound sources for:

- AiGOL explanation;
- replay explanation;
- governance explanation;
- recent progress;
- constitutional memory consultation.

### 2. Which prompt classes require provider assistance?

Provider assistance was used for:

- simple conversation;
- Slovenian conversation;
- replay explanation;
- governance explanation;
- current status;
- recent progress;
- provider-needed prompt;
- domain-related prompt;
- trading-domain prompt;
- ambiguous prompt.

Provider assistance remained proposal-only.

### 3. Which prompt classes fail closed?

Fail-closed classes:

- constitutional memory consultation through prompt-to-conversation path;
- unsupported prompt with provider unavailable;
- unsafe execution request;
- malformed prompt.

Each fail-closed case avoided worker invocation and execution request creation.

### 4. Which prompt classes route incorrectly?

Observed routing gaps:

- current status routed to provider instead of replay/dashboard context;
- unsafe execution request routed to provider by source router instead of direct unsafe/out-of-scope classification;
- ambiguous provider/execution prompt routed to provider instead of ambiguity handling;
- domain-related and trading-domain prompts routed to provider because canonical domain selection is not yet implemented.

### 5. Which prompt classes lack sufficient context assembly?

Classes with context assembly gaps:

- current status;
- recent progress;
- governance explanation;
- replay explanation;
- trading-domain prompt;
- domain-related prompt.

These prompts can receive provider-assisted responses, but the system does not yet assemble a canonical context bundle from dashboard, chain, governance, replay, and domain artifacts before response generation.

### 6. Which prompt classes lack domain selection support?

Classes with domain selection gaps:

- domain-related prompt;
- trading-domain prompt;
- ambiguous prompt that spans provider and execution concepts.

The system has Trading Domain governance artifacts, but no canonical `DOMAIN_SELECTION_REGISTRY_V1` yet.

### 7. Which prompt classes expose provider necessity ambiguity?

Provider necessity ambiguity appears in:

- current status;
- recent progress;
- governance explanation;
- replay explanation;
- domain-related prompt;
- trading-domain prompt;
- ambiguous prompt.

The system can use providers safely, but provider necessity is distributed across source routing, deterministic self-resolution, and provider-assisted fallback.

### 8. Does cognition preserve replay visibility across all cases?

Partially.

The runtime creates replay-visible artifacts in the temporary replay tree for prompt, router, conversation, and fail-closed cases. However, the top-level prompt-to-conversation return object does not consistently expose a simple `replay_visible = true` field for successful responses.

Replay evidence exists, but operator-facing coverage reporting should make this clearer.

### 9. Does provider use remain proposal-only?

Yes.

Observed provider use remained proposal-only:

```text
worker_invoked_count = 0
execution_requested_count = 0
```

Provider responses were validated by AiGOL before final response artifact creation.

### 10. What coverage percentage is achieved?

Representative prompt class coverage:

```text
100%
```

Successful response coverage:

```text
75%
```

Healthy fail-closed coverage:

```text
25%
```

Final coverage status:

```text
READY_WITH_GAPS
```

## Boundary

This coverage review does not introduce:

- runtime changes;
- governance mutation;
- execution behavior changes;
- worker creation;
- domain modification;
- provider authority;
- worker invocation;
- execution request creation.
