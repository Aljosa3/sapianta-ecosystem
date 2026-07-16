# Generation 31-09 — Distinct Human Execution Decision Binding

Status: operational; distinct second human decision binding complete.

Date: 2026-07-16

Verdict:

`DISTINCT_HUMAN_EXECUTION_DECISION_BINDING_OPERATIONAL`

Exactly one next blocker:

`CONFIRMED_GROUNDED_EXECUTION_DECISION_EXECUTION_AUTHORIZATION_BINDING_ABSENT`

## Constitutional scope

Generation 30 and accepted G31-03, G31-04, G31-05, G31-06, G31-07, and
G31-08 remain immutable baselines. G31-09 adds one transition:

```text
G31-04 proposal approval
  -> G31-05 goal-faithful Worker request
  -> G31-06 exact Repository Cognition grounding
  -> G31-08 pending execution-authorization review
  -> explicit second human APPROVE or REJECT
  -> existing execution-summary confirmation or explicit rejection result
  -> stop before execution authorization
```

No G31-09 path creates an execution-authorization request, decision, or
authorization artifact. It does not select, assign, dispatch, or invoke a
Worker; invoke a Provider; run a command; mutate a repository; deploy; validate
implementation output; or certify completion.

## Pre-implementation contract audit

| Existing contract | Reused G31-09 responsibility |
|---|---|
| G31-08 review validator and reconstructor | Proves the exact pending review, grounded scope, Repository Cognition freshness, and complete G31-04 through G31-08 lineage |
| `EXECUTION_SUMMARY_ARTIFACT_V1` | Supplies the pending non-authoritative review summary already bound to exact grounded scope |
| `create_execution_summary_confirmation` and `verify_execution_summary_confirmation` | Create and validate the one existing summary-bound confirmation for explicit second `APPROVE` |
| `load_json`, `replay_hash`, `verify_replay_hash`, and `write_json_immutable` | Supply canonical immutable transport and hash validation |
| Reference AiCLI contextual `/approve` and `/cancel` | Transport second approval or explicit rejection without a parallel command |
| Existing Platform Core and Human Interface projections | Carry and render review state without giving AiCLI policy or authorization authority |

The existing execution-authorization runtime is deliberately not called. It
would create authorization request, decision, and authorization artifacts and
cross the required stop boundary. The smallest missing binding is one
decision-result artifact containing the existing confirmation on approval or
an explicit non-confirming rejection.

## Strict two-decision model

G31-09 preserves exactly two meaningful human decisions:

1. the first `/approve` approves the immutable governed-development proposal;
2. the second contextual `/approve` approves proceeding toward execution and
   creates the existing execution-summary confirmation.

The first approval cannot satisfy the second checkpoint because the G31-09
runtime accepts only a validated pending G31-08 review. Passing the G31-04
proposal or approval artifact fails closed before confirmation.

There is no third human checkpoint in the accepted output. The G31-09
confirmation is the exact evidence a later execution-authorization binding
must consume without asking the user again.

Contextual `/cancel` at the G31-08 state means explicit rejection of the
execution decision. At compose, clarification, or proposal-review states,
`/cancel` retains its existing meanings.

## Canonical input and output contracts

### Input

The binding accepts only:

- one complete `GROUNDED_WORKER_REQUEST_EXECUTION_AUTHORIZATION_REVIEW_BINDING_ARTIFACT_V1`;
- exact `APPROVE` or `REJECT` decision text;
- session identity and session Replay root;
- human actor identity;
- deterministic decision time;
- current workspace for Repository Cognition freshness checks;
- one new immutable Replay directory below the exact session root.

### Output

G31-09 introduces one bounded result type:

`GROUNDED_EXECUTION_AUTHORIZATION_HUMAN_DECISION_RESULT_ARTIFACT_V1`

It has three statuses:

- `EXECUTION_DECISION_HUMAN_CONFIRMED`;
- `EXECUTION_DECISION_REJECTED`;
- `EXECUTION_DECISION_FAILED_CLOSED`.

An approved result contains the existing
`EXECUTION_SUMMARY_HUMAN_CONFIRMATION_ARTIFACT_V1`, validated against the exact
G31-08 execution summary. A rejected result contains no confirmation. A
failed-closed result contains only the source observation hash, failure
evidence, and false authority boundaries; it cannot contain a confirmation.

