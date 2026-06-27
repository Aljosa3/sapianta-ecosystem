# UBTR Implementation Phase 6 Compatibility Layer Retirement Audit V1

## Status

Audit complete.

Final verdict:

UBTR_REQUIRES_ADDITIONAL_MIGRATION

## Objective

Determine which Generation 1 compatibility layers can now be safely retired after Generation 2 implemented:

- Human input through UBTR;
- Human output through UBTR;
- semantic cognition orchestration;
- OCS cognition handoff;
- OCS cognition result integration into the Canonical Semantic Artifact.

This audit does not implement removals, change runtime behavior, change tests, redesign routing, or alter governance.

## Executive Summary

UBTR is now present in the live ACLI semantic path and records replay-visible lineage from human input through Canonical Semantic Artifact generation, semantic cognition orchestration, OCS cognition handoff, and cognition result integration.

However, compatibility layers remain materially required for Platform Core behavior.

The largest remaining dependency is the broad ACLI workflow routing fallback in:

`aigol/runtime/conversational_cli_runtime.py`

UBTR currently handles the canonical governance-artifact happy path and cognition lineage, but many certified workflows still depend on local marker functions, direct HIRR classifiers, lifecycle command grammars, proposal-only OCS marker rules, Product 1 routing markers, domain lifecycle markers, provider onboarding markers, native development markers, and legacy explanation sections.

Retiring compatibility layers now would reduce routing coverage and risk breaking certified Generation 1 operator scenarios.

## Current UBTR Coverage

Implemented UBTR coverage:

| Area | Current state | Evidence |
| --- | --- | --- |
| Human input | Implemented before conversational routing | `route_conversational_cli_intent()` calls `translate_human_to_governance()` and `create_canonical_semantic_artifact_from_translation()` |
| Canonical semantic artifact | Implemented | `aigol/runtime/canonical_semantic_artifact_runtime.py` |
| UBTR-first routing | Partial | `_classify_workflow_from_canonical_semantic_artifact()` routes only decisive governed development governance-artifact semantics |
| Semantic cognition decision | Implemented | `aigol/runtime/ubtr_semantic_cognition_orchestration_runtime.py` |
| OCS cognition handoff | Implemented | `aigol/runtime/ubtr_ocs_cognition_handoff_runtime.py` |
| OCS result integration | Implemented | `aigol/runtime/ubtr_cognition_result_integration_runtime.py` |
| Human output through UBTR | Implemented with compatibility rendering retained | `aigol/runtime/acli_human_friendly_explanation_runtime.py` |

## Compatibility Layer Inventory

### 1. ACLI Compatibility Routing

Primary file:

`aigol/runtime/conversational_cli_runtime.py`

Current compatibility behavior:

- UBTR is invoked first.
- `_classify_workflow_from_canonical_semantic_artifact()` may route when the Canonical Semantic Artifact is decisive.
- If not decisive, `_classify_workflow()` still executes the Generation 1 local marker matrix.

Local compatibility paths include:

- provider onboarding markers;
- freeform clarification markers;
- domain creation markers;
- proposal-only OCS escalation markers;
- proposal runtime markers;
- governance artifact creation markers;
- governed repository mutation markers;
- governed development workflow markers;
- native development context markers;
- Product 1 domain/capability markers;
- domain lifecycle markers;
- capability lifecycle markers;
- implementation-plan-to-execution markers;
- task-completion markers;
- OCS cognition markers;
- replay/status/dashboard markers;
- generic human execution-intent markers.

Classification:

PARTIALLY_REQUIRED

Retirement status:

Blocked by remaining workflow coverage dependencies.

Reason:

The UBTR-first route currently recognizes only a narrow governed-development governance-artifact path. Removing `_classify_workflow()` would break many registered ACLI workflows that are not yet fully represented as Canonical Semantic Artifact routing decisions.

Safe retirement candidates inside this layer:

