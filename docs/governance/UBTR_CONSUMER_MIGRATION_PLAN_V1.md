# UBTR Consumer Migration Plan V1

Status: migration planning artifact.

Input: `UBTR_CONSUMER_MIGRATION_AUDIT_V1`.

Feature Freeze: active.

This plan does not implement code, modify routing, modify governance, modify replay, modify translation logic, modify tests, or remove compatibility layers.

## 1. Purpose

This plan defines the deterministic migration path for Platform Core consumers to move from active local marker-based semantic interpretation toward Universal Bidirectional Translation Runtime consumed semantic artifacts.

UBTR remains the canonical semantic translation authority.

Local marker systems remain permitted only as compatibility fallback until each consumer is migrated, replay-protected, regression-tested, and explicitly certified.

## 2. Migration Principles

The migration must preserve:

- Feature Freeze constraints.
- Human authority.
- ACLI governance authority.
- approval boundaries.
- replay determinism.
- fail-closed behavior.
- provider isolation.
- worker isolation.
- deterministic routing behavior during compatibility mode.
- current certified ACLI/HIRR behavior until replacement is proven.

The migration must not:

- introduce a new translation architecture.
- remove compatibility layers immediately.
- treat explanations as semantic authority.
- treat providers as semantic authority.
- allow UBTR artifacts to approve, execute, mutate, or authorize.
- weaken existing deterministic marker coverage before UBTR parity is proven.

## 3. Canonical Artifact Inputs

Consumers should migrate toward these canonical UBTR artifacts:

| Consumer Need | Canonical Artifact |
| --- | --- |
| Human prompt normalization | Human -> Governance Universal Translation Artifact |
| intent family | `normalized_intent.intent_family` |
| requested action | `normalized_intent.requested_actions` |
| domain candidate | `normalized_intent.domain_candidate` and `translated_governance_payload.domain_candidate` |
| workflow candidate | `translated_governance_payload.workflow_candidate` |
| ambiguity | `ambiguity_flags` |
| confidence | `confidence` |
| approval requirement | `translated_governance_payload.approval_required` |
| execution requested | `translated_governance_payload.execution_requested` |
| provider relevance | `translated_governance_payload.provider_relevance` |
| worker relevance | `translated_governance_payload.worker_relevance` |
| artifact identifiers | `normalized_intent.entities.artifact_identifiers` |
| target paths | `normalized_intent.entities.target_paths` |
| operator explanation | Governance -> Human Universal Translation Artifact |
| replay-visible lineage | `translation_replay_reference` and `artifact_hash` |

If an existing local marker emits meaning that UBTR does not yet represent, the first migration step is to add replay-only comparison evidence, not to remove the local marker.

## 4. Consumer Migration Order

### Phase 0: Replay-Only Equivalence Capture

Order: first.

Consumers:

- ACLI conversational routing.
- HIRR intake.
- proposal-only OCS escalation.
- hardening runtime.

Work:

- Keep current local marker decisions authoritative for compatibility.
- Record UBTR-derived semantic fields beside current local decisions.
- Persist comparison evidence showing agreement, disagreement, confidence, ambiguity, and local fallback reason.
- Do not change selected workflow.
- Do not change clarification behavior.
- Do not change provider routing.

Temporary local markers retained:

- all current `_classify_workflow()` marker paths.
- all HIRR intake marker paths.
- `_proposal_only_ocs_escalation()` markers.
- hardening component/scenario token scanning.

Regression requirements:

- existing conversational routing tests remain unchanged.
- new replay-only comparison tests prove no behavior change.
- malformed translation artifact fails closed before comparison is trusted.

Exit criteria:

- every ACLI interaction records both local decision and UBTR semantic comparison.
- no workflow selection changes are introduced.

### Phase 1: ACLI Conversational Routing Read-Through

Order: after Phase 0.

Consumer:

- `conversational_cli_runtime._classify_workflow()`.

Target UBTR artifact:

- Human -> Governance Universal Translation Artifact.

Work:

- Feed `_classify_workflow()` a validated translated governance payload in addition to the raw prompt.
- Prefer UBTR fields only when they deterministically match existing certified local routing.
- Keep raw prompt marker routing as fallback.
- Record which source made the decision: `UBTR_MATCH`, `LOCAL_COMPATIBILITY_FALLBACK`, or `DIVERGENCE_FAIL_CLOSED`.

Temporary local markers retained:

- domain lifecycle markers.
- provider onboarding markers.
- governed development markers.
- governance artifact markers.
- native development markers.
- fallback OCS markers.

