# UBTR Exclusive Semantic Authority Migration Program V1

Status: migration program.

Inputs:

- `CANONICAL_SEMANTIC_AUTHORITY_ARCHITECTURE_AUDIT_V1`
- `UBTR_CONSUMER_MIGRATION_AUDIT_V1`
- `UBTR_CONSUMER_MIGRATION_PLAN_V1`

Feature Freeze: active.

This artifact defines a migration program only. It does not implement code, change runtime behavior, alter routing, redesign governance, modify replay, change HIRR, change PPP, change approval, change resume behavior, or remove compatibility layers.

## 1. Executive Summary

Platform Core Generation 1 identifies Universal Bidirectional Translation Runtime as the canonical semantic translation authority.

Current operational reality:

```text
Human
-> UBTR evidence is produced
-> local ACLI/HIRR/consumer semantic markers still participate
-> Platform Core consumers
-> Replay
```

Target architecture:

```text
Human
-> Universal Bidirectional Translation Runtime
-> Canonical Semantic Artifact
-> Platform Core consumers
-> Replay
-> Human-friendly explanation
```

The migration goal is not to create new architecture. The goal is to complete adoption of the already-defined UBTR architecture by moving every semantic consumer from prompt-local interpretation to canonical semantic artifact consumption.

The final state allows exactly one component to own semantic translation:

```text
Universal Bidirectional Translation Runtime
```

All other Platform Core components consume semantic artifacts, structured workflow state, or deterministic lifecycle commands.

## 2. Authority Boundary

Semantic authority is not governance authority.

UBTR may:

- translate human language into canonical semantic artifacts;
- translate governance state into human-readable artifacts;
- identify ambiguity;
- assign confidence;
- preserve semantic lineage;
- record replay-visible translation evidence.

UBTR may not:

- approve;
- reject;
- authorize;
- execute;
- invoke workers;
- invoke providers as authority;
- mutate governance;
- mutate replay;
- override workflow governance;
- bypass fail-closed behavior.

All approval, execution, worker, validation, and replay authority remains where it exists today.

## 3. Current Architecture

The current live architecture is compatibility-mode adoption:

```text
Human prompt
-> Human -> Governance UBTR artifact
-> ACLI/HIRR compatibility routing
-> local workflow and clarification markers
-> selected workflow or clarification
-> proposal / approval / execution path
-> replay
-> explanation
```

Current semantic interpretation is still performed in multiple locations:

- ACLI conversational routing.
- HIRR intake.
- HIRR continuity.
- governance artifact routing.
- proposal-only OCS escalation.
- human execution intent detection.
- native development intent routing.
- PPP handoff classification and routing support.
- hardening scenario classification.
- OCS semantic resolution.
- provider-assisted intent classification.

This is certification-safe only when described as:

```text
UBTR canonical with active compatibility layers
```

It is not yet:

```text
UBTR exclusive semantic authority
```

## 4. Target Architecture

The target architecture is:

```text
Human natural language
-> UBTR Human -> Governance translation
-> Canonical Semantic Artifact
-> HIRR-compatible clarification, if needed
-> workflow routing
-> PPP / OCS / approval / worker / replay consumers
-> UBTR Governance -> Human translation
-> operator explanation
```

Target rules:

- natural-language meaning is translated once by UBTR;
- consumers do not independently derive semantic meaning from the raw prompt;
- consumers may validate canonical semantic artifacts;
- consumers may apply governance rules to semantic artifacts;
- consumers may fail closed when artifacts are malformed, ambiguous, incomplete, or unauthorized;
- local markers may remain only as fallback until migration is complete;
- exact lifecycle commands remain deterministic workflow-control grammar, not semantic translation ownership.

## 5. Canonical Semantic Artifact Contract

Every semantic consumer should receive a validated Canonical Semantic Artifact derived from the Universal Translation Artifact Schema.

### Mandatory Fields

| Field | Purpose |
| --- | --- |
| `artifact_type` | Identifies the artifact as a Universal Translation artifact |
| `translation_id` | Stable semantic translation identity |
| `source_direction` | `HUMAN_TO_GOVERNANCE` or `GOVERNANCE_TO_HUMAN` |
| `source_payload` | Original source material and source hash |
| `normalized_intent` | Canonical intent family, actions, domain, entities, confidence |
| `translated_governance_payload` | Canonical governance-facing payload |
| `ambiguity_flags` | Ambiguity status, clarification status, clarification questions |
| `confidence` | Deterministic confidence level |
| `provider_metadata` | Provider participation metadata, even when provider count is zero |
| `deterministic_fallback_status` | Deterministic rule and fallback metadata |
| `authority_flags` | Explicit denial of approval, execution, mutation, governance, replay, worker, and provider authority |
| `artifact_hash` | Stable deterministic hash |
| `replay_reference` | Replay-visible storage reference |
| `created_at` | Creation timestamp |

