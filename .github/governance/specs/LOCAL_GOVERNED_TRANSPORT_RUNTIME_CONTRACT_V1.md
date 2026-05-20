# LOCAL_GOVERNED_TRANSPORT_RUNTIME_CONTRACT_V1

## Status

Contract v1.

## Purpose

This contract defines the strict bounded contract for the first localhost-only
governed semantic transport runtime before implementation.

This is a transport runtime contract, ingress contract, session binding
contract, replay append contract, authority boundary contract, and failure
semantics contract. It is not implementation, provider dispatch, execution
runtime, orchestration, autonomous continuation, durable replay backend,
distributed transport, or internet-exposed ingress.

## 1. Transport Scope

The runtime scope is limited to localhost-only semantic proposal transport.

Allowed:

- receive bounded semantic proposal transport envelopes over localhost only;
- validate transport envelopes deterministically;
- bind accepted envelopes to an explicit session;
- append a visible transport replay event;
- expose the accepted or rejected transport event to the continuity cockpit.

Forbidden:

- provider dispatch;
- execution;
- approval;
- orchestration;
- autonomous continuation;
- distributed runtime behavior;
- durable replay backend behavior;
- internet-exposed ingress;
- hidden background import;
- semantic inference runtime.

Transport success is visibility and continuity-ingestion readiness only. It is
not authorization.

## 2. Ingress Envelope

The runtime must accept only a governed transport envelope with all required
fields present.

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

Field requirements:

- `transport_id` identifies the transport envelope and must be deterministic for
  the canonical envelope content.
- `session_id` must be explicit and must match an operator-visible local
  session attachment.
- `proposal_id` must identify the semantic proposal carried by the envelope.
- `artifact_hash` must match the deterministic proposal artifact hash when the
  proposal artifact is present.
- `created_at_policy` must state whether time is externally supplied,
  deterministic fixture time, or rejected. The runtime must not silently add
  implicit timestamps.
- `source_label` must identify the semantic source class without creating
  authority, for example `CHATGPT_LOCAL_ARTIFACT` or `CLAUDE_LOCAL_ARTIFACT`.
- `semantic_proposal` contains the bounded semantic proposal object and must
  preserve existing proposal validation semantics.
- `authority_boundary_statement` must explicitly state transport-only,
  non-approval, non-dispatch, non-execution, and non-continuation semantics.
- `replay_policy` must request append-only visibility only.
- `lifecycle_policy` must request visibility-only lifecycle treatment and must
  not request execution lifecycle transition.

Unknown fields may be preserved for inspection only if the validator explicitly
allows them. Unknown fields must not create authority, lifecycle transitions,
dispatch, or execution semantics.

## 3. Session Binding

Session binding rules:

- `session_id` is required.
- Missing `session_id` fails closed.
- Ambiguous `session_id` fails closed.
- Unknown `session_id` fails closed.
- Session attachment must be operator-visible.
- The cockpit must show the accepted or rejected transport event in the attached
  session scope.
- No implicit session inheritance is allowed.
- No cross-session mutation is allowed.
- No automatic continuation is allowed.
- No automatic session escalation is allowed.

The runtime must not infer a session from active browser tabs, recent import
history, last active sidepanel state, cookies, browser page content, or ambient
runtime state.

## 4. Replay Append Semantics

Accepted transport envelopes may create exactly one append-only transport replay
event.

Replay append requirements:

- append-only transport event;
- immutable replay entry after append;
- deterministic `replay_event_id`;
- canonical JSON serialization;
- transport lineage reference to `transport_id`, `session_id`, `proposal_id`,
  and `artifact_hash`;
- operator-visible replay event ID;
- operator-visible accepted or rejected transport status;
- no replay rewrite;
- no replay repair;
- no inferred replay entries;
- no deletion or replacement of prior replay entries.

The replay append is visibility evidence only. It is not durable replay backend
certification, execution evidence, approval evidence, or dispatch evidence.

## 5. Authority Boundaries

The runtime must preserve these authority statements:

- transport success is not approval;
- transport success is not dispatch;
- transport success is not execution;
- transport success is not continuation authority;
- transport replay append is not lifecycle advancement;
- hash verification is integrity only, not semantic correctness;
- continuity ingestion is visibility only, not execution authorization;
- ChatGPT / LLMs remain semantic cognition only;
- AiGOL remains the governance substrate;
- providers are not invoked.

