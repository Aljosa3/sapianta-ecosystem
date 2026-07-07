# G15-HIR-00 - Clarification Resolution Audit

Status: CERTIFICATION AUDIT
Date: 2026-07-07
Scope: Platform Core clarification resolution from Human Intent Resolution through replay-backed clarification continuity.

## Executive Verdict

The repository already contains a deterministic clarification completion mechanism in the certified conversational runtime.

The observed repeated clarification in `./aicli submit` is not caused by AiCLI taking ownership of semantics. It occurs because the UHI project-context path submits each clarification answer back through `prepare_unified_human_interface_project_context()` as a fresh development-intent message instead of binding the answer to the active replay-backed clarification state.

No production implementation change was made in this audit milestone.

Final classification:

PLATFORM_CORE_UHI_CLARIFICATION_CONTINUITY_STAGE_MISSING

## Knowledge Reuse Audit

Existing reusable implementation was found and retained:

- `aigol/runtime/clarification_lifecycle_resolution_runtime.py`
  - reconstructs active, resolved, and superseded clarification state from replay.
  - exposes `active_clarification_state()` as the canonical replay-derived active clarification lookup.
- `aigol/runtime/clarification_continuity_runtime.py`
  - detects active clarification, decides whether an operator reply binds to it, and records general clarification continuity.
  - binds Human Intent clarification replies deterministically when the active clarification originated from `HUMAN_INTENT_CLARIFICATION_INTAKE`.
- `aigol/runtime/human_intent_clarification_continuity_runtime.py`
  - binds a human clarification answer to the active HIRR clarification.
  - records response, target refinement, resolution, workflow selection, CSA comparison, and replay evidence.
- `aigol/cli/aigol_cli.py`
  - already uses the replay-backed continuity path in `run_interactive_conversation()`.
- `aigol/runtime/platform_core_project_services.py`
  - owns the UHI project-context response model used by AiCLI submit.
  - currently resolves each supplied message through `resolve_development_intent()` rather than the replay-backed clarification-continuity resolver.
- Existing regression coverage:
  - `tests/test_conversational_cli_runtime_v1.py`
  - `tests/test_clarification_continuity_runtime_v1.py`
  - `tests/test_human_intent_clarification_live_acli_session_certification_v1.py`

No duplicate clarification resolver was introduced.

## Clarification Resolution Analysis

There are two relevant Platform Core paths.

The certified conversational runtime path is stateful and replay-backed:

1. It detects active clarification through `detect_active_clarification()`.
2. It gates the next operator message with `should_bind_operator_reply_to_active_clarification()`.
3. It routes Human Intent clarification replies into `continue_human_intent_clarification_to_workflow()`.
4. It records clarification response, resolution, workflow selection, and replay evidence.

Implementation evidence:

- `clarification_lifecycle_resolution_runtime.py` lines 30-54 reconstruct lifecycle state and expose the active clarification.
- `clarification_continuity_runtime.py` lines 67-85 bind Human Intent clarification replies when the active clarification originated from `HUMAN_INTENT_CLARIFICATION_INTAKE`.
- `aigol_cli.py` lines 3404-3423 detect active clarification and reply binding before normal routing.
- `aigol_cli.py` lines 3752-3795 call `continue_human_intent_clarification_to_workflow()` for HIRR clarification replies.

The UHI project-context path is message-local:

1. `prepare_unified_human_interface_project_context()` loads prior workspace state.
2. It calls `resolve_development_intent(message=message, workspace_state=prior_state)`.
3. It builds a conversation response from that fresh resolution.
4. It writes a UHI project-context artifact.

Implementation evidence:

- `platform_core_project_services.py` lines 147-228 perform the UHI project-context preparation.
- `platform_core_project_services.py` lines 171-192 resolve development intent, knowledge reuse, and conversation response.
- `platform_core_project_services.py` lines 1021-1126 determine `clarification_required`, `summary_admissible`, and `runtime_binding_admissible` for the current message.
- `aicli.py` lines 391-406 submit clarification replies back through `_submit_composed_request()`, which uses the UHI project-context path.

Therefore the existing deterministic clarification resolver is present, but it is not the component currently used by AiCLI submit clarification replies.

## Clarification State Transition Map

Certified conversational runtime:

Human intent

-> HIRR clarification intake

-> replay records open clarification

-> next human message is checked against active clarification

-> reply is bound to the active clarification

-> clarification response CSA capture is attempted

-> workflow target is deterministically refined

-> clarification resolution artifact is recorded

-> workflow selection artifact is recorded

-> lifecycle marks the previous clarification resolved

-> Platform Core proceeds according to the selected workflow.

UHI project-context submit path:

Human intent

-> UHI project context

-> `clarification_required = true`

-> AiCLI stores pending clarification and waits

-> human answer

-> answer is submitted as a new project-context message

-> `resolve_development_intent()` evaluates that answer independently

-> Platform Core may request another clarification if the answer does not independently satisfy development-intent admissibility.

This explains why a detailed human answer can still lead to a repeated or similar clarification in `./aicli submit`.

## Deterministic Sufficiency Rules

For HIRR continuity, sufficiency is not LLM judgment. It is deterministic replay-backed selection.

The Human Intent clarification continuity runtime:

- rejects unsafe escalation signals such as bypassing approval or invoking workers.
- recognizes confirmation signals for bounded file-write proof actions.
- recognizes unresolved ambiguity signals and routes to proposal-only OCS.
- recognizes advisory or governed workflow signals.
- otherwise preserves the prior target with low confidence.