Regression requirements:

- exact route parity for certified ACLI prompts.
- multilingual route parity.
- governance artifact route parity.
- governed development route parity.
- proposal-only OCS route parity.
- fail-closed unrestricted autonomous agent prompt.

Rollback strategy:

- disable UBTR decision preference and continue recording comparison evidence.
- retain local marker routing as the operational path.

Exit criteria:

- UBTR read-through produces identical routing for certified prompt corpus.
- divergences are explicitly classified and replay-visible.

### Phase 2: Proposal-Only OCS Escalation Migration

Order: after Phase 1.

Consumer:

- `_proposal_only_ocs_escalation()`.

Target UBTR artifact:

- Human -> Governance Universal Translation Artifact.
- `translated_governance_payload.provider_relevance`.
- `translated_governance_payload.execution_requested`.
- `normalized_intent.requested_actions`.
- `normalized_intent.domain_candidate`.
- `ambiguity_flags`.

Work:

- Use UBTR fields to determine proposal-only cognition eligibility.
- Keep local proposal-only markers as fallback for gaps in UBTR multilingual coverage.
- Record escalation reason using canonical UBTR fields.
- Preserve no-worker and no-side-effect guarantees.

Temporary local markers retained:

- explicit no-execution markers.
- Slovenian no-execution markers.
- governance document markers.
- proposal action markers.

Regression requirements:

- Slovenian proposal-only governance prompt reaches OCS cognition.
- English proposal-only governance prompt reaches OCS cognition.
- execution-like prompt without no-execution marker does not become proposal-only.
- worker invocation remains false.
- replay records escalation reason and provider selection.

Rollback strategy:

- return proposal-only decisions to local marker source while preserving UBTR comparison evidence.

Exit criteria:

- proposal-only route decisions are driven by UBTR where represented.
- local markers are used only when UBTR lacks the needed multilingual or operator-intent signal.

### Phase 3: HIRR Intake Migration

Order: after Phase 2.

Consumers:

- `human_intent_clarification_intake_runtime.py`.
- `classify_human_intent_for_clarification()`.
- `classify_development_intent_for_governed_routing()`.

Target UBTR artifact:

- Human -> Governance Universal Translation Artifact.
- `normalized_intent.intent_family`.
- `ambiguity_flags`.
- `confidence`.
- `translated_governance_payload.workflow_candidate`.
- `translated_governance_payload.clarification_required`.
- `translated_governance_payload.clarification_questions`.

Work:

- Generate HIRR-compatible intake artifacts from UBTR fields.
- Preserve existing HIRR artifact shape.
- Preserve existing clarification questions until UBTR parity is proven.
- Keep current intent-family marker checks as fallback.

Temporary local markers retained:

- business goal intent markers.
- general improvement markers.
- compliance markers.
- automation markers.
- problem statement markers.
- ambiguous intent fallback.
- development intent markers.

Regression requirements:

- all HIRR family classification tests.
- ambiguity and clarification-required tests.
- unknown intent fail-closed or clarification behavior.
- clarification question continuity.
- governed development routing from development intent.

Rollback strategy:

- continue using local HIRR classifier while retaining UBTR comparison evidence.

Exit criteria:

- HIRR-compatible artifacts can be generated from UBTR for certified HIRR corpus.
- divergences are documented and either fixed in UBTR or retained as local fallback.

### Phase 4: HIRR Continuity And Clarification Refinement

Order: after Phase 3.

Consumer:

- `human_intent_clarification_continuity_runtime.py`.

Target UBTR artifact:

- Human -> Governance Universal Translation Artifact for the original prompt.
- Human -> Governance Universal Translation Artifact for clarification response.
- linked replay references for the clarification turn.

Work:

- Translate clarification responses through UBTR before refinement.
- Preserve existing continuity state.
- Preserve clarification chain identity.
- Use UBTR ambiguity reduction as evidence, not unilateral authority.

Temporary local markers retained:

- clarification response interpretation.
- target preservation markers.
- proposal-only cognition routing continuity markers.

Regression requirements:

- clarification can promote ambiguous intent to workflow.
- target preservation remains deterministic.
- multilingual clarification remains supported.
- proposal-only cognition escalation after clarification remains side-effect free.

Rollback strategy:

- local continuity refinement remains active.

Exit criteria:

- UBTR can explain whether clarification reduced ambiguity.
- existing HIRR continuity behavior remains stable.

### Phase 5: Human Execution Intent Detection Migration

Order: after Phase 4.

