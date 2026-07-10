# G17-HI-02B - Platform Core Conversation Boundary Specification

Status: SPECIFICATION CERTIFIED

Date: 2026-07-09

Final verdict: SPECIFICATION_CERTIFIED

## Conversation Boundary

The Platform Core Conversation Boundary is the canonical contract between Platform Core and every Human Interface.

It defines how Platform Core exposes conversation state, admissible events, next actions, projection data, clarification state, approval state, continuation state, completion state, replay references, and session ownership.

Human Interfaces consume this boundary. They do not implement conversation logic.

The boundary is reusable unchanged by:

- `./aicli`
- AiGOL Next
- Web
- Mobile
- Voice
- REST
- Desktop
- MCP
- future Human Interfaces

The boundary is not a new cognition engine, not a new governance layer, not a new replay service, and not a new runtime orchestration engine. It is a canonical Platform Core exposure layer over already certified primitives.

## State Model

Platform Core owns the conversation state model.

Canonical conversation states:

| State | Meaning | Owner |
| --- | --- | --- |
| `CONVERSATION_IDLE` | No active request is pending. | Platform Core |
| `COMPOSING_INPUT` | Human Interface is collecting raw user input before submission. | Human Interface |
| `REQUEST_SUBMITTED` | A complete human request has entered Platform Core. | Platform Core |
| `INTENT_RESOLUTION_RUNNING` | Platform Core is resolving Human Intent and project context. | Platform Core |
| `CLARIFICATION_REQUIRED` | Platform Core requires additional human information before continuing. | Platform Core |
| `CLARIFICATION_AWAITING_REPLY` | A clarification question exists and the next expected input is a human reply. | Platform Core |
| `CLARIFICATION_REPLY_SUBMITTED` | A reply has entered Platform Core for binding and satisfaction verification. | Platform Core |
| `APPROVAL_REQUIRED` | Platform Core has produced an approval-ready summary or approval boundary. | Platform Core |
| `APPROVAL_AWAITING_HUMAN` | The next expected input is approval, rejection, or cancellation. | Platform Core |
| `RUNTIME_CONTINUATION_READY` | A governed runtime continuation is admissible. | Platform Core |
| `RUNTIME_RUNNING` | Platform Core runtime execution is active. | Platform Core |
| `RESULT_DELIVERED` | A result was projected to the Human Interface. | Platform Core |
| `CONVERSATION_COMPLETED` | The current conversation lifecycle reached a terminal completion state. | Platform Core |
| `CONVERSATION_CANCELED` | The current conversation lifecycle was canceled by human action. | Platform Core |
| `CONVERSATION_FAILED_CLOSED` | Platform Core closed the lifecycle due to invalid or unsafe state. | Platform Core |

`COMPOSING_INPUT` is interface-owned because the request has not yet entered Platform Core. Once submitted, the conversation state is Platform Core-owned.

Human Interfaces may maintain ephemeral input buffers, but they must not derive or mutate Platform Core conversation state from those buffers.

## Event Model

Conversation events are the only admissible inputs to the Platform Core Conversation Boundary.

Canonical events:

| Event | Meaning | Payload Source | Owner |
| --- | --- | --- | --- |
| `HUMAN_REQUEST_SUBMITTED` | Complete human request submitted. | Human Interface transport | Platform Core handles |
| `CLARIFICATION_REPLY_SUBMITTED` | Complete clarification reply submitted. | Human Interface transport | Platform Core handles |
| `HUMAN_APPROVAL_SUBMITTED` | Human approved a pending Platform Core approval request. | Human Interface transport | Platform Core handles |
| `HUMAN_REJECTION_SUBMITTED` | Human rejected a pending Platform Core approval request. | Human Interface transport | Platform Core handles |
| `HUMAN_CANCEL_SUBMITTED` | Human canceled a pending conversation boundary state. | Human Interface transport | Platform Core handles |
| `HUMAN_EXIT_REQUESTED` | Human asked the interface to close. | Human Interface transport | Platform Core determines session effect after submission boundary |
| `INPUT_EOF_OBSERVED` | Input stream ended. | Human Interface transport | Platform Core determines pending state effect after submission boundary |
| `INPUT_INTERRUPT_OBSERVED` | Human interrupted input capture. | Human Interface transport | Platform Core determines pending state effect after submission boundary |
| `RUNTIME_RESULT_RETURNED` | Existing Platform Core runtime returned result evidence. | Platform Core Runtime | Platform Core handles |
| `REPLAY_STATE_RESTORED` | Prior replay-backed conversation state was restored. | Platform Core replay | Platform Core handles |

