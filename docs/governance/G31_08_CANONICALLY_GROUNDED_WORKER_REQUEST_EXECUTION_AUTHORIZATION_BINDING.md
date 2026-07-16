# Generation 31-08 — Canonically Grounded Worker Request Execution Authorization Binding

Status: operational; bounded execution-authorization review binding complete.

Date: 2026-07-16

Verdict:

`GROUNDED_WORKER_REQUEST_EXECUTION_AUTHORIZATION_REVIEW_BINDING_OPERATIONAL`

Exactly one next blocker:

`GROUNDED_EXECUTION_AUTHORIZATION_REVIEW_DISTINCT_HUMAN_DECISION_BINDING_ABSENT`

## Constitutional scope

Generation 30 and accepted G31-02, G31-04, G31-05, G31-06, and G31-07 remain
immutable baselines. G31-08 implements one transition only:

```text
G31-04 proposal approval
  -> G31-05 goal-faithful Worker payload
  -> G31-06 exact repository grounding
  -> existing execution-summary review checkpoint
  -> stop pending a distinct human execution-authorization decision
```

This generation does not merge proposal approval with execution
authorization. It does not create human confirmation, an authorization
request, an authorization decision, or execution authorization. It does not
select, assign, dispatch, or invoke a Worker; invoke a Provider; execute a
command; mutate the repository; validate implementation output; or certify a
result.

## Pre-implementation contract audit

The smallest admissible transition reuses these existing owners:

| Existing contract | Owner | G31-08 use |
|---|---|---|
| `CANONICAL_REPOSITORY_SCOPE_GROUNDING_ARTIFACT_V1` validation and reconstruction | G31-06 Repository Cognition grounding | Supplies immutable upstream identities, exact source/test paths, symbols, hashes, mutation layers, and the grounded Worker request |
| `WORKER_REQUEST_ARTIFACT_V1` public validation | Existing implementation-request-to-Worker-request bridge | Supplies the unchanged objective, bounded work, validation requirements, and false execution flags |
| `EXECUTION_SUMMARY_ARTIFACT_V1` creation and validation | Existing execution-summary runtime | Represents the non-authoritative execution-authorization review and mandatory distinct human confirmation checkpoint |
| `EXECUTION_SUMMARY_HUMAN_CONFIRMATION_ARTIFACT_V1` | Existing execution-summary runtime | Remains absent in G31-08; it is the later human-decision evidence and is not synthesized from proposal approval |
| `EXECUTION_AUTHORIZATION_REQUEST_ARTIFACT_V1`, decision, authorization, and result | Existing execution-authorization runtime | Declared as the downstream lifecycle; none is created or invoked by G31-08 |
| `verify_replay_hash`, `load_json`, `write_json_immutable` | Canonical transport | Supplies public hash verification and immutable Replay persistence without copying G31-06 hash helpers |
| Platform Core turn summary, Human Interface runtime-entry projection, and reference AiCLI renderer | Existing Human Conversation Experience and presentation path | Transport and render canonical review state without owning policy or authorization semantics |

The existing execution-authorization runtime consumes an execution-ready
packet lineage and a separately confirmed execution summary. Calling
`authorize_execution_ready` in G31-08 would manufacture confirmation when it
is omitted and would cross the explicit human checkpoint. The G31-06 grounded
Worker request is not the runtime’s existing execution-ready packet family.

The smallest correct binding is therefore one immutable review-lineage
artifact containing the existing pending execution summary and the exact
G31-06 scope. No authorization runtime behavior was changed.

## Implemented binding

G31-08 introduces one bounded Platform Core binding artifact:

`GROUNDED_WORKER_REQUEST_EXECUTION_AUTHORIZATION_REVIEW_BINDING_ARTIFACT_V1`

Its positive status is:

`GROUNDED_WORKER_REQUEST_EXECUTION_AUTHORIZATION_REVIEW_REQUIRED`

Its fail-closed status is:

