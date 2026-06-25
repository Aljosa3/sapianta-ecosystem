# UNIVERSAL_BIDIRECTIONAL_TRANSLATION_RUNTIME_IMPLEMENTATION_PLAN_V1

Status: Ready

Target verdict:

```text
UNIVERSAL_BIDIRECTIONAL_TRANSLATION_RUNTIME_IMPLEMENTATION_READY
```

## 1. Purpose

This implementation plan converts `UNIVERSAL_BIDIRECTIONAL_TRANSLATION_RUNTIME_V1` into an incremental roadmap.

The implementation preserves:

- Human = Authority Layer;
- AiGOL = Governance Layer;
- LLM = Translation Layer only;
- Worker = Execution Layer;
- Replay = Evidence Layer.

The plan does not implement runtime code.

It defines phases, components, interfaces, replay artifacts, certification requirements, fail-closed behavior, implementation order, dependencies, milestones, and complexity.

## 2. Implementation Roadmap

Implementation phases:

```text
Phase 1: Human -> Governance Translation
Phase 2: Governance -> Human Translation
Phase 3: Adaptive Translation
Phase 4: Replay-derived Learning
```

Ordering principle:

```text
deterministic translation first
-> replay-visible explanation second
-> provider assistance third
-> replay-derived deterministic promotion last
```

## 3. Phase 1: Human -> Governance Translation

### 3.1 Objective

Translate human natural language into a non-authoritative governance intent candidate.

Scope:

- natural language intake;
- intent normalization;
- ambiguity detection;
- clarification generation;
- governance intent generation.

### 3.2 Runtime Components

Required components:

```text
universal_translation_intake_runtime.py
human_to_governance_translation_runtime.py
translation_ambiguity_detection_runtime.py
translation_clarification_runtime.py
governance_intent_candidate_runtime.py
human_to_governance_translation_replay.py
```

### 3.3 Interfaces

Required interface:

```text
translate_human_to_governance(
    translation_request_id,
    human_prompt,
    session_context,
    operator_context,
    available_products,
    available_domains,
    available_workflows,
    created_at,
    replay_dir,
) -> HumanToGovernanceTranslationCapture
```

Required output fields:

```text
translation_direction
original_human_prompt
normalized_prompt
governance_intent_candidate
domain_candidates
product_candidates
workflow_candidates
intent_family
ambiguity_status
clarification_questions
confidence
translation_source
authority_granted=false
replay_reference
```

### 3.4 Replay Artifacts

Phase 1 replay sequence:

```text
000_translation_intake_recorded.json
001_intent_normalization_recorded.json
002_ambiguity_detection_recorded.json
003_governance_intent_candidate_recorded.json
004_translation_handoff_recorded.json
```

Replay must prove:

- original prompt was preserved;
- translation did not approve;
- translation did not select authoritative workflow;
- ambiguity was classified;
- clarification questions were generated when required;
- HIRR/ACLI handoff was evidence-only.

### 3.5 Certification Requirements

Scenarios:

1. Clear development request.
2. Clear security-domain request.
3. Product request.
4. Ambiguous request.
5. Approval-bypass request.
6. Missing context.
7. Unsupported domain.
8. Replay reconstruction.

Required verdict:

```text
HUMAN_TO_GOVERNANCE_TRANSLATION_CERTIFIED
```

### 3.6 Fail-Closed Behavior

Fail closed when:

- prompt is empty;
- prompt contains unsafe approval bypass;
- domain cannot be determined and clarification is impossible;
- normalized intent conflicts with original prompt;
- replay artifact hash fails;
- translation attempts to grant authority.

### 3.7 Implementation Order

1. Define data models.
2. Implement deterministic intake and normalization.
3. Implement ambiguity detection.
4. Implement clarification generation.
5. Implement governance intent candidate generation.
6. Implement replay recording and reconstruction.
7. Add tests.
8. Certify Phase 1.

### 3.8 Acceptance Criteria

- deterministic translation works without providers;
- ambiguous input asks clarification;
- unsafe input fails closed;
- replay reconstructs;
- no authority flags are granted;
- ACLI can consume the candidate as evidence.

### 3.9 Complexity

Estimated complexity:

```text
MEDIUM
```

Reason:

It builds on existing ACLI/HIRR patterns but introduces a new replay-visible translation artifact family.