Human Interfaces may map local gestures or commands to events. They must not decide the semantic effect of the event after a Platform Core conversation state exists.

Examples:

- CLI `/send` maps to `HUMAN_REQUEST_SUBMITTED` or `CLARIFICATION_REPLY_SUBMITTED`, depending on Platform Core state.
- CLI `/approve` maps to `HUMAN_APPROVAL_SUBMITTED` only if Platform Core projection says approval is expected.
- REST `POST /conversation/events` can submit the same canonical event names.
- Voice confirmation can submit `HUMAN_APPROVAL_SUBMITTED` without creating a voice-specific approval rule.

## Action Model

Conversation actions are the admissible next operations returned by Platform Core.

Canonical actions:

| Action | Meaning | Human Interface Obligation |
| --- | --- | --- |
| `COLLECT_REQUEST` | Collect a new human request. | Render an input affordance. |
| `COLLECT_CLARIFICATION_REPLY` | Collect an answer to Platform Core clarification questions. | Render questions and collect reply. |
| `COLLECT_APPROVAL_DECISION` | Collect approval, rejection, or cancellation. | Render approval boundary and collect decision. |
| `DISPLAY_NON_DEVELOPMENT_RESPONSE` | Show a fail-closed or non-development response. | Render provided projection. |
| `DISPLAY_RUNTIME_PROGRESS` | Show runtime progress evidence. | Render progress projection. |
| `DISPLAY_RUNTIME_RESULT` | Show governed runtime result evidence. | Render result projection. |
| `DISPLAY_COMPLETION` | Show terminal conversation completion. | Render completion projection. |
| `WAIT_FOR_HUMAN` | The lifecycle is paused until human input is supplied. | Keep transport open if available. |
| `CLOSE_INTERFACE_SESSION` | Platform Core has reached a terminal state that permits session close. | Close or return terminal response. |

Actions are advisory for rendering and transport. They are authoritative for workflow progression.

Human Interfaces must not invent additional workflow actions such as `AUTO_APPROVE`, `SELECT_PROVIDER`, `RESOLVE_CLARIFICATION`, `RUN_WORKER`, or `CERTIFY_REPLAY`.

## Projection Model

The Conversation Boundary returns a presentation-neutral projection. The projection is owned by Platform Core and rendered by the Human Interface.

Canonical projection fields:

```text
conversation_projection
  projection_version
  session_id
  conversation_id
  turn_id
  state
  expected_event
  admissible_events
  next_action
  user_headline
  user_explanation
  question_set
  approval_summary
  runtime_progress
  runtime_result
  completion_summary
  fail_closed_response
  replay_reference
  replay_hash
  ownership
  boundary_flags
```

Projection rules:

- Platform Core decides `state`, `expected_event`, `admissible_events`, and `next_action`.
- Platform Core provides human-facing content such as `user_headline`, `user_explanation`, clarification questions, approval summary, runtime progress, and completion summary.
- Human Interfaces choose visual layout, voice delivery, terminal text, REST response shape, or mobile rendering.
- Human Interfaces must not change `state`, `expected_event`, `admissible_events`, replay references, or governance meaning.

Projection is the replacement for interface-local workflow interpretation.

## Ownership Matrix

| Responsibility | Platform Core | Human Interface |
| --- | --- | --- |
| Conversation state | Owns | Renders only |
| Conversation transitions | Owns | Submits events only |
| Human Intent Resolution | Owns | None |
| Knowledge Reuse | Owns | None |
| Clarification generation | Owns | Renders questions |
| Clarification satisfaction | Owns | Collects reply |
| Approval boundary | Owns | Renders approval prompt |
| Approval decision interpretation | Owns | Transports human decision |
| Runtime continuation | Owns | None |
| Governance | Owns | None |
| Replay evidence | Owns | Displays references |
| Certification | Owns | Displays result |
| Provider selection | Owns through existing Platform Core/provider services | None |
| Worker execution | Owns through existing runtime/worker services | None |
| Input collection | Receives completed events | Owns |
| Rendering | Supplies projection data | Owns presentation |
| Transport | Receives events | Owns |