`GROUNDED_WORKER_REQUEST_EXECUTION_AUTHORIZATION_REVIEW_FAILED_CLOSED`

The binding coordinator performs only these operations:

1. records the supplied G31-06 artifact as an immutable observation;
2. validates the G31-06 artifact against the current workspace;
3. reconstructs the complete nested G31-06 Replay;
4. validates the existing grounded Worker request;
5. copies the exact grounded evidence into an authorization-review scope;
6. creates the existing non-authoritative pending execution summary;
7. records one immutable review binding;
8. stops before human confirmation and all authorization or Worker stages.

If any validation fails, the runtime records only a fail-closed observation
hash, failure reason, false authority boundaries, and ordered Replay. It does
not retain a partially accepted scope or execution summary.

## Exact authorization-review evidence

The `authorization_scope` is a deterministic projection of G31-06 and contains
only:

- exact resolved workspace identity;
- grounding identity and artifact hash;
- Repository Cognition snapshot and grounding-evidence hashes;
- grounded Worker-request identity and hash;
- existing repository-relative source and focused-test paths;
- complete target evidence, including source identities and content hashes;
- existing symbols and symbol-evidence hashes;
- existing mutation layers and mapping rules;
- approved validation requirements;
- original human goal and hash;
- canonical Project Objective and hash;
- approved bounded work;
- unchanged Worker objective;
- complete approved-work lineage;
- one deterministic scope hash.

The existing `EXECUTION_SUMMARY_ARTIFACT_V1` carries this scope unchanged and
has:

- `summary_status: PENDING_HUMAN_CONFIRMATION`;
- `authorization_required: true`;
- `human_review_required: true`;
- all execution-summary authority flags false;
- an expected `EXECUTION_SUMMARY_HUMAN_CONFIRMATION_ARTIFACT_V1`;
- explicit constraints that proposal approval is not execution authorization
  and that the later authorization scope must be equal to the grounded scope.

The G31-08 artifact declares the existing downstream authorization artifact
types but creates none of them.

## Approval versus authorization

G31-04 proposal approval remains necessary upstream evidence. G31-08 proves it
is not sufficient execution authority:

| State | Value after G31-08 |
|---|---|
| proposal approval consumed | true, as immutable G31-04 lineage |
| proposal approval is execution authorization | false |
| distinct human execution authorization required | true |
| human confirmation recorded | false |
| authorization request created | false |
| authorization decision created | false |
| execution authorization created | false |
| execution authorized | false |
| dispatch blocked pending authorization | true |
| Worker selected | false |

The Human Interface projects and renders these values. It does not decide
policy, construct scope, confirm intent, or authorize execution.

## Scope continuity and fail-closed behavior

Validation recomputes the exact authorization scope from the nested validated
G31-06 artifact. A consumer cannot make a broadened scope valid merely by
rehashing the changed object.

The binding rejects:

- substituted G31-04, G31-05, or G31-06 identities;
- stale or substituted Repository Cognition evidence;
- changed workspace, paths, symbols, tests, layers, or content hashes;
- broadened repository targets;
- changed validation requirements;
- a substituted grounded Worker request;
- a changed original goal, Project Objective, bounded work, or Worker
  objective;
- a modified execution-summary scope or hash;
- synthesized human confirmation;
- any true authorization, Worker, Provider, execution, or mutation boundary;
- reordered or substituted G31-08 Replay wrappers;
- missing or invalid nested G31-06 Replay.

Invalid evidence never partially authorizes work. Failed review artifacts
contain no authorization scope and no execution summary.

## Replay continuity

G31-08 records two ordered immutable wrappers:

```text
000_repository_scope_grounding_source_recorded.json
001_execution_authorization_review_binding_recorded.json
```

Positive reconstruction verifies both wrapper hashes and order, validates the
review artifact with the public hash contract, reconstructs the nested G31-06
Replay, checks source grounding identity, re-observes current repository
evidence, recomputes the exact scope, verifies the existing execution summary,
and confirms every false authority boundary.