Both accepted decisions bind unchanged:

- session identity;
- Project Objective hash;
- Durable Governed Work hash;
- proposal preview hash;
- repository-scope grounding hash;
- grounded Worker-request hash;
- execution-summary hash;
- authorization-scope hash;
- G31-08 review hash;
- human actor and decision time.

## Approval lifecycle

```text
proposal /approve
  -> proposal approval consumed
  -> G31-08 review rendered
  -> state-aware guidance distinguishes the second decision
  -> second /approve
  -> existing execution-summary confirmation created
  -> G31-09 result recorded
  -> execution authorization remains absent
```

Expected and observed state:

- `proposal_approval_consumed: true`;
- `proposal_approval_is_execution_authorization: false`;
- `execution_summary_human_confirmation: true`;
- `authorization_request_created: false`;
- `authorization_decision_created: false`;
- `execution_authorization_artifact_created: false`;
- `execution_authorized: false`;
- `worker_selected: false`;
- `worker_dispatched: false`;
- `repository_mutated: false`.

## Rejection lifecycle

```text
proposal /approve
  -> G31-08 pending review
  -> contextual /cancel
  -> explicit Replay-visible REJECT
  -> no execution-summary confirmation
  -> no execution authorization or Worker continuation
```

Expected and observed state:

- `execution_summary_human_confirmation: false`;
- `execution_decision_rejected: true`;
- `execution_authorized: false`;
- `worker_selected: false`;
- `worker_dispatched: false`;
- `repository_mutated: false`.

## State-aware terminal behavior

After the first approval, AiCLI now renders:

```text
Development proposal approval is complete. A distinct execution decision is
now pending. Type /approve to approve proceeding toward execution, or /cancel
to reject it. No execution is authorized yet.
```

While that state remains pending:

- exact `/approve` transports `APPROVE`;
- exact `/cancel` transports `REJECT`;
- arbitrary text is rejected as ambiguous and leaves the pending review
  unchanged;
- `/exit` does not silently discard the review;
- EOF records `REFERENCE_UHI_SESSION_AWAITING_EXECUTION_DECISION`;
- AiCLI never interprets natural-language approval wording.

The Human Interface stores only the pending canonical review needed for
contextual transport. The new binding runtime owns validation, decision
semantics, confirmation construction, Replay prevention, and fail-closed
results.

## Fail-closed evidence

G31-09 fails closed before confirmation for:

- missing decision;
- ambiguous decision text;
- proposal-approval substitution;
- malformed or non-G31-08 artifacts;
- mismatched session or cross-session review path;
- changed review or execution summary;
- changed authorization scope;
- stale or substituted Repository Cognition evidence;
- changed grounded Worker request;
- already-consumed review;
- confirmation substitution;
- result or wrapper hash substitution;
- reordered Replay steps.

Failed attempts do not partially confirm, authorize, select, dispatch, invoke,
execute, mutate, deploy, or alter another pending conversation.

## Replay continuity

Each G31-09 attempt records two ordered immutable wrappers:

```text
000_execution_authorization_review_source_recorded.json
001_execution_human_decision_recorded.json
```

Positive reconstruction validates wrapper identity and order, validates the
decision result, reconstructs the full nested G31-08 Replay, revalidates the
current repository evidence, checks exact session containment, and validates
the execution-summary confirmation when present.

Rejection reconstruction proves the exact review was explicitly rejected and
that no confirmation exists. Failed reconstruction binds the rejected source
observation hash and preserves all false authority boundaries.

Accepted decisions are located through existing session Replay. A later
attempt for the same review fails closed with `human execution decision already
recorded`. Cross-session review paths fail before confirmation.

## Real PTY evidence

Three disposable Git workspaces each contained one existing implementation
and one focused test. The user supplied only the ordinary request:

```text
Improve the human interface terminal summary behavior. Include focused tests and validation.
```

No path, internal JSON, capability identity, prepared artifact, prompt, or
shell bridge was supplied.

### Approval session

Commands:

```text
/send
/approve
/approve
/exit
```

Observed:

