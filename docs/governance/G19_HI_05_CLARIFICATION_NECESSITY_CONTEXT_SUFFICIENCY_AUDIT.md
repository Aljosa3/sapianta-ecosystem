# G19-HI-05 Clarification Necessity and Context Sufficiency Audit

Status: AUDIT_ONLY.

Runtime behavior modified: no.

Governance scope: Platform Core clarification necessity, Human Intent Resolution, Platform Knowledge context, Project Services context assembly, deterministic clarification planning, Human Conversation Experience projection.

## Executive Verdict

Verdict:

`CLARIFICATION_NECESSITY_LACKS_FIRST_PASS_CONTEXT_SUFFICIENCY_TRANSITION`

Platform Core currently owns clarification necessity, but the ownership is implicit and split across Human Intent Resolution and deterministic clarification planning. The first deterministic failure is not Human Interface behavior. It occurs when Platform Core classifies an architecture prompt as needing an `architecture_outcome` clarification without first applying the same deterministic semantic slot satisfaction checks to the complete original request.

The observed prompt already contains the architecture outcome:

> Human Interfaces require only minimal bindings to Generation 19 Platform Core services and can become nearly stateless presentation adapters while Platform Core owns all Platform semantics.

That text satisfies the same semantic requirements later accepted for the `architecture_outcome` slot:

- reusable Platform Core behavior;
- Human Interface neutrality;
- observable user-visible outcome.

However, first-pass clarification planning still marks `architecture_outcome` as missing and generates:

`What outcome should the human interface architecture decision enable?`

The preferred remediation is a reusable Platform Core clarification necessity service that evaluates missing slots against all deterministic context before question generation.

## Observed Evidence

A temporary reproduction of the observed request produced:

- `work_type: AUDIT_ONLY`
- `mutation_allowed: False`
- `clarification_required: True`
- `clarification_reason: request is not a deterministic development request`
- `response_mode: CLARIFICATION`
- `selected_missing_slot: architecture_outcome`
- `missing_semantic_slots: architecture_outcome`
- `already_known_information_reused: True`
- generated question: `What outcome should the human interface architecture decision enable?`

This confirms three important facts:

1. G19-HI-02 work-type preservation is intact; the request remains `AUDIT_ONLY`.
2. The Human Interface is not inventing the clarification; it is rendering Platform Core output.
3. Platform Core records that known information was reused while still treating the architecture outcome as missing.

## Clarification Necessity Ownership Map

| Lifecycle responsibility | Current owner | Evidence | Audit finding |
| --- | --- | --- | --- |
| Request intake | Human Interface transport | `aicli` submits text to `prepare_unified_human_interface_project_context(...)` | Thin adapter boundary preserved. |
| Prior workspace restoration | Platform Core Project Services | `prepare_unified_human_interface_project_context(...)` loads latest workspace state before resolving intent | Correct owner. |
| Initial development intent resolution | Platform Core Project Services / HIRR | `resolve_development_intent(...)` sets `clarification_required` and `clarification_reason` | Necessity is first represented here. |
| Platform Knowledge reuse context | Platform Core Project Services | `knowledge_reuse` is assembled after intent resolution when no goal mapping exists | Knowledge exists, but does not currently clear already satisfied slots. |
| Conversation projection | Human Conversation Experience | `human_conversation_experience_from_resolution(...)` chooses `CLARIFICATION` when `intent["clarification_required"]` is true | Projection consumes intent state; it does not own sufficiency. |
| Clarification planning | Deterministic clarification planner | `deterministic_clarification_plan(...)` computes missing slots and selected question | Planner owns question selection but not a complete sufficiency transition. |
| Slot satisfaction for replies | Clarification Satisfaction Verification | `clarification_satisfaction_verification(...)` checks accepted requirements for active slots | Mature logic exists, but is only used after a question has been asked. |
| Completion/removal | Clarification completion transition | G19-HI-04 completion metadata clears satisfied pending clarification | Completion is now independent, but only after reply validation. |

Conclusion: Platform Core owns clarification necessity, but no explicit first-pass `clarification_necessity` artifact currently decides whether available context already satisfies a candidate missing slot.

