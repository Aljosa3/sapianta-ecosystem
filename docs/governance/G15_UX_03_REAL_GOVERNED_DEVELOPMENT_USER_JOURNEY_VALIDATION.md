# G15-UX-03 - Real Governed Development User Journey Validation

Status: VERIFIED

Date: 2026-07-08

Milestone: G15-UX-03

## Knowledge Reuse Audit

This verification reused the certified Generation 15 governed development path without redesigning Platform Core or AiCLI.

Reused capabilities:

- Reference Unified Human Interface: `aicli`
- Platform Core project services and Human Intent Resolution
- Replay-backed clarification continuity
- Clarification resolution state management
- Governed implementation summary generation
- Human approval handoff
- Canonical Human Interface runtime entry
- Governed Development Execution Bridge
- Certified runtime continuation
- Worker invocation and external worker adapter boundary
- Result validation and replay certification
- Governance evidence and runtime replay evidence

No new Platform Core ownership, AiCLI ownership, routing semantics, replay semantics, approval semantics, or governance semantics were introduced.

## End-to-End User Journey Verification

The verified journey used AiCLI submit mode with natural human input:

1. Human starts with a natural governed-development question:
   `Should this human interface clarification behavior belong in Platform Core architecture?`
2. Platform Core asks a clarification once.
3. Human answers naturally:
   `Change clarification state management so answered questions are recorded as reusable Platform Core behavior.`
4. Human submits the clarification with `/send`.
5. Platform Core produces a governed implementation summary.
6. Human approves with `/approve`.
7. AiCLI delegates to canonical Platform Core runtime entry.
8. Platform Core reaches the Governed Development Execution Bridge.
9. The certified runtime continuation reaches worker execution packaging.
10. Replay certification completes.

Observed deterministic evidence:

- session status: `REFERENCE_UHI_SUBMIT_CONVERSATION_COMPLETED`
- exit reason: `RUNTIME_COMPLETED`
- submitted request count: `2`
- clarification question count: `1`
- clarification render count: `1`
- approval count: `1`
- runtime entered: `true`
- runtime status: `REFERENCE_UHI_RUNTIME_BOUND`
- runtime response source: `ACLI_GOVERNED_DEVELOPMENT_EXECUTION_BRIDGE`
- runtime response status: `GOVERNED_DEVELOPMENT_BRIDGE_CERTIFIED_RUNTIME_COMPLETED`
- worker execution reached: `true`
- external task package reached: `true`
- replay certification reached: `true`
- replay certification status: `REPLAY_CERTIFICATION_COMPLETED`
- auto-continue stop reason: `WORKFLOW_COMPLETE`
- manual transfer required: `false`
- AiCLI authorizes: `false`
- AiCLI executes: `false`
- AiCLI owns replay: `false`

## UX Assessment

The successful path is usable as a governed development journey.

Strengths:

- The user can start naturally without naming internal runtime stages.
- Clarification is rendered as a single user-facing prompt.
- `/send` is sufficient to submit a clarification answer.
- The answered clarification is consumed and not reopened on the success path.
- The approval prompt is explicit and visible.
- Runtime continuation after `/approve` is automatic through Platform Core.
- Completion is replay-certified and does not require manual transfer.
- AiCLI remains understandable as an interface: it renders, accepts commands, and delegates.

Conversation quality:

- Clarification is understandable, but it is still governance-shaped rather than fully conversational.
- The approval summary provides enough operator context to approve or cancel.
- Runtime result output confirms key evidence fields, including worker execution and replay certification.

Workflow continuity:

- The verified journey moved from natural request to clarification, summary, approval, runtime entry, worker execution, and replay certification without architectural intervention.
- Platform Core preserved pending clarification and consumed it after `/send`.
- Runtime continuation did not stop at the Governed Development Execution Bridge.

## Remaining Friction Report

One exploratory run used the opener:

`I have an idea.`

Observed result:

- Platform Core asked clarification.
- The human provided a multi-line governed-development answer.
- Platform Core asked a second clarification instead of producing an approval summary.
- The session stopped awaiting further human input.

Assessment:

- This is UX friction, not an architectural blocker.
- Very vague openers can require more than one clarification turn.
- A user can still complete the workflow by providing a more directly scoped governed-development clarification answer.
- The behavior remains fail-closed and does not move responsibility into AiCLI.

Recommended future UX refinement:

- Improve first clarification wording for highly vague openers so the user is nudged toward the exact information needed for summary admissibility.
- Keep the refinement inside Platform Core Human Intent Resolution and clarification wording, not AiCLI.

## Validation Summary

Validation performed:

- Deterministic scripted AiCLI user journey with clarification, `/send`, `/approve`, certified runtime continuation, worker execution, and replay certification.
- Focused regression reuse:
  - `tests/test_g15_hir_07_clarification_resolution_state_management.py`
  - `tests/test_g15_runtime_06_governed_development_runtime_continuation.py`
- `git diff --check`

The verification run used deterministic fake provider and external worker adapters to avoid live-provider dependency while preserving the existing provider and worker adapter boundaries.

## Governance Report

G15-UX-03 verifies that a human can complete an entire governed development workflow through AiCLI using natural conversation and explicit approval.

Generation 14 ownership boundaries remain unchanged:

- AiCLI remains a thin Human Interface.
- Platform Core owns Human Intent Resolution, clarification semantics, runtime selection, runtime continuation, worker invocation, replay, and replay certification.
- Human approval remains explicit.
- Replay certification remains the completion evidence.
- Remaining UX friction is wording and guidance quality, not a missing runtime or ownership change.

Conclusion:

The complete governed development user journey is operationally valid. The success path reaches replay-certified completion, and the remaining friction is bounded to highly vague initial requests that may need additional clarification.