## 4. Phase 2: Governance -> Human Translation

### 4.1 Objective

Translate authoritative governance state into human-readable explanation.

Scope:

- replay translation;
- approval translation;
- execution translation;
- ERR translation;
- worker result translation.

### 4.2 Runtime Components

Required components:

```text
governance_to_human_translation_runtime.py
approval_state_translation_runtime.py
execution_state_translation_runtime.py
err_state_translation_runtime.py
worker_result_translation_runtime.py
replay_state_translation_runtime.py
governance_to_human_translation_replay.py
```

### 4.3 Interfaces

Required interface:

```text
translate_governance_to_human(
    translation_request_id,
    governance_state,
    workflow_state,
    proposal_state,
    approval_state,
    execution_state,
    validation_state,
    replay_state,
    created_at,
    replay_dir,
) -> GovernanceToHumanTranslationCapture
```

Required output fields:

```text
translation_direction
authoritative_state_reference
human_summary
what_i_understood
what_will_happen
what_will_not_happen
approval_explanation
next_action
replay_visibility
explanation_transparency
confidence
completeness
rendered_operator_view
rendered_operator_view_hash
authority_granted=false
```

### 4.4 Replay Artifacts

Phase 2 replay sequence:

```text
000_authoritative_state_reference_recorded.json
001_governance_state_translation_recorded.json
002_approval_translation_recorded.json
003_execution_translation_recorded.json
004_err_translation_recorded.json
005_worker_result_translation_recorded.json
006_rendered_operator_view_recorded.json
```

Replay must prove:

- rendered explanation came from authoritative state;
- output did not modify governance;
- missing evidence was disclosed;
- worker and ERR output were translated as evidence, not authority;
- rendered operator view hash matches replay.

### 4.5 Certification Requirements

Scenarios:

1. Proposal explanation.
2. Approval explanation.
3. Rejection explanation.
4. Modification explanation.
5. Execution success explanation.
6. Validation failure explanation.
7. ERR unavailable explanation.
8. Worker failure explanation.
9. Replay reconstruction explanation.
10. Missing replay reference.

Required verdict:

```text
GOVERNANCE_TO_HUMAN_TRANSLATION_CERTIFIED
```

### 4.6 Fail-Closed Behavior

Fail closed when:

- authoritative state is missing;
- state hash mismatch occurs;
- rendered output cannot be tied to state;
- translation attempts to authorize execution;
- worker result cannot be verified;
- ERR evidence cannot be reconstructed.

### 4.7 Implementation Order

1. Define governance-state input schema.
2. Implement proposal and approval translation.
3. Implement execution and validation translation.
4. Implement ERR translation.
5. Implement worker result translation.
6. Implement rendered operator view replay.
7. Add tests.
8. Certify Phase 2.

### 4.8 Acceptance Criteria

- governance state is explainable without providers;
- replay, ERR, and worker results are translated plainly;
- missing evidence is visible;
- explanation transparency is present;
- rendered operator view reconstructs.

### 4.9 Complexity

Estimated complexity:

```text
MEDIUM_HIGH
```

Reason:

It touches multiple state families: approval, execution, ERR, worker result, validation, and replay.

## 5. Phase 3: Adaptive Translation

### 5.1 Objective

Add optional provider-assisted translation while preserving deterministic fallback.

Scope:

- provider comparison;
- confidence estimation;
- ambiguity scoring;
- adaptive provider escalation;
- deterministic fallback.

### 5.2 Runtime Components

Required components:

```text
adaptive_translation_policy_runtime.py
translation_provider_request_runtime.py
translation_provider_response_runtime.py
translation_provider_comparison_runtime.py
translation_confidence_synthesis_runtime.py
translation_provider_escalation_runtime.py
adaptive_translation_replay.py
```

### 5.3 Interfaces

Required interface:

```text
run_adaptive_translation(
    translation_request_id,
    deterministic_translation,
    ambiguity_artifact,
    provider_candidates,
    escalation_policy,
    created_at,
    replay_dir,
) -> AdaptiveTranslationCapture
```

Provider request interface:

```text
authoritative_state
bounded_translation_task
preservation_requirements
domain_context
product_context
replay_reference
```

Provider response interface:

```text
provider_id
provider_role=TRANSLATION_PROVIDER
provider_tier
translation_candidate
confidence
limitations
preserved_identifiers
advisory_only=true
authority_granted=false
```