## Clarification Preparation Lifecycle

Current deterministic lifecycle:

1. Human Interface submits the original request.
2. Project Services restores prior workspace state.
3. If no active pending clarification exists, Project Services calls `resolve_development_intent(...)`.
4. `resolve_development_intent(...)` determines goal/guided/continuation/collaborative signals.
5. It sets `clarification_required` for some conditions and sets `summary_admissible` to false when clarification is required.
6. Project Services assembles `knowledge_reuse`.
7. Human Conversation Experience calls `deterministic_clarification_plan(...)`.
8. The planner derives missing semantic slots.
9. `_clarification_missing_slots(...)` adds `architecture_outcome` when architecture language and an inferred candidate exist.
10. The planner selects `architecture_outcome`.
11. Human Conversation Experience emits a clarification question.
12. Human Interface renders that question.

Expected lifecycle with context sufficiency:

1. Human Interface submits the original request.
2. Project Services restores prior workspace state.
3. Platform Core resolves initial intent and candidate slots.
4. Platform Core assembles available deterministic context.
5. Clarification necessity evaluates each candidate missing slot against the original request, workspace state, prior clarifications, Platform Knowledge, and deterministic semantic requirement rules.
6. Already satisfied slots are removed before question generation.
7. Only genuinely unresolved slots reach deterministic clarification planning.
8. If no slots remain, approval or fail-closed informational projection proceeds according to work type and admissibility.

## Context Sufficiency Evaluation Map

| Context source | Currently available before question presentation? | Used to generate clarification? | Used to suppress already answered original-request slots? |
| --- | --- | --- | --- |
| Complete original request | Yes | Yes, via lowered text and detectors | Partially. It detects architecture language, but does not satisfy `architecture_outcome` from the same text. |
| Workspace replay state | Yes | Yes | Yes for some continuation and active objective cases. |
| Previous clarification answers | Yes | Yes | Yes after G19-HI-04 for completed clarifications. |
| Platform Knowledge reuse | Yes | Yes | Partially. It influences reuse slots but does not clear architecture outcome sufficiency. |
| Candidate capability discovery | Yes | Yes | Partially. It can create architecture outcome demand, but not prove outcome sufficiency. |
| Clarification satisfaction rules | Yes as code | No for first-pass original request sufficiency | No. These rules are applied to replies, not to the original request. |
| Work type metadata | Yes | Yes | Yes for runtime blocking; unrelated to necessity suppression. |

The key gap is asymmetry:

- reply text is checked by `_clarification_reply_satisfies_slot(...)`;
- original request text is not checked by an equivalent first-pass slot sufficiency function before `_clarification_missing_slots(...)` emits questions.

## Deterministic Root Cause

Root cause:

`_clarification_missing_slots(...)` treats architecture phrasing as evidence that an architecture outcome is missing whenever `_architecture_question_detected(...)` is true and a candidate exists. It does not check whether the complete original request already satisfies `architecture_outcome`.

Evidence:

- `prepare_unified_human_interface_project_context(...)` calls `resolve_development_intent(...)` before assembling fallback `knowledge_reuse`, then passes both into Human Conversation Experience.
- `resolve_development_intent(...)` creates the initial `clarification_required` state.
- `human_conversation_experience_from_resolution(...)` chooses clarification mode when `intent["clarification_required"]` is true.
- `deterministic_clarification_plan(...)` calls `_clarification_missing_slots(...)` when summary is not admissible.
- `_clarification_missing_slots(...)` unconditionally appends `architecture_outcome` for architecture language plus candidate.
- `_accepted_semantic_requirements(...)` and `_clarification_reply_satisfies_slot(...)` can recognize the observed answer as sufficient, but they are only applied to clarification replies.

First deterministic failure point:

`aigol/runtime/platform_core_project_services.py::_clarification_missing_slots`

It creates a missing `architecture_outcome` slot without first performing deterministic sufficiency evaluation against the original request and assembled context.

## Direct Answers To Audit Questions

1. Does Platform Core inspect the complete original request before generating clarification?

