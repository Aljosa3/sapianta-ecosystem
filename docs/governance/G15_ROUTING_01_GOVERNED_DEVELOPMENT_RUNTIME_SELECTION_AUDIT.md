# G15-ROUTING-01 - Governed Development Runtime Selection Audit

Status: AUDIT COMPLETE

Milestone: G15-ROUTING-01

Scope: deterministic audit only. No production code, runtime behavior, routing behavior, Human Interface behavior, replay semantics, governance semantics, or Platform Core ownership was modified.

## 1. Knowledge Reuse Audit

Existing Platform Core capabilities reused:

- Human Intent Resolution and Development Intent Resolution in `aigol/runtime/platform_core_project_services.py`.
- Canonical Semantic Artifact generation in `aigol/runtime/conversational_cli_runtime.py` through `create_canonical_semantic_artifact_from_translation(...)`.
- UBTR semantic cognition orchestration in the conversational routing path.
- Conversational Routing in `aigol/runtime/conversational_cli_runtime.py`.
- Runtime Entry in `aigol/runtime/human_interface_runtime_entry_service.py`.
- Governed Development Runtime bridge in `aigol/cli/aigol_cli.py` through `propose_acli_governed_development_execution(...)`.
- Native development context routing, post-entry continuation, runtime dispatch, worker invocation, replay evidence, and runtime certification already certified by Generation 15 runtime reports.

No architectural duplication was introduced. The audit uses existing replay-visible routing artifacts and existing governance reports as evidence rather than defining a new runtime selector.

## 2. Architectural Review

Runtime selection is deterministic, but it is layered:

1. Platform Core Project Services prepare UHI project context and run Development Intent Resolution.
2. Canonical Human Interface Runtime Entry filters approved requests into `runtime_prompts` only when `runtime_binding_admissible` is true.
3. The certified conversational runtime records routing visibility, source routing, universal intake, CSA/UBTR routing, and workflow selection.
4. The selected workflow enters either a conversational/read-only/clarification path, a native development/context continuation path, or the governed development runtime bridge.

AiCLI remains a thin Human Interface. It captures composed text, renders Platform Core summaries or clarification questions, collects approval, and delegates to `run_human_interface_runtime_entry(...)`. It does not own runtime selection semantics.

## 3. Runtime Selection Analysis

Conversational Routing is selected or retained when the deterministic inputs do not authorize immediate governed runtime continuation. The relevant conditions are:

- Development Intent Resolution reports `summary_admissible` false or `runtime_binding_admissible` false.
- A clarification is required because the request is ambiguous, underspecified, or requires deterministic workspace state.
- The request is non-development, read-only, status/replay/audit oriented, proposal-only, or lifecycle-specific.
- The request has no certified workflow mapping and must fail closed instead of entering execution.
- The conversational router cannot produce decisive CSA-based routing and falls back to the default provider-assisted conversation workflow.
- A stateful continuation is active, such as pending approval, pending clarification, or pending post-entry continuation, and the active workflow must continue without rerouting.

Governed Development Runtime is selected when:

- Development Intent Resolution identifies a deterministic development request.
- The canonical runtime prompt is native-development admissible.
- `summary_admissible` and `runtime_binding_admissible` are true.
- Human approval has been collected by the Human Interface.
- Runtime Entry invokes the certified governed runner with the canonical runtime prompt.
- Conversational routing or stateful routing selects `GOVERNED_DEVELOPMENT_WORKFLOW` or the native development/context path that continues into PPP, authorization, worker lifecycle, result validation, replay certification, and workflow completion.

CSA participation is real but not exclusive. `route_conversational_cli_intent(...)` creates Translation, Canonical Semantic Artifact, UBTR cognition, and workflow-selection artifacts. CSA can deterministically select `GOVERNED_DEVELOPMENT_WORKFLOW` when its workflow identity, semantic identity, actions, confidence, and ambiguity fields are sufficient. If the CSA is not decisive, compatibility routing remains available and replay-visible.

Development Intent Resolution also exists and is invoked for UHI runtime entry. `prepare_unified_human_interface_project_context(...)` calls `resolve_development_intent(...)` unless an active clarification continuity state is being resolved. `run_human_interface_runtime_entry(...)` invokes project context preparation before entering the governed runner and only forwards canonical runtime prompts whose resolution is runtime-binding admissible.

