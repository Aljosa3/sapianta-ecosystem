# LOCAL_GOVERNED_TRANSPORT_RUNTIME_IMPLEMENTATION_REVIEW_V1

## Status

Review complete.

Decision: `READY_FOR_PURE_LOCAL_HANDLER_IMPLEMENTATION`

## Purpose

This review determines whether the narrow local governed transport runtime can
safely be implemented.

This is review only. It does not implement an endpoint, provider dispatch,
execution, approval automation, orchestration, autonomous continuation, durable
replay backend, distributed transport, or hidden background import.

## Reviewed Implementation Path

Approved implementation path:

- pure local handler first;
- no endpoint unless separately approved;
- localhost endpoint deferred;
- explicit `session_id` required;
- deterministic transport envelope validation;
- semantic proposal hash verification;
- append-only in-memory transport event construction;
- cockpit-visible transport status;
- compact rejection rendering.

## 1. Minimal Files To Change

The safe implementation surface is narrow:

- `sapianta_system/runtime/semantic_transport.py`
  - create pure local handler and deterministic helpers.
- `tests/test_local_governed_transport_runtime.py`
  - validate handler behavior and forbidden capabilities.
- `browser_companion/sidepanel.js`
  - optional read-only rendering helper for transport reports.
- `browser_companion/sidepanel.html`
  - optional minimal static container if the current cockpit cannot host
    transport report visibility.
- sidepanel test file
  - only if rendering changes.

Do not modify `governed_local_preview_runtime.py` in this milestone. Endpoint
work remains deferred and requires a separate implementation review or explicit
implementation request.

## 2. Handler Function Shape

Recommended pure handler:

```python
handle_local_governed_transport(
    *,
    envelope: dict,
    session_registry: dict,
) -> dict
```

Handler constraints:

- pure deterministic function;
- no filesystem reads or writes;
- no network calls;
- no subprocess calls;
- no providers;
- no dispatch;
- no approval;
- no execution;
- no lifecycle mutation;
- no replay mutation outside returned in-memory event object;
- no global mutable state;
- no time, random, environment, or browser state dependency;
- no endpoint binding.

The handler may construct an in-memory append candidate named
`transport_event`, but it must not persist it.

## 3. Input Envelope Shape

Required envelope fields:

- `transport_id`
- `session_id`
- `proposal_id`
- `artifact_hash`
- `created_at_policy`
- `source_label`
- `semantic_proposal`
- `authority_boundary_statement`
- `replay_policy`
- `lifecycle_policy`

The handler must fail closed if any required field is missing, malformed, or
authority-bearing beyond the contract.

## 4. Output Transport Report Shape

Recommended output report fields:

- `status`
- `transport_id`
- `session_id`
- `proposal_id`
- `replay_event_id`
- `hash_verification_status`
- `authority_label`
- `rejection_reason`
- `validation`
- `transport_event`
- `operator_visibility`
- `non_authority_guarantees`

The output report must be deterministic for the same `envelope` and
`session_registry`.

## 5. Session Binding Checks

The handler must verify:

- `session_id` exists in the envelope;
- `session_id` exists in the explicit `session_registry`;
- the session is operator-visible;
- the session is not ambiguous;
- the session does not request continuation;
- the session binding does not mutate another session.

Rejected session conditions return `TRANSPORT_REJECTED_SESSION`.

No implicit session source may be used. The handler must not infer a session
from active browser tabs, sidepanel state, recent imports, cookies, runtime
state, or file names.

## 6. Replay Event Construction

The handler may return a transport event object with:

- `replay_event_id`
- `event_type`
- `transport_status`
- `transport_id`
- `session_id`
- `proposal_id`
- `artifact_hash`
- `hash_verification_status`
- `source_label`
- `authority_label`
- `rejection_reason`
- `lineage_refs`
- `visibility_scope`
- `created_at_policy`

Construction rules:

- canonical JSON input;
- deterministic `replay_event_id`;
- append-candidate only;
- no persistence;
- no replay rewrite;
- no replay repair;
- no inferred replay entries;
- no durable replay backend semantics.

