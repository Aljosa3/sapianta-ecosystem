# UBTR Consumer Migration Audit V1

Status: audit artifact.

Scope: Platform Core Generation 1 semantic-consumer migration.

Feature Freeze: active.

This audit does not modify runtime behavior, routing, governance, replay, translation logic, providers, workers, or tests.

## 1. Executive Summary

Universal Bidirectional Translation Runtime is the intended canonical semantic translation authority for Platform Core Generation 1.

Repository evidence shows that UBTR is implemented as replay-visible translation infrastructure:

- `aigol/runtime/universal_translation_artifact_schema.py` defines the canonical artifact schema and fail-closed validation.
- `aigol/runtime/human_to_governance_translation_runtime.py` creates Human -> Governance translation artifacts.
- `aigol/runtime/governance_to_human_translation_runtime.py` creates Governance -> Human translation artifacts.
- `aigol/runtime/adaptive_translation_escalation_runtime.py` validates and escalates Universal Translation artifacts.
- `aigol/runtime/replay_derived_translation_learning_runtime.py` consumes translation replay artifacts and emits proposal-only improvement candidates.
- `aigol/runtime/universal_translation_runtime_integration.py` records integration artifacts for Human -> Governance and Governance -> Human paths.

However, UBTR is not yet the single semantic authority used by every Platform Core consumer.

The live ACLI path records Universal Translation evidence before workflow selection, but workflow selection still consumes the original human prompt through local deterministic classifiers. The most direct evidence is in `aigol/runtime/conversational_cli_runtime.py`:

```text
translate_human_to_governance(...)
analysis = _classify_workflow(human_prompt)
```

This means UBTR is canonical by architecture and replay evidence, while local compatibility layers remain active and still influence routing outcomes.

## 2. Audit Method

The audit reviewed repository references to:

- Universal Translation Runtime
- Universal Bidirectional Translation Runtime
- translation artifacts
- Human -> Governance translation
- Governance -> Human translation
- HIRR
- conversational routing
- proposal-only cognition routing
- explanation runtimes
- hardening evidence
- local semantic marker systems

The audit inspected runtime modules, governance artifacts, and test references. No runtime code or tests were changed.

## 3. Canonical Authority Verification

### 3.1 Is UBTR currently the single semantic authority?

Answer: PARTIALLY.

UBTR is the intended canonical semantic authority and produces replay-visible translation artifacts. It is not yet the exclusive source of semantic meaning for all Platform Core consumers.

Evidence:

- `conversational_cli_runtime.route_conversational_cli_intent()` invokes `translate_human_to_governance()` before routing.
- The same function then calls `_classify_workflow(human_prompt)`, which performs workflow selection from the raw operator prompt.
- `_proposal_only_ocs_escalation()` performs local marker-based proposal-only detection using terms such as `proposal only`, `samo pripraviti`, `governance document`, `summarize`, `explain`, `compare`, and `brainstorm`.
- `human_intent_clarification_intake_runtime.py` performs local intent-family classification for HIRR.
- `human_execution_intent_detection.py` performs local marker-based generic governed execution and artifact creation detection.

### 3.2 Can two different Platform Core components independently derive semantic meaning from the same operator prompt?

Answer: YES.

Independent derivation currently occurs in at least:

- UBTR Human -> Governance translation: `human_to_governance_translation_runtime.translate_human_to_governance()`
- ACLI workflow routing: `conversational_cli_runtime._classify_workflow()`
- Proposal-only OCS escalation: `conversational_cli_runtime._proposal_only_ocs_escalation()`
- HIRR intake: `human_intent_clarification_intake_runtime.classify_human_intent_for_clarification()`
- Governed development classification: `human_intent_clarification_intake_runtime.classify_development_intent_for_governed_routing()`
- Generic execution detection: `human_execution_intent_detection.detect_human_execution_intent()`
- Native development routing: `conversation_native_development_intent_routing.py`
- OCS semantic resolution: `ocs_semantic_resolution_runtime.py`
- Provider-assisted semantic suggestion paths: `provider_assisted_intent_classification.py`

### 3.3 Are explanation runtimes semantic authorities?

Answer: NO.