Failed reconstruction verifies the observation hash and proves that no scope,
summary, confirmation, authorization, selection, dispatch, invocation, or
mutation was recorded.

## Human Interface composition

The Platform Core operational path now composes G31-08 immediately after
G31-06. Its turn summary reports `AUTHORIZATION_REVIEW` and
`WAITING_FOR_APPROVAL`, with the next action explicitly requiring a distinct
execution-authorization approval or rejection.

`human_interface_runtime_entry_service` transports canonical review fields.
The reference AiCLI renders status and hashes plus the approval-versus-
authorization and dispatch boundaries. AiCLI contains no call to
`authorize_execution_ready`, no Worker selector, and no scope or policy
interpretation.

## Real PTY validation

A disposable Git repository was created with exactly:

- `aigol/runtime/human_interface.py`, containing one `render_summary` function;
- `tests/test_human_interface.py`, containing one focused test.

The real command was:

```text
./aicli --session-id G31-08-PTY \
  --created-at 2026-07-16T00:00:00Z \
  --runtime-root /tmp/sapianta-g31-08-runtime \
  --workspace /tmp/sapianta-g31-08-pty
```

The user supplied only this ordinary request and terminal control commands:

```text
Improve the human interface terminal summary behavior. Include focused tests and validation.
/send
/approve
/exit
```

No paths, JSON, capability identities, prepared artifacts, prompts, or shell
bridges were supplied by the user.

Observed positive evidence:

| Evidence | Result |
|---|---|
| G31-04 proposal and approval | rendered and consumed |
| G31-05 Worker payload | created with immutable task and payload hashes |
| G31-06 grounding | `CANONICAL_REPOSITORY_SCOPE_GROUNDED` |
| grounded targets | `aigol/runtime/human_interface.py`, `tests/test_human_interface.py` |
| grounded Worker-request hash | `sha256:70cb1774aebcc200a07676f27a0269b3c02d780bf0f48e1d7bc2a5432a4131ef` |
| authorization scope hash | `sha256:d793f137fc5bff2b988aaac5ce94abb34f42752908fe26c00f14926280070da2` |
| execution summary hash | `sha256:67d044fb1aa075c4c5320c7066c01ef18f60e4eacd4156ec05727cffcc9aeb5b` |
| review binding hash | `sha256:2fc38ce0c62df6bc5bc06050e903fa2c53df4b5ffc26cab58b5908be05e240b6` |
| current execution authorization | false |
| Worker selected or dispatched | false |
| Provider or Worker invoked | false |
| repository mutated | false |

The completed PTY Replay reconstructed successfully. An external audit then
substituted the observed source content without changing the recorded
grounding. Reconstruction failed closed with:

```text
repository target evidence is stale or substituted
```

This proves a tampered or broadened state cannot be reconstructed as review-
ready. The disposable repository and runtime were removed afterward.

## Validation results

Focused groups overlap and must not be summed.

| Validation | Exact result |
|---|---|
| Focused G31-08 | 33 passed, 0 skipped, 0 failed |
| G31-04 through G31-06 regressions | 83 passed, 0 skipped, 0 failed |
| Approval and execution-authorization group | 53 passed, 0 skipped, 0 failed |
| Repository Cognition, Project Services, PPP, and Worker-request group | 40 passed, 0 skipped, 0 failed |
| Clarification, Human Interface, and AiCLI group | 73 passed, 0 skipped, 0 failed |
| G28, G29, G30, and G31-02 group | 117 passed, 0 skipped, 0 failed |
| Replay-or-Governance selection | 1,375 passed, 0 skipped, 0 failed; 4,916 deselected |
| Governance conformance tests | 5 passed, 0 skipped, 0 failed |
| Full repository suite | **6,289 passed, 4 skipped, 0 failed** |
| targeted `py_compile` | passed |
| `git diff --check` | passed |
| real PTY positive and tamper validation | passed |