- duplicate repeated calls to `_is_improvement_proposal_runtime_prompt()`;
- duplicate repeated calls to `_is_proposal_runtime_prompt()`;
- duplicate repeated calls to `_is_task_completion_native_development_prompt()`;
- late fallback route from `GENERIC_GOVERNED_ARTIFACT_CREATION` to `GOVERNANCE_ARTIFACT_CREATION`, once regression proves standard operator governance-artifact prompts always normalize to `GOVERNED_DEVELOPMENT_WORKFLOW`.

Do not retire yet:

- the overall `_classify_workflow()` fallback;
- lifecycle/status/replay command grammar;
- Product 1 routing markers;
- native development markers;
- provider onboarding markers;
- proposal-only OCS marker rules.

Affected runtime files:

- `aigol/runtime/conversational_cli_runtime.py`
- `aigol/runtime/conversation_native_development_intent_routing.py`
- `aigol/runtime/native_development_task_intake_runtime.py`
- `aigol/runtime/human_execution_intent_detection.py`
- `aigol/runtime/human_intent_clarification_intake_runtime.py`

Required regression coverage before retirement:

- all conversational routing tests;
- governed development routing tests;
- governance artifact unification tests;
- Product 1 routing tests;
- provider onboarding routing tests;
- native development context routing tests;
- proposal-only OCS escalation tests;
- lifecycle continuation tests;
- ambiguous prompt tests;
- multilingual prompt tests.

Rollback strategy:

Retain the current compatibility marker matrix behind a fallback function until UBTR route parity is proven for every registered workflow.

Certification impact:

Retiring this layer prematurely would risk Generation 1 certified behavior. Keep active until UBTR has consumer parity.

### 2. HIRR Marker Interpretation

Primary files:

- `aigol/runtime/human_intent_clarification_intake_runtime.py`
- `aigol/runtime/human_execution_intent_detection.py`

Current compatibility behavior:

- `classify_human_intent_for_clarification()` classifies business, problem, automation, compliance, ambiguous, improvement, continuation, and bounded file-write proof intents by phrase markers.
- `classify_development_intent_for_governed_routing()` resolves development intents to `GOVERNED_DEVELOPMENT_WORKFLOW` by local deterministic markers.
- `detect_human_execution_intent()` detects generic governed domain/artifact/execution requests using local creation, naming, governance, artifact, and execution terms.

Classification:

STILL_REQUIRED

Reason:

HIRR compatibility classifiers still provide clarification-first behavior, fail-closed generic execution handling, and low-confidence routing outcomes that are not yet fully replaced by Canonical Semantic Artifact consumers.

Safe retirement candidates:

None at full-function level.

Possible future retirement candidates:

- migrate `classify_development_intent_for_governed_routing()` to consume Canonical Semantic Artifact action/domain/entity fields;
- migrate `detect_human_execution_intent()` to consume Canonical Semantic Artifact execution intent, approval state, and entity fields;
- migrate `classify_human_intent_for_clarification()` to consume UBTR ambiguity and clarification state.

Required regression coverage before retirement:

- HIRR clarification tests;
- development intent routing tests;
- generic execution fail-closed tests;
- bounded file-write proof tests;
- continuation command tests;
- multilingual clarification tests.

Rollback strategy:

Keep the HIRR marker classifiers as fallback until UBTR artifacts encode all HIRR intent-family, confidence, clarification, and expected workflow target fields with parity.

Certification impact:

Removing these classifiers now would weaken clarification-first behavior and fail-closed governance. Not safe to retire.

### 3. Local Semantic Parsing

Primary file:

`aigol/runtime/conversational_cli_runtime.py`

Local semantic parsing includes:

- `_proposal_only_ocs_escalation()`;
- `_is_ocs_llm_cognition_prompt()`;
- `_is_plain_domain_proposal_prompt()`;
- `_is_plain_ocs_intake_prompt()`;
- `_is_provider_onboarding_domain_prompt()`;
- `_is_operator_decision_support_prompt()`;
- `_is_native_development_context_prompt()`;
- many `_is_*_prompt()` workflow helpers.