Explanation runtimes are downstream renderers. They may translate authoritative state into human-facing language, and optional LLM-assisted explanation may provide advisory wording, but neither grants authority, changes workflow state, routes requests, approves execution, invokes workers, or mutates replay.

Evidence:

- `acli_llm_assisted_explanation_runtime.py` states that provider-assisted explanations are advisory only and that ACLI runtime state remains the source of truth.
- The LLM-assisted explanation artifact records `advisory_only`, `visibility_only`, `approval_authority: false`, `execution_authority: false`, `worker_authority: false`, and `governance_authority: false`.
- `universal_translation_runtime_integration.create_operator_explanation_through_universal_translation()` builds explanations from Governance -> Human translation artifacts and optional LLM-assisted explanation, but does not alter workflow state.

### 3.4 Are Human-Friendly Explanation Runtime and LLM-Assisted Explanation Runtime downstream renderers only?

Answer: YES.

They consume authoritative state or translated governance state and render operator-facing explanations. They do not own workflow selection or semantic routing.

### 3.5 Are ACLI/HIRR marker systems now compatibility layers only?

Answer: PARTIALLY.

Architecturally, ACLI/HIRR marker systems should become compatibility layers as UBTR adoption proceeds. Operationally, they still participate directly in routing and clarification decisions. They are therefore active compatibility layers, not passive legacy shims.

## 4. Current Consumer Inventory

| Consumer | UBTR Consumption | Local Interpretation | Compatibility Layer | Migration Status | Risk |
| --- | --- | --- | --- | --- | --- |
| Universal Translation Artifact Schema | Direct canonical schema | None | No | FULLY_MIGRATED | Low |
| Human -> Governance Translation Runtime | Produces UBTR artifacts | Deterministic translation rules inside UBTR | No | FULLY_MIGRATED | Low |
| Governance -> Human Translation Runtime | Produces UBTR artifacts | Deterministic rendering rules inside UBTR | No | FULLY_MIGRATED | Low |
| Adaptive Translation Escalation Runtime | Validates and compares UBTR artifacts | Escalation policy only | No | FULLY_MIGRATED | Low |
| Replay-Derived Translation Learning Runtime | Consumes UBTR replay artifacts | Pattern analysis only, proposal-only | No | FULLY_MIGRATED | Low |
| Universal Translation Runtime Integration | Records translation evidence around routing and explanation | Delegates routing to existing ACLI path | Yes | PARTIALLY_MIGRATED | Medium |
| ACLI CLI Entrypoint | Indirect through conversational runtime | Lifecycle and approval command handling | Yes | PARTIALLY_MIGRATED | Medium |
| Conversational CLI Runtime | Records Human -> Governance translation before routing | `_classify_workflow()` and proposal-only markers | Yes | PARTIALLY_MIGRATED | High |
| HIRR Intake Runtime | None direct | Intent-family marker classifiers | Yes | NOT_MIGRATED | High |
| HIRR Continuity Runtime | None direct | Clarification refinement and proposal-only escalation signals | Yes | NOT_MIGRATED | High |
| Human Execution Intent Detection | None direct | Creation, execution, governance-artifact markers | Yes | NOT_MIGRATED | Medium |
| Native Development Intent Routing | None direct | Local native-development intent markers | Yes | NOT_MIGRATED | Medium |
| Platform Core Routing | Usually consumes structured workflow artifacts | No general natural-language translation | N/A | FULLY_MIGRATED | Low |
| PPP Runtime | Consumes structured context, OCS, and replay artifacts | Handoff/resource validation, not general NL semantics | Partial | PARTIALLY_MIGRATED | Medium |
| Approval Runtime | Consumes proposal and approval command state | Approval command parsing | Compatibility | LEGACY_COMPATIBILITY | Low |
| Resume/Lifecycle Runtime | Consumes replay-restored workflow state | Lifecycle command parsing | Compatibility | LEGACY_COMPATIBILITY | Low |
| Replay Runtime | Stores and reconstructs artifacts | No authority or interpretation | N/A | FULLY_MIGRATED | Low |
| Hardening Runtime | Detects UBTR evidence in captured interactions | Local component/scenario token detection | Yes | PARTIALLY_MIGRATED | Medium |
| Deterministic Explanation Runtime | May consume translated/authoritative state | Human rendering rules only | Yes | PARTIALLY_MIGRATED | Low |
| LLM-Assisted Explanation Runtime | Consumes authoritative state and deterministic explanation | Provider wording only | Yes | FULLY_MIGRATED | Low |
| OCS Semantic Resolution Runtime | None direct in core semantic resolution | OCS semantic artifact construction | Separate semantic subsystem | PARTIALLY_MIGRATED | Medium |
| Provider-Assisted Intent Classification | None direct | Provider-assisted semantic suggestion path | Separate semantic subsystem | PARTIALLY_MIGRATED | Medium |
| Legacy intent classifiers | None direct | Direct deterministic classification | Yes | LEGACY_COMPATIBILITY | Medium |