### Mandatory Semantic Payload Fields

| Field | Purpose |
| --- | --- |
| `intent_family` | Consumer-neutral intent family |
| `requested_actions` | CREATE, UPDATE, IMPLEMENT, REVIEW, EXPLAIN, COMPARE, SUMMARIZE, UNKNOWN, or equivalent canonical action set |
| `domain_candidate` | Candidate domain |
| `workflow_candidate` | Candidate workflow, not authoritative workflow selection |
| `approval_required` | Whether governance approval may be required |
| `execution_requested` | Whether execution appears requested |
| `provider_relevance` | Whether provider cognition is relevant |
| `worker_relevance` | Whether worker execution may become relevant after approval |
| `entities` | Artifact identifiers, target paths, named domains, subjects |
| `clarification_required` | Whether clarification is required before governance decision |
| `clarification_questions` | Deterministic clarification questions |

### Optional Fields

Optional fields may include:

- `workflow_id` once selected by governance;
- `workflow_selection_reference`;
- `replay_chain_id`;
- `turn_reference`;
- `semantic_identity`;
- `semantic_equivalence_group`;
- `translation_lineage`;
- `migration_source`;
- `compatibility_fallback_reason`;
- `local_marker_comparison`;
- `multilingual_normalization`;
- `operator_language`;
- `provider_translation_candidates`;
- `comparison_result`.

Optional fields must not grant authority.

### Replay Identity

Replay identity must preserve:

- translation replay reference;
- translation artifact hash;
- source prompt hash;
- chain id when available;
- turn reference when available;
- workflow selection reference once workflow selection occurs;
- compatibility fallback source when local markers are used.

### Workflow Identity

Workflow identity is not owned by UBTR.

UBTR may propose `workflow_candidate`. Workflow selection remains governed by ACLI/workflow routing.

Consumers must distinguish:

```text
semantic workflow candidate
```

from:

```text
governed selected workflow
```

### Semantic Identity

Semantic identity should be derived from:

- source payload hash;
- normalized intent;
- requested actions;
- domain candidate;
- entity set;
- ambiguity state;
- translation runtime version.

Semantic identity is used for comparison, hardening, and replay-derived learning. It is not approval or execution authority.

## 6. Consumer Inventory

| Consumer | Current Semantic Input | Desired Semantic Input | Compatibility Remaining | Complexity | Dependencies |
| --- | --- | --- | --- | --- | --- |
| ACLI | human prompt, local command checks, routing capture | Canonical Semantic Artifact plus structured lifecycle commands | approval/lifecycle commands, fallback markers | High | Phase 1 and replay provenance |
| Conversational CLI Runtime | raw prompt and local markers | Canonical Semantic Artifact for workflow routing | `_classify_workflow` fallback | High | Phase 0 comparison corpus |
| HIRR Intake | local intent-family markers | UBTR ambiguity, confidence, intent family | HIRR marker fallback | High | routing read-through |
| HIRR Continuity | clarification response markers | UBTR artifacts for original and clarification turns | continuity fallback | High | HIRR intake migration |
| Workflow Routing | local candidate and structured workflow registry | UBTR workflow candidate plus governance validation | route fallback | Medium | ACLI/HIRR migration |
| Proposal-Only OCS Escalation | local proposal-only markers | UBTR provider relevance, execution flag, action/domain | multilingual fallback markers | Medium | ACLI routing read-through |
| PPP | structured context and some source prompt recovery | UBTR semantic annotation plus structured context artifacts | native development fallback | Medium | context handoff stability |
| Approval Runtime | exact approval commands and proposal state | structured command state; Governance -> Human semantic artifact for explanations | command grammar | Low | safe resume summaries |
| Resume Runtime | lifecycle commands and replay-restored proposal state | structured command state; Governance -> Human summary artifact | command grammar | Low | replay migration |
| Replay Runtime | all recorded artifacts | all UBTR artifacts and decision-source provenance | legacy replay fields | Medium | all phases emit stable metadata |
| Hardening Runtime | token scans and derived event metadata | UBTR semantic identity and structured replay fields | legacy token scan | Medium | replay migration |
| Deterministic Explanation Runtime | authoritative state and local render fields | Governance -> Human Canonical Semantic Artifact | renderer compatibility | Low | G->H translation adoption |
| LLM-Assisted Explanation Runtime | authoritative state and deterministic explanation | Governance -> Human artifact plus deterministic explanation | provider renderer fallback | Low | explanation integration |
| Human -> Governance Translation Runtime | human prompt | canonical producer | none | Complete | no migration |
| Governance -> Human Translation Runtime | governance state | canonical producer | none | Complete | no migration |

