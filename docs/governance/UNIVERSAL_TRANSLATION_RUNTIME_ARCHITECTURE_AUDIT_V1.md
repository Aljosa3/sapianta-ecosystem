# UNIVERSAL_TRANSLATION_RUNTIME_ARCHITECTURE_AUDIT_V1

## 1. Audit Purpose

This artifact audits the Universal Translation Runtime concept across AiGOL Platform Core.

This is an architecture audit only.

No runtime behavior, routing, governance, replay, provider logic, worker logic, or tests were modified.

## 2. Audit Question

Recent ACLI diagnostics showed that proposal-only OCS escalation depends on ACLI-local deterministic semantic markers such as:

- `governance_document_marker`
- `proposal_action_marker`
- `explicit_governance_artifact_with_no_execution`

The audit question is whether this matches the intended Universal Translation Runtime architecture, where human natural language should first become canonical governance intent before HIRR, OCS, PPP, workers, replay, and governance consumers act on it.

## 3. Repository Evidence

### 3.1 Universal Translation Specifications

Repository evidence confirms that Universal Translation Runtime architecture is specified:

- `docs/governance/UNIVERSAL_BIDIRECTIONAL_TRANSLATION_RUNTIME_V1.md`
- `docs/governance/UNIVERSAL_BIDIRECTIONAL_TRANSLATION_RUNTIME_IMPLEMENTATION_PLAN_V1.md`
- `docs/governance/UNIVERSAL_TRANSLATION_ARTIFACT_SCHEMA_V1.md`
- `docs/governance/HUMAN_TO_GOVERNANCE_TRANSLATION_RUNTIME_V1.md`
- `docs/governance/GOVERNANCE_TO_HUMAN_TRANSLATION_RUNTIME_V1.md`
- `docs/governance/ADAPTIVE_TRANSLATION_ESCALATION_RUNTIME_V1.md`
- `docs/governance/REPLAY_DERIVED_TRANSLATION_LEARNING_RUNTIME_V1.md`
- `docs/governance/UNIVERSAL_TRANSLATION_RUNTIME_INTEGRATION_V1.md`

The conceptual architecture states:

```text
Human
-> Universal Bidirectional Translation Runtime
-> Universal ACLI / HIRR / Governance
```

and:

```text
Governance State
-> Universal Bidirectional Translation Runtime
-> Human
```

The translation runtime is explicitly non-authoritative. It may translate, identify ambiguity, request clarification, compare provider translations, and record evidence. It may not select authoritative workflow, approve execution, authorize workers, mutate proposals, mutate replay, override HIRR, or bypass ACLI.

### 3.2 Runtime Implementation Evidence

Repository evidence confirms that runtime modules exist:

- `aigol/runtime/universal_translation_artifact_schema.py`
- `aigol/runtime/human_to_governance_translation_runtime.py`
- `aigol/runtime/governance_to_human_translation_runtime.py`
- `aigol/runtime/adaptive_translation_escalation_runtime.py`
- `aigol/runtime/replay_derived_translation_learning_runtime.py`
- `aigol/runtime/universal_translation_runtime_integration.py`

Regression evidence exists:

- `tests/test_universal_translation_artifact_schema_v1.py`
- `tests/test_human_to_governance_translation_runtime_v1.py`
- `tests/test_governance_to_human_translation_runtime_v1.py`
- `tests/test_adaptive_translation_escalation_runtime_v1.py`
- `tests/test_replay_derived_translation_learning_runtime_v1.py`
- `tests/test_universal_translation_runtime_integration_v1.py`

### 3.3 Operational ACLI Integration Evidence

`aigol/runtime/conversational_cli_runtime.py` imports and invokes:

```text
translate_human_to_governance(...)
```

inside:

```text
route_conversational_cli_intent(...)
```

before calling:

```text
_classify_workflow(human_prompt)
```

The routing decision artifact records:

- `universal_translation_reference`
- `universal_translation_hash`
- `universal_translation_direction`
- `universal_translation_confidence`

This proves Universal Translation is replay-visible in the operational ACLI routing path.

### 3.4 Compatibility Layer Evidence

`docs/governance/UNIVERSAL_TRANSLATION_RUNTIME_INTEGRATION_V1.md` explicitly describes the current mode:

```text
human_prompt
-> translate_human_to_governance
-> _classify_workflow
-> workflow selection
```

It also states:

```text
The routing result remains deterministic and preserves the existing workflow selection logic.
```

This is the key architectural distinction. Universal Translation evidence exists before routing, but workflow selection still depends on the existing local classifier.

## 4. Search Findings

The repository contains many references to:

- Universal Translation Runtime
- Translation Runtime
- Human -> Governance translation
- Governance -> Human translation
- Semantic Contract
- Intent Translation
- Natural Language intent classification

No repository references were found for:

- `GIR`
- `ExecutionIntentPackage`

Semantic Contract references exist primarily in the MOC / browser companion path:

- `schemas/semantic_contract.schema.json`
- `aigol/moc/contract_validation.py`
- `aigol/moc/advisory_contract_generation.py`
- `docs/governance/cognition/MOC_V1_SPEC.md`
- `browser_companion/sidepanel.html`
- `browser_companion/sidepanel.js`

These are adjacent semantic-contract systems, not the same runtime as Universal Translation Runtime.

## 5. Architecture Timeline

### Phase A: Early Semantic Contract / MOC Layer

The repository contains an older or parallel semantic-contract model:

```text
Human Intent
-> Intent Normalization
-> Governance Retrieval
-> Semantic Contract
-> Advisory Proposal
-> Human Approval
-> Worker Task
-> Governed Return
```

This model is implemented through MOC and browser companion artifacts. It is advisory and bounded, but it is not the canonical ACLI Universal Translation Runtime.

### Phase B: ACLI / HIRR Deterministic Routing

ACLI and HIRR evolved deterministic marker-based classifiers for:

- workflow selection;
- clarification intake;
- governed development detection;
- governance artifact creation;
- OCS cognition routing;
- provider onboarding;
- lifecycle commands;
- domain and worker routing.

This produced working deterministic behavior but distributed semantic interpretation across many components.

### Phase C: Universal Bidirectional Translation Runtime

The Universal Translation architecture was later specified as a cross-platform translation layer:

```text
Human Natural Language
-> Governance Intent
```

and:

```text
Governance State
-> Human Natural Language
```

### Phase D: Additive Implementation

Runtime schema, deterministic translation, adaptive escalation, replay-derived learning, and integration wrappers were implemented.

The operational ACLI path now records Universal Translation evidence before routing.

### Phase E: Compatibility Layer, Not Full Consumer Migration

The current operational path still uses `_classify_workflow(human_prompt)` for workflow selection. Translation output is recorded and hash-bound, but it is not the authoritative input consumed by most workflow-selection conditions.

This is an incomplete migration, not absence of implementation.

## 6. Implemented vs Specified Comparison

| Capability | Specified | Implemented | Operationally Canonical |
| --- | --- | --- | --- |
| Universal translation artifact schema | Yes | Yes | Yes for translation artifacts |
| Human -> Governance translation | Yes | Yes | Evidence layer only for ACLI routing |
| Governance -> Human translation | Yes | Yes | Available through integration runtime |
| Translation authority flags | Yes | Yes | Yes |
| Replay-visible translation artifacts | Yes | Yes | Yes |
| Translation before ACLI routing | Yes | Yes | Yes as evidence |
| Workflow selection consumes canonical translated intent | Implied as migration target | No | No |
| Downstream semantic consumers use one shared translation layer | Yes as target | Partial | No |
| Adaptive provider translation escalation | Yes | Implemented as separate runtime | Not generally invoked in live ACLI routing |
| Replay-derived learning | Yes | Implemented as proposal-only runtime | Not automatic behavior mutation |
| Direct local marker systems deprecated | Yes as future phase | Not completed | Still active |

## 7. Actual Implementation Path

The current Human -> ACLI path is:

```text
Human Prompt
-> aigol_cli.py
-> route_conversational_cli_intent(...)
-> translate_human_to_governance(...)
-> record Universal Translation replay reference/hash
-> _classify_workflow(human_prompt)
-> local deterministic marker checks
-> HIRR / clarification / workflow selection
-> selected workflow
-> OCS or PPP or Worker path when selected
-> Replay
```

The current proposal-only OCS path is:

