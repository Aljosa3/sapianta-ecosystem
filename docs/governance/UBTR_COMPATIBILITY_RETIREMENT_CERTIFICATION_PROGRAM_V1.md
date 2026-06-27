# UBTR Compatibility Retirement Certification Program V1

## Status

Defined.

Final verdict:

UBTR_COMPATIBILITY_RETIREMENT_PROGRAM_READY

## Objective

Define the certification program required before retiring each Generation 1 compatibility layer now that UBTR is canonical in the live Human -> UBTR -> OCS -> UBTR -> Human flow.

This program does not modify runtime code, modify tests, retire compatibility logic, change governance, change replay, change routing, or change approval semantics.

## Certification Principle

A compatibility layer may be retired only when the UBTR path proves equivalent or superior behavior for the same operator scenario set while preserving:

- governance boundaries;
- replay determinism;
- approval boundaries;
- fail-closed behavior;
- provider non-authority;
- worker non-authority;
- historical replay interpretability;
- rollback capability.

No compatibility layer may be removed because it appears redundant. Removal requires replay-visible parity evidence.

## Compatibility Layers In Scope

This program covers the layers identified by:

`UBTR_IMPLEMENTATION_PHASE_6_COMPATIBILITY_LAYER_RETIREMENT_AUDIT_V1`

Layers:

1. duplicate local route checks;
2. late direct `GOVERNANCE_ARTIFACT_CREATION` fallback;
3. ACLI broad compatibility routing;
4. proposal-only OCS marker routing;
5. HIRR marker interpretation;
6. development intent marker interpretation;
7. human execution intent detection;
8. local workflow semantic parsing;
9. legacy explanation rendering;
10. legacy routing decision evidence.

## Universal Removability Criteria

A compatibility layer is removable only when all criteria are satisfied:

| Criterion | Requirement |
| --- | --- |
| Functional parity | UBTR path selects the same workflow, clarification, or explanation outcome as the compatibility path for the certified scenario set. |
| Semantic parity | Canonical Semantic Artifact contains the fields previously inferred by local markers. |
| Replay parity | Replay records enough evidence to explain the decision without the retired compatibility code. |
| Fail-closed parity | Malformed or ambiguous UBTR artifacts fail closed at least as safely as the compatibility path. |
| Regression parity | Targeted and full-suite tests pass with compatibility disabled for the layer under certification. |
| Operator parity | Human-facing output remains understandable and no required approval or replay instruction disappears. |
| Rollback | The retired layer can be restored without replay schema migration. |
| Certification record | A governance artifact records evidence, limitations, and final removal decision. |

## Program Evidence Model

Each retirement certification package must contain:

- layer identifier;
- affected files;
- pre-retirement behavior summary;
- UBTR replacement behavior summary;
- parity scenario list;
- replay references or replay artifact hashes from parity execution;
- regression results;
- fail-closed evidence;
- rollback plan;
- certification decision;
- remaining limitations.

Required decision values:

- `RETIREMENT_CERTIFIED`
- `RETIREMENT_CERTIFIED_WITH_LIMITATIONS`
- `RETIREMENT_DEFERRED`

## Layer Certification Requirements

### Layer 1: Duplicate Local Route Checks

Purpose:

Preserve duplicate checks in `_classify_workflow()` that route proposal, improvement-proposal, and task-completion prompts.

Remaining dependency:

These duplicates are not known to provide distinct behavior, but that must be proven.

Affected runtime files:

- `aigol/runtime/conversational_cli_runtime.py`

Retirement prerequisites:

- identify exact duplicate branches;
- prove first retained branch covers every test case covered by duplicate branch;
- prove no branch-order side effect changes selected workflow.

Parity evidence required:

- before/after route result for proposal prompts;
- before/after route result for improvement proposal prompts;
- before/after route result for native task-completion prompts.

Replay evidence required:

- route decision artifact hash before cleanup;
- route decision artifact hash after cleanup, allowing expected hash drift caused by code path consolidation but requiring equivalent workflow, confidence, and matched semantic class.

Regression requirements:

- conversational CLI routing suite;
- proposal runtime routing tests;
- improvement proposal routing tests;
- native development context routing tests;
- full pytest.

Rollback strategy:

Restore duplicate branches from the previous commit if any route parity fails.

Certification impact:

Low risk. This is the first recommended retirement because it reduces maintenance without changing semantic authority.

Objective removability criteria:

All duplicate-branch scenario outputs are behaviorally equivalent and full suite passes.

### Layer 2: Late Direct `GOVERNANCE_ARTIFACT_CREATION` Fallback