### 5.4 Replay Artifacts

Phase 3 replay sequence:

```text
000_adaptive_policy_recorded.json
001_provider_request_recorded.json
002_provider_response_recorded.json
003_provider_comparison_recorded.json
004_confidence_synthesis_recorded.json
005_escalation_decision_recorded.json
006_deterministic_fallback_recorded.json
```

Replay must prove:

- provider output was advisory;
- provider comparison did not grant authority;
- escalation reason was recorded;
- fallback occurred when provider failed;
- confidence did not alter governance decisions.

### 5.5 Certification Requirements

Scenarios:

1. No provider required.
2. Tier 1 provider succeeds.
3. Tier 1 unavailable -> deterministic fallback.
4. Tier 1 ambiguous -> Tier 2 escalation.
5. Provider disagreement.
6. Malformed provider output.
7. Provider attempts authority.
8. Multi-provider comparison.
9. Confidence synthesis.
10. Replay reconstruction.

Required verdict:

```text
ADAPTIVE_TRANSLATION_CERTIFIED
```

### 5.6 Fail-Closed Behavior

Fail closed or fallback when:

- provider response malformed;
- provider claims authority;
- provider omits preservation fields;
- provider disagreement exceeds threshold;
- confidence is unknown and ambiguity is material;
- ERR cannot resolve required provider and deterministic fallback is unavailable.

### 5.7 Implementation Order

1. Define provider request and response schemas.
2. Implement provider validation.
3. Implement deterministic fallback replay.
4. Implement comparison for two providers.
5. Implement confidence synthesis.
6. Implement adaptive escalation policy.
7. Add replay reconstruction.
8. Certify Phase 3.

### 5.8 Acceptance Criteria

- provider assistance is optional;
- deterministic fallback remains available;
- provider comparison is replay-visible;
- authority boundaries are preserved;
- provider confidence is explanation/translation quality only.

### 5.9 Complexity

Estimated complexity:

```text
HIGH
```

Reason:

Provider comparison, escalation policy, and confidence synthesis introduce more states and failure cases.

## 6. Phase 4: Replay-Derived Learning

### 6.1 Objective

Convert frequently repeated, human-approved translation patterns into deterministic translation rules.

Scope:

- translation replay analysis;
- repeated translation detection;
- candidate deterministic rules;
- human approval workflow;
- deterministic translation promotion.

### 6.2 Runtime Components

Required components:

```text
translation_replay_analysis_runtime.py
translation_pattern_detection_runtime.py
translation_rule_candidate_runtime.py
translation_rule_approval_runtime.py
deterministic_translation_promotion_runtime.py
translation_rule_registry_runtime.py
translation_learning_replay.py
```

### 6.3 Interfaces

Required interface:

```text
analyze_translation_replay(
    analysis_id,
    replay_roots,
    pattern_threshold,
    created_at,
    replay_dir,
) -> TranslationReplayAnalysisCapture
```

Rule candidate interface:

```text
candidate_rule_id
source_replay_references
pattern_summary
proposed_matcher
proposed_output
confidence
risk_classification
requires_human_approval=true
```

Promotion interface:

```text
approved_rule_id
approval_reference
rule_version
deterministic_rule_definition
validation_result
promotion_replay_reference
```

### 6.4 Replay Artifacts

Phase 4 replay sequence:

```text
000_translation_replay_analysis_recorded.json
001_pattern_detection_recorded.json
002_rule_candidate_recorded.json
003_human_review_recorded.json
004_rule_approval_recorded.json
005_deterministic_promotion_recorded.json
006_rule_registry_update_recorded.json
```

Replay must prove:

- source replay references exist;
- candidate rule came from repeated evidence;
- human approval occurred before promotion;
- promoted rule was validated;
- prior replay remains reconstructable.

### 6.5 Certification Requirements

Scenarios:

1. Repeated phrase creates candidate.
2. Insufficient pattern does not create candidate.
3. Candidate rejected by human.
4. Candidate approved and promoted.
5. Promoted rule used in future deterministic translation.
6. Promotion rollback.
7. Prior replay reconstruction after promotion.
8. Provider suggestion does not auto-promote.
9. Conflicting patterns fail closed.
10. Rule versioning.

Required verdict:

```text
REPLAY_DERIVED_TRANSLATION_LEARNING_CERTIFIED
```