## Human Interface Contract

Every Human Interface must implement only this contract:

1. Render the current Platform Core projection.
2. Collect user input appropriate to `next_action`.
3. Convert user interaction into a canonical event.
4. Submit the event to the Platform Core Conversation Boundary.
5. Render the next projection.

Human Interfaces must not:

- keep authoritative pending clarification state
- keep authoritative pending approval state
- decide whether clarification is satisfied
- decide whether approval is required
- decide runtime continuation
- select providers
- invoke workers
- create replay evidence
- certify replay
- mutate governance
- declare conversation completion except when Platform Core projection returns `CLOSE_INTERFACE_SESSION`

Allowed Human Interface local state:

- text input buffer
- transport connection state
- rendering preference
- terminal prompt history
- local UI focus/scroll state
- transient network retry state

Disallowed Human Interface local state:

- canonical workflow state
- semantic intent state
- clarification lifecycle state
- approval lifecycle state
- runtime continuation state
- governance state
- replay authority state

## Runtime Continuation Contract

Platform Core returns runtime continuation only through explicit boundary fields.

Canonical continuation fields:

```text
runtime_continuation
  continuation_status
  continuation_allowed
  continuation_reason
  continuation_runtime
  runtime_binding_admissible
  canonical_runtime_prompt
  required_human_event
  replay_reference
  replay_hash
```

Rules:

- `continuation_allowed` is Platform Core-owned.
- `canonical_runtime_prompt` is Platform Core-owned.
- Human Interfaces may display the prompt summary but must not derive a runtime prompt.
- Runtime Entry remains the canonical execution boundary.
- If continuation is blocked, Human Interfaces must render the blocking explanation and collect the expected event.

Continuation states:

- `CONTINUATION_NOT_REQUIRED`
- `CONTINUATION_BLOCKED`
- `CONTINUATION_REQUIRES_CLARIFICATION`
- `CONTINUATION_REQUIRES_APPROVAL`
- `CONTINUATION_READY`
- `CONTINUATION_RUNNING`
- `CONTINUATION_COMPLETED`
- `CONTINUATION_FAILED_CLOSED`

## Clarification Contract

Platform Core owns the clarification lifecycle.

Canonical clarification fields:

```text
clarification
  clarification_status
  clarification_required
  clarification_questions
  clarification_question_bindings
  active_clarification_reference
  active_clarification_hash
  clarification_reply_bound
  clarification_satisfied
  pending_semantic_slots
  clarification_continuity_replay_reference
```

Clarification statuses:

- `NO_CLARIFICATION`
- `CLARIFICATION_REQUIRED`
- `CLARIFICATION_AWAITING_REPLY`
- `CLARIFICATION_REPLY_RECEIVED`
- `CLARIFICATION_RESOLVED`
- `CLARIFICATION_STILL_REQUIRED`
- `CLARIFICATION_SUPERSEDED`
- `CLARIFICATION_FAILED_CLOSED`

Rules:

- Platform Core generates questions.
- Platform Core binds replies to active clarification.
- Platform Core verifies satisfaction.
- Platform Core records continuity replay.
- Human Interfaces only render questions and collect replies.
- A Human Interface may cancel input capture, but Platform Core owns the resulting conversation state after cancellation is submitted.

## Approval Contract

Platform Core owns the approval lifecycle.

Canonical approval fields:

```text
approval
  approval_status
  approval_required
  approval_request
  approval_summary
  approval_scope
  risk_class
  requested_action
  human_decision_required
  approval_replay_reference
  approval_hash
```

Approval statuses:

- `NO_APPROVAL_REQUIRED`
- `PENDING_HUMAN_APPROVAL`
- `APPROVED`
- `REJECTED`
- `CANCELED`
- `APPROVAL_FAILED_CLOSED`

Rules:

- Platform Core decides whether approval is required.
- Platform Core creates approval request artifacts.
- Human Interfaces collect approval, rejection, or cancellation.
- Human Interfaces must not treat a UI button click as governance approval until Platform Core accepts the canonical event and updates the boundary state.
- Approval does not imply provider invocation or worker execution unless Runtime Entry and downstream governance authorize it.