Purpose:

Route generic governed artifact creation prompts detected by `detect_human_execution_intent()`.

Remaining dependency:

The fallback can still route to `GOVERNANCE_ARTIFACT_CREATION`, a component workflow that does not represent the complete operator-facing governed development lifecycle.

Affected runtime files:

- `aigol/runtime/conversational_cli_runtime.py`
- `aigol/runtime/human_execution_intent_detection.py`

Retirement prerequisites:

- prove standard operator governance-artifact prompts route to `GOVERNED_DEVELOPMENT_WORKFLOW`;
- prove named artifact prompts preserve explicit identifiers;
- prove no-execution governance-document prompts route to OCS proposal-only cognition when appropriate;
- prove direct `GOVERNANCE_ARTIFACT_CREATION` remains available only as an internal component if still required.

Parity evidence required:

- exact prompts for governance artifact creation;
- named artifact prompts such as `ACLI_USAGE_GUIDELINES_V1`;
- Slovenian governance artifact prompts;
- no-execution governance document prompts;
- historical failing prompts from operator validation.

Replay evidence required:

- UBTR translation artifact;
- Canonical Semantic Artifact;
- routing decision artifact;
- proposal or OCS cognition evidence;
- no worker invocation before approval.

Regression requirements:

- governance artifact unification tests;
- governed development bridge tests;
- conversational routing tests;
- proposal fidelity tests;
- approval/rejection/modification tests;
- full pytest.

Rollback strategy:

Keep a feature-local fallback branch that can restore direct `GOVERNANCE_ARTIFACT_CREATION` routing if any certified artifact creation route regresses.

Certification impact:

Medium positive if certified. It removes an incomplete operator-facing route and strengthens the unified governed development lifecycle.

Objective removability criteria:

No certified operator prompt requires direct `GOVERNANCE_ARTIFACT_CREATION` route, and all operator artifact creation prompts retain proposal, explanation, approval, validation, and replay behavior.

### Layer 3: Proposal-Only OCS Marker Routing

Purpose:

Route proposal-only requests such as create governance document, summarize, explain, compare, brainstorm, or generate implementation proposal into `OCS_LLM_COGNITION` without worker execution.

Remaining dependency:

`_proposal_only_ocs_escalation()` still uses local text markers and multilingual phrases rather than Canonical Semantic Artifact fields and UBTR cognition decision output.

Affected runtime file:

- `aigol/runtime/conversational_cli_runtime.py`

Retirement prerequisites:

- CSA must encode proposal-only classification;
- CSA must encode execution prohibition/no-worker/no-mutation intent;
- UBTR Phase 3-5 cognition lineage must expose enough fields for route selection;
- multilingual proposal-only prompts must produce equivalent CSA fields.

Parity evidence required:

- English governance document requests;
- Slovenian governance document requests;
- summarize/explain/compare/brainstorm prompts;
- explicit no-worker/no-file-write prompts;
- prompts with execution markers that must not be proposal-only.

Replay evidence required:

- UBTR semantic cognition decision;
- OCS cognition request when needed;
- OCS handoff evidence;
- cognition-integrated CSA;
- provider invocation status;
- worker invocation status.

Regression requirements:

- proposal-only OCS escalation tests;
- multilingual routing tests;
- OCS cognition diagnostic tests;
- provider unavailable tests;
- fail-closed unsupported request tests;
- full pytest.

Rollback strategy:

Keep `_proposal_only_ocs_escalation()` as fallback until UBTR-native proposal-only classification has completed at least one hardening cycle.

Certification impact:

Medium risk. Retiring too early may recreate the real-world issue where proposal-only cognition was not observed.

Objective removability criteria:

Every certified proposal-only scenario reaches the same workflow through UBTR-derived fields, with replay proving no worker execution and no approval bypass.

### Layer 4: HIRR Marker Interpretation

Purpose:

Provide clarification-first handling for broad human intent families.

Remaining dependency:

`classify_human_intent_for_clarification()` still creates intent-family, confidence, clarification question, and expected workflow target outputs from local phrase markers.

Affected runtime file:

- `aigol/runtime/human_intent_clarification_intake_runtime.py`

Retirement prerequisites:

- CSA must encode all HIRR intent families;
- CSA ambiguity and clarification state must map to existing HIRR outputs;
- UBTR must preserve low-confidence and unknown-intent behavior;
- multilingual clarification prompts must remain supported.

Parity evidence required:

- business goal prompts;
- problem statement prompts;
- automation prompts;
- compliance prompts;
- ambiguous prompts;
- general improvement prompts;
- continuation prompts;
- bounded file-write proof prompts;
- unknown prompts.