## Governance result

Repository governance remains:

`PARTIALLY_CONFORMANT`

The read-only deterministic conformance engine reports:

- checks passed: 18;
- checks failed: 2;
- critical violations: 0;
- deterministic: true;
- fail-closed: true;
- read-only: true;
- report hash:
  `0790499ee53f9a82e15225e15eff1c2637b7e60523fa38be0c921281abe4cbea`.

The two known findings remain unchanged: missing expected/installed root
pre-commit hooks and missing `promotion_gate_v02` and `check_layer_freeze`
tokens in the system hook. G31-08 does not hide or repair them. Neither finding
invalidates the bounded operational transition.

## Change size and minimality

Final direct-worktree statistics:

```text
 aigol/cli/aicli.py                                      |  10 +
 aigol/cli/aigol_cli.py                                  | 137 +-
 aigol/runtime/grounded_worker_request_execution_authorization_binding.py | 579 +
 aigol/runtime/human_interface_runtime_entry_service.py  |  34 +
 docs/governance/G31_08_CANONICALLY_GROUNDED_WORKER_REQUEST_EXECUTION_AUTHORIZATION_BINDING.md | 599 +
 tests/test_g15_runtime_06_governed_development_runtime_continuation.py | 15 +-
 tests/test_g31_08_grounded_worker_request_execution_authorization_binding.py | 546 +
 7 files changed, 1915 insertions(+), 5 deletions(-)
```

Category totals:

- runtime and CLI: **757 additions, 3 deletions**;
- tests: **559 additions, 2 deletions**;
- documentation: **599 additions, 0 deletions**;
- total: **1,915 additions, 5 deletions** across 7 files.

Runtime size is dominated by explicit immutable lineage, exact-scope
validation, false authority boundaries, and nested Replay reconstruction. It
introduces one module and no class, index, router, selector, policy engine,
approval system, authorization system, Worker request, or Replay subsystem.

No G31-06 helper was copied. In particular, the new module contains none of:

- `def _verify_hash`;
- `def _relative_path`;
- `def _unique_relative_paths`.

It uses public `verify_replay_hash` for artifact and wrapper identity.

### New-file justification

- `aigol/runtime/grounded_worker_request_execution_authorization_binding.py`
  owns the one new evidence transition, its validation, ordered Replay, and
  canonical rendering. Existing artifacts cannot retain the G31-06 scope plus
  the pending human checkpoint without changing their accepted ownership.
- `tests/test_g31_08_grounded_worker_request_execution_authorization_binding.py`
  supplies the focused positive, identity, scope, authority, stale-evidence,
  tamper, Replay, and real-AiCLI evidence.
- this report records the constitutional evidence, validation, limits, and
  next bounded transition.

### Modified-runtime justification

- `aigol/cli/aigol_cli.py` invokes the binding after G31-06 and projects the
  canonical review state into the existing workflow summary. It performs no
  authorization logic.
- `aigol/runtime/human_interface_runtime_entry_service.py` transports the
  already-decided review status and boundaries to the reference interface.
- `aigol/cli/aicli.py` renders canonical fields only.

The G15 test update is compatibility evidence: the same route now ends at the
G31-08 review state instead of the superseded G31-06 terminal state.

## Authority confirmation

The operational result truthfully preserves:

- Platform Core ownership of the exact review scope and state;
- Repository Cognition ownership of targets and evidence;
- the execution-summary runtime’s human-confirmation checkpoint;
- the execution-authorization runtime as the unchanged later authority;
- Human Interface transport/rendering only;
- Replay ownership of immutable reconstruction;
- separate Worker and Provider authority.

The following are all false: execution authorized, Worker selected, Worker
assigned, Worker dispatched, Worker invoked, Provider invoked, execution
started, repository mutated, validation executed, certification reached,
Human Interface authorization authority, and Human Interface policy authority.

## Progress and exactly one next blocker