## Completion Lifecycle

Platform Core owns completion lifecycle.

Canonical completion fields:

```text
completion
  completion_status
  completion_reason
  result_delivered
  runtime_status
  runtime_result
  replay_certification_status
  session_close_allowed
  completion_replay_reference
  completion_hash
```

Completion statuses:

- `NOT_COMPLETED`
- `RESULT_DELIVERED`
- `RUNTIME_COMPLETED`
- `CONVERSATION_CANCELED`
- `AWAITING_HUMAN_INPUT`
- `FAILED_CLOSED`

Rules:

- `AWAITING_HUMAN_INPUT` is not terminal unless transport mode is one-shot and Platform Core projection explicitly permits return to caller.
- Clarification-required state is not completion.
- Approval-required state is not completion.
- `session_close_allowed` is Platform Core-owned.
- Human Interfaces may close local transport only when Platform Core projection permits closure or when the transport itself is interrupted before a Platform Core event boundary.

## Replay Implications

Every Platform Core conversation transition must be replay-visible.

Replay requirements:

- Every accepted event receives a replay reference.
- Every state transition receives a replay hash or links to a replay-backed artifact.
- Clarification state must link to active clarification evidence.
- Approval state must link to approval request/result evidence.
- Runtime continuation must link to Runtime Entry and downstream runtime evidence.
- Completion must link to turn completion, result delivery, or workspace state evidence.
- Interface rendering must not be required to reconstruct Platform Core state.

Human Interface telemetry may be recorded separately as presentation evidence, but it is not authoritative conversation replay.

## Session Ownership

Platform Core owns the session after a complete event enters the Conversation Boundary.

Human Interfaces own local transport sessions only.

Session ownership rules:

- Platform Core owns canonical `session_id`, `conversation_id`, `turn_id`, replay references, pending state, continuation state, and completion state.
- Human Interfaces may own socket IDs, terminal process state, browser tabs, mobile navigation state, REST request IDs, and voice stream state.
- A Human Interface local session ending must not imply Platform Core conversation completion unless Platform Core accepted a terminal event or projected `session_close_allowed: true`.
- Platform Core must be able to reconstruct conversation state from replay without requiring interface-local state.

## Canonical Boundary Shape

A Platform Core Conversation Boundary response SHOULD conform to this conceptual shape:

```text
platform_core_conversation_boundary
  boundary_version
  session
    session_id
    conversation_id
    turn_id
    session_owner: PLATFORM_CORE
  state
    conversation_state
    lifecycle_status
    terminal
    session_close_allowed
  projection
    next_action
    expected_event
    admissible_events
    user_headline
    user_explanation
    render_payload
  clarification
    ...
  approval
    ...
  continuation
    ...
  completion
    ...
  replay
    replay_reference
    replay_hash
    evidence_links
  ownership
    platform_core_owns_conversation: true
    human_interface_owns_rendering: true
    human_interface_owns_transport: true
    human_interface_owns_input_collection: true
    human_interface_owns_workflow: false
    human_interface_owns_governance: false
    human_interface_owns_replay: false
```

This shape is intentionally presentation-neutral.

## Architectural Findings

1. G17-HI-02A found that existing Platform Core primitives are sufficient foundation for this boundary.

2. The missing architectural artifact is a canonical boundary specification and, later, a reusable implementation point that all Human Interfaces can consume.

3. The boundary must reuse existing Platform Core services rather than duplicate them.

4. `./aicli` should eventually consume this boundary instead of owning pending summary, pending clarification, session status, and next-action interpretation locally.

5. The boundary preserves thin-interface architecture by letting each interface render differently without owning conversation logic.

6. The boundary prevents accidental migration of workflow, clarification, approval, continuation, governance, replay, and certification responsibility into Human Interfaces.

## Final Verdict

SPECIFICATION_CERTIFIED

The Platform Core Conversation Boundary is certified as the canonical specification for exposing conversation lifecycle state and actions to Human Interfaces.

The specification preserves the constitutional ownership model:

- Platform Core owns conversation state, transitions, clarification, approval, continuation, workflow lifecycle, replay, and certification.
- Human Interfaces own rendering, transport, and user input collection only.

Implementation is not performed by this milestone.
