# ACLI_LLM_ASSISTED_EXPLANATION_LAYER_V1

Status: Ready

Scope: ACLI operator explanation architecture

Target verdict:

```text
ACLI_LLM_ASSISTED_EXPLANATION_LAYER_READY
```

## 1. Purpose

This artifact defines how ACLI may use LLM providers to improve human-facing explanation of technical runtime state while preserving existing authority boundaries.

The purpose is not to make LLMs part of routing, governance, approval, execution, validation, or replay authority. The purpose is to allow optional provider-assisted explanation when deterministic ACLI explanation is insufficient for operator comprehension.

The explanation layer must help an operator understand:

- what ACLI understood;
- which workflow ACLI selected;
- what state the workflow is in;
- whether approval is required;
- what will and will not happen next;
- where replay evidence is recorded.

## 2. Architecture Review

The existing deterministic explanation layer remains the baseline.

The optional LLM-assisted explanation layer belongs after ACLI has already produced technical runtime state:

```text
Human Prompt
-> HIRR
-> Deterministic Routing
-> Workflow Selection
-> Technical Runtime State
-> Deterministic Explanation
-> Optional Provider-Assisted Explanation
-> Human Review
-> Replay
```

The provider-assisted explanation may consume replay-visible technical state and produce a plain-language rendering for the operator.

It must not:

- classify intent;
- select workflows;
- alter routing confidence;
- approve proposals;
- authorize execution;
- create worker requests;
- invoke workers;
- modify repository state;
- modify governance artifacts;
- modify deterministic replay history;
- override deterministic explanation;
- hide fail-closed state.

If provider assistance fails, is unavailable, malformed, or attempts to claim authority, ACLI must fall back to deterministic explanation or fail closed for the provider-assisted explanation only.

## 3. Authority Analysis

ACLI remains authoritative for workflow state.

Authoritative state includes:

- HIRR classification;
- routing decision;
- workflow selection;
- proposal status;
- approval requirement;
- approval decision;
- authorization status;
- execution status;
- validation status;
- replay references;
- fail-closed status.

The LLM provider is non-authoritative.

Provider output may:

- paraphrase technical state;
- explain terminology;
- summarize why approval is required;
- clarify what the operator can type next;
- identify uncertainty already present in technical artifacts;
- improve readability.

Provider output may not:

- create new facts;
- claim approval exists;
- claim execution is authorized;
- claim validation passed;
- change the selected workflow;
- soften fail-closed language into success language;
- infer missing approval or replay evidence;
- recommend bypassing governance.

The displayed explanation must identify provider-assisted content as explanatory only.

## 4. Replay Impact

Replay must remain the source of truth.

Each ACLI turn using provider-assisted explanation must preserve both:

- the technical runtime state used as explanation input;
- the rendered explanation shown to the operator.

Required replay evidence:

- explanation request identifier;
- source technical artifact references;
- source technical artifact hashes;
- deterministic explanation hash;
- provider identifier, when used;
- provider request payload hash;
- provider response hash;
- rendered explanation hash;
- authority flags showing explanation is non-authoritative;
- fallback status when provider assistance is unavailable or rejected;
- replay reference for the explanation artifact.

The replay record must make it possible to reconstruct:

- what ACLI knew deterministically;
- what the deterministic explanation said;
- whether a provider was asked for assistance;
- what the provider returned;
- what was displayed to the operator;
- whether provider output was accepted for display or rejected.

Replay reconstruction must fail closed if the explanation artifact claims authority or if source hashes do not match.

## 5. Provider Role Definition

Provider role:

```text
Provider = optional explanation assistant
```

The provider may receive a bounded explanation context such as:

- workflow name;
- current workflow state;
- approval status;
- mutation status;
- validation status;
- replay location;
- deterministic explanation text;
- known failure reason;
- allowed operator choices.

The provider must not receive secrets or uncontrolled repository content unless the selected workflow already permits that content and replay can record the exposure safely.

Provider output must be constrained to:

- explanation text;
- optional terminology clarification;
- optional uncertainty notes;
- optional operator-facing next-step summary.

Provider output must include no executable instructions beyond approved operator choices already supplied by ACLI.

## 6. Deterministic Baseline

The deterministic explanation remains required even when provider assistance is enabled.

The deterministic explanation must be sufficient to operate ACLI without a provider.

Provider assistance is allowed only as a derived rendering over deterministic facts.

If the provider explanation conflicts with deterministic state, ACLI must prefer deterministic state and either:

- display only the deterministic explanation; or
- display the provider explanation with the conflicting portion removed and replay-visible rejection evidence.

The preferred initial implementation is conservative:

```text
deterministic explanation required
provider explanation optional
provider failure does not block deterministic operation
provider authority claim rejected
```

## 7. Deterministic Learning Path