Implementation evidence:

- `human_intent_clarification_continuity_runtime.py` lines 72-142 bind the reply and persist continuity steps.
- `human_intent_clarification_continuity_runtime.py` lines 451-575 begin deterministic signal classification and fail closed on unsafe escalation.
- `human_intent_clarification_continuity_runtime.py` lines 688-719 translate the clarification response and create a Canonical Semantic Artifact capture.
- `human_intent_clarification_continuity_runtime.py` lines 722-748 reject CSA routing when execution was requested, provider or worker invocation appeared, or clarification remains required.

Regression evidence:

- `tests/test_conversational_cli_runtime_v1.py` lines 1077-1135 prove that a clarification response can bind, resolve clarification, resume workflow, preserve provider and worker non-invocation, and produce replay evidence.
- `tests/test_conversational_cli_runtime_v1.py` lines 1137-1188 prove unresolved ambiguity after clarification routes to proposal-only OCS with human confirmation still required.
- `tests/test_conversational_cli_runtime_v1.py` lines 1191-1207 prove unsafe clarification answers fail closed before OCS, provider, worker, authorization, or execution.
- `tests/test_clarification_continuity_runtime_v1.py` lines 111-135 prove general clarification replies resume without provider fallback.

## Canonical Semantic Artifact Conditions

Clarification answers can produce CSA lineage only through the continuity path.

HIRR continuity calls `translate_human_to_governance()` and then `create_canonical_semantic_artifact_from_translation()` for the clarification response. The CSA may influence routing only when deterministic parity is available and the semantic artifact does not itself require clarification.

The audited UHI project-context reply path does not call the HIRR continuity runtime. It evaluates the reply as a new development request. Therefore a repeated clarification in that path does not prove that CSA creation failed; it proves the reply was not evaluated through the replay-backed clarification completion stage.

## Root Cause Analysis

The root cause of repeated clarification in the observed AiCLI submit workflow is:

`./aicli submit` clarification replies are forwarded to Platform Core, but through the UHI project-context resolver rather than the certified replay-backed HIRR clarification-continuity resolver.

This creates a deterministic mismatch:

- Platform Core has already asked a clarification question.
- The human provides an answer.
- AiCLI remains thin and forwards the answer.
- The UHI project-context path evaluates that answer as a new message.
- The active clarification replay state is not consumed.
- The answer may not independently look like an admissible governed development request.
- Platform Core correctly asks for clarification again from that message-local perspective.

This is not an AiCLI semantic ownership defect. It is a missing Platform Core UHI clarification-continuity integration stage.

## Architectural Review

Generation 14 ownership boundaries remain preserved:

- Platform Core owns Human Intent Resolution.
- Platform Core owns clarification semantics.
- Platform Core owns replay-backed clarification lifecycle.
- Platform Core owns semantic sufficiency and workflow selection.
- Human Interfaces capture input, render output, and forward replies.
- Provider Platform remains unchanged.
- Worker Platform remains unchanged.
- Replay remains the source of clarification lifecycle evidence.

The smallest architecturally correct future correction is not to teach AiCLI how to evaluate clarification answers. The correction belongs inside Platform Core project services: before treating a UHI follow-up message as a fresh development request, Platform Core should inspect active clarification replay state and route eligible replies through the existing clarification-continuity runtimes.

## Implementation Summary

No production code was modified.

No tests were modified.

This audit intentionally did not implement the future Platform Core UHI clarification-continuity binding stage because the existing certified primitives need to be integrated without duplicating conversation semantics or moving state into AiCLI.

Recommended follow-up milestone:

G15-HIR-01 - Platform Core UHI Clarification Continuity Binding

Required future behavior:

- UHI project services inspect replay for active clarification state.
- If an active clarification exists, Platform Core evaluates the human reply through existing continuity runtimes.
- Only if no active clarification exists, or the reply is deterministically a new request, should UHI project services enter fresh development-intent resolution.
- AiCLI remains unchanged except for consuming the improved Platform Core response.

## Validation Summary

Validation commands executed:

- `python -m py_compile aigol/cli/aicli.py aigol/cli/aigol_cli.py aigol/runtime/platform_core_project_services.py aigol/runtime/clarification_continuity_runtime.py aigol/runtime/clarification_lifecycle_resolution_runtime.py aigol/runtime/human_intent_clarification_continuity_runtime.py`
- `python -m pytest -q`
- `git diff --check`

Validation result:

- `python -m py_compile ...` passed.
- `python -m pytest -q` passed: `5817 passed, 4 skipped`.
- `git diff --check` passed.

## Files Modified

- `docs/governance/G15_HIR_00_CLARIFICATION_RESOLUTION_AUDIT.md`

## Boundary Confirmation

This audit preserves certified ownership:

- AiCLI remains a thin Human Interface.
- No Platform Core responsibility moved into AiCLI.
- No governance behavior changed.
- No provider behavior changed.
- No worker behavior changed.
- Replay semantics remain read-only for audit and authoritative for clarification lifecycle.
- No speculative runtime transition was added.

## Final Determination

The repository has deterministic clarification resolution in the conversational runtime.

The observed repeated clarification in `./aicli submit` identifies a missing Platform Core UHI integration stage, not missing primitive clarification-resolution capability.

The project should proceed to a focused implementation milestone that wires UHI project services to the existing replay-backed clarification continuity layer.