Evidence-scoped progress toward complete no-copy/paste conversational governed
development is **92%**, using the same denominator as G31-03 (62%), G31-04
(72%), G31-05 (80%), and G31-06/G31-07 (87%). This is a planning estimate, not
a certification claim.

The one next blocker is:

`GROUNDED_EXECUTION_AUTHORIZATION_REVIEW_DISTINCT_HUMAN_DECISION_BINDING_ABSENT`

G31-08 exposes the distinct checkpoint and stops. The reference AiCLI does not
yet consume a second, review-bound human approval or rejection into the
existing `EXECUTION_SUMMARY_HUMAN_CONFIRMATION_ARTIFACT_V1`. Proposal approval
must not fill that gap. Worker selection, Provider availability, execution,
mutation, validation, and certification are downstream observations and are
not bundled into this blocker.

## Proposed Generation 31-09 prompt

```text
# Generation 31-09 — Distinct Grounded Execution-Authorization Human Decision Binding

Treat Generation 30 and accepted G31-02, G31-04, G31-05, G31-06, G31-07, and
G31-08 as immutable baselines.

G31-08 verdict:

GROUNDED_WORKER_REQUEST_EXECUTION_AUTHORIZATION_REVIEW_BINDING_OPERATIONAL

First true blocker:

GROUNDED_EXECUTION_AUTHORIZATION_REVIEW_DISTINCT_HUMAN_DECISION_BINDING_ABSENT

Primary priority:

NO_COPY_PASTE_CONVERSATIONAL_GOVERNED_DEVELOPMENT_THROUGH_AICLI

## Objective

Implement exactly one transition.

Consume one explicit second human approval or rejection for the exact pending
G31-08 execution-authorization review. Bind an approval to the existing
EXECUTION_SUMMARY_HUMAN_CONFIRMATION_ARTIFACT_V1, or retain an existing
fail-closed rejected/clarification state.

Stop before creation of execution authorization, Worker selection, assignment,
dispatch, Provider invocation, Worker invocation, or repository mutation.

Proposal approval must remain distinct and must not be reused as this second
human decision.

## Required reuse

First locate and document the existing contracts for:

- G31-08 review artifact validation and reconstruction;
- EXECUTION_SUMMARY_ARTIFACT_V1;
- create_execution_summary_confirmation and its validator;
- existing Platform Core conversation continuation and approval/rejection
  presentation;
- existing execution-authorization runtime as a later unchanged owner;
- Replay reconstruction;
- Human Interface opaque decision transport.

Reuse those contracts. Do not create a new approval system, confirmation
system, authorization system, policy engine, router, selector, Worker request,
clarification system, or Replay subsystem.

## Required lifecycle

Demonstrate through real ./aicli operation:

G31-04 proposal and first approval
  -> G31-05 goal-faithful Worker payload
  -> G31-06 exact repository grounding
  -> G31-08 pending execution-authorization review
  -> explicit second human approve or reject decision
  -> existing summary-bound human confirmation for approval, or fail-closed
     rejected/clarification state
  -> stop before execution authorization and Worker selection

The second decision must bind exactly:

- G31-08 review identity and hash;
- execution-summary identity and hash;
- authorization-scope hash;
- complete G31-04 through G31-08 lineage;
- human actor and deterministic decision time;
- one explicit APPROVE or existing fail-closed non-approval outcome.

The decision must not broaden workspace, paths, symbols, tests, layers,
validation requirements, objective, bounded work, operations, commands, or
authority.

## Fail-closed requirements

Reject before confirmation readiness if:

- any G31-04 through G31-08 identity changes;
- the execution summary or authorization scope changes;
- Repository Cognition evidence is stale or substituted;
- the second decision is missing, ambiguous, replayed, substituted, or bound to
  another session or review;
- proposal approval is presented as the second decision;
- a rejection is interpreted as approval;
- the transition would implicitly call authorize_execution_ready, create
  execution authorization, select a Worker, invoke a Provider or Worker, or
  mutate the repository.

Invalid evidence must not partially confirm or authorize work.

## Minimal-change rule

Prefer existing create_execution_summary_confirmation and conversation-state
bindings. Introduce at most one bounded continuation artifact only if the
existing confirmation cannot preserve the required G31-08 lineage directly.

Do not modify G31-08 behavior. Do not adapt or call the authorization runtime
until a later bounded generation proves compatible execution-ready lineage.

If broad changes are required, stop and report the deterministic reason.

Report git diff --stat, runtime/test/documentation line counts, justification
for every runtime file, and any duplicated helper logic.

## Focused tests

Prove:

- first proposal approval and second execution decision remain distinct;
- the second approval binds the exact G31-08 summary and scope;
- rejection remains non-authorizing and fail closed;
- missing, duplicate, stale, substituted, reordered, cross-session, or
  broadened decisions fail closed;
- no command, target, authority, Worker, or Provider is invented;
- no execution authorization, Worker selection, dispatch, invocation, or
  mutation occurs;
- AiCLI owns no confirmation, authorization, or policy semantics;
- Replay reconstructs and rejects tampering;
- unrelated G28-G31 routes remain unchanged.

## PTY validation

Use a disposable Git repository containing one implementation and one focused
test. Through real PTY-backed ./aicli, submit one ordinary bounded
natural-language change request and demonstrate:

1. G31-04 proposal and first approval;
2. G31-05 Worker payload;
3. G31-06 repository grounding;
4. G31-08 separate authorization review;
5. an explicit second human approval producing only the existing confirmation;
6. a fresh rejection or tampered-decision case failing closed;
7. complete Replay reconstruction;
8. truthful stop before execution authorization and Worker selection.

The user must not supply paths, internal JSON, capability names, prepared
artifacts, Codex prompts, or shell bridges. Remove the repository afterward.

## Validation

Run and report exact results for:

- focused G31-09 tests;
- G31-04 through G31-08 regressions;
- execution-summary confirmation and execution-authorization tests;
- Repository Cognition, PPP, and Worker-request tests;
- clarification, approval, Human Interface, and AiCLI tests;
- G28, G29, G30, and G31-02;
- Replay and Governance;
- py_compile;
- git diff --check;
- full repository suite.

## Documentation

Add:

docs/governance/G31_09_DISTINCT_GROUNDED_EXECUTION_AUTHORIZATION_HUMAN_DECISION_BINDING.md

Document exact reuse, decision identity, first-versus-second approval semantics,
scope continuity, rejection behavior, Replay, PTY evidence, authority
boundaries, validation, change size, and exactly one next blocker or readiness
verdict.

## Non-goals

Do not:

- redesign certified architecture;
- merge proposal approval with execution authorization;
- modify G31-08 behavior;
- create execution authorization;
- select, assign, dispatch, or invoke a Worker;
- invoke a Provider;
- mutate the repository;
- implement Worker cognition, validation, certification, or completion;
- repair Provider availability or governance hook drift;
- bundle downstream blockers;
- claim complete no-copy/paste readiness.

## Required final report

Provide implementation verdict, changed files and change size, reused
confirmation contracts, exact decision evidence, positive and fail-closed PTY
results, Replay and tamper evidence, first-versus-second approval confirmation,
authority boundaries, exact validation and governance results, exactly one next
blocker or readiness verdict, no-copy/paste progress, exact git status and
commit commands, and the complete bounded next-generation prompt.

Architectural minimalism is mandatory.
```

## Final conclusion

The bounded G31-08 transition is operational. A canonically grounded Worker
request now reaches an immutable, exact-scope execution-authorization review
through real AiCLI operation. The existing distinct human checkpoint is
visible and Replay-bound, while proposal approval, authorization, Worker,
Provider, execution, and mutation boundaries remain separate.

No-copy/paste conversational governed development is not yet complete. The
only accepted next transition is consumption of the distinct review-bound
human decision.
