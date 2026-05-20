# LOCAL_GOVERNED_TRANSPORT_RUNTIME_IMPLEMENTATION_PLAN_V1

## Status

Implementation plan v1.

Readiness decision: `READY_FOR_NARROW_IMPLEMENTATION_REVIEW`

## Purpose

This plan defines the narrow implementation path for the first localhost-only
governed semantic transport runtime based on
`LOCAL_GOVERNED_TRANSPORT_RUNTIME_CONTRACT_V1`.

This is not implementation. It does not add provider dispatch, execution,
approval automation, orchestration, autonomous continuation, durable replay
backend, distributed transport, internet-exposed ingress, or hidden background
import.

## Scope

Allowed implementation scope:

- localhost-only binding;
- semantic proposal transport only;
- explicit `session_id`;
- deterministic transport envelope validation;
- semantic proposal hash verification;
- append-only visible replay event;
- cockpit-visible transport event;
- compact rejection rendering.

Forbidden implementation scope:

- provider dispatch;
- execution;
- approval automation;
- orchestration;
- autonomous continuation;
- durable replay backend;
- distributed transport;
- internet-exposed ingress;
- hidden background import;
- automatic ingestion;
- replay rewrite;
- lifecycle mutation.

## Minimal Files To Change

Preferred minimal implementation surface:

- `sapianta_system/runtime/semantic_transport.py`
  - pure deterministic validation helpers;
  - transport envelope validation;
  - status selection;
  - deterministic replay event construction.
- `sapianta_system/runtime/preview/governed_local_preview_runtime.py`
  - optional localhost-only route if the implementation chooses an HTTP preview
    transport endpoint.
  - route must be disabled by omission unless explicitly added in the
    implementation milestone.
- `browser_companion/sidepanel.js`
  - render visible transport event status;
  - render compact rejection reason;
  - render session attachment, replay event ID, hash status, and authority
    labels.
- `browser_companion/sidepanel.html`
  - add only the smallest read-only transport visibility surface if current
    sections cannot host it.
- `tests/test_local_governed_transport_runtime.py`
  - deterministic transport contract tests.
- `tests/test_browser_companion_sidepanel.py` or a new focused sidepanel test
  - cockpit rendering and no-authority checks if sidepanel rendering changes.

No new provider files, worker files, orchestration files, durable storage files,
or background extension scripts should be added for v1.

## Endpoint Shape

Endpoint is optional and must be explicitly chosen by the implementation
milestone.

If implemented, the only admissible endpoint shape is:

- method: `POST`
- path: `/governed-semantic-transport`
- bind: `127.0.0.1` only
- content type: `application/json`
- request body: governed transport ingress envelope
- response body: deterministic transport result

Response fields should include:

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

The endpoint must not:

- call providers;
- dispatch execution;
- approve actions;
- create execution lifecycle transitions;
- read browser page content;
- discover files;
- persist durable replay;
- continue work after the request returns.

If an endpoint is not implemented, the same contract may first be implemented as
a pure local handler invoked by tests and sidepanel-local flows.

## Ingress Envelope Handling

Required fields:

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

Validation order:

1. parse JSON;
2. validate required fields and field types;
3. validate explicit `session_id`;
4. validate semantic proposal mode and required proposal fields;
5. verify `artifact_hash` against canonical semantic proposal content;
6. validate authority boundary statement;
7. validate replay policy is append-only visibility only;
8. validate lifecycle policy is visibility-only and non-execution;
9. compute deterministic transport status;
10. construct deterministic transport event for rendering.

Validation must fail closed and must never infer missing fields.

## Session-Binding Checks

The implementation must check:

- `session_id` is present;
- `session_id` is unambiguous;
- `session_id` belongs to an operator-visible session attachment;
- transport event renders within the selected session scope;
- no implicit session inheritance occurs;
- no cross-session mutation occurs;
- no automatic continuation occurs.

Missing, unknown, ambiguous, or hidden session attachment returns
`TRANSPORT_REJECTED_SESSION`.

## Replay Event Schema

