# FINALIZE_LOCAL_GOVERNED_TRANSPORT_RUNTIME_ATTACHMENT_V1

## Status

Frozen and certified.

This milestone finalizes the Browser Companion attachment layer for
`LOCAL_GOVERNED_TRANSPORT_RUNTIME_V1`.

## References

- `.github/governance/finalize/FINALIZE_LOCAL_GOVERNED_TRANSPORT_RUNTIME_V1.md`
- `.github/governance/specs/LOCAL_GOVERNED_TRANSPORT_RUNTIME_CONTRACT_V1.md`
- `.github/governance/plans/LOCAL_GOVERNED_TRANSPORT_RUNTIME_IMPLEMENTATION_PLAN_V1.md`
- `agol_bridge/transport/local_governed_transport.py`
- `browser_companion/sidepanel.html`
- `browser_companion/sidepanel.js`
- `tests/test_local_governed_transport_runtime_attachment.py`

## Certified Included Components

1. Explicit operator-triggered attachment
2. Visible session binding
3. Deterministic local transport invocation
4. Cockpit-visible transport report
5. Compact rejection rendering
6. Append-candidate replay visibility only
7. Session-scoped transport visibility
8. Non-authority labels

## Attachment Runtime Summary

The Browser Companion sidepanel now includes an explicit
`Attach Governed Transport` operator control and visible local transport session
input. The attachment flow builds a deterministic governed transport envelope
from the current semantic proposal cockpit state, invokes the local governed
transport handler path, and renders the returned transport report in the
cockpit.

This attachment is operator-triggered only. It does not run automatically during
semantic proposal import, file import, hash verification, replay loading, or
continuity rendering.

## Certified Operational Flow

ChatGPT semantic proposal
-> operator-triggered cockpit attach
-> local governed transport runtime invocation
-> deterministic transport validation
-> append-candidate replay event creation
-> cockpit-visible transport report
-> session-scoped replay visibility

## Cockpit-Visible Transport Report

The cockpit renders:

- transport status
- `replay_event_id`
- `session_id`
- `proposal_id`
- authority label
- integrity / hash status
- rejection reason
- compact rejection label
- append-candidate visibility
- non-authority guarantees

## Replay Visibility Guarantee

Transport replay visibility is append-candidate only. The attachment layer does
not write durable replay, mutate replay history, repair replay history, infer
missing replay entries, create lifecycle transitions, or treat the replay event
as approval, dispatch, execution, or continuation authority.

## Authority Guarantees

This milestone introduces:

- no HTTP endpoint
- no server or listener
- no `fetch()`
- no background worker or listener
- no durable browser storage
- no provider dispatch
- no approval
- no execution
- no orchestration
- no autonomous continuation
- no hidden persistence
- no automatic ingestion

## Certified Rejection Labels

Compact rejection rendering includes:

- `HASH_MISMATCH`
- `UNKNOWN_SESSION`
- `UNSAFE_MODE`
- `AUTHORITY_REJECTED`
- `REPLAY_POLICY_REJECTED`
- `SCHEMA_REJECTED`

## Test Evidence

Relevant validation:

- `python -B -m pytest tests/test_local_governed_transport_runtime_attachment.py`
- `python -B -m pytest tests`
- `git diff --check`

The focused test suite verifies explicit operator-triggered invocation,
deterministic transport invocation, accepted transport rendering, rejected
transport rendering, explicit session binding, append-candidate replay
visibility, no automatic invocation, no endpoint, no provider/dispatch/approval/
execution/orchestration behavior, no durable persistence, and no hidden runtime
behavior.

## Explicit Risk

The Browser Companion uses a JS-side deterministic invocation mirror for cockpit
attachment, while the Python primitive remains canonical.

Any future endpoint, localhost interop bridge, Python/JS runtime unification, or
durable transport bridge requires a separate governance gate. This finalize does
not certify endpoint behavior, server behavior, network transport, durable
replay, provider dispatch, execution, approval, orchestration, or autonomous
continuation.

## Closure Statement

`LOCAL_GOVERNED_TRANSPORT_RUNTIME_ATTACHMENT_V1` is finalized as an explicit,
operator-triggered, sidepanel-local attachment layer for governed semantic
transport visibility. It preserves local-only, read-only, session-scoped,
append-candidate semantics and does not add endpoint, listener, provider,
approval, execution, orchestration, durable persistence, or autonomous
continuation authority.