Replay evidence required:

- UBTR translation artifact;
- CSA ambiguity state;
- CSA clarification state;
- HIRR-compatible output artifact;
- fail-closed evidence for malformed artifacts.

Regression requirements:

- HIRR clarification tests;
- ACLI human prompt acceptance tests;
- real ACLI scenario tests;
- lifecycle continuation command tests;
- multilingual prompt tests;
- full pytest.

Rollback strategy:

Maintain HIRR marker classifier as fallback until CSA-to-HIRR parity is certified for every intent family.

Certification impact:

High risk. This layer protects clarification-first governance. Retire late.

Objective removability criteria:

UBTR-derived HIRR output exactly preserves intent family, confidence, clarification behavior, expected targets, and fail-closed behavior for all certified HIRR scenario packs.

### Layer 5: Development Intent Marker Interpretation

Purpose:

Route natural development prompts into `GOVERNED_DEVELOPMENT_WORKFLOW`.

Remaining dependency:

`classify_development_intent_for_governed_routing()` and related local prompt checks still detect development intents by phrase and subject markers.

Affected runtime files:

- `aigol/runtime/human_intent_clarification_intake_runtime.py`
- `aigol/runtime/conversational_cli_runtime.py`

Retirement prerequisites:

- CSA must encode development intent, requested action, target artifact, repository mutation relevance, and approval requirement;
- proposal generation must preserve artifact names and target paths from CSA;
- approval continuation and replay resume must work through CSA lineage.

Parity evidence required:

- add/create/implement prompts;
- governance artifact creation prompts;
- document update prompts;
- repository mutation prompts;
- ambiguous development prompts;
- same-session and cross-session approval prompts.

Replay evidence required:

- CSA action/entity fields;
- governed development proposal hash;
- approval binding;
- repository mutation evidence where approved;
- validation evidence;
- replay reconstruction evidence.

Regression requirements:

- governed development workflow tests;
- execution bridge tests;
- approval continuation tests;
- proposal content fidelity tests;
- repository mutation worker tests;
- full pytest.

Rollback strategy:

Keep development marker routing available until every no-copy-paste and real-world ACLI development scenario passes through CSA-derived route selection.

Certification impact:

High risk because this is the primary certified development interface.

Objective removability criteria:

All certified governed development prompts route through UBTR-derived CSA fields with unchanged proposal, approval, execution, validation, and replay behavior.

### Layer 6: Human Execution Intent Detection

Purpose:

Detect generic governed domain/artifact/execution requests and fail closed on generic execution requests without certified mappings.

Remaining dependency:

`detect_human_execution_intent()` still protects fail-closed behavior for generic governed execution language.

Affected runtime file:

- `aigol/runtime/human_execution_intent_detection.py`

Retirement prerequisites:

- CSA must represent execution request, target kind, target name, execution authority absence, and routing action;
- generic governed execution must still fail closed without a certified workflow mapping;
- generic artifact/domain creation must route to certified workflows or clarification.

Parity evidence required:

- governed domain creation prompts;
- governed artifact creation prompts;
- generic governed execution prompts;
- malformed target names;
- named/called target patterns.

Replay evidence required:

- CSA execution intent field;
- approval state;
- worker relevance;
- fail-closed reason;
- no authorization evidence.

Regression requirements:

- execution intent detection tests;
- conversational CLI fail-closed tests;
- domain clarification tests;
- governed development tests;
- full pytest.

Rollback strategy:

Retain detector as last-resort safety fallback until CSA execution-intent fields are certified.

Certification impact:

High risk. This layer enforces important fail-closed semantics.

Objective removability criteria:

All generic execution and creation prompts produce identical safe routing or fail-closed outcomes through UBTR-derived fields.

### Layer 7: Local Workflow Semantic Parsing

Purpose:

Route broad workflow families not yet represented by CSA route consumers.

Remaining dependency:

Many `_is_*_prompt()` helpers in `conversational_cli_runtime.py` still determine workflow selection for Product 1, provider onboarding, domain lifecycle, capability lifecycle, OCS cognition, replay/status/dashboard, and native development.

Affected runtime files:

- `aigol/runtime/conversational_cli_runtime.py`
- `aigol/runtime/conversation_native_development_intent_routing.py`
- `aigol/runtime/native_development_task_intake_runtime.py`

Retirement prerequisites:

- every registered workflow must have a CSA route contract;
- each route contract must specify CSA fields, confidence thresholds, ambiguity behavior, and fail-closed behavior;
- workflow registry tests must prove UBTR route coverage.