An accepted or rejected transport event should be a deterministic object:

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

Required semantics:

- append-only;
- immutable after append;
- canonical JSON serialization;
- deterministic `replay_event_id`;
- no replay rewrite;
- no replay repair;
- no inferred replay entries;
- no durable replay backend semantics.

## Failure Statuses

The implementation must use only:

- `TRANSPORT_ACCEPTED`
- `TRANSPORT_REJECTED_SCHEMA`
- `TRANSPORT_REJECTED_HASH`
- `TRANSPORT_REJECTED_SESSION`
- `TRANSPORT_REJECTED_AUTHORITY`
- `TRANSPORT_REJECTED_UNSAFE_MODE`
- `TRANSPORT_REJECTED_REPLAY_POLICY`

Unknown or ambiguous failures must map to a rejection status, not acceptance.

## Operator Visibility Requirements

The cockpit must render:

- transport event;
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

## Tests Required

Create deterministic tests for:

- valid transport envelope returns `TRANSPORT_ACCEPTED`;
- missing required fields return `TRANSPORT_REJECTED_SCHEMA`;
- mismatched artifact hash returns `TRANSPORT_REJECTED_HASH`;
- missing, unknown, or ambiguous session returns `TRANSPORT_REJECTED_SESSION`;
- unsafe mode returns `TRANSPORT_REJECTED_UNSAFE_MODE`;
- authority claims return `TRANSPORT_REJECTED_AUTHORITY`;
- replay rewrite or durable replay policy returns
  `TRANSPORT_REJECTED_REPLAY_POLICY`;
- deterministic replay event ID for identical input;
- append-only replay event construction;
- no replay rewrite or repair;
- no lifecycle mutation;
- no provider calls;
- no dispatch;
- no approval;
- no execution;
- no orchestration;
- no autonomous continuation;
- no hidden persistence;
- endpoint, if added, binds localhost only;
- cockpit renders compact rejection reason and non-authority labels.

Suggested validation commands:

```bash
python -B -m pytest tests/test_local_governed_transport_runtime.py
python -B -m pytest tests/test_browser_companion_sidepanel.py
git diff --check
```

If the implementation touches the preview HTTP runtime, also run:

```bash
python -B -m pytest tests/test_governed_local_preview_runtime.py
```

## Explicit Non-Goals

This plan does not authorize:

- provider dispatch;
- execution;
- approval automation;
- orchestration;
- autonomous continuation;
- durable replay backend;
- distributed transport;
- internet-exposed ingress;
- hidden background import;
- ChatGPT API integration;
- browser scraping;
- automatic file discovery;
- semantic inference runtime.

## Rollback Plan

Rollback must be simple and non-destructive:

1. remove the optional `/governed-semantic-transport` route if added;
2. remove transport rendering hooks from the sidepanel;
3. retain existing file import and semantic proposal validation behavior;
4. retain existing replay session behavior;
5. retain governance artifacts documenting the deferred runtime;
6. rerun relevant sidepanel and preview runtime tests;
7. verify `git diff --check`.

The rollback must not alter existing governance semantics, sidepanel file
import, hash verification, continuity synthesis, or replay session behavior.

## Readiness Gate Before Implementation

Implementation may proceed only if:

- this plan and `LOCAL_GOVERNED_TRANSPORT_RUNTIME_CONTRACT_V1` remain accepted
  as the controlling scope;
- endpoint shape is explicitly selected or explicitly deferred;
- session attachment source is defined without ambient inference;
- replay event schema is fixed before code;
- compact rejection rendering is defined before code;
- tests are written for all failure statuses;
- no durable replay backend, provider dispatch, execution, approval,
  orchestration, internet ingress, hidden background import, or autonomous
  continuation is added.

Gate decision: `READY_FOR_NARROW_IMPLEMENTATION_REVIEW`.

The next safe step is an implementation review or a tightly scoped
implementation milestone for pure validation and visible transport event
rendering. Runtime endpoint implementation should remain optional until the
session attachment contract is concrete.