- first approval consumed the proposal;
- G31-08 reached exact positive grounding and pending review;
- state-aware guidance requested the distinct decision;
- second approval produced `EXECUTION_DECISION_HUMAN_CONFIRMED`;
- the existing confirmation artifact validated;
- `approval_count: 2`;
- execution authorization, Worker selection, dispatch, and mutation remained
  false.

### Rejection session

Commands:

```text
/send
/approve
/cancel
/exit
```

Observed:

- `EXECUTION_DECISION_REJECTED`;
- no human-confirmation artifact;
- `approval_count: 1`;
- execution authorization, Worker selection, dispatch, and mutation remained
  false.

### Stale-evidence session

After the G31-08 review was rendered but before the second `/approve`, the
auditor changed the observed source file. The second decision returned:

```text
decision_status: EXECUTION_DECISION_FAILED_CLOSED
failure_reason: repository target evidence is stale or substituted
execution_summary_human_confirmation: False
execution_authorized: False
worker_dispatched: False
repository_mutated: False
```

All three Replays reconstructed successfully in their approved, rejected, or
failed-closed state. The disposable workspaces and runtime were removed.

## Authority boundaries

The following remain false for approved, rejected, and failed decisions:

- proposal approval is execution authorization;
- authorization request created;
- authorization decision created;
- execution authorization artifact created;
- execution authorized;
- Worker selected, assigned, dispatched, or invoked;
- Provider invoked;
- command executed;
- repository mutated;
- deployment reached;
- Human Interface decision authority;
- Human Interface authorization authority.

The existing execution-summary runtime owns confirmation construction. The
G31-09 Platform Core binding owns decision validation. AiCLI transports exact
contextual commands and renders canonical state only.

## Focused and full validation

Focused groups overlap and must not be summed.

| Validation group | Exact result |
|---|---|
| Focused G31-09 | 21 passed, 0 skipped, 0 failed |
| G31-04 through G31-08 | 116 passed, 0 skipped, 0 failed |
| Approval, execution summary, and authorization | 59 passed, 0 skipped, 0 failed |
| Repository Cognition, PPP, and Worker request | 40 passed, 0 skipped, 0 failed |
| Human Interface, AiCLI, and clarification | 73 passed, 0 skipped, 0 failed |
| G28, G29, and Generation 30 | 111 passed, 0 skipped, 0 failed |
| Replay selection | 1,091 passed, 0 skipped, 0 failed; 5,221 deselected |
| Governance selection | 327 passed, 0 skipped, 0 failed; 5,985 deselected |
| Governance conformance tests | 5 passed, 0 skipped, 0 failed |
| Full repository suite, run once after focused suites | **6,310 passed, 4 skipped, 0 failed** |
| targeted `py_compile` | passed |
| `git diff --check` | passed |
| PTY approval, rejection, stale evidence, and Replay | passed |

## Governance result

Governance remains:

`PARTIALLY_CONFORMANT`

The deterministic read-only engine reports:

- checks passed: 18;
- checks failed: 2;
- critical violations: 0;
- deterministic: true;
- fail-closed: true;
- read-only: true;
- report hash:
  `0790499ee53f9a82e15225e15eff1c2637b7e60523fa38be0c921281abe4cbea`.

The two known findings remain the missing expected/installed root pre-commit
hooks and missing `promotion_gate_v02` and `check_layer_freeze` tokens in the
system hook. G31-09 does not repair or hide them.

## Minimal-change accounting

Final G31-09-only worktree statistics:

```text
 aigol/cli/aicli.py                                      | 122 +-
 aigol/cli/aigol_cli.py                                  |   3 +
 aigol/runtime/grounded_execution_authorization_human_decision_binding.py | 365 +
 aigol/runtime/human_interface_runtime_entry_service.py  |   5 +
 docs/governance/G31_09_DISTINCT_HUMAN_EXECUTION_DECISION_BINDING.md | 693 +
 tests/test_g31_09_distinct_human_execution_decision_binding.py | 507 +
 6 files changed, 1692 insertions(+), 3 deletions(-)
```

Category totals:

- runtime and CLI: **492 additions, 3 deletions**;
- tests: **507 additions, 0 deletions**;
- documentation: **693 additions, 0 deletions**;
- total: **1,692 additions, 3 deletions** across 6 files.