Yes, but incompletely. The request is inspected for routing signals, architecture terms, guided development terms, candidate targets, and work type. It is not inspected with the full semantic slot satisfaction rules before marking `architecture_outcome` missing.

2. Can clarification answers already present in the request be detected automatically?

Yes. Existing reply satisfaction logic already recognizes architecture outcome requirements deterministically. The same requirements can be reused against the original request, provided the result is represented as first-class Platform Core sufficiency metadata.

3. Does Platform Knowledge participate in clarification sufficiency evaluation?

Partially. Platform Knowledge participates in reuse and candidate context, but it does not currently own or complete slot sufficiency. It should remain an input, not the owner.

4. Does HIRR evaluate semantic sufficiency or only missing structured fields?

It evaluates semantic signals and structured admissibility, but first-pass sufficiency is not complete. Reply satisfaction has richer semantic requirement checks than original-request necessity.

5. Is clarification generated before available context has been fully assembled?

The initial `clarification_required` flag is set before fallback `knowledge_reuse` assembly. The final question is generated after context assembly, but the planner consumes an already blocking intent state and lacks a slot sufficiency removal phase.

6. Which Platform Core component owns clarification necessity?

Currently, ownership is implicit across `resolve_development_intent(...)`, `human_conversation_experience_from_resolution(...)`, and `deterministic_clarification_plan(...)`. Architecturally, Project Services should own the orchestration, while a dedicated Platform Core clarification necessity service should own the sufficiency decision.

7. Should clarification necessity become an explicit Platform Core service rather than an implicit side effect?

Yes. A first-class artifact would make the decision replay-visible, reusable across Human Interfaces, and independent from rendering.

8. Can clarification slots be deterministically satisfied from existing request context?

Yes. The architecture outcome slot can be satisfied from the observed prompt using the same deterministic requirement vocabulary already used for clarification replies.

9. Would such behavior preserve Platform Core governance while reducing unnecessary human interaction?

Yes. It would keep semantics in Platform Core, avoid Human Interface heuristics, stay fail-closed when requirements are not satisfied, and reduce only redundant clarification.

## Reusable Platform Core Components

| Existing component | Reuse role |
| --- | --- |
| `semantic_slot_for_clarification_question(...)` | Stable mapping from question text to semantic slot. |
| `_required_semantic_requirements(...)` | Canonical required requirements per slot. |
| `_accepted_semantic_requirements(...)` | Deterministic text-to-requirement acceptance. |
| `_clarification_reply_satisfies_slot(...)` | Existing deterministic satisfaction predicate, reusable after generalization beyond replies. |
| `clarification_decision_explainability(...)` | Explainability model for accepted/unresolved requirements. |
| `deterministic_clarification_plan(...)` | Question selection should consume sufficiency-filtered slots. |
| `knowledge_reuse` context | Input evidence for sufficiency, especially reuse/delta slots. |
| `resolve_governed_work_type(...)` | Preserves `AUDIT_ONLY` and blocks implementation runtime independently. |

## Minimal Remediation Strategy

No runtime implementation is included in this audit.

Minimal Platform Core correction:

1. Introduce a replay-visible `PLATFORM_CORE_CLARIFICATION_NECESSITY_EVALUATION_V1` artifact.
2. Evaluate candidate missing slots against deterministic context before question generation.
3. Generalize existing reply satisfaction helpers so they can evaluate any text source:
   - original request;
   - bound clarification reply;
   - prior completed clarification;
   - relevant workspace or knowledge evidence when explicitly mapped.
4. Add per-slot metadata:
   - `candidate_missing_slots`;
   - `satisfied_from_original_request`;
   - `satisfied_from_workspace_context`;
   - `satisfied_from_previous_clarification`;
   - `remaining_missing_slots`;
   - `clarification_required_after_sufficiency`;
   - `clarification_necessity_authority: PLATFORM_CORE`.
5. Make `deterministic_clarification_plan(...)` consume `remaining_missing_slots`, not raw detector-produced slots.
6. Preserve fail-closed behavior: if a slot cannot be deterministically satisfied, keep the question.
7. Keep all Human Interfaces unchanged except for consuming the resulting Platform Core projection.