## 7. Compatibility-Layer Retirement Plan

| Compatibility Layer | Why It Exists | Removal Prerequisites | Retirement Milestone |
| --- | --- | --- | --- |
| `_classify_workflow(human_prompt)` local markers | Certified routing behavior predates UBTR consumption | UBTR route parity for certified prompt corpus | Phase 3 completion |
| `_proposal_only_ocs_escalation()` local markers | Proposal-only policy implemented before UBTR exclusive adoption | UBTR provider relevance and execution flags cover proposal-only cases | Phase 2 completion |
| HIRR intent-family marker checks | HIRR existed before UBTR canonical artifact consumption | UBTR ambiguity and intent family generate equivalent HIRR artifacts | Phase 4 completion |
| HIRR continuity markers | Clarification refinement requires stable target preservation | UBTR turn-pair comparison preserves target and ambiguity reduction | Phase 5 completion |
| human execution intent markers | Generic execution detection predates UBTR | UBTR action, approval, execution, and worker relevance parity | Phase 6 completion |
| native development prompt markers | Native development flow predates UBTR semantic annotation | UBTR action/domain signals cover native development corpus | Phase 7 completion |
| PPP prompt reconstruction fallback | Legacy handoff protection and recovery | replay-restored structured context plus UBTR annotation available | Phase 7 completion |
| approval command parsing | Structured governance command grammar | Not retired; remains command grammar, not semantic authority | Not applicable |
| lifecycle command parsing | Structured workflow continuation grammar | Not retired; remains lifecycle grammar, not semantic authority | Not applicable |
| replay legacy fields | Historical replay compatibility | migration metadata and canonical artifacts available for new sessions | Phase 8 completion |
| hardening token scan | Legacy session classification | structured replay and UBTR fields available | Phase 9 completion |

Approval and lifecycle command parsing are intentionally retained. They are not semantic translation owners when handling exact deterministic commands.

## 8. Migration Phases

### Phase 0: Exclusive Authority Readiness Baseline

Prerequisites:

- `UBTR_CONSUMER_MIGRATION_AUDIT_V1`.
- `UBTR_CONSUMER_MIGRATION_PLAN_V1`.
- current Platform Core test baseline.

Implementation scope:

- none in this artifact.
- future implementation should add replay-only semantic provenance comparison.

Regression scope:

- no behavior change.
- prove existing routes remain unchanged.

Rollback strategy:

- no runtime change exists to roll back.

Exit criteria:

- baseline corpus identifies every semantic consumer and local marker source.

### Phase 1: ACLI Semantic Ingress

Prerequisites:

- replay-only comparison available.
- UBTR artifact validation stable.

Implementation scope:

- ACLI receives a Canonical Semantic Artifact for every natural-language turn.
- ACLI stores semantic identity and translation reference in routing capture.
- ACLI keeps local routing as fallback until parity is proven.

Regression scope:

- conversational routing.
- governed development prompts.
- governance artifact prompts.
- multilingual prompts.
- proposal-only prompts.
- unknown intent prompts.

Rollback strategy:

- route using current local classifier while retaining UBTR evidence.

Exit criteria:

- ACLI no longer invokes semantic consumers without first producing a validated Canonical Semantic Artifact for natural-language input.

### Phase 2: Conversational Routing Consumption

Prerequisites:

- Phase 1 complete.
- routing equivalence evidence exists.

Implementation scope:

- workflow routing consumes UBTR workflow candidate and semantic fields.
- local marker checks become fallback only.
- decision source is replay-visible.

Regression scope:

- full conversational CLI routing suite.
- proposal-only OCS escalation suite.
- governed development bridge suite.
- fail-closed routing suite.

Rollback strategy:

- set decision source back to local compatibility.

Exit criteria:

- routing can be explained from UBTR artifact fields for certified prompt families.

### Phase 3: Proposal-Only OCS Escalation

Prerequisites:

- routing consumes UBTR artifact.
- provider relevance and execution request fields are stable.

Implementation scope:

- proposal-only cognition uses UBTR canonical fields.
- no-execution and no-worker intent is represented in semantic payload.
- multilingual operator language is represented by UBTR, not duplicated marker lists.

Regression scope:

- proposal-only governance document prompts.
- summarize/explain/compare/brainstorm prompts.
- Slovenian proposal-only prompts.
- execution-like prompts that must not become proposal-only.
- provider unavailable fail-closed behavior.

