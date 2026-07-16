# G31-10 Confirmed Grounded Execution Decision to Execution Authorization Binding

Status: implemented and operationally validated.

Date: 2026-07-16

Verdict:

`CONFIRMED_GROUNDED_EXECUTION_DECISION_EXECUTION_AUTHORIZATION_BINDING_OPERATIONAL`

Next blocker:

`AUTHORIZED_GROUNDED_EXECUTION_WORKER_SELECTION_BINDING_ABSENT`

## Constitutional scope

G31-10 preserves the accepted Generation 30 and committed G31-02 through
G31-09 baselines. It implements one transition only:

```text
approved G31-09 human execution decision
  -> existing execution-ready artifact families
  -> existing execution-authorization request
  -> existing execution-authorization decision
  -> existing execution-authorization artifact
  -> stop before Worker selection
```

It adds no approval system, third human checkpoint, authorization runtime,
policy engine, canonical artifact family, Worker request, state store, router,
selector, or Replay subsystem.

## Mandatory discovery result

The canonical execution-summary contracts are implemented by:

- `create_execution_summary` and `verify_execution_summary` for
  `EXECUTION_SUMMARY_ARTIFACT_V1`;
- `create_execution_summary_confirmation` and
  `verify_execution_summary_confirmation` for
  `EXECUTION_SUMMARY_HUMAN_CONFIRMATION_ARTIFACT_V1`.

The G31-08 review already creates the exact pending execution summary. G31-09
creates the one summary-bound human confirmation only after the second
`/approve`.

The canonical authorization consumer is `authorize_execution_ready`. It owns
construction of:

- `EXECUTION_AUTHORIZATION_REQUEST_ARTIFACT_V1`;
- `EXECUTION_AUTHORIZATION_DECISION_ARTIFACT_V1`;
- `EXECUTION_AUTHORIZATION_ARTIFACT_V1`;
- `EXECUTION_AUTHORIZATION_RESULT_ARTIFACT_V1`.

`reconstruct_execution_authorization_replay` is the existing deterministic
authorization Replay validator.

The authorization consumer requires the established execution candidate,
packet, validation, and ready artifact families. The existing governed-handoff
and OCS projections cannot truthfully consume G31-09: each validates a
different source handoff contract. Reusing either would substitute lineage.
G31-10 therefore adds one bounded projection into those existing artifact
families. It does not define a new artifact family.

## Minimal call chain

The implemented call chain is:

```text
validate_distinct_human_execution_decision
  -> reconstruct_distinct_human_execution_decision
  -> existing execution candidate/packet/validation/ready families
  -> reconstruct_confirmed_grounded_execution_ready_replay
  -> authorize_execution_ready
       with the exact G31-08 execution summary
       and exact G31-09 human confirmation
  -> reconstruct_execution_authorization_replay
  -> stop
```

The projection packet carries `authorization_scope` as an exact copy of the
G31-08 scope. The existing authorization runtime now prefers that exact scope
when present and retains its prior three-field packet projection for all
existing callers. Its authorization artifact copies the request scope instead
of independently projecting the packet a second time. Replay requires request
and authorized scope equality.

## Exact authorization evidence

For an accepted G31-09 decision, operational evidence proves:

- `execution_summary_human_confirmation: true`;
- `execution_authorization_request_created: true`;
- `execution_authorization_decision_created: true`;
- `execution_authorization_artifact_created: true`;
- `execution_authorized: true`;
- `third_human_confirmation_requested: false`;
- Worker selection, assignment, dispatch, and invocation remain false;
- Provider invocation remains false;
- command execution remains false;
- repository mutation remains false.

The request and authorization scopes equal the G31-08 scope as whole JSON
objects. That preserves:

- workspace root;
- repository grounding identity and hash;
- Repository Cognition snapshot and evidence hashes;
- grounded Worker request identity and hash;
- source and focused-test paths;
- symbols and content hashes;
- mutation-layer classifications;
- validation requirements;
- original human goal and Project Objective;
- approved bounded work;
- G31-04 through G31-06 lineage carried by the grounded request;
- G31-08 review and execution-summary lineage;
- G31-09 decision and confirmation lineage through the execution-ready packet.

The authorization remains non-transferable and non-recursive under the
existing authorization contract. No target, command, operation, authority, or
lifecycle stage is added.

## Two-decision model and no-third-confirmation proof

The first `/approve` consumes the G31-04 proposal approval. It does not
authorize execution.

The second `/approve` is handled by G31-09 and creates the existing
execution-summary confirmation. G31-10 passes that exact artifact to
`authorize_execution_ready` through its existing
`human_confirmation_artifact` parameter. Consequently, the authorization
runtime does not execute its compatibility default that can synthesize a
confirmation for older callers.

