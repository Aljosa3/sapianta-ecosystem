# FINALIZE_LOCAL_GOVERNED_TRANSPORT_RUNTIME_V1

## Status

Frozen and certified.

This milestone finalizes the first pure local governed semantic transport
runtime handler.

## References

- `.github/governance/specs/LOCAL_GOVERNED_TRANSPORT_RUNTIME_CONTRACT_V1.md`
- `.github/governance/plans/LOCAL_GOVERNED_TRANSPORT_RUNTIME_IMPLEMENTATION_PLAN_V1.md`
- `.github/governance/review/LOCAL_GOVERNED_TRANSPORT_RUNTIME_IMPLEMENTATION_REVIEW_V1.md`
- `agol_bridge/transport/local_governed_transport.py`
- `agol_bridge/transport/__init__.py`
- `tests/test_local_governed_transport_runtime.py`

## Certified Included Components

1. Pure local handler only
2. Explicit session binding
3. Required transport envelope field validation
4. Semantic proposal hash verification
5. Unsafe proposed mode rejection
6. Authority claim rejection
7. Replay policy enforcement
8. Lifecycle policy enforcement
9. Deterministic append-candidate replay event construction
10. Cockpit-visible transport report
11. Input envelope immutability
12. Session registry immutability

## Runtime Summary

`handle_local_governed_transport(*, envelope, session_registry)` validates a
governed semantic transport envelope against an explicit in-memory session
registry and returns a deterministic transport report.

The handler is local and pure. It does not open an HTTP endpoint, bind a
localhost server, start a browser listener, read files, write files, call
providers, dispatch tasks, approve actions, execute work, mutate replay,
mutate lifecycle state, or persist durable artifacts.

## Certified Statuses

- `TRANSPORT_ACCEPTED`
- `TRANSPORT_REJECTED_SCHEMA`
- `TRANSPORT_REJECTED_HASH`
- `TRANSPORT_REJECTED_SESSION`
- `TRANSPORT_REJECTED_AUTHORITY`
- `TRANSPORT_REJECTED_UNSAFE_MODE`
- `TRANSPORT_REJECTED_REPLAY_POLICY`

## Transport Report Shape

The handler returns:

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

## Replay Event Shape

The returned `transport_event` is an append-candidate only and contains:

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

The event is deterministic and visibility-scoped. It is not persisted, appended
to durable replay, used as execution evidence, or treated as lifecycle
advancement.

## Deterministic Guarantees

- Identical valid inputs produce identical transport reports.
- Identical valid inputs produce identical `replay_event_id` values.
- Hash verification uses canonical JSON serialization of semantic proposal
  content excluding `artifact_hash`.
- Rejection statuses are deterministic for the same envelope and session
  registry.
- No time, random, environment, network, filesystem, browser, or endpoint state
  contributes to handler output.

## Session Binding Guarantees

- `session_id` is required.
- Unknown sessions fail closed.
- Missing sessions fail closed.
- Ambiguous sessions fail closed.
- Non-operator-visible sessions fail closed.
- Session continuation requests fail closed.
- Cross-session mutation requests fail closed.
- No implicit session inheritance is used.

## Authority Guarantees

The runtime introduces:

- no HTTP endpoint;
- no server or listener;
- no provider dispatch;
- no approval;
- no execution;
- no orchestration;
- no autonomous continuation;
- no durable persistence;
- no replay write;
- no lifecycle transition;
- no hidden background import;
- no browser scraping.

`TRANSPORT_ACCEPTED` means semantic transport envelope acceptance for
cockpit-visible continuity only. It is not approval, dispatch, execution,
provider authorization, durable replay certification, or continuation authority.

## No-Mutation Guarantees

Tests certify that the handler does not mutate:

- the supplied `envelope`;
- the supplied `session_registry`;
- replay state;
- lifecycle state;
- runtime state;
- sidepanel state.

## Test Evidence

Relevant validation:

- `python -B -m pytest tests/test_local_governed_transport_runtime.py`
- `python -B -m pytest tests`
- `git diff --check`

The focused test suite verifies accepted transport, missing-field rejection,
hash mismatch rejection, malformed hash rejection, missing/unknown/non-visible
session rejection, ambiguous session rejection, unsafe mode rejection, authority
claim rejection, replay policy rejection, lifecycle policy rejection,
deterministic replay event IDs, append-candidate-only semantics, input
immutability, session registry immutability, and absence of provider, dispatch,
approval, execution, orchestration, endpoint, and persistence behavior.

## Certified Exclusions

- HTTP endpoint
- localhost server
- browser background listener
- provider dispatch
- approval automation
- execution
- orchestration
- autonomous continuation
- durable persistence
- replay mutation
- replay repair
- lifecycle mutation
- hidden persistence
- filesystem IO
- network IO
- subprocess calls

## Risks Remaining

- The handler produces an append-candidate replay event only; future append or
  durable replay behavior must be governed separately.
- Future endpoint work must preserve explicit session binding and
  operator-visible transport status.
- `TRANSPORT_ACCEPTED` can be over-trusted unless non-authority labels remain
  visible in cockpit rendering.
- This milestone does not provide no-copy/paste automation by itself; it creates
  the pure local validation primitive needed for a later governed ingress path.

## Closure Statement

`LOCAL_GOVERNED_TRANSPORT_RUNTIME_V1` is finalized as a deterministic,
side-effect-free, pure local governed semantic transport handler. It validates
explicit transport envelopes and returns cockpit-visible transport reports
without endpoints, listeners, provider dispatch, approval, execution,
orchestration, durable persistence, replay mutation, lifecycle mutation, or
input/session mutation.