## 4. Root Cause Analysis

There is no current production runtime blocker in this milestone.

The apparent ambiguity comes from naming and layering. Conversational Routing is both a certified workflow router and a compatibility/fallback entry layer for conversation-native operation. Governed Development Runtime is a downstream execution-capable workflow that is reached only after deterministic development intent, approval, runtime entry gating, routing, and continuation gates all permit it.

The current behavior is intentionally fail-closed:

- Generic governed execution intent without a certified workflow mapping fails closed.
- Ambiguous development requests remain clarification-bound.
- Non-admissible requests do not become runtime prompts.
- Conversational fallback does not bypass approval, authorization, worker dispatch, or replay certification.

## 5. Ownership Verification

Runtime selection semantics are Platform Core-owned.

- Development intent owner: Platform Core Project Services, specifically `resolve_development_intent(...)`.
- UHI runtime-entry gating owner: `run_human_interface_runtime_entry(...)`.
- CSA/UBTR workflow-routing owner: Conversational CLI Runtime, specifically `route_conversational_cli_intent(...)`.
- Governed Development Runtime bridge owner: certified conversation runtime orchestration in `aigol/cli/aigol_cli.py`.
- Human Interface owner: rendering and input capture only.

AiCLI does not authorize, execute, select providers, own replay, own workspace, own goal mapping, or own runtime selection.

## 6. Migration Readiness Assessment

Governed Development Runtime is ready to be the deterministic default for governed implementation requests after Platform Core determines:

- deterministic development intent,
- native runtime admissibility,
- no clarification requirement,
- human approval,
- runtime-entry admissibility,
- replay-visible routing and continuation gates.

Conversational Routing currently acts as both a certified router and a compatibility/fallback layer. That role is acceptable because it is replay-visible, deterministic, and fail-closed. A future explicit Runtime Selection artifact could improve operational readability, but this audit does not identify a missing production implementation required for certified runtime completion.

Implementation readiness verdict:

`NO_G15_ROUTING_01_PRODUCTION_IMPLEMENTATION_REQUIRED`

## 7. Validation Summary

Validation commands required:

- `python -m py_compile`
- `python -m pytest -q`
- `git diff --check`

Validation results:

- `python -m py_compile aigol/runtime/platform_core_project_services.py aigol/runtime/human_interface_runtime_entry_service.py aigol/runtime/conversational_cli_runtime.py aigol/runtime/conversation_native_development_intent_routing.py aigol/cli/aigol_cli.py aigol/cli/aicli.py` passed.
- `python -m pytest -q` passed: `5829 passed, 4 skipped in 141.54s`.
- `git diff --check` passed before and after validation-section update.

## 8. Boundary Confirmation

This milestone did not modify:

- production code,
- AiCLI,
- runtime behavior,
- routing behavior,
- governance semantics,
- replay semantics,
- approval semantics,
- worker ownership,
- Platform Core ownership.

Generation 14 ownership boundaries remain unchanged. Platform Core remains the sole owner of runtime selection semantics. Human Interfaces may render or submit Platform Core decisions but do not own those decisions.

## 9. Governance Report

G15-ROUTING-01 deterministically explains the runtime selection path:

- Conversational Routing is selected for non-admissible, clarification, read-only, proposal-only, lifecycle, compatibility, fallback, or stateful continuation cases.
- Governed Development Runtime is selected for deterministic governed implementation requests after approval and runtime-entry admissibility.
- Runtime selection is deterministic and replay-visible.
- Development Intent Resolution exists and participates in UHI runtime entry.
- CSA participates in workflow routing and is sufficient when semantic identity, workflow identity, action set, confidence, and ambiguity fields are decisive.
- A named standalone Runtime Selection stage is not required for current production completion, though it may be a future auditability improvement.
- Conversational Routing does act as a compatibility/fallback runtime, but it does not bypass governed execution controls.
- No Platform Core production implementation change is required by this audit.

Certification conclusion:

`G15_ROUTING_01_RUNTIME_SELECTION_AUDIT_COMPLETE`