Consumer:

- `human_execution_intent_detection.py`.

Target UBTR artifact:

- Human -> Governance Universal Translation Artifact.
- `translated_governance_payload.execution_requested`.
- `translated_governance_payload.approval_required`.
- `translated_governance_payload.worker_relevance`.
- `normalized_intent.requested_actions`.
- `normalized_intent.entities`.

Work:

- Use UBTR to distinguish create/update/implement/review intents.
- Preserve fail-closed behavior for generic governed execution requests without certified mapping.
- Preserve approval requirement.
- Keep local creation/execution/governance-artifact markers as fallback.

Temporary local markers retained:

- creation terms.
- execution terms.
- governance artifact terms.
- artifact kind terms.
- naming markers.

Regression requirements:

- generic governed artifact creation.
- generic governed domain creation.
- generic governed execution fail-closed.
- no execution authority granted by translation.

Rollback strategy:

- revert to local detector while leaving UBTR evidence intact.

Exit criteria:

- UBTR execution-intent fields match local detector outcomes for certified prompts.

### Phase 6: Native Development And PPP Handoff Migration

Order: after Phase 5.

Consumers:

- native development intent routing.
- PPP handoff integration.
- OCS-to-PPP binding.
- PPP resource selection.

Target UBTR artifact:

- Human -> Governance Universal Translation Artifact.
- structured context artifacts already produced by ACLI/OCS.
- replay-linked task intake and context assembly artifacts.

Work:

- Use UBTR to annotate native development intent and action class.
- Continue using structured context artifacts for PPP handoff.
- Do not replace PPP validation semantics with free-text interpretation.
- Do not re-parse the original prompt when replay-restored context exists.

Temporary local markers retained:

- native development prompt markers.
- task completion markers.
- PPP resource selection validation rules.

Regression requirements:

- native development context assembly.
- continue ppp from restored context.
- PPP consumes restored native context artifact.
- workflow identity and replay chain identity preservation.
- no HIRR re-entry on lifecycle continuation.

Rollback strategy:

- retain current structured handoff and local native development detection.

Exit criteria:

- UBTR provides semantic annotation, while PPP continues to consume structured context as authority for handoff.

### Phase 7: Approval And Resume Consumers

Order: after Phase 6.

Consumers:

- approval runtime.
- same-session approval bridge.
- cross-session approval resume.
- lifecycle continuation runtime.

Target UBTR artifact:

- none for deterministic commands unless the command is natural-language ambiguous.
- Governance -> Human Universal Translation Artifact for operator-facing summaries.

Work:

- Keep `APPROVE`, `APPROVE THIS PROPOSAL`, `REJECT`, `REQUEST_MODIFICATION`, `continue`, `resume`, `cancel`, `retry`, and `clarify` as structured lifecycle commands.
- Do not route deterministic lifecycle commands through UBTR.
- Use Governance -> Human translation for re-presenting restored proposal state.
- Use UBTR only for ambiguous operator prose that is not an exact command.

Temporary local markers retained:

- approval command parsing.
- lifecycle command parsing.
- safe approval resume confirmation parsing.

Regression requirements:

- same-session approval wins over clarification continuity.
- cross-session approval requires safe re-presentation.
- bare `APPROVE` after restart does not execute.
- `APPROVE THIS PROPOSAL` executes only with valid restored proposal.
- request modification does not authorize execution.
- reject does not authorize execution.

Rollback strategy:

- continue using structured command path unchanged.

Exit criteria:

- approval/resume behavior remains command-deterministic.
- UBTR is used only for explanation or ambiguous prose, not command authority.

### Phase 8: Replay Consumer Migration

Order: parallel after Phase 1, complete after Phase 7.

Consumer:

- replay runtime and replay reconstruction consumers.

Target UBTR artifact:

- all Universal Translation Artifacts and integration artifacts.

Work:

- Ensure replay reconstruction can link:
  - original prompt.
  - Human -> Governance artifact.
  - workflow selection.
  - local fallback source, if any.
  - Governance -> Human explanation artifact.
  - approval and execution artifacts.
- Replay remains source of truth.
- Replay does not make semantic decisions.

Temporary local markers retained:

- none as authority.
- legacy marker fields may remain as historical evidence.

Regression requirements:

- translation artifact hash reconstruction.
- integration artifact reconstruction.
- local fallback source reconstruction.
- malformed artifact fail-closed.

Rollback strategy:

- keep legacy replay references readable.

Exit criteria:

- replay can prove whether a decision came from UBTR or local compatibility fallback.