Parity evidence required:

- one scenario per registered workflow;
- one ambiguous prompt per workflow family;
- one unsupported prompt per workflow family;
- multilingual prompts where supported.

Replay evidence required:

- CSA route contract reference;
- routing decision artifact;
- `semantic_routing_source` showing UBTR-native route;
- no compatibility fallback.

Regression requirements:

- full conversational CLI routing suite;
- workflow registry coverage test;
- Product 1 routing tests;
- provider onboarding tests;
- native development tests;
- full pytest.

Rollback strategy:

Migrate one workflow family at a time. Keep compatibility route branch for non-migrated workflow families.

Certification impact:

Highest risk. Retire only after all smaller layers are certified.

Objective removability criteria:

Every conversationally routable workflow is selected from CSA fields, and compatibility fallback is not exercised in the certified scenario pack.

### Layer 8: Legacy Explanation Rendering

Purpose:

Maintain certified human-friendly explanation sections and deterministic fallback when UBTR output translation is unavailable.

Remaining dependency:

`acli_human_friendly_explanation_runtime.py` stores `compatibility_explanation`, compatibility hash, and fallback status.

Affected runtime file:

- `aigol/runtime/acli_human_friendly_explanation_runtime.py`

Retirement prerequisites:

- UBTR Governance -> Human projection must satisfy every required explanation section;
- operator-facing text must remain clear for non-technical operators;
- deterministic fallback must remain available;
- replay must record rendered output hash and source.

Parity evidence required:

- proposal explanation;
- approval explanation;
- rejection explanation;
- request modification explanation;
- execution explanation;
- validation explanation;
- replay review explanation;
- fail-closed explanation.

Replay evidence required:

- Governance -> Human translation artifact;
- rendered operator output hash;
- fallback status;
- explanation source transparency.

Regression requirements:

- human-friendly explanation tests;
- LLM-assisted explanation tests;
- operator experience tests;
- approval workflow tests;
- replay reconstruction tests;
- full pytest.

Rollback strategy:

Stop displaying compatibility text first, but continue storing compatibility hashes for one migration cycle. Restore display if operator tests regress.

Certification impact:

Medium risk. Retirement can improve UX, but losing certified sections would harm operator confidence.

Objective removability criteria:

UBTR output alone satisfies the human-friendly explanation contract for every certified operator journey.

### Layer 9: Legacy Routing Decision Evidence

Purpose:

Record whether a route came from CSA or compatibility fallback.

Remaining dependency:

`semantic_routing_source` and matched-term evidence support migration auditability.

Affected runtime file:

- `aigol/runtime/conversational_cli_runtime.py`

Retirement prerequisites:

- compatibility fallback must no longer be used in certified scenarios;
- historical replay interpretation must remain possible;
- hardening evidence must retain route provenance.

Parity evidence required:

- all routes show UBTR-native source in certified scenario pack;
- no route requires compatibility fallback for production scope.

Replay evidence required:

- stable route source field;
- migration status metadata;
- historical compatibility replay examples.

Regression requirements:

- route artifact schema tests;
- hardening evidence completeness tests;
- replay reconstruction tests;
- full pytest.

Rollback strategy:

Do not remove the field. Retire only the expectation that `COMPATIBILITY_FALLBACK` appears as a normal successful route.

Certification impact:

Low-to-medium. Field should remain for audit even after compatibility behavior retires.

Objective removability criteria:

Compatibility fallback is absent from current certified replay, while historical replay remains reconstructable.

## Recommended Retirement Order

Retire from lowest risk to highest risk:

1. Duplicate local route checks.
2. Late direct `GOVERNANCE_ARTIFACT_CREATION` operator-facing fallback.
3. Compatibility explanation as primary display.
4. Proposal-only OCS marker routing.
5. Development intent marker interpretation.
6. Human execution intent detection.
7. HIRR marker interpretation.
8. Local workflow semantic parsing for remaining workflow families.
9. Compatibility fallback as accepted successful routing source.

Rationale:

- Start with behavior-preserving cleanup.
- Then remove incomplete operator-facing route paths.
- Then improve presentation after UBTR output parity.
- Then migrate high-value semantic routes.
- Retire broad workflow parsing only after every workflow has a CSA route contract.

## Certification Work Packages

### UBTR_RETIREMENT_BATCH_01

Scope:

- duplicate local route checks.

Risk:

Low.

Required evidence:

- route parity;
- targeted routing tests;
- full pytest.

Expected decision:

`RETIREMENT_CERTIFIED`

### UBTR_RETIREMENT_BATCH_02

Scope:

