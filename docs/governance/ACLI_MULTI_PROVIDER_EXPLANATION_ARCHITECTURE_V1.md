# ACLI_MULTI_PROVIDER_EXPLANATION_ARCHITECTURE_V1

Status: Ready

Scope: ACLI explanation provider architecture with adaptive escalation

Extension:

```text
ADAPTIVE_EXPLANATION_ESCALATION_V1
```

Target verdict:

```text
ADAPTIVE_EXPLANATION_ESCALATION_READY
```

## 1. Purpose

This artifact extends ACLI explanation architecture with an adaptive escalation model for human-facing explanations.

The purpose is to allow ACLI to improve operator comprehension when deterministic explanations are insufficient, while preserving the existing governance boundaries:

- deterministic ACLI runtime state remains authoritative;
- explanation providers remain non-authoritative;
- provider output cannot approve, authorize, execute, validate, mutate, or alter replay truth;
- replay records explanation inputs, escalation decisions, provider participation, operator clarification requests, and final displayed text.

This artifact does not redesign ACLI, HIRR, workflow routing, approval, execution, validation, replay, or provider governance.

## 2. Escalation Architecture

The canonical escalation ladder is:

```text
Deterministic Explanation
-> Low-Cost Explanation Provider
-> High-Capability Explanation Provider
-> Multi-Provider Explanation Comparison
```

The ladder is optional and bounded. Deterministic explanation remains the preferred default path.

The escalation ladder is invoked only when ACLI has already produced authoritative technical state:

```text
Human Prompt
-> HIRR
-> Routing
-> Workflow Selection
-> Technical Runtime State
-> Deterministic Explanation
-> Optional Explanation Escalation
-> Human Review
-> Replay
```

Escalation may improve wording, summarize technical state, or clarify operator next steps. It may not change the technical state.

## 3. Authority Model

ACLI remains authoritative for:

- workflow state;
- selected workflow;
- approval requirement;
- approval decision;
- authorization state;
- mutation state;
- validation state;
- replay references;
- fail-closed status.

Explanation providers are authoritative for nothing.

Providers may:

- restate deterministic facts in clearer language;
- explain runtime terms;
- identify which parts of the deterministic explanation may confuse an operator;
- propose clearer wording;
- ask for operator clarification when ACLI has recorded ambiguity.

Providers may not:

- infer approval;
- claim execution is authorized;
- claim validation passed;
- change workflow status;
- hide fail-closed state;
- propose bypassing approval;
- create or modify repository artifacts;
- alter replay evidence;
- become the source of truth for any runtime fact.

Provider output must be labeled as explanatory and non-authoritative when displayed or stored.

## 4. Provider Tiering Model

### 4.1 Tier 0: Deterministic Explanation

Tier 0 is the default.

Inputs:

- technical runtime state;
- deterministic workflow status;
- approval state;
- validation state;
- replay references.

Output:

- deterministic operator explanation;
- diagnostics section;
- replay-visible rendered text.

Escalation should not occur when Tier 0 is sufficient.

### 4.2 Tier 1: Low-Cost Explanation Provider

Tier 1 may be used for simple paraphrasing.

Appropriate use:

- operator asks "what does this mean?";
- deterministic explanation contains too many status constants;
- explanation can be improved without complex reasoning;
- no conflicting runtime facts exist.

Constraints:

- provider receives only bounded explanation context;
- provider output is checked against authoritative runtime fields;
- provider cannot introduce new actions beyond ACLI-approved choices;
- deterministic explanation remains available.

### 4.3 Tier 2: High-Capability Explanation Provider

Tier 2 may be used when the explanation requires deeper synthesis.

Appropriate use:

- multiple workflow states are visible;
- rejection or modification state needs careful explanation;
- validation failure requires operator-friendly summary;
- replay path has multiple evidence locations;
- operator confusion persists after Tier 1.

Constraints:

- same non-authority rules as Tier 1;
- stronger conflict checks against runtime state;
- explicit replay record of why Tier 2 was selected;
- higher-cost use must be justified in replay.

### 4.4 Tier 3: Multi-Provider Explanation Comparison

Tier 3 uses more than one provider and compares explanation outputs.

Appropriate use:

- high-stakes operator-facing explanations;
- provider outputs disagree;
- Tier 2 output is ambiguous or conflicts with deterministic state;
- certification or audit review requires confidence in explanation clarity;
- repeated operator confusion appears in replay.

The comparison runtime remains non-authoritative.

It may identify:

- agreement between providers;
- disagreement between providers;
- unsupported claims;
- ambiguity;
- missing context;
- preferred wording for human review.

It may not approve, authorize, execute, mutate, or replace deterministic ACLI state.

## 5. Escalation Decision Model

Escalation must be deterministic where possible.

Valid escalation triggers include:

- operator explicitly requests a simpler explanation;
- operator asks a clarification question about current state;
- deterministic explanation contains a failure reason longer than a configured threshold;
- deterministic explanation contains multiple replay references without labels;
- deterministic explanation includes more than a configured number of runtime constants;
- workflow is waiting for `REQUEST_MODIFICATION` details;
- validation failed and the raw failure reason is technical;
- provider-assisted explanation from a lower tier is malformed;
- provider-assisted explanation conflicts with deterministic state;
- multi-provider comparison is required by certification or audit policy.

Invalid escalation triggers:

- desire to improve routing;
- desire to change approval state;
- desire to decide whether execution should proceed;
- desire to generate repository mutations;
- desire to replace deterministic explanation entirely.

Every escalation decision must produce replay-visible evidence.

## 6. Ambiguity Detection Options

Ambiguity detection may be deterministic, provider-assisted, or operator-requested.

### 6.1 Deterministic Ambiguity Detection

Recommended default.

Signals:

