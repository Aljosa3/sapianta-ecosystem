# G30-07 Fail-Closed In-Session Artifact Attachment Retry Continuity

Status: implemented, bounded, and operationally validated.

## Purpose

G30-07 closes the bounded G30-06 retry-continuity limitation. When explicit
canonical artifact ingress rejects an in-session attachment before semantic
continuation or invocation, Platform Core keeps the original owner-specific
Generation 29 clarification active. The user may then attach a different
opaque reference in the same AiCLI process and session.

The integration adds no classifier, selector, route, lifecycle stage,
capability registry, execution authority, or artifact-discovery mechanism.
Generation 29, G28, explicit canonical artifact ingress, Governance, and
canonical presentation remain unchanged.

## Retry ownership

Platform Core alone decides whether an attachment failure is retryable. AiCLI
only transports the opaque reference, renders the governed result, retains the
opaque active clarification supplied by Platform Core, and accepts another
`/attach` command.

Each retry state preserves:

- session identity;
- the G29 clarification owner;
- the `input_artifact_family` semantic slot;
- originating Project Objective hash;
- originating route reference and hash;
- clarification-envelope reference and hash;
- parent operational turn;
- deterministic attempt number and identity;
- current and prior ingress references and hashes.

The Project Objective is not restarted and the failed artifact never satisfies
the semantic slot.

## Operational lifecycle

```text
G29 owner-specific clarification
  -> /attach invalid opaque reference
  -> existing G29-08 explicit canonical artifact ingress
  -> canonical fail-closed result
  -> Platform Core marks bounded retry eligible
  -> unchanged clarification owner/envelope/slot remains active
  -> /attach valid opaque reference
  -> existing G29-08 ingress
  -> existing G29-06 continuation route
  -> Platform Knowledge
  -> existing G29-04 lifecycle
  -> unchanged G28 certified invocation
  -> Canonical Platform Presentation
  -> Replay reconstruction
```

An attachment attempt is recorded at the operational binding boundary. It is
not a new routing or capability-invocation stage.

## Retryable and terminal states

`ATTACHMENT_RETRY_ELIGIBLE` is allowed only when ingress failed closed,
semantic continuation did not produce a route, and capability invocation has
not started. The original clarification remains active in that one bounded
case.

`ATTACHMENT_RETRY_COMPLETED` records a successful continuation and completed
certified invocation. `ATTACHMENT_RETRY_TERMINAL` covers any non-retryable
outcome.

Platform Core rejects retry after or across:

- stale, cancelled, or completed clarification;
- session, owner, or semantic-slot mismatch;
- tampered clarification-envelope lineage;
- duplicate attachment transport;
- any state in which invocation started or completed;
- a prior non-retryable attachment state.

No failed attempt partially satisfies the clarification. Invalid evidence
cannot reach G29-06 continuation, G29-04, or G28, and it cannot invoke a
Provider or Worker or mutate the repository.

## Attempt lineage and Replay

Every attempt receives a deterministic identity derived from the session,
unchanged clarification-envelope hash, attempt number, and opaque transport
hash. Immutable attempt records form a previous-reference and previous-hash
chain.

Reconstruction validates each attempt and its G29-08 ingress record, then
verifies:

- consecutive attempt ordering;
- unique transport hashes;
- stable session, owner, slot, and clarification envelope;
- prior-attempt reference and hash continuity;
- retry eligibility before a later attempt;
- ingress-resolution reference, status, and hash;
- downstream route reference and hash only after valid continuation.

This detects removed or reordered failed attempts, attempt substitution,
cross-session continuation, owner or slot substitution, replay of a consumed
attachment, and continuation after a terminal state. Operational-turn
reconstruction binds the latest attempt record to the unchanged clarification
and ingress lineage.

## Human Interface neutrality

AiCLI does not open or inspect the artifact, classify ingress failure, decide
retry eligibility, validate semantic compatibility, change clarification
ownership, select a capability, or invoke execution. It renders Platform Core's
failed-closed result and reuses only the active clarification state returned by
Platform Core.

The interface continues to report:

- `aicli_authorizes: False`;
- `aicli_executes: False`;
- `aicli_owns_replay: False`.

## Terminal acceptance scenario

On 2026-07-15, the real `./aicli` executable was run as one process with one
session identity:

```text
Analyze Platform Capability Composition Coverage.
Audit only.
/send
/attach /tmp/g30-07-terminal-acceptance/invalid.json
/attach /tmp/g30-07-terminal-acceptance/valid.json
/exit
```

The first attachment was a correctly wrapped artifact tampered after wrapper
hashing. Platform Core returned
`GOVERNED_READ_ONLY_WORK_FAILED_CLOSED`, `FAILED_CLOSED`, attempt 1, and
explicitly retained the original clarification. It reported no Provider,
Worker, or repository mutation.

The second attachment was a compatible immutable canonical wrapper. In the
same process and session it completed the existing certified route with
`GOVERNED_READ_ONLY_WORK_BOUND` and `PRESENTATION_READY`. The session
closed with no approval, execution, or Replay authority assigned to AiCLI.

## Validation evidence

Deterministic validation completed on 2026-07-15:

- focused G30-07 tests covering all 20 required positive, negative, authority,
  and Replay cases: 11 passed;
- all implemented Generation 30 regressions: 37 passed;
- G29 and G28 regressions: 73 passed;
- Human Interface tests: 22 passed;
- selected Replay reconstruction and integrity tests: 31 passed;
- selected Governance tests: 9 passed;
- full repository suite: 6,166 passed, 4 skipped, 0 failed;
- `py_compile` and `git diff --check`: passed;
- real terminal invalid-then-valid same-session acceptance: passed.

The governance conformance engine remains deterministically
`PARTIALLY_CONFORMANT`: 18 checks passed, two checks failed, and there were
zero critical violations. Both findings are the pre-existing hook drift:

- the root expected/installed pre-commit hooks are missing;
- the system pre-commit hook lacks `promotion_gate_v02` and
  `check_layer_freeze`.

G30-07 introduces no new governance finding and does not conceal the existing
partial conformance.

## Remaining limitations

- Retry is intentionally limited to pre-continuation ingress failure.
- References must identify existing immutable wrappers in a G29-08 allowed
  root.
- AiCLI intentionally offers no artifact browsing, discovery, repair, or
  compatibility advice.
- A duplicate opaque attachment is rejected rather than silently replayed.
- Cancellation and successful completion consume the active clarification;
  later attachment commands require a new governed request.

These constraints preserve certified ownership, fail-closed behavior, and
Replay continuity.

## Reusable certification conclusion

The unchanged operational lifecycle now supports deterministic failed-ingress
retry continuity. A final Generation 30 operational certification milestone
can exercise the complete terminal matrix—knowledge query, governed
implementation, direct read-only work, clarification, valid attachment,
invalid-then-valid retry, cancellation, and Replay reconstruction—without
adding Platform Core responsibility.
