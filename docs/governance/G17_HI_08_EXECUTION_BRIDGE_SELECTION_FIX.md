# G17-HI-08 Execution Bridge Selection Fix

Status: implemented.

Final verdict: `EXECUTION_BRIDGE_SELECTION_IMPLEMENTED`.

## Executive Summary

Approved canonical Human Interface runtime-entry prompts now select the existing Governed Development Execution Bridge before generic conversational routing.

The implementation preserves Human Interface thin-adapter behavior. `./aicli` and AiGOL Next still collect human input and approval, then delegate to `run_human_interface_runtime_entry(...)`. Platform Core runtime remains responsible for workflow selection, bridge continuation, worker lifecycle, and replay-backed completion.

## Root Cause Reference

G17-HI-06 concluded that approved Human Interface runtime entry reached `run_human_interface_runtime_entry(...)` and `run_interactive_conversation(...)`, but did not invoke the existing governed runtime path.

G17-HI-07 narrowed the cause to an execution bridge selection defect. The approved prompt entered native conversational routing, reached provider resolution, and failed closed before the existing governed-development bridge could be selected.

## Implementation Summary

The fix is scoped to `aigol/cli/aigol_cli.py`.

Implemented changes:

- Added a canonical Human Interface bridge selector for `operator_context="CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY"` with `auto_continue=True`.
- Added deterministic synthetic routing evidence for canonical Human Interface governed bridge selection.
- Routed approved runtime-entry native development prompts to `CONVERSATIONAL_GOVERNED_DEVELOPMENT_WORKFLOW` before generic conversational routing.
- Preserved existing bridge proposal and continuation calls.
- Added bridge turn-summary references so runtime-entry status continues to expose execution summary and human confirmation evidence.
- Added a regression test proving canonical runtime entry selects the governed bridge before native conversational routing.

No new execution concept was introduced.

## Execution Path Before

Before this fix:

1. Human approved a governed implementation summary.
2. `./aicli` or AiGOL Next delegated to `run_human_interface_runtime_entry(...)`.
3. Runtime entry invoked `run_interactive_conversation(...)`.
4. The approved runtime prompt entered generic conversational routing.
5. The selected path was native development conversation.
6. Native development continuation reached provider routing.
7. Provider availability failures stopped the turn before governed-development bridge execution.

Observed terminal status was partial binding.

## Execution Path After

After this fix:

1. Human approves a governed implementation summary.
2. Human Interface delegates to `run_human_interface_runtime_entry(...)`.
3. Runtime entry invokes `run_interactive_conversation(...)` with canonical Human Interface operator context and `auto_continue=True`.
4. The canonical Human Interface bridge selector activates for native development runtime prompts.
5. Synthetic routing evidence records `GOVERNED_DEVELOPMENT_WORKFLOW` selection without invoking generic native conversational routing.
6. Existing `propose_acli_governed_development_execution(...)` creates the governed bridge proposal.
7. Existing `_continue_governed_development_bridge_to_certified_runtime(...)` continues through the governed development pipeline.
8. Existing worker lifecycle and replay certification fields determine bound runtime status.

## Reused Platform Core Capabilities

The implementation reuses:

- `run_human_interface_runtime_entry(...)`
- `run_interactive_conversation(...)`
- `propose_acli_governed_development_execution(...)`
- `_continue_governed_development_bridge_to_certified_runtime(...)`
- existing post-context PPP continuation
- existing worker request, assignment, dispatch, invocation, result validation, and replay certification
- existing replay hashing and immutable evidence semantics
- existing Human Interface approval and clarification lifecycle

## Validation Results

Focused validation:

```text
python -m pytest tests/test_g14_30_canonical_human_interface_runtime_entry_service_v1.py
4 passed
```

Regression cluster validation:

```text
python -m pytest tests/test_g14_03_aigol_next_runtime_binding_v1.py tests/test_g14_04_conversational_development_workflow_v1.py tests/test_g14_05_persistent_development_workspace_v1.py tests/test_g14_06_project_guidance_assistant_v1.py tests/test_g14_07_goal_oriented_development_experience_v1.py tests/test_g14_19_development_intent_resolution_unification_v1.py tests/test_g15_runtime_06_governed_development_runtime_continuation.py tests/test_g14_30_canonical_human_interface_runtime_entry_service_v1.py
19 passed
```

Full validation:

```text
python -m pytest tests/
5889 passed, 1 skipped
```

## Architectural Impact Assessment

Platform Core ownership is preserved.

Replay ownership is preserved.

Governance ownership is preserved.

Human Interface remains a thin projection layer.

The fix does not redesign Runtime, Governance, Replay, PCCL, or Human Interface architecture. It only selects an already-existing bridge path earlier for approved canonical Human Interface runtime-entry prompts.

## Final Verdict

`EXECUTION_BRIDGE_SELECTION_IMPLEMENTED`