## 5. Migration Matrix

### FULLY_MIGRATED

These consumers either are UBTR components or do not independently derive semantic meaning from natural language:

- Universal Translation Artifact Schema
- Human -> Governance Translation Runtime
- Governance -> Human Translation Runtime
- Adaptive Translation Escalation Runtime
- Replay-Derived Translation Learning Runtime
- Replay persistence and reconstruction for translation artifacts
- LLM-Assisted Explanation Runtime, for its renderer-only role

### PARTIALLY_MIGRATED

These consumers record or consume UBTR evidence but retain local semantic behavior:

- Universal Translation Runtime Integration
- ACLI CLI Entrypoint
- Conversational CLI Runtime
- PPP integration paths
- Hardening Runtime
- Deterministic Explanation Runtime
- OCS Semantic Resolution Runtime
- Provider-Assisted Intent Classification

### NOT_MIGRATED

These consumers still derive natural-language meaning without consuming UBTR artifacts as canonical input:

- HIRR Intake Runtime
- HIRR Continuity Runtime
- Human Execution Intent Detection
- Native Development Intent Routing
- direct conversational workflow marker checks

### LEGACY_COMPATIBILITY

These consumers are valid compatibility surfaces, but should not be treated as final canonical semantic ownership:

- approval command parsing
- lifecycle command parsing
- old deterministic intent classifiers
- raw prompt fallback routing
- marker-based proposal-only escalation

## 6. Compatibility Layer Inventory

Current compatibility layers include:

1. `conversational_cli_runtime.route_conversational_cli_intent()`

   Creates UBTR evidence, then preserves HIRR-compatible routing by calling `_classify_workflow(human_prompt)`.

2. `universal_translation_runtime_integration.route_human_request_through_universal_translation()`

   Records `migration_mode: CANONICAL_TRANSLATION_BEFORE_HIRR_COMPATIBILITY` and `compatibility_layer_active: True`.

3. `human_intent_clarification_intake_runtime.py`

   Classifies intent families through local deterministic marker functions and returns HIRR-compatible clarification artifacts.

4. `human_intent_clarification_continuity_runtime.py`

   Refines clarification state and proposal-only cognition routing through local continuity logic.

5. `human_execution_intent_detection.py`

   Detects generic governed artifact creation, governed domain creation, and generic governed execution through local marker terms.

6. `_proposal_only_ocs_escalation()`

   Routes proposal-only cognition using ACLI-local marker families rather than a canonical translated intent payload.

7. Hardening scenario detection

   Detects exercised components and scenario coverage using local token scanning of interaction evidence.

These layers preserve compatibility and certification continuity, but they mean UBTR is not yet the only semantic decision source.

## 7. Semantic Interpretation Points

The current implementation has these semantic interpretation points:

| Interpretation Point | Source Input | UBTR Artifact Used As Decision Source | Notes |
| --- | --- | --- | --- |
| Human -> Governance translation | Human prompt | Yes | Canonical translation artifact created |
| Conversational workflow selection | Human prompt | No | Uses local `_classify_workflow()` |
| Proposal-only OCS escalation | Human prompt | No | Uses local semantic markers |
| HIRR intake | Human prompt | No | Uses local intent-family classifiers |
| HIRR continuity | Clarification response | No | Uses local refinement rules |
| Generic execution detection | Human prompt | No | Uses local execution/artifact markers |
| Native development detection | Human prompt | No | Uses local development markers |
| OCS semantic resolution | OCS source artifacts | No direct UBTR dependency | Separate cognition semantic layer |
| PPP handoff | Context and OCS artifacts | No direct UBTR dependency | Mostly structured handoff validation |
| Governance -> Human explanation | Governance state | Yes when using UBTR integration | Renderer role |
| LLM-assisted explanation | Authoritative state | Indirect | Advisory renderer only |
| Hardening scenario classification | Interaction evidence | Indirect | Local derived evidence classification |