No third prompt is rendered, requested, stored, or reconstructed. Focused and
PTY evidence verifies that the confirmation hash in the authorization request
and authorization artifact equals the G31-09 confirmation hash.

## Rejection and fail-closed behavior

A G31-09 rejection remains non-confirming. AiCLI does not call the G31-10
binding for rejection, so no execution-ready projection, authorization
request, decision, or authorization artifact is created.

The binding fails closed before authorization for:

- missing, rejected, failed, replayed, or cross-session decisions;
- changed decision or upstream identity hashes;
- summary or confirmation substitution;
- broadened paths, focused tests, symbols, mutation layers, or scope;
- stale Repository Cognition source evidence;
- changed grounded Worker-request or G31-04 through G31-09 lineage;
- reordered or substituted execution-ready or authorization Replay;
- any scope difference between request and authorization.

Duplicate decision consumption is rejected by validated existing packet
Replay evidence within the session. Invalid evidence never partially creates
authorization artifacts.

## Replay continuity

Successful Replay continuity is:

```text
G31-04 approved identities
  -> G31-05 goal-faithful Worker payload
  -> G31-06 grounded Worker request and Repository Cognition evidence
  -> G31-08 exact authorization review and execution summary
  -> G31-09 second human decision and confirmation
  -> existing execution candidate
  -> existing execution packet with exact authorization scope
  -> existing execution validation
  -> existing execution-ready status
  -> existing authorization request
  -> existing authorization decision
  -> existing authorization artifact
  -> existing authorization result
```

The PTY lineage reconstructed to:

- `GROUNDED_WORKER_REQUEST_EXECUTION_AUTHORIZATION_REVIEW_REQUIRED`;
- `EXECUTION_DECISION_HUMAN_CONFIRMED`;
- `EXECUTION_READY`;
- `EXECUTION_AUTHORIZED`.

The final reconstruction retained Worker assignment, dispatch, and invocation
as false.

## Real PTY validation

A disposable Git repository contained one existing implementation and one
focused test. A real `./aicli` process ran under a pseudo-terminal.

The human input was limited to an ordinary natural-language request,
`/send`, and contextual approval or rejection commands. No path, JSON,
capability identity, prepared artifact, prompt, or shell bridge was supplied.

Positive evidence:

1. the request produced the G31-04 proposal;
2. the first `/approve` produced the G31-05 payload, G31-06 grounding, and
   G31-08 review;
3. the second `/approve` produced G31-09 confirmation;
4. authorization was created immediately without a third prompt;
5. the terminal rendered `EXECUTION_AUTHORIZED`;
6. it truthfully stated that no Worker was assigned, dispatched, invoked, or
   executed.

Negative evidence:

1. a separate PTY session used `/cancel` for the second decision;
2. it rendered `EXECUTION_DECISION_REJECTED`;
3. no authorization capture or authorization Replay was created;
4. execution and repository mutation remained false.

Nested Replay reconstruction passed after the positive session. The disposable
repository, runtime, and terminal transcripts were then removed.

## Authority boundaries

Platform Core continues to own lifecycle semantics. Governance owns execution
authorization policy and evidence. Replay owns deterministic reconstruction.
Worker and Provider authority remain separate. AiCLI only transports the
contextual decision, delegates to the Platform Core binding, and renders the
returned canonical result.

The reference interface retains:

- `aicli_authorizes: false`;
- `aicli_executes: false`;
- `aicli_owns_replay: false`.

G31-10 does not select, assign, dispatch, or invoke a Worker; invoke a
Provider; execute a command; or mutate a repository.

## Minimal-change and duplication accounting

Production additions remain below the mandatory stop threshold: 339 lines
added and 7 removed. Exactly one new production module was introduced.

The new module is justified because no existing truthful execution-ready
projection accepts G31-09 lineage. It contains only:

- one public binding that validates the confirmed decision, creates existing
  execution-ready artifacts, and calls the existing authorization consumer;
- one public reconstructor that validates those existing artifacts and nested
  G31 lineage;
- constants describing the existing projection version, Replay steps,
  prohibited operations, and stop boundaries.

The existing authorization runtime was modified only to recognize the bounded
projection and carry an exact packet scope through request, authorization, and
Replay. AiCLI was modified only to invoke and render the Platform Core result
after the second approval.

No `_verify_hash`, `_relative_path`, `_unique_relative_paths`, `_persist`, or
wrapper-verification helper was copied. The implementation uses the public
`replay_hash`, `with_replay_hash`, `verify_replay_hash`, `load_json`, and
`write_json_immutable` transport contracts.

## Validation

Focused results before the full suite:

- focused G31-10 plus G31-09 and authorization contracts: 45 passed;
- G31-04 through G31-10: 149 passed;
- Project Context, PPP, Worker request, execution summary, and authorization:
  49 passed;