### 6.6 Fail-Closed Behavior

Fail closed when:

- source replay references are missing;
- replay hashes mismatch;
- pattern conflicts with existing deterministic rule;
- candidate lacks human approval;
- validation fails;
- rule would grant authority;
- rule would bypass ACLI/HIRR.

### 6.7 Implementation Order

1. Define replay analysis schema.
2. Implement repeated pattern detection.
3. Implement rule candidate generation.
4. Implement human review and approval capture.
5. Implement deterministic rule registry.
6. Implement promotion and rollback.
7. Implement replay reconstruction.
8. Certify Phase 4.

### 6.8 Acceptance Criteria

- no automatic learning;
- human approval required;
- promoted rules are deterministic;
- promoted rules are versioned;
- prior replay remains reconstructable;
- provider suggestions remain evidence until approved.

### 6.9 Complexity

Estimated complexity:

```text
HIGH
```

Reason:

Replay-derived learning requires pattern analysis, approval governance, rule registry, migration safety, and backward compatibility.

## 7. Dependency Graph

```text
Phase 1 Human -> Governance Translation
    -> Phase 2 Governance -> Human Translation
        -> Phase 3 Adaptive Translation
            -> Phase 4 Replay-derived Learning
```

Detailed dependencies:

```text
Data models
-> deterministic translation artifacts
-> replay recording and reconstruction
-> ACLI/HIRR handoff
-> governance-state explanation
-> provider request/response schema
-> provider comparison
-> confidence synthesis
-> replay-derived analysis
-> human-approved deterministic promotion
```

Blocking dependencies:

| Dependent Phase | Blocking Requirement |
| --- | --- |
| Phase 2 | Phase 1 replay artifact conventions and confidence model |
| Phase 3 | Phase 1 and Phase 2 deterministic fallback outputs |
| Phase 4 | Phase 1-3 replay evidence and human approval runtime |

## 8. Milestones

### Milestone UBT-001

```text
Human -> Governance deterministic translation implemented
```

Exit criteria:

- clear request translates;
- ambiguity clarifies;
- unsafe request fails closed;
- replay reconstructs.

### Milestone UBT-002

```text
Governance -> Human deterministic translation implemented
```

Exit criteria:

- proposal, approval, execution, ERR, worker, replay states explainable;
- rendered operator view replayed.

### Milestone UBT-003

```text
Adaptive provider-assisted translation implemented
```

Exit criteria:

- provider success;
- provider failure fallback;
- provider comparison;
- confidence synthesis;
- replay reconstruction.

### Milestone UBT-004

```text
Replay-derived translation learning implemented
```

Exit criteria:

- repeated translation patterns produce candidates;
- human approval required;
- deterministic rule promotion works;
- rollback and replay compatibility verified.

## 9. Estimated Implementation Complexity

| Phase | Complexity | Primary Risk |
| --- | --- | --- |
| Phase 1 | MEDIUM | Confusing evidence-only translation with authoritative routing |
| Phase 2 | MEDIUM_HIGH | Explaining multiple governance states without hiding diagnostics |
| Phase 3 | HIGH | Provider comparison and confidence must remain non-authoritative |
| Phase 4 | HIGH | Replay-derived learning must not become automatic self-modification |

Overall complexity:

```text
HIGH
```

Recommended implementation style:

```text
small deterministic core first
strict replay evidence
provider assistance only after deterministic certification
learning only after approval-governed promotion is certified
```

## 10. Global Acceptance Criteria

The implementation roadmap is complete when:

- Phase 1-4 components are defined;
- every phase has interfaces;
- every phase has replay artifacts;
- every phase has certification requirements;
- every phase has fail-closed behavior;
- implementation order is explicit;
- dependency graph is defined;
- milestones are defined;
- complexity is estimated;
- no phase grants LLM authority;
- no phase bypasses ACLI, HIRR, approval, replay, ERR passivity, or worker contracts.

## 11. Final Verdict

```text
UNIVERSAL_BIDIRECTIONAL_TRANSLATION_RUNTIME_IMPLEMENTATION_READY
```

The Universal Bidirectional Translation Runtime can be implemented incrementally through deterministic Human -> Governance translation, deterministic Governance -> Human translation, optional adaptive provider-assisted translation, and replay-derived deterministic learning governed by human approval.