### Phase 9: Hardening Consumer Migration

Order: after replay migration has stable fields.

Consumer:

- `acli_hardening_runtime.py`.

Target UBTR artifact:

- Human -> Governance and Governance -> Human translation artifacts.
- routing comparison artifacts.
- hardening event derived evidence.

Work:

- Replace local token scans where possible with explicit replay fields.
- Keep token scanning as fallback for legacy sessions.
- Record whether hardening scenario classification used UBTR, structured replay fields, or legacy token scanning.

Temporary local markers retained:

- component detection tokens.
- scenario catalog token triggers.

Regression requirements:

- successful workflow hardening event.
- fail-closed workflow hardening event.
- persisted metrics across restart.
- scenario coverage from structured replay fields.
- legacy replay still classified.

Rollback strategy:

- use local token scan fallback.

Exit criteria:

- hardening metrics derive from structured replay and translation evidence for new sessions.

## 5. Migration Dependency Graph

```text
Phase 0 Replay-Only Equivalence Capture
-> Phase 1 ACLI Conversational Routing Read-Through
-> Phase 2 Proposal-Only OCS Escalation
-> Phase 3 HIRR Intake
-> Phase 4 HIRR Continuity
-> Phase 5 Human Execution Intent Detection
-> Phase 6 Native Development And PPP Handoff
-> Phase 7 Approval And Resume Consumers
-> Phase 8 Replay Consumer Migration
-> Phase 9 Hardening Consumer Migration
```

Phase 8 may begin during Phase 1, but it cannot be considered complete until every earlier phase emits stable provenance fields.

Phase 7 must not convert deterministic lifecycle commands into semantic translation requests.

## 6. Compatibility Layer Retention Rules

Compatibility layers may remain while any of the following are true:

- UBTR does not yet encode a field required by a certified local marker.
- UBTR and local marker output diverge on certified prompt corpus.
- regression coverage is missing.
- replay provenance cannot reconstruct the decision source.
- rollback cannot be performed without behavior change.
- multilingual behavior is less complete than the local fallback.

Compatibility layers may be retired only when:

- UBTR artifact fields cover the behavior.
- comparison evidence shows parity or explicitly approved improvement.
- regression coverage exists.
- replay records migration state.
- removal is approved through governed development.

## 7. Rollback Strategy

Every phase must be reversible by configuration or scoped implementation guard.

Rollback requirements:

- preserve local marker path.
- preserve UBTR replay artifacts.
- preserve comparison evidence.
- preserve workflow output shape.
- preserve existing tests.
- mark rollback reason in replay when a migrated path returns to compatibility fallback.

Rollback must never:

- erase translation replay.
- erase prior local decisions.
- reinterpret historical replay.
- mutate governance records.
- grant execution authority.

## 8. Certification Impact

The migration improves certification precision by making semantic provenance explicit.

Before migration:

- UBTR is canonical architecture.
- compatibility layers remain active.
- certification must state that UBTR is canonical with compatibility layers.

After Phase 0:

- certification can prove local and UBTR semantic decisions side by side.

After Phases 1-5:

- certification can claim ACLI/HIRR semantic intake is UBTR-consumed for migrated prompt families.

After Phases 6-9:

- certification can claim Platform Core consumers derive natural-language semantic meaning from UBTR artifacts or structured replay artifacts, with local markers retained only as documented fallback.

Certification must not claim UBTR fully replaces all local markers until:

- all consumers in this plan are migrated.
- fallback usage is limited to documented legacy sessions or unsupported semantic gaps.
- full regression and replay reconstruction pass.

## 9. Explicit Non-Goals

This plan does not:

- introduce a new translation architecture.
- redesign UBTR.
- redesign HIRR.
- redesign ACLI.
- redesign OCS.
- redesign PPP.
- redesign approval.
- redesign replay.
- introduce provider authority.
- introduce worker authority.
- make explanation runtimes semantic authorities.
- remove compatibility layers immediately.
- change current runtime behavior.
- change tests.
- repair proposal-only routing.
- implement multilingual expansion.
- implement autonomous replay-derived rule promotion.

## 10. Acceptance Criteria

The migration plan is ready when it defines:

- consumer-by-consumer migration order.
- the UBTR artifact each consumer should consume.
- temporary local marker retention.
- regression requirements.
- rollback strategy.
- certification impact.
- explicit non-goals.

This artifact satisfies those criteria.

## Final Verdict

UBTR_CONSUMER_MIGRATION_PLAN_READY