- G28, G29, Generation 30, G31-02, Human Interface, and AiCLI: 158 passed;
- Replay- and Governance-pattern suites: 341 passed.
- full repository suite: **6,323 passed, 1 skipped, 0 failed** in 286.99
  seconds;
- targeted `py_compile`: passed;
- `git diff --check`: passed;
- governance conformance: 18 checks passed, 2 checks failed, 0 critical
  violations.

Counts overlap and must not be summed.

Repository governance remains `PARTIALLY_CONFORMANT`, deterministic,
fail-closed, and read-only. The two failures are the pre-existing hook-drift
findings: missing expected/installed root pre-commit hooks, and the system
pre-commit hook missing `promotion_gate_v02` and `check_layer_freeze`. G31-10
does not hide or repair them. They produced zero critical violations and did
not invalidate this operational transition.

## Progress and next blocker

Evidence-scoped no-copy/paste conversational governed-development progress is
**97%** on the established G31 denominator. Whole-project progress toward a
certified enterprise-demonstrable Product 1 with conversational governed
development is **86%**. These are planning estimates, not certification
claims.

Exactly one next blocker remains:

`AUTHORIZED_GROUNDED_EXECUTION_WORKER_SELECTION_BINDING_ABSENT`

G31-11 should consume the exact execution authorization and select at most one
compatible certified Worker through existing Worker registry and policy
contracts, then stop before assignment or dispatch.

## Bounded G31-11 prompt

```text
# Generation 31-11 — Authorized Grounded Execution to Certified Worker Selection Binding

Treat Generation 30 and committed G31-02 through G31-10 as immutable accepted
baselines.

G31-10 verdict:

CONFIRMED_GROUNDED_EXECUTION_DECISION_EXECUTION_AUTHORIZATION_BINDING_OPERATIONAL

First true blocker:

AUTHORIZED_GROUNDED_EXECUTION_WORKER_SELECTION_BINDING_ABSENT

Primary priority:

NO_COPY_PASTE_CONVERSATIONAL_GOVERNED_DEVELOPMENT_THROUGH_AICLI

## Objective

Implement exactly one transition:

valid G31-10 execution authorization
  -> existing certified Worker eligibility and selection policy
  -> one immutable Worker selection result or existing fail-closed result
  -> stop before assignment or dispatch

Reuse the existing Worker registry, capability evidence, selection policy,
authorization validation, Replay, Human Conversation Experience, and Canonical
Presentation. Do not create another registry, selector, Worker identity,
authorization system, state store, router, or Replay subsystem.

## Required behavior

Selection must consume the exact G31-10 authorization request, decision,
authorization artifact, grounded scope, required Worker role, validation
requirements, mutation layers, and complete G31-04 through G31-10 lineage.

Select exactly one already registered, certified, compatible Worker only when
deterministic evidence proves compatibility. If no Worker or multiple
materially different Workers are compatible, use existing owner-specific
clarification or fail closed. Do not ask a Provider, LLM, AiCLI, or the Worker
to choose.

Stop with Worker assignment, dispatch, Provider invocation, Worker invocation,
command execution, and repository mutation all false.

## Fail-closed requirements

Reject stale, substituted, broadened, reordered, cross-session, revoked,
expired, non-transferable, scope-mismatched, or Replay-invalid authorization.
Reject missing or incompatible Worker certification, capabilities, mutation
layers, validation support, or registry identity. Invalid evidence must not
partially select, assign, or dispatch a Worker.

## Minimal-change gate

First locate the existing Worker selection and registry contracts and report
the minimal call chain. Prefer one existing-function binding. Stop before
implementation if the transition requires a new registry, selector, policy
engine, canonical artifact family, copied validation/Replay helpers, more than
one production module, or more than 350 production additions.

## Validation

Add focused G31-11 coverage for exact authorization consumption, one compatible
selection, zero/multiple compatibility failure, tamper and Replay rejection,
and all stop boundaries. Run G31-04 through G31-10, Worker registry and policy,
authorization, Human Interface/AiCLI, G28-G30, Replay, Governance, py_compile,
git diff --check, then the full repository suite once.

Perform a real PTY-backed ./aicli validation in a disposable repository. The
human supplies only an ordinary request and contextual decisions. Demonstrate
one deterministic Worker selection or truthful fail-closed absence, complete
Replay, and no assignment, dispatch, invocation, command, or mutation. Remove
the disposable repository afterward.

## Documentation

Add:

docs/governance/G31_11_AUTHORIZED_GROUNDED_EXECUTION_CERTIFIED_WORKER_SELECTION_BINDING.md

Report exact changed files, size and symbols, reused contracts, PTY evidence,
Replay/tamper evidence, validation/governance counts, authority boundaries,
one next blocker or readiness verdict, progress estimates, git status, commit
commands, and a complete bounded G31-12 prompt. Do not commit.
```