The 492-line production change is below the mandatory 500-line stop
condition. No class, state store, router, planner, policy engine, approval
subsystem, authorization subsystem, Worker behavior, Provider behavior,
repository discovery, or new Human Interface command was added.

## New production symbols

| Symbol | Added span | Responsibility and caller | Why an existing symbol was insufficient |
|---|---:|---|---|
| `bind_distinct_human_execution_decision` | 81 lines | Coordinates exact review validation, session binding, replay prevention, confirmation/rejection construction, and persistence; called by AiCLI contextual transport | Existing confirmation constructor validates one summary but does not bind G31-08 review/session/grounding lineage or rejection |
| `validate_distinct_human_execution_decision` | 78 lines | Validates result identity, nested review, exact hashes, confirmation/rejection semantics, and false authority boundaries; called by binder, reconstructor, renderer, tests | No existing validator knows the G31-08-to-decision result |
| `reconstruct_distinct_human_execution_decision` | 26 lines | Reconstructs the two ordered G31-09 wrappers and nested G31-08 Replay; called by tests and future consumers | Existing G31-08 reconstructor stops before a human decision |
| `render_distinct_human_execution_decision` | 18 lines | Renders both approvals, confirmation/rejection, actual authorization, dispatch, mutation, and Replay; called by AiCLI | Existing G31-08 renderer presents only pending review |
| `_accepted_result` | 44 lines | Materializes exact approved/rejected result lineage; called only by binder | Existing confirmation artifact cannot represent explicit rejection or the complete G31 lineage |
| `_failed_result` | 33 lines | Materializes non-confirming fail-closed observation; called only by binder | Existing confirmation constructor rejects invalid input by exception and does not record a G31 attempt |
| `_reject_prior_decision` | 16 lines | Detects already accepted decisions through immutable session Replay; called only by binder | No public consumer checks G31-08 review consumption |
| `_ensure_replay_available` | 6 lines | Prevents partial overwrite of either G31-09 wrapper; called only by binder | `write_json_immutable` protects individual files, not the required pair preflight |
| `_persist` | 7 lines | Builds the G31-09-specific ordered wrapper and delegates immutable canonical writing; called twice by binder | Transport exposes immutable JSON writing but no generic ordered artifact wrapper contract |
| `_text` | 4 lines | Applies the local non-empty FailClosed input boundary; called by binder | No public generic FailClosed string validator exists |
| `_record_contextual_execution_decision` | 42 lines | Transports `/approve` or `/cancel` plus pending canonical review to the binding and projects returned canonical fields; called only by `run_reference_uhi_session` | Existing proposal approval branch cannot represent a second contextual decision |

Modified existing production functions:

- `run_reference_uhi_session` retains the canonical pending review, maps
  existing commands by state, blocks ambiguity/exit, and renders the result;
- `_render_help` changes two descriptions without adding commands;
- `_interactive_grounded_worker_request_execution_authorization_review_turn_summary`
  transports the complete canonical review artifact;
- `run_human_interface_runtime_entry` projects that artifact to the reference
  Human Interface.

## Duplication audit

The G31-07 helper observations were not copied:

- no `_verify_hash`;
- no `_relative_path`;
- no `_unique_relative_paths`.

No canonicalization, timestamp, path, or hash algorithm was added. Public
`replay_hash`, `verify_replay_hash`, and immutable JSON transport are reused.

Three small local idioms are disclosed:

- `_text` is a four-line near-duplicate of contract-specific required-string
  guards because no public generic FailClosed string validator exists;
- `_ensure_replay_available` repeats the repository’s artifact-specific pair
  preflight pattern;
- `_persist` repeats the artifact-specific wrapper shape while delegating all
  canonical serialization, hashing, append-only enforcement, and IO to public
  transport helpers.

They do not create competing canonicalization or Replay systems. Moving these
two artifact-specific operations into shared transport during G31-09 would
broaden the bounded change and modify a certified cross-runtime contract.

## Progress and next blocker

Evidence-scoped progress toward complete no-copy/paste conversational governed
development is **95%**, using the established denominator: G31-03 62%, G31-04
72%, G31-05 80%, G31-06/G31-07 87%, and G31-08 92%.