```text
Human Prompt
-> route_conversational_cli_intent(...)
-> translate_human_to_governance(...) recorded
-> _proposal_only_ocs_escalation(normalized)
-> OCS_LLM_COGNITION if local markers match
-> OCS provider path
-> proposal-only preservation
-> no PPP unless explicit execution required
-> no worker
-> Replay
```

The intended architecture target is closer to:

```text
Human Prompt
-> Universal Translation Runtime
-> canonical governance-intent candidate
-> HIRR consumes translated intent
-> workflow resolution
-> OCS / PPP / Worker according to governance state
-> Replay
```

## 8. Semantic Interpretation Inventory

### 8.1 Universal Translation Runtime

Files:

- `aigol/runtime/human_to_governance_translation_runtime.py`
- `aigol/runtime/governance_to_human_translation_runtime.py`
- `aigol/runtime/adaptive_translation_escalation_runtime.py`
- `aigol/runtime/replay_derived_translation_learning_runtime.py`

Uses shared translation layer:

```text
Yes
```

Role:

- creates canonical translation artifacts;
- records normalized intent;
- records translated governance payload;
- preserves authority-denial flags;
- records replay evidence.

Limitation:

- Human -> Governance translation currently has a limited deterministic vocabulary;
- its output is recorded but not consumed as the primary workflow-selection input by ACLI.

### 8.2 ACLI Conversational Routing

File:

- `aigol/runtime/conversational_cli_runtime.py`

Uses shared translation layer:

```text
Partially
```

Evidence:

- calls `translate_human_to_governance`;
- records translation reference and hash;
- then calls `_classify_workflow(human_prompt)`.

Local interpretation examples:

- `_proposal_only_ocs_escalation`
- `_is_ocs_llm_cognition_prompt`
- `_is_plain_ocs_intake_prompt`
- `_is_plain_domain_proposal_prompt`
- `_is_governance_artifact_creation_prompt`
- `_is_governed_development_workflow_prompt`
- `_is_native_development_context_prompt`
- `_is_operator_decision_support_prompt`
- many Product 1, domain, provider, lifecycle, replay, and worker prompt checks.

Conclusion:

ACLI is the largest duplicated semantic interpretation point.

### 8.3 HIRR / Human Intent Clarification

Files:

- `aigol/runtime/human_intent_clarification_intake_runtime.py`
- `aigol/runtime/human_intent_clarification_continuity_runtime.py`

Uses shared translation layer:

```text
No direct dependency observed
```

Local interpretation examples:

- `_business_goal_intent`
- `_general_improvement_intent`
- `_continuation_intent`
- `_bounded_file_write_proof_intent`
- `_problem_statement_intent`
- `_automation_intent`
- `_compliance_intent`
- `_development_intent`
- `_expected_workflow_targets`

Conclusion:

HIRR maintains its own intent families and deterministic signal vocabulary.

### 8.4 Human Execution Intent Detection

File:

- `aigol/runtime/human_execution_intent_detection.py`

Uses shared translation layer:

```text
No
```

Local interpretation examples:

- `_CREATION_TERMS`
- `_EXECUTION_TERMS`
- `_GOVERNANCE_ARTIFACT_TERMS`
- `_ARTIFACT_KIND_TERMS`
- `_is_generic_governed_domain_creation`
- `_is_generic_governed_artifact_creation`
- `_is_generic_governed_execution_request`

Conclusion:

Execution-intent detection duplicates action/domain vocabulary outside Universal Translation.

### 8.5 OCS Cognition

Files:

- `aigol/runtime/ocs_llm_cognition_end_to_end_runtime.py`
- `aigol/runtime/ocs_semantic_resolution_runtime.py`
- `aigol/runtime/ocs_clarification_runtime.py`
- `aigol/runtime/improvement_intent_cognition_routing_runtime.py`

Uses shared translation layer:

```text
Mostly no
```

OCS has its own semantic resolution and clarification artifacts. Improvement-intent cognition routing consumes replay-derived intent artifacts, not Universal Translation artifacts.

Conclusion:

OCS has semantic interpretation and clarification concepts adjacent to, but not unified with, Universal Translation.

### 8.6 PPP / Resource Routing

Files:

- `aigol/runtime/conversation_ppp_routing_integration.py`
- `aigol/runtime/conversation_ppp_resource_selection_routing.py`
- `aigol/runtime/clarified_intent_resource_selection_routing_runtime.py`
- `aigol/runtime/replay_derived_intent_resource_selection_routing_runtime.py`
- `aigol/runtime/ocs_to_ppp_binding_runtime.py`