Classification:

STILL_REQUIRED

Reason:

UBTR now produces semantic and cognition lineage, but many workflows still consume local boolean marker functions as routing authority. The Canonical Semantic Artifact does not yet expose every field required to replace these local helpers for every workflow family.

Retirement candidates:

| Candidate | Status | Reason |
| --- | --- | --- |
| `_proposal_only_ocs_escalation()` | Partially retire later | UBTR Phase 3-5 now creates cognition request/handoff/result lineage, but proposal-only OCS route still uses local markers for operator-visible workflow selection. |
| `_is_governance_artifact_creation_prompt()` fallback | Partially retire later | UBTR-first route handles safe explicit governance artifact prompts, but fallback still protects broader language. |
| duplicate proposal/improvement checks | Safe to consolidate after tests | Duplicated in `_classify_workflow()` and likely cleanup-safe, but this audit does not implement cleanup. |
| broad Product 1/domain/provider/native markers | Not safe | Still outside narrow UBTR routing parity. |

Required regression coverage:

- one test per registered conversational workflow;
- one multilingual test per human-facing workflow family;
- parity tests comparing UBTR route result and legacy marker route result;
- replay reconstruction tests for both UBTR-selected and compatibility-selected paths.

Rollback strategy:

Migrate one workflow family at a time. Keep legacy marker route as fallback with explicit `semantic_routing_source`.

Certification impact:

Local semantic parsing is architectural drift relative to exclusive UBTR authority, but it remains certification-preserving compatibility for Generation 1.

### 4. Legacy Explanation Rendering

Primary file:

`aigol/runtime/acli_human_friendly_explanation_runtime.py`

Current compatibility behavior:

- UBTR Governance -> Human translation is primary when available.
- Existing deterministic human-friendly explanation sections remain as `compatibility_explanation`.
- The artifact records `compatibility_fallback_active: True`.
- `primary_render_source` is `UBTR_GOVERNANCE_TO_HUMAN_TRANSLATION` when UBTR output exists, otherwise `LEGACY_HUMAN_FRIENDLY_EXPLANATION`.

Classification:

PARTIALLY_REQUIRED

Reason:

UBTR output now exists, but the compatibility explanation still carries certified operator sections and protects presentation behavior if UBTR output translation fails.

Safe retirement candidates:

- retire compatibility rendering as the primary operator display only after operator-output regression proves UBTR projections satisfy all required sections;
- retain compatibility rendering as diagnostic evidence until replay compatibility certification confirms no downstream tests or operators depend on the legacy text sections.

Do not retire yet:

- `compatibility_explanation`;
- `compatibility_explanation_hash`;
- `compatibility_fallback_active`;
- deterministic section builder;
- transparency rendering.

Required regression coverage:

- explanation rendering tests;
- approval-facing explanation tests;
- replay reconstruction tests;
- LLM-assisted explanation fallback tests;
- fail-closed explanation tests;
- operator transcript tests.

Rollback strategy:

Keep `primary_render_source` and fallback fields. Disable legacy display only after UBTR output parity tests pass, while still retaining hash-visible compatibility evidence for at least one migration cycle.

Certification impact:

Premature retirement could reduce operator clarity. Keep active until UBTR output projections fully cover the certified human-friendly explanation contract.

### 5. Legacy Routing Decisions

Primary file:

`aigol/runtime/conversational_cli_runtime.py`

Current behavior:

Routing artifacts record both:

- UBTR references and hashes;
- compatibility routing source and marker-derived matched terms.

`semantic_routing_source` is:

- `CANONICAL_SEMANTIC_ARTIFACT` when the UBTR-first classifier decides;
- `COMPATIBILITY_FALLBACK` otherwise.