Mandatory operator labels:

- `SEMANTIC_TRANSPORT_ONLY`
- `SESSION_REPLAY_ONLY`
- `HASH_VERIFIED_IS_INTEGRITY_ONLY`
- `CERTIFIED_FOR_CONTINUITY_INGESTION_IS_NOT_APPROVAL`
- `CONTINUITY_VISIBLE_IS_NOT_EXECUTION_AUTHORIZATION`

## 6. Failure Semantics

The runtime must return one of the following statuses:

- `TRANSPORT_ACCEPTED`
- `TRANSPORT_REJECTED_SCHEMA`
- `TRANSPORT_REJECTED_HASH`
- `TRANSPORT_REJECTED_SESSION`
- `TRANSPORT_REJECTED_AUTHORITY`
- `TRANSPORT_REJECTED_UNSAFE_MODE`
- `TRANSPORT_REJECTED_REPLAY_POLICY`

Status meaning:

- `TRANSPORT_ACCEPTED`: the envelope is structurally valid, hash-valid where
  required, session-bound, authority-bounded, replay-policy-bounded, and ready
  for continuity cockpit visibility.
- `TRANSPORT_REJECTED_SCHEMA`: required fields are missing, malformed, or
  unsupported.
- `TRANSPORT_REJECTED_HASH`: `artifact_hash` is missing, malformed, or does not
  match canonical proposal content.
- `TRANSPORT_REJECTED_SESSION`: `session_id` is missing, ambiguous, unknown, or
  not operator-visible.
- `TRANSPORT_REJECTED_AUTHORITY`: the envelope or proposal implies approval,
  dispatch, execution, continuation, provider authority, orchestration, or
  semantic authority escalation.
- `TRANSPORT_REJECTED_UNSAFE_MODE`: the proposal requests `EXECUTE`,
  `AUTO_EXECUTE`, `AUTONOMOUS`, `PROVIDER_RUNTIME`, `ORCHESTRATION`, or any
  unsupported mode.
- `TRANSPORT_REJECTED_REPLAY_POLICY`: replay policy requests rewrite, repair,
  mutation, inference, durable replay backend behavior, hidden replay state, or
  omitted replay visibility.

Failure must be deterministic, fail-closed, and operator-visible. Rejections
must include a compact rejection reason and detailed inspection evidence.

## 7. Operator Visibility

The continuity cockpit must render:

- visible transport event;
- visible session attachment;
- visible replay event ID;
- visible hash verification status;
- visible authority label;
- visible rejection reason;
- visible source label;
- visible proposal ID;
- visible transport ID;
- visible non-authority statements.

The operator must be able to distinguish:

- localhost-only transport from internet ingress;
- transport success from approval;
- replay append from durable replay backend;
- continuity visibility from execution authorization;
- hash verification from semantic correctness;
- session attachment from autonomous continuation.

## 8. Security / Governance Risks

Known risks:

- hidden localhost ingress perception;
- CSRF or origin ambiguity for localhost requests;
- background injection;
- hidden background listener behavior;
- session confusion;
- replay over-trust;
- hash over-trust;
- certification over-trust;
- provider-dispatch collapse risk;
- semantic authority escalation through proposal wording;
- durable replay backend confusion;
- automatic continuation pressure.

Required controls:

- localhost-only binding;
- explicit session binding;
- deterministic request identity;
- fail-closed malformed request handling;
- authority statement validation;
- unsafe mode rejection;
- append-only replay event constraints;
- operator-visible transport state;
- no provider, dispatch, approval, execution, orchestration, durable replay, or
  autonomous continuation behavior.

## Recommended Implementation Path

Before runtime code, create a narrow implementation review or plan that defines:

1. localhost binding behavior and rejection rules;
2. ingress envelope validation helpers;
3. deterministic identity and hash helpers;
4. explicit session registry or explicit session attachment input;
5. append-only session replay event schema;
6. cockpit-visible transport event rendering;
7. compact rejection reason rendering;
8. tests proving no provider calls, dispatch, approval, execution,
   orchestration, durable replay backend, internet ingress, hidden persistence,
   replay rewrite, lifecycle mutation, or autonomous continuation.