Uses shared translation layer:

```text
No direct canonical dependency observed
```

PPP receives bounded context, clarified intent, OCS output, or replay-derived intent artifacts. It validates handoff structure and resource routing, but does not consume Universal Translation artifacts as canonical semantic input.

### 8.7 Worker Routing and Worker Invocation

Files:

- `aigol/runtime/worker_invocation_request_runtime.py`
- `aigol/runtime/worker_assignment_runtime.py`
- `aigol/runtime/worker_dispatch_runtime.py`
- `aigol/runtime/worker_invocation_runtime.py`
- `aigol/runtime/domain_and_worker_resolution_registry.py`

Uses shared translation layer:

```text
No
```

Worker path correctly remains downstream of governance and approval. It should not use translation as authority. However, worker selection inputs are not standardized around Universal Translation artifacts.

### 8.8 Replay

Files:

- `aigol/runtime/transport/replay.py`
- `aigol/runtime/*replay*`
- `aigol/runtime/conversational_cli_runtime.py`
- `aigol/runtime/universal_translation_runtime_integration.py`

Uses shared translation layer:

```text
As evidence, yes
```

Replay stores translation artifacts and references when produced. Replay does not make semantic decisions, which is correct.

### 8.9 Prompt Interpretation / Legacy Intent Classifiers

Files:

- `aigol/runtime/intent_classifier.py`
- `sapianta_bridge/nl_envelope/intent_classifier.py`
- `aigol/moc/*`
- `agol_bridge/semantic_contract.py`

Uses shared translation layer:

```text
No
```

These components maintain separate deterministic intent/semantic-contract vocabularies.

## 9. Duplicated Interpretation Points

Duplicated interpretation exists in at least these categories:

| Interpretation Category | Current Owners |
| --- | --- |
| Human action detection | UTR, ACLI, HIRR, human execution intent detection, bridge intent classifiers |
| Governance artifact/document detection | UTR, ACLI, human execution intent detection, semantic contract systems |
| Proposal-only detection | ACLI proposal-only OCS helper, OCS proposal-only lifecycle gates |
| Clarification need | UTR ambiguity flags, HIRR clarification intake, OCS clarification |
| Domain detection | UTR, ACLI, HIRR, domain routing, bridge classifiers |
| Execution/no-execution detection | UTR governance payload, ACLI explicit execution check, human execution intent detection, worker request gates |
| Provider relevance | UTR payload says provider relevance, ACLI/OCS routing makes actual provider decisions |
| Human-readable explanation | Governance-to-human UTR, ACLI human-friendly explanation runtime, LLM-assisted explanation runtime |

## 10. Canonical Translation Ownership

Canonical ownership is currently split:

1. Universal Translation Runtime owns translation artifacts and replay evidence.
2. ACLI owns live workflow selection.
3. HIRR owns clarification intent families.
4. OCS owns cognition semantics and provider comparison.
5. PPP owns proposal/resource handoff semantics.
6. Workers own execution-bound input validation.
7. Replay owns source-of-truth evidence.

The architecture wants UTR to own translation. The implementation currently makes UTR a mandatory evidence precursor in ACLI routing, but not the sole semantic input to workflow selection.

## 11. Proposal-Only Implications

Proposal-only cognition routing currently consumes ACLI-local semantic markers:

```text
_proposal_only_ocs_escalation(normalized)
```

It does not consume:

```text
translation_artifact["normalized_intent"]
translation_artifact["translated_governance_payload"]
translation_artifact["ambiguity_flags"]
```

Therefore, proposal-only routing is not yet using canonical translated intent as its primary semantic source.

This explains the observed issue:

```text
Rad bi ustvaril kratek governance artefakt, ki povzame današnji namen testiranja ACLI v realni uporabi.
```

The prompt contains a human-recognizable proposal-only summary request, but the ACLI-local marker list does not recognize the exact Slovenian morphology. A mature UTR-owned path would ideally normalize:

```text
ustvaril kratek governance artefakt
povzame
```

into a canonical governance intent such as:

```text
proposal_only: true
action: SUMMARIZE_OR_DRAFT
domain: GOVERNANCE
execution_requested: false
provider_relevance: POSSIBLE
```