## 7. Failure Status Handling

The handler must use only:

- `TRANSPORT_ACCEPTED`
- `TRANSPORT_REJECTED_SCHEMA`
- `TRANSPORT_REJECTED_HASH`
- `TRANSPORT_REJECTED_SESSION`
- `TRANSPORT_REJECTED_AUTHORITY`
- `TRANSPORT_REJECTED_UNSAFE_MODE`
- `TRANSPORT_REJECTED_REPLAY_POLICY`

Unknown, ambiguous, or contradictory input must reject. Acceptance is allowed
only after schema, hash, session, authority, unsafe mode, replay policy, and
lifecycle policy checks all pass.

## 8. Cockpit Visibility Requirements

If sidepanel rendering is included, it must remain read-only and render:

- transport status;
- session attachment;
- replay event ID;
- hash verification status;
- authority label;
- compact rejection reason;
- source label;
- proposal ID;
- transport ID;
- non-authority labels.

Mandatory labels:

- `SEMANTIC_TRANSPORT_ONLY`
- `SESSION_REPLAY_ONLY`
- `HASH_VERIFIED_IS_INTEGRITY_ONLY`
- `CERTIFIED_FOR_CONTINUITY_INGESTION_IS_NOT_APPROVAL`
- `CONTINUITY_VISIBLE_IS_NOT_EXECUTION_AUTHORIZATION`

Rendering must not invoke the handler automatically unless the user performs an
explicit local action in a later approved milestone.

## 9. Test Requirements

Tests must prove:

- valid envelope returns `TRANSPORT_ACCEPTED`;
- missing fields return `TRANSPORT_REJECTED_SCHEMA`;
- malformed hash returns `TRANSPORT_REJECTED_HASH`;
- hash mismatch returns `TRANSPORT_REJECTED_HASH`;
- missing session returns `TRANSPORT_REJECTED_SESSION`;
- unknown session returns `TRANSPORT_REJECTED_SESSION`;
- non-visible session returns `TRANSPORT_REJECTED_SESSION`;
- unsafe mode returns `TRANSPORT_REJECTED_UNSAFE_MODE`;
- approval, dispatch, execution, provider, orchestration, or continuation claims
  return `TRANSPORT_REJECTED_AUTHORITY`;
- replay rewrite, repair, inference, hidden state, or durable replay policy
  returns `TRANSPORT_REJECTED_REPLAY_POLICY`;
- deterministic output for identical inputs;
- deterministic `replay_event_id`;
- handler does not mutate `envelope`;
- handler does not mutate `session_registry`;
- no filesystem, network, subprocess, provider, sidepanel, runtime, replay, or
  lifecycle calls are introduced;
- no dispatch, approval, execution, orchestration, or autonomous continuation is
  introduced.

## 10. Rollback Boundary

Rollback boundary:

- remove `sapianta_system/runtime/semantic_transport.py` if newly created;
- remove `tests/test_local_governed_transport_runtime.py`;
- remove optional sidepanel rendering hooks if added;
- retain semantic proposal file import, hash verification, continuity cockpit,
  and replay session behavior;
- do not touch preview runtime endpoint code because endpoint work is not part
  of this reviewed implementation.

## Risk Summary

Remaining risks:

- later pressure to add the endpoint before session attachment semantics are
  proven;
- operator confusion if append-candidate event is presented as durable replay;
- authority over-trust if `TRANSPORT_ACCEPTED` is not paired with non-authority
  labels;
- future collapse from transport into dispatch unless provider calls remain
  explicitly forbidden.

## Final Guardrails

Implementation may proceed only as a pure local handler. Endpoint work is
deferred. The handler must be deterministic, in-memory, explicit-input-only,
non-authoritative, non-executing, non-persistent, and side-effect free.

Next safe step: implement `sapianta_system/runtime/semantic_transport.py` and
`tests/test_local_governed_transport_runtime.py` only, unless the implementation
request explicitly includes read-only sidepanel rendering.