Rollback strategy:

- restore local proposal-only marker decision source.

Exit criteria:

- proposal-only OCS routing has no decisive local marker dependency for certified cases.

### Phase 4: HIRR Intake

Prerequisites:

- UBTR ambiguity and confidence fields stable.
- ACLI semantic ingress complete.

Implementation scope:

- HIRR artifacts generated from Canonical Semantic Artifact.
- local intent-family classifiers move to fallback.
- HIRR preserves existing artifact shape.

Regression scope:

- business goal intent.
- general improvement intent.
- compliance intent.
- automation intent.
- problem statement intent.
- development intent.
- ambiguous intent.
- clarification questions.

Rollback strategy:

- local HIRR classifier remains available.

Exit criteria:

- HIRR no longer independently derives semantic meaning for certified prompt families.

### Phase 5: HIRR Continuity

Prerequisites:

- HIRR intake migration.
- clarification-turn UBTR artifacts available.

Implementation scope:

- clarification responses produce UBTR artifacts.
- ambiguity reduction and target preservation are derived from linked semantic artifacts.
- local continuity markers fallback only.

Regression scope:

- multi-turn clarification.
- target preservation.
- clarification promotion to workflow.
- multilingual clarification.
- fail-closed incomplete clarification.

Rollback strategy:

- local continuity runtime remains available.

Exit criteria:

- HIRR continuity no longer uses raw clarification prose as semantic authority for certified flows.

### Phase 6: Human Execution Intent And Governance Artifact Detection

Prerequisites:

- HIRR intake and routing consumption migrated.

Implementation scope:

- execution intent detection consumes UBTR action, approval, execution, worker, and entity fields.
- governance artifact detection consumes UBTR entities and domain/action candidates.
- local execution markers fallback only.

Regression scope:

- artifact creation.
- domain creation.
- governed execution fail-closed.
- approval-required behavior.
- no authority granted by semantic translation.

Rollback strategy:

- local execution detector remains available.

Exit criteria:

- artifact and execution intent are derived from UBTR for certified cases.

### Phase 7: PPP And Native Development Consumers

Prerequisites:

- native development and execution intent fields represented by UBTR.
- replay-restored context handoff remains certified.

Implementation scope:

- native development flows consume UBTR semantic annotation.
- PPP consumes structured context artifacts and UBTR semantic references.
- PPP does not rebuild semantic context from raw prompt when a restored artifact exists.

Regression scope:

- native development context assembly.
- continue ppp.
- replay-restored PPP continuation.
- resource selection.
- OCS-to-PPP binding.
- workflow identity and replay identity preservation.

Rollback strategy:

- current structured context and local native markers remain available.

Exit criteria:

- PPP receives semantic context by artifact reference, not prompt re-interpretation.

### Phase 8: Approval And Resume Semantic Boundary

Prerequisites:

- Governance -> Human translation artifacts available for proposal state.

Implementation scope:

- exact commands remain structured lifecycle grammar.
- natural-language approval-adjacent prose may be translated by UBTR before governance interpretation.
- restored proposal summaries use Governance -> Human artifacts.

Regression scope:

- same-session approve.
- cross-session approve.
- approve this proposal.
- reject.
- request modification.
- cancel.
- retry.
- clarify.
- pending clarification plus pending governed proposal precedence.

Rollback strategy:

- command grammar remains unchanged.

Exit criteria:

- approval/resume consumers do not act as semantic interpreters except for deterministic command grammar.

### Phase 9: Replay Canonicalization

Prerequisites:

- consumers emit decision-source provenance.

Implementation scope:

- replay reconstruction links every semantic decision to a Canonical Semantic Artifact or compatibility fallback.
- legacy decisions remain readable.
- replay does not reinterpret semantics.

Regression scope:

- translation replay reconstruction.
- route replay reconstruction.
- approval replay reconstruction.
- execution replay reconstruction.
- hardening replay reconstruction.
- malformed semantic artifact fail-closed.

Rollback strategy:

- preserve legacy replay readers.

Exit criteria:

- replay can deterministically prove semantic source for each routed interaction.

### Phase 10: Hardening And Metrics Migration

Prerequisites:

- replay semantic provenance stable.

Implementation scope:

- hardening runtime classifies scenarios from structured replay and UBTR semantic identity.
- local token scan remains only for legacy sessions.

Regression scope:

- successful hardening event.
- fail-closed hardening event.
- persisted metrics.
- scenario coverage.
- workflow coverage.
- legacy replay compatibility.

Rollback strategy:

- local token scan fallback remains.

Exit criteria:

- new hardening evidence does not rely on local semantic marker scans.

### Phase 11: Compatibility Retirement Certification

Prerequisites:

- phases 1-10 complete.
- no certified prompt family depends on local semantic markers.

Implementation scope:

- remove or disable compatibility markers only through governed implementation work.
- preserve legacy replay compatibility.

Regression scope:

- full Platform Core suite.
- real-world operator scenario pack.
- replay reconstruction.
- fail-closed injection.
- multilingual prompt suite.
- provider unavailable.
- worker unavailable.

Rollback strategy:

- retain archived compatibility mode until one release cycle after retirement certification.

Exit criteria:

- UBTR is the exclusive semantic authority for natural-language input across Platform Core.

## 9. Regression Strategy

Regression must verify:

- semantic determinism;
- replay determinism;
- workflow determinism;
- explanation consistency;
- compatibility fallback;
- rollback behavior;
- malformed semantic artifact fail-closed behavior;
- no approval authority from translation;
- no execution authority from translation;
- no worker invocation from translation;
- no provider authority from translation;
- multilingual semantic parity;
- legacy replay readability.

Required regression groups:

1. UBTR artifact schema validation.
2. Human -> Governance translation.
3. Governance -> Human translation.
4. ACLI conversational routing.
5. HIRR intake and continuity.
6. proposal-only OCS escalation.
7. governed development workflow.
8. approval continuation and safe resume.
9. lifecycle continuation.
10. PPP handoff and replay-restored continuation.
11. hardening evidence capture.
12. full Platform Core suite.

## 10. Certification Impact

Exclusive UBTR semantic authority is not required to preserve current Platform Core Generation 1 certification when certification language remains:

```text
UBTR canonical with compatibility layers
```

Exclusive UBTR semantic authority is required before Platform Core can certify:

```text
UBTR fully exclusive semantic authority
```

Recommended certification sequencing:

1. Generation 1 formal certification may proceed with documented compatibility layers if all current invariants pass.

2. Exclusive UBTR migration should be treated as post-certification hardening or a Generation 1.x governed migration program.

3. Full compatibility-layer retirement should be considered a Generation 2 boundary unless product release discipline explicitly approves it as a hardening-only change.

Therefore:

- Required for current Gen1 certification: NO.
- Recommended after certification: YES.
- Candidate Generation 2 boundary: YES, for complete local-marker retirement.

## 11. Implementation Roadmap

| Roadmap Item | Phase | Scope | Risk |
| --- | --- | --- | --- |
| Semantic provenance comparison | 0 | replay-only evidence | Low |
| ACLI semantic ingress | 1 | translation before all NL consumers | Medium |
| Routing read-through | 2 | route from UBTR with fallback | High |
| Proposal-only migration | 3 | OCS escalation from semantic artifact | Medium |
| HIRR intake migration | 4 | HIRR artifact from UBTR | High |
| HIRR continuity migration | 5 | linked turn semantics | High |
| Execution intent migration | 6 | action/execution fields | Medium |
| PPP/native migration | 7 | semantic references plus structured context | Medium |
| Approval/resume boundary | 8 | commands remain grammar; prose uses UBTR | Low |
| Replay canonicalization | 9 | semantic source reconstruction | Medium |
| Hardening migration | 10 | structured evidence classification | Medium |
| Compatibility retirement | 11 | remove marker authority | High |

## 12. Non-Goals

This program does not:

- implement migration.
- change runtime behavior.
- remove compatibility layers now.
- introduce a new semantic architecture.
- make UBTR governance authority.
- make providers semantic authority.
- make explanation runtimes semantic authority.
- redesign HIRR.
- redesign ACLI.
- redesign PPP.
- redesign approval.
- redesign resume.
- redesign replay.
- alter Feature Freeze constraints.
- claim current runtime is already exclusively UBTR-driven.

## 13. Success Criteria

The migration program is successful when future implementation can demonstrate:

```text
Human
-> UBTR
-> Canonical Semantic Artifact
-> ACLI / HIRR / Routing / PPP / Approval / Resume / Replay / Hardening consumers
-> Replay
-> Governance -> Human explanation
```

with:

- no natural-language semantic meaning independently derived by consumers;
- compatibility layers inactive for certified prompt families;
- deterministic fallback preserved for legacy and malformed cases;
- replay able to prove semantic source and decision source;
- all governance, approval, provider, worker, replay, and fail-closed invariants preserved.

## Final Verdict

UBTR_EXCLUSIVE_SEMANTIC_AUTHORITY_MIGRATION_PROGRAM_READY