Repeated provider-assisted explanation patterns may later become deterministic explanations only through the governed replay-derived improvement path.

The allowed learning path is:

```text
Replay Evidence
-> Explanation Pattern Observation
-> Improvement Proposal
-> Human Review
-> Human Approval
-> Bounded Implementation
-> Validation
-> Replay
-> Certification
```

Replay-derived explanation learning must not:

- update prompts silently;
- update deterministic templates automatically;
- change routing behavior;
- change workflow behavior;
- change approval behavior;
- promote provider text directly into runtime logic;
- bypass human approval.

The replay-derived improvement proposal must include:

- source replay references;
- observed operator confusion or repeated explanation pattern;
- proposed deterministic wording;
- affected workflow states;
- authority boundary analysis;
- validation plan;
- rollback plan.

Human approval is required before any provider-derived wording becomes deterministic ACLI behavior.

## 8. Implementation Options

### Option A: Deterministic Only

Keep the existing deterministic explanation layer as the only operator-facing explanation.

Benefits:

- simplest authority model;
- no provider dependency;
- easiest replay reconstruction;
- lowest operational risk.

Limitations:

- less adaptive to operator confusion;
- slower UX refinement.

### Option B: Optional Single-Provider Explanation

Generate deterministic explanation first, then ask one approved provider to produce a clearer plain-language version.

Required safeguards:

- provider output marked non-authoritative;
- deterministic source facts preserved;
- conflict detection against key status fields;
- replay evidence for request and response;
- deterministic fallback on provider failure.

This is the recommended first implementation option if provider assistance is needed.

### Option C: Multi-Provider Explanation Comparison

Use existing multi-provider cognition and comparison capabilities to generate and compare explanations.

Benefits:

- disagreement visibility;
- lower risk of single-provider misleading wording;
- stronger audit evidence.

Costs:

- more replay artifacts;
- slower operator feedback;
- higher implementation complexity.

This option should be reserved for high-stakes explanation contexts or certification review, not the default CLI path.

### Option D: Replay-Derived Deterministic Promotion

Use replay evidence from provider-assisted explanations to propose deterministic template improvements.

This option is not a live explanation path. It is a governed improvement path and must follow replay-derived improvement governance.

## 9. Recommended Runtime Boundary

Recommended boundary:

```text
ACLI deterministic runtime produces state.
ACLI deterministic explanation renders baseline explanation.
Optional provider explanation renders non-authoritative plain-language help.
ACLI validates provider explanation against authority flags.
Replay records both deterministic and provider-assisted explanation evidence.
Human remains authority.
```

The provider-assisted explanation artifact should be separate from the deterministic explanation artifact so reviewers can distinguish:

- certified technical state;
- deterministic explanation;
- provider-assisted rendering;
- final displayed text.

The provider-assisted explanation must never be the only replay evidence for workflow state.

## 10. Fail-Closed Requirements

ACLI must reject provider-assisted explanation when:

- source technical state is missing;
- deterministic explanation is missing;
- provider output claims authority;
- provider output contradicts approval, mutation, validation, or fail-closed state;
- provider output suggests unsupported operator actions;
- provider output hides replay location;
- provider output is malformed;
- provider output cannot be replayed.

Failure of optional provider explanation must not authorize execution and must not mutate repository state.

## 11. Implementation Plan

Minimum implementation work:

1. Define a provider-assisted explanation artifact contract.
2. Add an optional explanation provider adapter call after deterministic explanation creation.
3. Validate provider output against deterministic state.
4. Render provider-assisted text only when validation passes.
5. Persist provider request, response, validation result, and displayed explanation.
6. Add replay reconstruction checks.
7. Add tests for provider success, provider unavailability, contradiction rejection, authority-claim rejection, and deterministic fallback.

No routing, approval, execution, validation, worker, or workflow behavior should change.

## 12. Validation Strategy

Validation must prove:

- deterministic explanation still works without a provider;
- provider-assisted explanation is marked non-authoritative;
- provider output cannot alter workflow state;
- provider output cannot authorize execution;
- provider output cannot hide approval requirements;
- replay records technical state and explanation state separately;
- malformed or conflicting provider output is rejected;
- replay reconstruction detects tampering.

Suggested tests:

```bash
python -m pytest tests/test_acli_human_friendly_explanation_runtime_v1.py
python -m pytest tests/test_ocs_llm_cognition_end_to_end_runtime_v1.py -k provider
git diff --check
```

## 13. Final Verdict

ACLI may use LLM providers for human-facing explanation only when provider participation remains optional, non-authoritative, replay-visible, and subordinate to deterministic ACLI state.

The recommended next step is optional single-provider explanation behind deterministic fallback, with replay-derived promotion to deterministic wording allowed only through governed improvement proposal and human approval.

```text
ACLI_LLM_ASSISTED_EXPLANATION_LAYER_READY
```