Evidence-scoped overall project progress toward a certified,
enterprise-demonstrable Product 1 with conversational governed development is
**84%**. Both figures are planning estimates, not certification claims.

Exactly one first blocker remains for G31-10:

`CONFIRMED_GROUNDED_EXECUTION_DECISION_EXECUTION_AUTHORIZATION_BINDING_ABSENT`

G31-09 proves the exact second human decision and stops. The existing
execution-authorization runtime does not yet consume this G31 lineage and
confirmation as its execution-ready authorization input. G31-10 must bind the
accepted second decision to the existing authorization request/decision/
artifact lifecycle without asking the human again and must stop before Worker
selection.

## Complete bounded G31-10 prompt

```text
# Generation 31-10 — Confirmed Grounded Execution Decision to Execution Authorization Binding

Treat Generation 30 and accepted G31-02 through G31-09 as immutable baselines.

G31-09 verdict:

DISTINCT_HUMAN_EXECUTION_DECISION_BINDING_OPERATIONAL

First true blocker:

CONFIRMED_GROUNDED_EXECUTION_DECISION_EXECUTION_AUTHORIZATION_BINDING_ABSENT

Primary priority:

NO_COPY_PASTE_CONVERSATIONAL_GOVERNED_DEVELOPMENT_THROUGH_AICLI

## Objective

Implement exactly one transition.

Consume one approved G31-09 human execution-decision result and bind its exact
G31-08 grounded scope and existing execution-summary confirmation into the
existing execution-authorization request, decision, and authorization
lifecycle.

Do not ask the human for a third confirmation.

Produce either:

1. the existing immutable execution-authorization request, decision, and
   authorization artifact bound to the exact G31-09 confirmation and G31-08
   scope; or
2. the existing fail-closed authorization result when exact compatibility or
   evidence is insufficient.

Stop before Worker selection, assignment, dispatch, Provider invocation,
Worker invocation, command execution, or repository mutation.

## Required reuse

First locate and document the existing contracts for:

- G31-09 decision validation and reconstruction;
- EXECUTION_SUMMARY_ARTIFACT_V1;
- EXECUTION_SUMMARY_HUMAN_CONFIRMATION_ARTIFACT_V1;
- EXECUTION_AUTHORIZATION_REQUEST_ARTIFACT_V1;
- EXECUTION_AUTHORIZATION_DECISION_ARTIFACT_V1;
- EXECUTION_AUTHORIZATION_ARTIFACT_V1;
- existing authorization policy and validators;
- any required execution-ready packet lineage;
- existing Replay reconstruction;
- Human Conversation Experience and Canonical Presentation.

Reuse those contracts. Do not create another approval, confirmation,
authorization, policy, router, selector, Worker-request, state-store, or Replay
subsystem.

Before implementation, determine whether the existing authorization runtime
can consume the G31-09 lineage directly. If it requires an execution-ready
packet, identify the smallest existing deterministic projection that preserves
the exact G31-08 scope. Do not invent a parallel packet family.

## Required lifecycle

Demonstrate through real ./aicli operation:

G31-04 proposal and first approval
  -> G31-05 Worker request
  -> G31-06 repository grounding
  -> G31-08 authorization review
  -> G31-09 second human approval and existing confirmation
  -> existing execution-authorization request
  -> existing authorization decision
  -> existing execution-authorization artifact
  -> stop before Worker selection

The G31-09 second approval is the final human decision for this transition.
Authorization must consume it exactly and must not create or request another
human confirmation.

Authorization scope must equal the G31-08 authorization scope exactly:

- workspace;
- source and focused-test paths;
- symbols and evidence hashes;
- mutation layers;
- validation requirements;
- original human goal;
- Project Objective;
- approved bounded work;
- grounded Worker request;
- complete G31-04 through G31-09 lineage.

It must not broaden targets, commands, operations, authority, duration, or
lifecycle stage.

## Rejection and fail-closed requirements

A G31-09 rejection must never reach authorization.

Fail closed before authorization if:

- any G31-04 through G31-09 identity changes;
- the second human decision is absent, rejected, failed, replayed, substituted,
  or cross-session;
- the execution summary or confirmation changes;
- the grounded scope, repository evidence, Worker request, or mutation layer
  changes;
- authorization scope differs from G31-08 by any field;
- required execution-ready lineage is absent or incompatible;
- authorization policy or Replay validation fails;
- the transition would select or dispatch a Worker, invoke a Provider or
  Worker, execute a command, or mutate the repository.

Invalid evidence must not partially authorize work.

## Architectural and minimal-change constraints

Do not:

- redesign Platform Core, G28, G29, G30, Replay, Governance, or G31-04 through
  G31-09;
- create a third human checkpoint;
- create another authorization runtime or policy engine;
- create a new Worker request or repository grounding;
- add Worker selection, assignment, dispatch, or invocation;
- invoke a Provider;
- execute commands or mutate the repository;
- repair Provider availability or governance hook drift;
- bundle downstream Worker blockers.

Prefer an existing-function binding. Introduce at most one bounded projection
artifact only if deterministic evidence proves the existing authorization
contract cannot represent the G31-09 lineage directly.

If more than 500 production lines are required, stop after investigation and
report the deterministic reason before implementing the larger change.

Report exact insertions/deletions, runtime/test/documentation totals, every new
production symbol and caller, new-file justification, and duplicate-helper
audit. Do not copy G31-07 or G31-09 helper observations.

## Focused tests

Prove at minimum:

1. exact approved G31-09 confirmation reaches existing authorization;
2. no third human confirmation is created;
3. rejection cannot authorize;
4. failed, missing, ambiguous, replayed, or cross-session decision fails;
5. execution-summary or confirmation substitution fails;
6. exact authorization scope equals G31-08 evidence;
7. broadened paths, symbols, tests, layers, validation, or authority fails;
8. stale Repository Cognition evidence fails;
9. G31-04 through G31-09 identity substitution fails;
10. authorization Replay reconstructs and rejects reordering/substitution;
11. no Worker is selected, assigned, dispatched, or invoked;
12. no Provider is invoked;
13. no command executes and no repository mutation occurs;
14. AiCLI owns no authorization or policy semantics;
15. unrelated G28-G31 routes remain unchanged.

## Real PTY validation

Use a disposable Git repository with one implementation and one focused test.

Through real PTY-backed ./aicli, submit one ordinary bounded natural-language
change request and demonstrate:

1. proposal approval;
2. grounded Worker request;
3. separate G31-09 human execution approval;
4. deterministic creation of existing execution authorization without a third
   prompt;
5. truthful stop before Worker selection;
6. a rejection or tampered-confirmation case failing closed;
7. complete nested Replay reconstruction;
8. no dispatch, invocation, command, or mutation.

The user must not supply paths, JSON, capability identities, prepared
artifacts, prompts, or shell bridges. Remove the disposable repository.

## Validation strategy

Run focused suites first. After they pass, run the full repository suite once.

Report exact counts for:

- focused G31-10;
- G31-04 through G31-09 regressions;
- execution-summary and authorization tests;
- Repository Cognition, PPP, and Worker-request tests;
- Human Interface and AiCLI tests;
- G28, G29, and Generation 30;
- Replay and Governance;
- py_compile;
- git diff --check;
- full repository suite.

## Documentation

Add:

docs/governance/G31_10_CONFIRMED_GROUNDED_EXECUTION_DECISION_EXECUTION_AUTHORIZATION_BINDING.md

Document exact reuse, no-third-confirmation evidence, authorization scope,
Replay, rejection and tamper behavior, authority boundaries, PTY evidence,
minimal-change accounting, validation, and exactly one next blocker or
readiness verdict.

## Required final report

Provide implementation verdict, plain-language summary, exact changed files,
commit commands, canonical contracts, authorization lifecycle, PTY evidence,
Replay/tamper evidence, no-third-confirmation proof, authority confirmation,
exact validation/governance counts, per-symbol accounting, project and
no-copy/paste progress, exactly one next blocker or readiness verdict, and the
complete bounded G31-11 prompt.

Architectural minimalism is mandatory.
```

## Final conclusion

G31-09 operationally closes the distinct-human-decision blocker. A real user
can approve a proposal and then separately approve or reject proceeding toward
execution through the existing state-aware AiCLI commands. Approval creates
the existing execution-summary confirmation; rejection remains explicitly
non-confirming. Neither state authorizes execution or crosses the Worker,
Provider, command, or mutation boundary.