This preserves Platform Core ownership and avoids Human Interface-specific heuristics.

## Regression Scenarios

Required regression scenarios:

1. Architecture outcome present in original request:
   - Prompt contains `Human Interfaces require only minimal bindings... Platform Core owns all Platform semantics`.
   - Expected: no `architecture_outcome` clarification is generated from that slot.

2. Architecture subject present but outcome absent:
   - Prompt asks whether a behavior belongs in Platform Core architecture without outcome language.
   - Expected: `architecture_outcome` remains required.

3. Architecture outcome present but subject absent:
   - Prompt says reusable outcome is desired but does not name the behavior/artifact.
   - Expected: `architecture_subject` or equivalent slot remains required.

4. AUDIT_ONLY work type with sufficient architecture outcome:
   - Expected: work type remains `AUDIT_ONLY`, `mutation_allowed: false`, no runtime implementation approval is prepared.

5. IMPLEMENTATION work type with sufficient outcome:
   - Expected: no redundant clarification; approval preparation may proceed only if all implementation admissibility checks pass.

6. Reuse request with sufficient delta in original prompt:
   - Expected: `reuse_delta` is satisfied from original request and not asked again.

7. Reuse request with evidence but no delta:
   - Expected: `reuse_delta` remains pending.

8. Previous completed clarification:
   - Expected: G19-HI-04 completion metadata continues to suppress repeated accepted questions.

9. Human Interface parity:
   - `./aicli`, `aigol next`, Web, REST, Voice, and future adapters receive the same Platform Core projection for the same request.

## Affected Artifacts And Functions

Primary affected runtime functions for a future implementation:

- `aigol/runtime/platform_core_project_services.py::prepare_unified_human_interface_project_context`
- `aigol/runtime/platform_core_project_services.py::resolve_development_intent`
- `aigol/runtime/platform_core_project_services.py::human_conversation_experience_from_resolution`
- `aigol/runtime/platform_core_project_services.py::deterministic_clarification_plan`
- `aigol/runtime/platform_core_project_services.py::_clarification_missing_slots`
- `aigol/runtime/platform_core_project_services.py::_required_semantic_requirements`
- `aigol/runtime/platform_core_project_services.py::_accepted_semantic_requirements`
- `aigol/runtime/platform_core_project_services.py::_clarification_reply_satisfies_slot`

Primary test areas:

- `tests/test_g15_hir_08_deterministic_clarification_planner.py`
- `tests/test_g15_hir_10_clarification_satisfaction_verification.py`
- `tests/test_g19_hi_04_clarification_completion_lifecycle.py`
- a new G19-HI-05 regression test module for first-pass context sufficiency.

## Certification Readiness

Current status:

`NOT_CERTIFICATION_READY_FOR_CONTEXT_SUFFICIENCY`

Reason:

Clarification completion and work-type preservation are hardened, but clarification necessity does not yet have first-class sufficiency metadata. The system remains deterministic and fail-closed, but it can request redundant clarification when the original prompt already satisfies the active semantic slot.

Readiness after minimal remediation:

`READY_FOR_TARGETED_G19_HI_05_CERTIFICATION`

Certification should require:

- replay-visible clarification necessity artifact;
- no Human Interface heuristics;
- no runtime implementation for `AUDIT_ONLY`;
- no repeated completed clarification from G19-HI-04;
- no redundant first-pass clarification when original request satisfies the slot;
- preserved fail-closed clarification when deterministic sufficiency is absent.

## Final Conclusion

Platform Core can deterministically recognize that a clarification answer is already present in the original request, but the current pipeline does not apply that recognition before generating clarification.

The minimal correction is not to reduce clarification generally. It is to make clarification necessity a first-class Platform Core lifecycle decision:

available deterministic context

-> candidate missing slots

-> slot sufficiency evaluation

-> remaining missing slots only

-> clarification generation.

This preserves Platform Core governance, keeps Human Interfaces thin, reuses existing clarification satisfaction logic, and prevents unnecessary clarification when the required answer is already present.