and ACLI would route from that structured candidate rather than re-evaluating raw words.

## 12. Architectural Classification

The current state is not:

```text
UNIVERSAL_TRANSLATION_RUNTIME_NOT_IMPLEMENTED
```

because UTR schemas, runtimes, replay reconstruction, adaptive escalation, replay-derived learning, integration wrappers, and regression tests exist.

The current state is not fully:

```text
UNIVERSAL_TRANSLATION_RUNTIME_CANONICAL
```

because operational workflow selection still uses ACLI/HIRR local semantic markers as the decisive path.

The most precise classification is:

```text
UNIVERSAL_TRANSLATION_RUNTIME_PARTIALLY_IMPLEMENTED
```

with architectural drift in semantic ownership caused by incomplete migration.

## 13. Where Drift Began

The drift appears to begin at the compatibility-layer milestone:

```text
human_prompt
-> translate_human_to_governance
-> _classify_workflow
-> workflow selection
```

The integration intentionally preserved existing routing behavior while adding translation evidence. This was a safe migration choice under feature-freeze and certification pressure, but it left semantic ownership split.

The drift is therefore not a governance defect. It is an incomplete migration from additive evidence integration to canonical consumer migration.

## 14. What Remains Canonical

The following remain canonical:

- translation artifact schema;
- authority-denial flags;
- replay-visible translation artifacts;
- Human -> Governance translation evidence;
- Governance -> Human translation evidence;
- translation non-authority;
- provider non-authority;
- human authority;
- replay as source of truth;
- fail-closed validation of malformed translation artifacts.

## 15. What Became Duplicated

The following became duplicated:

- action vocabulary;
- domain vocabulary;
- proposal-only vocabulary;
- explanation vocabulary;
- ambiguity/clarification vocabulary;
- execution/no-execution vocabulary;
- provider relevance vocabulary;
- workflow target mapping.

## 16. Migration Complexity

Migration complexity is moderate to high.

Reasons:

- ACLI routing has many certified local branches with regression coverage.
- HIRR clarification behavior is independently certified.
- OCS cognition has its own semantic resolution and clarification artifacts.
- PPP and worker lifecycles depend on existing replay-visible handoff structures.
- Translation is non-authoritative by design, so migration must avoid making UTR an authority layer.

The safe migration path would be incremental:

1. Preserve existing local classifiers.
2. Add comparison evidence between translated intent and local routing decision.
3. Add diagnostics for disagreement.
4. Add tests proving no authority transfer.
5. Gradually migrate selected branches to consume canonical translated fields.
6. Keep local markers as deterministic fallback until certification proves parity.

## 17. Migration Risk

Risks:

- routing regressions if translated intent vocabulary is narrower than current ACLI markers;
- over-routing to OCS if translation provider relevance is treated as authority;
- approval boundary confusion if `execution_requested` in translation payload is misread as authorization;
- replay drift if old and new routing evidence are not linked;
- certification drift if documents continue to state "fully integrated" while runtime remains compatibility-layer based.

## 18. Recommendations

This audit does not recommend immediate implementation changes.

Recommended architectural follow-up work:

1. Create a UTR consumer migration plan that distinguishes evidence integration from decision consumption.
2. Define canonical fields needed by ACLI routing:
   - normalized action;
   - normalized domain;
   - proposal-only classification;
   - execution-requested classification;
   - provider relevance;
   - ambiguity status;
   - multilingual normalized terms.
3. Add audit-only comparison between `_classify_workflow(human_prompt)` and `translated_governance_payload`.
4. Add replay evidence for translation/routing agreement and disagreement.
5. Keep ACLI-local markers as deterministic fallback during migration.
6. Update certification/readiness documents to distinguish:
   - UTR evidence integration;
   - UTR canonical decision consumption.
7. Treat proposal-only OCS routing as a temporary implementation branch until it consumes canonical translated intent.

## 19. Non-Goals

This audit does not:

- redesign UTR;
- redesign HIRR;
- redesign ACLI routing;
- change OCS escalation;
- change PPP handoff;
- change worker authorization;
- change replay semantics;
- change provider behavior;
- modify runtime code;
- modify tests.

## 20. Final Verdict

UNIVERSAL_TRANSLATION_RUNTIME_PARTIALLY_IMPLEMENTED