- direct `GOVERNANCE_ARTIFACT_CREATION` fallback.

Risk:

Medium.

Required evidence:

- governance artifact route parity;
- governed development lifecycle evidence;
- no incomplete lifecycle path.

Expected decision:

`RETIREMENT_CERTIFIED_WITH_LIMITATIONS` until hardening confirms real-world prompts.

### UBTR_RETIREMENT_BATCH_03

Scope:

- compatibility explanation display.

Risk:

Medium.

Required evidence:

- operator experience parity;
- explanation replay parity;
- deterministic fallback retained.

Expected decision:

`RETIREMENT_CERTIFIED_WITH_LIMITATIONS`

### UBTR_RETIREMENT_BATCH_04

Scope:

- proposal-only OCS marker routing.

Risk:

Medium-high.

Required evidence:

- UBTR proposal-only CSA fields;
- OCS request/handoff/result lineage;
- provider unavailable fail-closed tests.

Expected decision:

`RETIREMENT_DEFERRED` until CSA proposal-only fields are fully specified and implemented.

### UBTR_RETIREMENT_BATCH_05

Scope:

- development intent markers;
- human execution intent detection.

Risk:

High.

Required evidence:

- governed development route parity;
- fail-closed generic execution parity;
- approval/replay continuity.

Expected decision:

`RETIREMENT_DEFERRED` until CSA execution-intent fields are certified.

### UBTR_RETIREMENT_BATCH_06

Scope:

- HIRR marker interpretation.

Risk:

High.

Required evidence:

- HIRR intent-family parity;
- clarification-state parity;
- multilingual parity.

Expected decision:

`RETIREMENT_DEFERRED` until UBTR-derived HIRR output is certified.

### UBTR_RETIREMENT_BATCH_07

Scope:

- broad local workflow semantic parsing.

Risk:

Highest.

Required evidence:

- CSA route contract for every registered workflow;
- full workflow registry parity;
- hardening scenario coverage.

Expected decision:

`RETIREMENT_DEFERRED`

### UBTR_RETIREMENT_BATCH_08

Scope:

- compatibility fallback as accepted successful routing source.

Risk:

Highest.

Required evidence:

- no certified scenario uses fallback;
- historical replay remains reconstructable.

Expected decision:

`RETIREMENT_DEFERRED`

## Certification Gate Checklist

Before any compatibility layer is retired:

- [ ] affected layer is identified by name and file;
- [ ] UBTR replacement path exists;
- [ ] parity scenario pack exists;
- [ ] replay evidence package exists;
- [ ] fail-closed tests exist;
- [ ] targeted regression passes;
- [ ] full pytest passes;
- [ ] rollback patch or re-enable path is documented;
- [ ] certification artifact records decision;
- [ ] governance invariants remain unchanged.

## Replay Requirements

Every retirement certification must record:

- prior compatibility route evidence;
- UBTR replacement route evidence;
- Canonical Semantic Artifact hash;
- UBTR translation lineage;
- OCS cognition lineage if cognition participates;
- rendered human output hash if explanation participates;
- approval state where relevant;
- worker/provider non-invocation where relevant;
- fail-closed evidence for malformed or unsupported input.

Replay must allow deterministic reconstruction of why the retired compatibility layer was no longer needed.

## Rollback Requirements

Every retirement must support rollback without:

- replay schema migration;
- governance model changes;
- approval model changes;
- provider model changes;
- worker model changes;
- losing historical replay interpretability.

Rollback options:

- restore prior branch;
- reactivate compatibility fallback;
- route only the failing workflow family back to compatibility;
- preserve UBTR evidence while using compatibility decision result.

## Certification Impact Model

| Retirement type | Certification effect |
| --- | --- |
| Duplicate cleanup | Maintenance improvement, low certification impact |
| Incomplete route removal | Positive operator lifecycle impact if parity proven |
| Explanation compatibility display retirement | UX simplification if operator parity proven |
| Proposal-only marker retirement | Semantic authority improvement, medium risk |
| Development/execution marker retirement | Major semantic authority improvement, high risk |
| HIRR marker retirement | Major architecture alignment, high risk |
| Broad local parser retirement | UBTR exclusivity milestone, highest risk |

## Non-Goals

This program does not:

- retire any layer;
- modify runtime behavior;
- modify tests;
- remove replay fields;
- redesign UBTR;
- redesign HIRR;
- redesign routing;
- redesign governance;
- change approval semantics;
- change provider behavior;
- change worker behavior.

## Final Verdict

UBTR_COMPATIBILITY_RETIREMENT_PROGRAM_READY