Classification:

STILL_REQUIRED

Reason:

This dual evidence is necessary during migration to prove whether a route was UBTR-native or fallback-derived.

Safe retirement candidates:

- remove `COMPATIBILITY_FALLBACK` as an expected successful route only after all registered workflow routes can be driven from Canonical Semantic Artifact fields;
- retain the field itself for replay interpretability even after compatibility fallbacks are retired.

Required regression coverage:

- route artifact schema tests;
- replay reconstruction tests;
- semantic routing source parity tests;
- hardening evidence completeness tests;
- release-candidate full suite.

Rollback strategy:

Preserve `semantic_routing_source` as a stable replay field. If a UBTR migration fails, fallback can be re-enabled without changing replay consumers.

Certification impact:

Keep legacy routing decision evidence until migration is certified.

## Retirement Readiness Matrix

| Compatibility Layer | Classification | Retirement Readiness | Blocker |
| --- | --- | --- | --- |
| ACLI `_classify_workflow()` fallback | Partially required | Not ready | Many registered workflows still rely on local markers |
| UBTR-first governed development route | Safe to keep as primary | Already migrated | None |
| Proposal-only OCS marker routing | Partially required | Not ready | UBTR cognition lineage exists, but workflow selection still depends on local markers |
| HIRR clarification markers | Still required | Not ready | UBTR ambiguity does not yet replace all intent-family outputs |
| Development intent markers | Still required | Not ready | Canonical artifact parity not proven across all prompts |
| Human execution intent markers | Still required | Not ready | Fail-closed generic execution behavior depends on current detector |
| Legacy explanation sections | Partially required | Not ready for removal | Operator section parity and fallback behavior still needed |
| Duplicate proposal/improvement prompt checks | Safe to consolidate later | Candidate | Requires narrow regression only |
| Late `GOVERNANCE_ARTIFACT_CREATION` fallback | Candidate after route parity | Blocked | Must prove all standard governance artifact prompts route to governed development |
| `semantic_routing_source` field | Required evidence | Do not retire | Needed for migration auditability |

## Retirement Candidates

### Candidate A: Duplicate Prompt Checks

Affected file:

`aigol/runtime/conversational_cli_runtime.py`

Description:

Some proposal and task-completion checks appear more than once in `_classify_workflow()`.

Retirement classification:

SAFE TO CONSOLIDATE AFTER NARROW REGRESSION

Required tests:

- conversational CLI routing suite;
- proposal runtime routing tests;
- improvement proposal routing tests.

Rollback:

Restore duplicate checks if parity fails.

Certification impact:

Low if behavior is proven unchanged.

### Candidate B: Late Generic Governance Artifact Route To `GOVERNANCE_ARTIFACT_CREATION`

Affected files:

- `aigol/runtime/conversational_cli_runtime.py`
- `aigol/runtime/human_execution_intent_detection.py`

Description:

The earlier governance-artifact unification objective normalized standard operator artifact requests into `GOVERNED_DEVELOPMENT_WORKFLOW`. A late generic execution-intent fallback can still route `GENERIC_GOVERNED_ARTIFACT_CREATION` to `GOVERNANCE_ARTIFACT_CREATION`, which historically lacks the complete operator lifecycle.

Retirement classification:

RETIREMENT CANDIDATE, BLOCKED BY ROUTE PARITY PROOF

Required tests:

- exact governance artifact prompts;
- named artifact prompts;
- Slovenian governance artifact prompts;
- no-execution governance document prompts;
- governed development proposal/approval/execution/replay tests.

Rollback:

Keep the current fallback until parity proves no real operator prompt depends on direct `GOVERNANCE_ARTIFACT_CREATION` as an operator-facing route.

Certification impact:

Potentially positive after proof because it removes an incomplete operator lifecycle route. Not safe without regression coverage.

### Candidate C: Compatibility Explanation As Primary Display

Affected file:

`aigol/runtime/acli_human_friendly_explanation_runtime.py`

Description:

UBTR output translation is now primary when available, but compatibility text is still rendered and hashed.

Retirement classification:

PARTIAL RETIREMENT CANDIDATE

Required tests:

- operator explanation tests;
- approval flow tests;
- resume flow tests;
- fail-closed explanation tests;
- replay reconstruction tests.

Rollback:

Keep `compatibility_explanation` persisted even if no longer displayed as primary.

Certification impact:

Could simplify operator output later, but not required for current certification.

## Blocked Retirement Areas

Do not retire yet:

1. ACLI local marker routing for broad workflow coverage.
2. HIRR marker interpretation.
3. human execution intent detection.
4. proposal-only OCS escalation markers.
5. Product 1 routing markers.
6. native development context markers.
7. provider onboarding markers.
8. status/replay/audit/dashboard command markers.
9. compatibility explanation replay fields.

Reason:

Each still supports certified Generation 1 behavior or migration evidence that UBTR does not yet fully replace.

## Required Additional Migration

Before compatibility retirement, implement or certify:

1. Canonical Semantic Artifact fields for every registered ACLI workflow.
2. Consumer parity tests for every `_classify_workflow()` branch.
3. UBTR-consumed HIRR intent-family output.
4. UBTR-consumed execution intent output.
5. UBTR-consumed proposal-only OCS routing.
6. UBTR output projection parity for every required explanation section.
7. Replay schema compatibility for migrated and legacy route evidence.
8. Hardening coverage proving real operator prompts no longer depend on fallback markers.

## Regression Strategy

For each retired compatibility layer:

1. Add a parity test showing old marker route and new UBTR route choose the same workflow.
2. Add a replay reconstruction test for the new UBTR-only route.
3. Add a fail-closed test for malformed Canonical Semantic Artifact input.
4. Add a rollback test proving fallback can still be enabled during migration.
5. Run the full conversational CLI suite.
6. Run the full Platform Core pytest suite.

## Rollback Strategy

Compatibility retirement must be reversible by restoring fallback use without changing governance artifacts or replay schema.

Required rollback properties:

- keep `semantic_routing_source`;
- keep UBTR lineage fields;
- keep compatibility fallback code until one migration cycle after retirement;
- keep replay fields for old artifacts;
- avoid deleting tests until replacement parity tests exist.

## Certification Impact

Current compatibility layers are not merely legacy clutter. They preserve Generation 1 certified operator behavior while UBTR migration expands.

Retirement is a Generation 2 implementation objective, not a prerequisite for the already-certified Generation 1 core.

Current certification impact:

| Area | Impact |
| --- | --- |
| Governance | No defect found |
| Replay | Compatibility evidence remains useful |
| Routing | Broad fallback still required |
| HIRR | Marker classifiers still required |
| Explanation | Compatibility rendering still protects operator clarity |
| UBTR | Canonical but not exclusive |

## Recommendation

Do not perform broad compatibility retirement yet.

Proceed with a phased retirement plan:

1. Consolidate duplicate local route checks.
2. Prove governance artifact route parity and retire direct operator-facing `GOVERNANCE_ARTIFACT_CREATION` fallback.
3. Migrate proposal-only OCS routing to consume UBTR cognition decision fields.
4. Migrate HIRR clarification to consume UBTR ambiguity and clarification state.
5. Migrate development/execution intent detection to consume CSA action, entity, approval, and execution fields.
6. Retire compatibility explanation display after UBTR output projection parity.
7. Retain compatibility replay fields for historical reconstruction.

## Non-Goals

This audit does not:

- remove compatibility code;
- change runtime behavior;
- change routing;
- change HIRR;
- change governance;
- change replay;
- change tests;
- alter approval boundaries;
- alter provider behavior;
- alter worker behavior.

## Final Verdict

UBTR_REQUIRES_ADDITIONAL_MIGRATION
