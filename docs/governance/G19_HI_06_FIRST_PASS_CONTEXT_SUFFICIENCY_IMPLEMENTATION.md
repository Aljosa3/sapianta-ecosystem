# G19-HI-06 First-Pass Context Sufficiency Implementation

Status: implemented.

Runtime behavior changed: Platform Core clarification generation now evaluates first-pass context sufficiency before presenting clarification questions.

Human Interface behavior changed: no Human Interface semantic logic was added.

## Objective

Implement the G19-HI-05 audit recommendation:

Original Request

-> Context Assembly

-> Context Sufficiency Evaluation

-> Deterministic Slot Satisfaction

-> Remaining Missing Slots

-> Clarification Generation only if required

## Implementation Summary

Added `PLATFORM_CORE_CLARIFICATION_CONTEXT_SUFFICIENCY_EVALUATION_V1`.

The deterministic clarification planner now:

1. derives candidate missing slots through the existing `_clarification_missing_slots(...)` path;
2. evaluates those slots against the complete original request and assembled deterministic context;
3. records satisfied slots and unresolved requirements in a replay-visible artifact;
4. ranks only remaining missing slots;
5. generates clarification only when a slot remains unresolved.

The Human Conversation Experience now consumes `clarification_required_after_sufficiency` instead of treating the earlier intent-level `clarification_required` flag as final.

The returned development intent artifact is enriched with:

- `clarification_context_sufficiency_version`;
- `clarification_required_before_context_sufficiency`;
- `clarification_required_after_context_sufficiency`;
- `clarification_context_sufficiency_evaluation`;
- `candidate_missing_semantic_slots`;
- `remaining_missing_semantic_slots`;
- `satisfied_semantic_slots_from_context`;
- `clarification_suppressed_by_context_sufficiency`.

## Platform Core Ownership

The correction is entirely in `aigol/runtime/platform_core_project_services.py`.

No Human Interface heuristics were introduced.

`./aicli` continues to:

- submit text to Platform Core;
- render Platform Core conversation output;
- collect human approval or clarification input;
- delegate runtime entry after approval.

## Deterministic Reuse

The implementation reuses existing deterministic slot semantics:

- `_clarification_missing_slots(...)`;
- `_required_semantic_requirements(...)`;
- `_accepted_semantic_requirements(...)`;
- deterministic clarification planning;
- Human Conversation Experience projection;
- work-type preservation.

First-pass context sufficiency intentionally uses the stricter requirement set instead of the more permissive interactive reply predicate. A slot is satisfied from original request context only when all required semantic requirements for that slot are present.

Explicit human requests for clarification, such as "need clarification", remain clarification-first. This preserves the G19-HI-04 completion lifecycle path and prevents broad governance terms in an explicitly ambiguous prompt from being treated as sufficient context.

## Behavior Confirmed

An `AUDIT_ONLY` request that already states the architecture outcome:

`Human Interfaces require only minimal bindings to Generation 19 Platform Core services and can become nearly stateless presentation adapters while Platform Core owns all Platform semantics.`

now produces:

- `work_type: AUDIT_ONLY`;
- `clarification_required_before_context_sufficiency: true`;
- `clarification_required_after_context_sufficiency: false`;
- `clarification_required: false`;
- `satisfied_semantic_slots_from_context: ["architecture_outcome"]`;
- no clarification question;
- no pending approval;
- no runtime implementation.

An architecture request that names a subject but omits the outcome still produces:

- `clarification_required_after_context_sufficiency: true`;
- `selected_missing_slot: architecture_outcome`;
- `What outcome should the human interface architecture decision enable?`

## Regression Coverage

Added:

- `tests/test_g19_hi_06_first_pass_context_sufficiency.py`

Regression scenarios:

1. Original request satisfies `architecture_outcome` before clarification.
2. Insufficient architecture context still asks for `architecture_outcome`.
3. `AUDIT_ONLY` remains non-mutating and does not enter approval/runtime.
4. Human Interface authority remains false.
5. No LLM reasoning or probabilistic matching is used.

## Certification Readiness

Status:

`READY_FOR_TARGETED_G19_HI_06_CERTIFICATION`

Required certification evidence:

- focused G19-HI-06 regression tests pass: `tests/test_g19_hi_06_first_pass_context_sufficiency.py`;
- G15 deterministic clarification planner tests continue to pass: `tests/test_g15_hir_08_deterministic_clarification_planner.py`;
- G15 clarification satisfaction verification tests continue to pass: `tests/test_g15_hir_10_clarification_satisfaction_verification.py`;
- G19-HI-04 clarification completion lifecycle tests continue to pass: `tests/test_g19_hi_04_clarification_completion_lifecycle.py`;
- G19-HI-02 work-type preservation tests continue to pass: `tests/test_g19_hi_02_governed_work_type_preservation.py`;
- Human Conversation Experience tests continue to pass: `tests/test_g14_38_platform_core_human_conversation_experience_v1.py`;
- governance conformance remains unchanged except for known repository hook drift.

## Boundary Confirmation

G19-HI-06 preserves:

- Platform Core ownership of clarification necessity;
- Human Interface thin adapter architecture;
- deterministic and replay-visible semantics;
- work-type preservation from G19-HI-02;
- clarification completion lifecycle from G19-HI-04;
- fail-closed behavior when deterministic sufficiency is absent.

It does not:

- introduce Human Interface-specific heuristics;
- invoke provider or LLM reasoning;
- bypass Human Intent Resolution;
- bypass work-type runtime blocking;
- authorize or execute runtime work for audit-only requests.