## 8. Proposal-Only Implications

Proposal-only cognition routing is the clearest active drift from single-authority UBTR adoption.

The current route:

```text
Human prompt
-> translate_human_to_governance(...)
-> _classify_workflow(human_prompt)
-> _proposal_only_ocs_escalation(normalized prompt)
-> OCS_LLM_COGNITION
```

The intended canonical route after full migration would be:

```text
Human prompt
-> UBTR Human -> Governance artifact
-> canonical translated governance payload
-> workflow selection / OCS escalation policy
-> OCS_LLM_COGNITION when policy allows
```

The current implementation is execution-safe and replay-visible, but the proposal-only classification still depends on ACLI-local semantic markers.

## 9. Certification Impact

The audit does not identify a governance defect.

The audit does not identify a replay defect.

The audit does not identify an approval-boundary defect.

The audit does not identify provider-authority or worker-authority violations.

The certification impact is narrower:

- Platform Core can truthfully claim UBTR is the canonical semantic translation architecture.
- Platform Core cannot yet claim UBTR is the sole runtime semantic decision source for every consumer.
- Compatibility layers are still necessary for certified ACLI/HIRR behavior.
- Future certification language should say "UBTR canonical with active compatibility layers" until local semantic routing consumers are migrated.

## 10. Remaining Migration Work

No repair is implemented by this audit.

Recommended future migration work, without architectural redesign:

1. Compare UBTR translated governance payloads against existing ACLI routing outputs in replay-only audit mode.

2. Migrate `_classify_workflow()` to consume a canonical translated intent candidate after deterministic equivalence is proven.

3. Migrate proposal-only OCS escalation from local markers to translated governance payload fields.

4. Migrate HIRR intake to consume UBTR ambiguity and normalized-intent fields while preserving current clarification behavior.

5. Keep lifecycle and approval command parsing outside UBTR unless commands carry natural-language semantic ambiguity.

6. Preserve deterministic fallback for all migrated consumers.

7. Retire local marker systems only after regression coverage proves equivalent or improved deterministic behavior.

## 11. Regression Coverage Needed After Migration

Future migration should include regression coverage for:

- raw prompt and translated payload agreement
- governance artifact creation routing
- proposal-only OCS routing
- multilingual proposal-only prompts
- HIRR ambiguity detection
- clarification promotion to workflow routing
- approval command precedence
- lifecycle continuation command precedence
- replay reconstruction of translation evidence
- fail-closed malformed translation artifact handling
- no worker invocation from translation or explanation artifacts

## 12. Answers To Required Audit Questions

1. Is UBTR currently the single semantic authority?

   PARTIALLY. It is canonical by architecture and evidence, but not exclusive in live consumers.

2. Can two different Platform Core components independently derive semantic meaning from the same operator prompt?

   YES. UBTR, ACLI routing, HIRR, execution-intent detection, native development routing, and provider-assisted classification can each derive meaning.

3. Are explanation runtimes semantic authorities?

   NO. They render authoritative state and optional advisory provider wording.

4. Are Human-Friendly Explanation Runtime and LLM-Assisted Explanation Runtime downstream renderers only?

   YES. They do not route, approve, execute, or mutate governance state.

5. Are ACLI/HIRR marker systems now compatibility layers only?

   Architecturally YES. Operationally PARTIALLY: they still decide routing and clarification in live paths.

## 13. Certification Statement

UBTR adoption is sufficient to establish canonical translation evidence and replay-visible translation lineage.

UBTR adoption is not yet complete enough to remove local semantic compatibility systems from ACLI, HIRR, OCS proposal-only routing, or hardening scenario classification.

Platform Core Generation 1 should preserve the current compatibility layers during Feature Freeze. Any migration should be staged as evidence-preserving hardening, not new architecture.

## Final Verdict

UBTR_CANONICAL_WITH_COMPATIBILITY_LAYERS
