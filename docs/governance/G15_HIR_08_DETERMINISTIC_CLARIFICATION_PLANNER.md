# G15-HIR-08 - Deterministic Clarification Planner

Status: IMPLEMENTED

Date: 2026-07-08

Milestone: G15-HIR-08

## Knowledge Reuse Audit

This milestone reused existing Platform Core evidence and did not introduce an alternate clarification authority.

Reused capabilities:

- Human Intent Resolution in `platform_core_project_services.py`
- Replay-backed UHI clarification continuity
- Clarification resolution state management
- Project workspace state replay
- Project guidance and knowledge reuse evidence
- Candidate capability discovery
- Canonical governed development summary preparation
- Platform Capability Certification Registry
- Governance evidence references and certified artifacts
- Runtime evidence recorded in workspace implementation history

No LLM reasoning, probabilistic routing, Human Interface semantics, or alternate replay path was introduced.

## Architectural Review

Clarification Planning is implemented inside Platform Core project services because that component already owns:

- UHI project context preparation;
- deterministic development intent resolution;
- replay-backed clarification state;
- human conversation experience artifacts.

AiCLI remains a renderer and input collector. It does not select clarification questions, rank uncertainty, own clarification semantics, or mutate planner state.

## Clarification Planning Review

The planner emits a replay-visible artifact:

`PLATFORM_CORE_DETERMINISTIC_CLARIFICATION_PLAN_ARTIFACT_V1`

The artifact records:

- deterministic input sequence;
- workspace and replay context availability;
- certification registry availability;
- candidate governed goals;
- missing semantic slots;
- ranked uncertainty;
- selected missing slot;
- exactly one selected clarification question;
- authority and boundary flags.

The planner selects one question only when summary creation is not yet deterministic. If the request is already summary-admissible, the planner records no missing slot and no question.

## Deterministic Clarification Analysis

The planner ranks missing semantic slots from existing evidence:

- continuation reference;
- capability target choice;
- capability target;
- desired outcome;
- architecture outcome or subject;
- reuse delta or reuse goal;
- implementation specificity;
- active objective delta.

The selected question targets the highest-value remaining semantic gap. Generic multi-question templates are no longer used by UHI project services for planned clarification.

Examples of improved deterministic behavior:

- Vague opener `I have an idea.` now produces one target-capability question instead of two generic questions.
- Resolved clarification no longer carries a latent planner question.
- Existing workspace context can suppress clarification for continuation requests.
- Architecture questions target the missing ownership/outcome slot rather than asking broad generic questions.

## Implementation Summary

Implemented:

- `PLATFORM_CORE_DETERMINISTIC_CLARIFICATION_PLANNER_VERSION`
- `deterministic_clarification_plan`
- missing-slot ranking helpers
- one-question planner output
- conversation artifact planner evidence fields
- UHI project services wiring from workspace replay into the planner

The implementation is deterministic, replay-visible, and scoped to Platform Core project services.

## Validation Summary

Required validation:

- `python -m py_compile`
- `python -m pytest -q`
- `git diff --check`

Focused regression:

- `python -m pytest tests/test_g15_hir_08_deterministic_clarification_planner.py -q`

## Regression Test Summary

Added:

- `tests/test_g15_hir_08_deterministic_clarification_planner.py`

Coverage demonstrates:

- existing context suppresses unnecessary clarification;
- previously answered clarification is not repeated;
- only one clarification is generated;
- the clarification targets the smallest remaining semantic gap;
- vague-opener clarification count decreases;
- AiCLI remains non-authoritative.

## Files Modified

- `aigol/runtime/platform_core_project_services.py`
- `tests/test_g15_hir_08_deterministic_clarification_planner.py`
- `docs/governance/G15_HIR_08_DETERMINISTIC_CLARIFICATION_PLANNER.md`

## Boundary Confirmation

Generation 14 ownership boundaries remain unchanged.

- Platform Core owns clarification planning and clarification semantics.
- AiCLI remains a thin Human Interface.
- Governance, replay, CSA, runtime, and certification semantics are unchanged.
- The planner never bypasses clarification when deterministic uncertainty remains.
- The planner never guesses user intent or invokes provider reasoning.
- Replay-visible planner evidence is recorded inside the existing conversation artifact.

## Governance Report

G15-HIR-08 replaces generic UHI clarification templates with deterministic clarification planning. Platform Core now evaluates existing project, replay, governance, certification, conversation, and candidate-goal evidence before asking the smallest useful clarification question.

The result is a more natural governed development conversation while preserving fail-closed behavior, replay evidence, Human Intent Resolution, governed runtime continuation, replay certification, and all Generation 14 ownership boundaries.