- missing proposal target paths;
- missing replay location labels;
- fail-closed reason present;
- multiple possible next actions;
- operator entered `REQUEST_MODIFICATION`;
- workflow state is waiting for operator input;
- technical status constants appear in primary output.

### 6.2 Operator-Requested Ambiguity

The operator may request clarification with prompts such as:

```text
Explain this in simpler terms.
What should I do next?
Why is approval required?
What changed?
Where is the replay evidence?
```

These requests should be recorded as operator clarification requests.

### 6.3 Provider-Assisted Ambiguity Detection

A provider may be asked whether an explanation is likely confusing, but the result is advisory.

Provider ambiguity analysis may not:

- change workflow state;
- decide escalation alone;
- suppress deterministic explanation;
- remove diagnostic evidence.

## 7. Replay Impact

Replay must record the full explanation chain.

Required replay evidence:

- authoritative technical state references;
- deterministic explanation artifact and hash;
- ambiguity signals detected;
- escalation decision;
- escalation tier selected;
- reason for escalation;
- provider identifiers used;
- provider request payload hashes;
- provider response hashes;
- provider output validation result;
- comparison artifact, when multi-provider comparison is used;
- final rendered explanation shown to the operator;
- operator clarification requests;
- authority flags proving all provider output is non-authoritative;
- fallback result when escalation fails or is rejected.

Replay reconstruction must verify:

- deterministic explanation existed before provider escalation;
- provider output did not alter authoritative state;
- escalation reason matches recorded ambiguity signals or operator request;
- displayed provider text matches the persisted provider-assisted explanation artifact;
- comparison artifacts are present when Tier 3 is used;
- no provider output claims approval, authorization, mutation, validation success, or replay authority.

## 8. Operator Clarification Request Recording

When an operator asks for clarification, ACLI should record:

- original operator prompt;
- current workflow state;
- deterministic explanation hash;
- clarification request text;
- whether escalation was used;
- selected provider tier;
- final explanation displayed;
- replay reference.

Clarification requests are evidence of usability friction. They do not authorize runtime action.

## 9. Cost Impact

The escalation model is cost-aware.

Cost posture:

- Tier 0 has no provider cost and must remain the default.
- Tier 1 should be used for low-risk, low-cost paraphrase assistance.
- Tier 2 should require explicit escalation reason or repeated confusion.
- Tier 3 should be rare and reserved for high-stakes, conflicting, or review-sensitive explanations.

Cost controls:

- deterministic thresholding before provider use;
- provider budget limits per session;
- operator opt-in for provider-assisted explanation;
- maximum escalation tier per workflow class;
- replay-visible cost class for each provider call;
- fallback to deterministic explanation when budget is exhausted.

Cost must never be a reason to bypass governance, hide confusion, or present unsupported state.

## 10. Deterministic Learning Path

Replay-derived patterns may later promote improved deterministic explanations.

Allowed path:

```text
Replay Evidence
-> Operator Confusion Pattern
-> Explanation Improvement Proposal
-> Human Review
-> Human Approval
-> Bounded Implementation
-> Validation
-> Replay
-> Certification
```

Valid promotion candidates:

- repeated operator clarification requests for the same status;
- repeated Tier 1 paraphrases accepted by operators;
- repeated Tier 2 explanations that clarify validation failures;
- repeated provider comparisons showing stable explanation wording;
- audit findings that diagnostic fields should be relabeled.

Promotion is forbidden when:

- provider text includes unsupported claims;
- provider text changes governance meaning;
- provider text alters approval semantics;
- provider text reduces fail-closed visibility;
- provider text hides replay evidence;
- no human approval exists.

Deterministic explanation remains the preferred default even after improvements are promoted.

## 11. Implementation Recommendations

### P0: Keep Deterministic Explanation Default

No provider should be invoked unless:

- the operator requests clarification;
- deterministic ambiguity triggers fire;
- workflow policy permits escalation.

### P0: Add Escalation Decision Artifact

Define an artifact for:

- source deterministic explanation hash;
- ambiguity signal;
- selected tier;
- escalation reason;
- provider budget class;
- authority flags.

### P0: Add Provider Output Validation

Reject provider output that:

- contradicts authoritative state;
- claims authority;
- suggests unsupported operator actions;
- omits approval or replay boundaries;
- hides fail-closed state.

### P1: Add Low-Cost Provider Path

Implement Tier 1 as optional paraphrase assistance over deterministic explanation.

### P1: Add Operator Clarification Capture

Persist operator clarification prompts as replay evidence and link them to explanation artifacts.

### P2: Add High-Capability Provider Path

Use Tier 2 only when Tier 1 is insufficient or ambiguity is high.

### P2: Add Multi-Provider Explanation Comparison

Use existing comparison architecture for high-stakes explanation review or repeated provider disagreement.

## 12. Validation Strategy

Validation must prove:

- deterministic explanation works without providers;
- escalation does not alter workflow state;
- provider output is marked non-authoritative;
- provider output cannot authorize execution;
- provider output cannot hide replay or approval boundaries;
- escalation decisions are replayed;
- operator clarification requests are replayed;
- provider failure falls back to deterministic explanation;
- multi-provider disagreement does not change authority.

Suggested validation:

```text
python -m pytest tests/test_acli_human_friendly_explanation_runtime_v1.py
python -m pytest tests/test_cognition_comparison_runtime_v1.py
git diff --check
```

## 13. Final Verdict

Adaptive explanation escalation is ready as an architecture pattern.

The escalation ladder is permitted only because it remains optional, replay-visible, cost-aware, and non-authoritative. ACLI runtime state remains the source of operational truth, and deterministic explanation remains the preferred default.

```text
ADAPTIVE_EXPLANATION_ESCALATION_READY
```
