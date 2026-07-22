# Generation 31-24G-R04-R04-R07 Authenticated Replacement Request to Single-Use Authorization Consumption Binding

Status: operational; bounded implementation and deterministic validation complete.

Date: 2026-07-22

Verdict:

`G31_AUTHENTICATED_REPLACEMENT_REQUEST_TO_SINGLE_USE_AUTHORIZATION_CONSUMPTION_BINDING_OPERATIONAL`

Exactly one next state:

`G31_24G_R04_R04_R08_CONSUMED_REPLACEMENT_REQUEST_TO_EXISTING_CERTIFIED_WORKER_SELECTION_BINDING_REQUIRED`

## Constitutional scope

This result treats Generation 30 and the accepted G31 common-entry, R05, and
R06 results as immutable certified baselines. It binds one already-recorded R06
authenticated replacement request to the existing hardened replacement owner's
single-use authorization-consumption event. It does not reopen or redistribute
Platform Core, Governance, Replay, Certification, Human Interface, Worker,
Provider, authorization, request, or mutation authority.

The transition stops after immutable consumption and Replay reconstruction.
Worker selection, assignment, dispatch, invocation, Provider invocation,
command execution, target opening, repository mutation, restoration, rollback,
and recovery remain unreached.

No live PTY workflow was run, as required.

## Baseline evidence

The implementation began from:

- branch: `master`;
- HEAD: `5760196ce981d83bff900d1b181272a88320b5bc`;
- HEAD subject: `feat(runtime): bind mutation authorization to authenticated request`;
- R06 verdict:
  `G31_MUTATION_AUTHORIZATION_TO_AUTHENTICATED_REPLACEMENT_REQUEST_BINDING_OPERATIONAL`;
- R06 next state:
  `G31_24G_R04_R04_R07_AUTHENTICATED_REPLACEMENT_REQUEST_TO_SINGLE_USE_AUTHORIZATION_CONSUMPTION_BINDING_REQUIRED`.

All pre-existing modified and untracked protected paths were recorded before
implementation and were preserved byte-for-byte. Nothing was staged or committed.

## Existing contracts reused

The implementation reuses the following existing contracts without creating a
parallel subsystem:

| Requirement | Existing owner reused |
|---|---|
| authenticated request schema and validation | `AUTHORIZED_REPLACE_EXISTING_FILE_REQUEST_V2` and `validate_authenticated_replace_request_v2` |
| request construction | `create_g31_authenticated_replace_request` |
| R06 request recording | `record_authenticated_replace_request_v2` |
| request and lifecycle Replay | `reconstruct_authenticated_replace_replay_v2` |
| authorization validation and actor-bound Replay | existing R05 authorization and actor reconstruction owners |
| deterministic lifecycle destinations | `g31_replace_destinations` |
| immutable event persistence | existing `_persist_v2_event` exclusive writer |
| single-use identity | existing `AUTHORIZATION_CONSUMPTION_CLAIMED` event with the authorization hash |
| common application transition | `run_human_interface_runtime_entry` |
| lifecycle aggregation | `_authorize_g31_mutation_decision` and `_continue_g31_application_transition` |
| user-visible result | existing Canonical Presentation collection |

No new authorization, request, locking, Replay, Worker, Provider, command,
mutation, restoration, rollback, or recovery subsystem was introduced. No new
artifact family or runtime module was added.

## Exact request-to-consumption sequence

The common application transition now performs exactly this bounded sequence for
an authentic `APPROVED` V3 mutation decision:

```text
reconstruct exact APPROVED V3 decision
  -> reconstruct exact mutation authorization and actor-bound Replay
  -> construct and record exactly one authenticated R06 request
  -> reconstruct the exact request-only Replay
  -> require request Replay as the sole predecessor
  -> persist one AUTHORIZATION_CONSUMPTION_CLAIMED event through _persist_v2_event
  -> reconstruct request plus consumption Replay
  -> aggregate canonical lifecycle state and presentation
  -> stop before Worker selection
```

`consume_authenticated_replace_authorization_v2` does not record the R06 request.
It validates the already-recorded request, reconstructs the request-only stage,
claims the authorization once through the existing exclusive event writer, and
reconstructs the resulting two-event chain.

The R05 authorization construction owner is not called by the consumption owner.
The consumption owner accepts the exact request and uses existing validation and
Replay reconstruction to prove its authorization lineage.

## Single-use identity and evidence binding

The immutable consumption identity is exactly:

```text
consumption_identity == authorization_hash
```

The consumed identity remains transitively and directly bound to:

- authorization ID, hash, status, actor, and actor-bound Replay;
- request ID and request hash;
- repository and session identity;
- mutation decision and decision Replay;
- candidate and candidate Replay;
- Repository Cognition grounding and candidate provenance;
- existing target path;
- expected preimage and postimage hashes;
- exact replacement content and content hash;
- source and replacement modes;
- fixed hardened lifecycle destinations;
- the request-stage Replay hash and sole predecessor wrapper.

The request-stage Replay reconstruction is retained unchanged in the common-entry
result. The consumption reconstruction separately records
`request_stage_replay_hash`, the final lifecycle Replay hash, and the exact
authorization-hash consumption identity.

## Replay and concurrency

The existing immutable writer uses exclusive creation. Two concurrent claims for
one request therefore have exactly one winner. The winner persists the canonical
consumption wrapper; the competing claim fails closed. A sequential second claim
also fails because the lifecycle is no longer request-only.

Replay reconstruction now validates the full immutable identity carried by every
hardened V2 event, not merely the event's request hash. It also validates the
canonical request event type and empty payload, and the canonical consumption event
type and exact authorization-hash payload.

Tests prove rejection of:

- absent, corrupt, unexpected, removed, substituted, or reordered request Replay;
- substituted request or consumption event types or payloads;
- changed authorization ID, hash, status, actor, or Replay;
- changed repository, session, decision, candidate, grounding, or provenance;
- changed target, preimage, postimage, replacement content or hash;
- changed source mode, replacement mode, worker identity, or destination;
- changed request hash;
- a non-request lifecycle artifact before consumption;
- duplicate sequential and competing concurrent claims.

Invalid evidence reaches no consumption event. Once a valid immutable winner exists,
later Replay tampering causes reconstruction to fail closed and does not create a
second claim.

## Common-entry and adapter boundaries

`run_human_interface_runtime_entry` remains the public application transition. An
in-memory non-AiCLI adapter reaches the same canonical state. The test supplies
terminal-only display fields and proves that they are absent from the authenticated
request and do not affect the consumption identity.

AiCLI still calls only the common runtime entry and owns no request, Replay,
consumption, authorization, Worker, Provider, command, mutation, restoration,
rollback, or recovery semantics. Static import-boundary tests prove that AiCLI does
not call the new bounded owner or the hardened private lifecycle owners.

Canonical Presentation now truthfully renders:

- authorization consumed: true;
- the exact single-use consumption identity;
- authorization consumption reached: true;
- Worker selection reached: false;
- repository mutated: false.

## Forbidden downstream reachability

Focused spies and canonical result flags prove zero calls or effects for:

- Worker selection, assignment, dispatch, and invocation;
- Provider invocation;
- authenticated replacement execution and recovery;
- target opening;
- command execution;
- replacement-byte writes and repository mutation;
- atomic restoration, rollback, and recovery.

The only hardened lifecycle files created by the positive transition are:

```text
000_request.json
001_consumption.json
```

No journal, started, atomic, result, completion, termination, rollback, or recovery
event is persisted.

## Minimality, symbols, and change size

Exactly two production files were modified, within the three-file ceiling. No new
production file was introduced.

Production delta before this report:

- **116 insertions, 4 deletions**;
- `aigol/runtime/human_interface_runtime_entry_service.py`: 22 insertions,
  3 deletions;
- `aigol/workers/filesystem_replace_worker.py`: 94 insertions, 1 deletion.

Exactly one new production symbol was added:

- `consume_authenticated_replace_authorization_v2` — validates an already-recorded
  R06 request, requires exact request-only Replay, persists the existing immutable
  consumption event once, reconstructs the two-event chain, and returns explicit
  stop-boundary flags.

Exactly three existing production symbols were modified:

- `reconstruct_authenticated_replace_replay_v2` — validates full event identity and
  canonical request/consumption event semantics;
- `_authorize_g31_mutation_decision` — calls the bounded consumption owner after the
  one R06 recording step and retains its reconstruction;
- `_continue_g31_application_transition` — renders truthful consumption and stop
  state through Canonical Presentation.

No hash, path, destination, locking, serialization, or Replay helper was copied.
In particular, no local `_verify_hash`, `_relative_path`, or
`_unique_relative_paths` helper was added. The event identity projection inside the
existing reconstructor is validation data, not a second hashing or Replay owner.

Test delta before this report:

- **411 insertions, 11 deletions**;
- one new 397-line focused R07 test module;
- 14 insertions and 11 deletions across four predecessor expectation modules.

The predecessor test changes only update the common-entry expected terminal state
from request-only/unconsumed to request-plus-consumption/consumed. They do not alter
the immutable R01, R05, or R06 runtime implementations.

## Validation

Validation was run in the required order. Distinct focused results were:

- focused R07: **33 passed, 0 skipped, 0 failed**;
- R06 request binding: **19 passed, 0 skipped, 0 failed**;
- R05 authorization: **11 passed, 0 skipped, 0 failed**;
- R01 common-entry and adapters: **4 passed, 0 skipped, 0 failed**;
- hardened request and consumption owner: **31 passed, 0 skipped, 0 failed**;
- candidate, V3 decision, authorization, actor Replay, and AiCLI V3 lineage:
  **37 passed, 0 skipped, 0 failed**;
- G0-G30 Human Interface, AiCLI, Canonical Presentation, and operational route:
  **88 passed, 0 skipped, 0 failed**;
- directly affected earlier G31 common-entry lifecycle:
  **24 passed, 0 skipped, 0 failed**;
- architecture and runtime-boundary group:
  **51 passed, 0 skipped, 0 failed**;
- Governance conformance tests: **5 passed, 0 skipped, 0 failed**;
- all Generation 31 tests in the authoritative full-suite XML:
  **523 passed, 0 skipped, 0 failed**;
- targeted `py_compile`: passed;
- parent `git diff --check`: passed;
- all three nested repository `git diff --check` checks: passed;
- complete repository suite, run exactly once after focused success:
  **6,692 passed, 4 skipped, 0 failed** in **4,364.75 seconds (1:12:44)**.

Focused counts overlap the full suite and must not be added together.

The four full-suite skips are visible and non-blocking:

1. the collected nested credit constitutional-flow item;
2. local runtime ingestion requiring a socket unavailable in the sandbox;
3. real localhost post-invocation requiring a socket unavailable in the sandbox;
4. opt-in real OpenAI Provider certification requiring its environment flag and
   API key.

No live Provider call and no live R07 PTY workflow were attempted.

## Governance result

The deterministic read-only conformance engine remains:

`PARTIALLY_CONFORMANT`

- checks passed: 18;
- checks failed: 2;
- critical violations: 0;
- deterministic: true;
- fail-closed: true;
- read-only: true;
- report hash:
  `0790499ee53f9a82e15225e15eff1c2637b7e60523fa38be0c921281abe4cbea`.

The two known findings remain unchanged: the root expected and installed pre-commit
hooks are missing, and the system pre-commit hook lacks `promotion_gate_v02` and
`check_layer_freeze`. R07 neither hides nor repairs that drift.

## Protected state and nested repositories

Pre-implementation and post-validation SHA-256 values are identical:

| Protected path | SHA-256 |
|---|---|
| `diagnostic_evidence.json` | `a626a69a8020bc730876119c52701a94de9ab6e4772cc64c1f5d017296650203` |
| `governed_return.json` | `e82f47c0c13678725993b21e2af2e0437edccaed324f861a7b58e77d7f8e787d` |
| `lineage.json` | `07b95505521e70f51cdddecc1057fd3a208b198445693c9a8da1e996df5799dd` |
| `provider_stderr.txt` | `d47a06d59aba2814c3fb7460049fc2ccbfc834196c956d6c6558e8be8b079e24` |
| `provider_stdout.txt` | `a73a499e2e9133c03d7babfd5c4dec7967f31e2bfb354ea9dd41df0a15c08cb3` |
| `governed_returns.jsonl` | `dbc7b63f2a17c50c43bbb4fde4f44c1dbae8d25d550fb6b4d4daa14e17126161` |
| each protected marker | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

The nested repositories remain clean at their original commits:

- `sapianta-domain-credit`: `8615e1e290471a67e4e764c6ab2138340bc7936f`;
- `sapianta_system`: `3183bab71f8f30397c0309dd2e6d846d14a11f66`;
- `sapianta-domain-trading`: `d3038dc4ba36ffbaee9161172b4c852e8e6acbda`.

Nothing is staged and no commit was created.

## Progress estimate

Evidence-scoped planning estimates only:

- Generation 31 no-copy/paste governed-development lifecycle: **99.97%**;
- whole project toward the current bounded Product 1 and governed-development
  objective: **98.1%**.

These are not production-readiness or certification claims. Single-use consumption
is operational; Worker selection, dispatch, invocation, command execution, mutation,
post-mutation validation, certification, and release remain separately governed.

## Exact scoped delta and Git status

The documentation delta is **595 insertions, 0 deletions** in
this one required report. The complete R07-scoped delta is eight files with
**1,122 insertions and 15 deletions**:

- two modified production files;
- four modified predecessor test files;
- one new focused test file;
- this one new governance report.

Exact final `git status --short`:

```text
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/diagnostic_evidence.json
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/governed_return.json
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/lineage.json
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/provider_stderr.txt
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/provider_stdout.txt
 M .runtime/aigol/ledger/governed_returns.jsonl
 M aigol/runtime/human_interface_runtime_entry_service.py
 M aigol/workers/filesystem_replace_worker.py
 M tests/test_g31_24g_r04_r04_r04_aicli_v3_mutation_decision_transport.py
 M tests/test_g31_24g_r04_r04_r04_r01_common_entry_adapter_repair.py
 M tests/test_g31_24g_r04_r04_r05_canonical_v3_to_mutation_authorization.py
 M tests/test_g31_24g_r04_r04_r06_mutation_authorization_to_authenticated_request.py
?? WORKER_INVOCATION_ARTIFACT_V1
?? WORKER_INVOKED
?? docs/governance/G31_24G_R04_R04_R07_AUTHENTICATED_REPLACEMENT_REQUEST_TO_SINGLE_USE_AUTHORIZATION_CONSUMPTION_BINDING.md
?? invocation
?? tests/test_g31_24g_r04_r04_r07_authenticated_request_consumption.py
```

The first six modified paths and the three untracked marker paths are pre-existing
protected state and are not part of the R07 scoped delta.

## Scoped commit commands

No command below was executed:

```bash
git add aigol/runtime/human_interface_runtime_entry_service.py
git add aigol/workers/filesystem_replace_worker.py
git add tests/test_g31_24g_r04_r04_r04_aicli_v3_mutation_decision_transport.py
git add tests/test_g31_24g_r04_r04_r04_r01_common_entry_adapter_repair.py
git add tests/test_g31_24g_r04_r04_r05_canonical_v3_to_mutation_authorization.py
git add tests/test_g31_24g_r04_r04_r06_mutation_authorization_to_authenticated_request.py
git add tests/test_g31_24g_r04_r04_r07_authenticated_request_consumption.py
git add docs/governance/G31_24G_R04_R04_R07_AUTHENTICATED_REPLACEMENT_REQUEST_TO_SINGLE_USE_AUTHORIZATION_CONSUMPTION_BINDING.md
git commit -m "feat(runtime): bind authenticated request to single-use consumption"
```

## Deterministic verdict

`G31_AUTHENTICATED_REPLACEMENT_REQUEST_TO_SINGLE_USE_AUTHORIZATION_CONSUMPTION_BINDING_OPERATIONAL`

One exact authenticated R06 request now consumes one exact authorization exactly
once through the existing immutable event writer. Request and consumption Replay
reconstruct, duplicate and concurrent attempts fail closed, adapters remain neutral,
and every forbidden downstream owner remains unreachable.

Exactly one next state:

`G31_24G_R04_R04_R08_CONSUMED_REPLACEMENT_REQUEST_TO_EXISTING_CERTIFIED_WORKER_SELECTION_BINDING_REQUIRED`

## Complete bounded G31-24G-R04-R04-R08 prompt

```text
# Generation 31-24G-R04-R04-R08
# Consumed Replacement Request to Existing Certified Worker Selection Binding

Treat Generation 30 and accepted G31 common-entry, R05, R06, and R07 results as
immutable certified baselines.

R07 verdict:

G31_AUTHENTICATED_REPLACEMENT_REQUEST_TO_SINGLE_USE_AUTHORIZATION_CONSUMPTION_BINDING_OPERATIONAL

Required state:

G31_24G_R04_R04_R08_CONSUMED_REPLACEMENT_REQUEST_TO_EXISTING_CERTIFIED_WORKER_SELECTION_BINDING_REQUIRED

## Objective

Bind exactly one reconstructed R07 single-use consumption claim and its exact
authenticated replacement request to the existing certified Worker-selection owner.

Produce either:

1. one immutable Worker-selection result bound to the exact consumed request and
   authorization; or
2. a deterministic fail-closed state when consumption, request, authorization,
   Worker eligibility, lifecycle, or Replay evidence is invalid.

Stop before Worker assignment, dispatch, invocation, Provider invocation, command
execution, repository mutation, restoration, rollback, or recovery.

## Required reuse

First inspect and document the existing contracts for:

- R07 request and consumption Replay reconstruction;
- the existing certified Worker registry and selection owner;
- Worker eligibility and operation compatibility;
- existing Worker-selection artifacts and Replay;
- G31 common-entry lifecycle aggregation;
- Human Conversation Experience and Canonical Presentation.

Reuse those contracts. Do not create a new selector, registry, request,
authorization, consumption, policy, Replay, Worker, Provider, command, or mutation
subsystem.

The request's existing Worker identity is evidence to validate. It must not allow
AiCLI or the adapter to choose, replace, or broaden the Worker.

## Required lifecycle

Demonstrate through `run_human_interface_runtime_entry`:

exact reconstructed APPROVED V3 decision
  -> exact reconstructed mutation authorization
  -> exact reconstructed authenticated replacement request
  -> exact reconstructed single-use consumption claim
  -> existing certified Worker-selection owner
  -> immutable selection evidence and Replay
  -> aggregate canonical lifecycle state and presentation
  -> stop before Worker assignment or dispatch

The selected Worker, operation, repository, session, target, expected state,
replacement content, modes, decision, candidate, grounding, provenance,
authorization, request, consumption, and Replay lineage must equal the consumed R07
evidence exactly.

R05 authorization, R06 request recording, and R07 consumption must not be repeated.
They may be consulted only through existing validation or reconstruction contracts.

## Fail-closed requirements

Reject before selection readiness when:

- request or consumption Replay is absent, reordered, duplicated, stale, or
  tampered;
- consumption identity differs from the exact authorization hash;
- authorization is absent, rejected, unconsumed, duplicated, or substituted;
- request, repository, session, decision, candidate, grounding, provenance, target,
  expected state, replacement content, mode, destination, or lifecycle differs;
- the requested Worker or operation is uncertified, unavailable, incompatible, or
  broader than the consumed request;
- lifecycle evidence exists after the expected consumption boundary;
- terminal, UI, or adapter fields attempt to influence selection;
- selection would implicitly assign, dispatch, or invoke a Worker, invoke a
  Provider, execute a command, open a mutation target, or mutate a repository.

Invalid evidence must not partially select a Worker and must not alter the immutable
request or consumption chain.

## Common-entry and adapter boundaries

Keep `run_human_interface_runtime_entry` as the public application transition.
AiCLI may transport and render only. It must not call selection, registry, request,
consumption, Replay, Worker, Provider, command, mutation, restoration, rollback, or
recovery owners.

Prove the same transition through a non-AiCLI in-memory adapter and prove that
terminal display fields do not affect canonical selection identity.

## Forbidden downstream reachability

Do not:

- assign or dispatch a Worker;
- invoke a Worker or Provider;
- open the target for mutation;
- construct or execute a shell command;
- write replacement bytes or mutate the repository;
- persist hardened execution events after the permitted selection boundary;
- perform restoration, rollback, or recovery.

Do not run a live PTY workflow.

## Minimal-change rule

Prefer an existing-function binding. Modify at most three production files. Add no
new artifact family, registry, selector, or Replay subsystem. If the existing
certified selector cannot consume the reconstructed R07 evidence without broad
execution changes, stop and report the first exact deterministic blocker instead of
creating a parallel owner.

Report exact production, test, and documentation line counts; every new production
symbol and responsibility; every modified production symbol; and any duplicated
helper logic.

## Tests

Prove at minimum:

- exact consumed request yields exactly one existing certified Worker selection;
- selected Worker and operation equal the consumed request exactly;
- unconsumed, duplicate, rejected, missing, or unreconstructible paths select none;
- exact request and consumption Replay is required and retained unchanged;
- altered authorization, consumption, Worker, operation, repository, session,
  decision, candidate, grounding, provenance, target, expected state, replacement
  content, mode, destination, request hash, or Replay fails before selection;
- incompatible or uncertified Worker evidence fails closed;
- conflicting later lifecycle evidence fails closed;
- terminal and UI fields do not affect selection identity;
- a non-AiCLI adapter reaches the same result;
- AiCLI owns no Worker selection semantics;
- assignment, dispatch, Worker, Provider, command, target-open, mutation,
  restoration, rollback, and recovery spies remain zero;
- selection Replay reconstructs and rejects reordering, substitution, duplication,
  or removal;
- R01 and R05-R07 plus existing certified Worker-selection tests remain compatible.

Use pytest temporary session roots for all new Replay writes.

## Validation

Run in order and report exact pass, skip, and fail counts for:

1. focused R08 tests;
2. R07 consumption-binding tests;
3. R06 request-binding tests;
4. R05 authorization tests;
5. R01 common-entry and adapter tests;
6. existing certified Worker-selection tests;
7. relevant request, consumption, authorization, decision, candidate, and Replay
   tests;
8. relevant G0-G30 Human Interface neutrality and presentation tests;
9. affected downstream G31 compatibility tests;
10. architecture and import-boundary tests;
11. Governance tests and the read-only conformance engine;
12. targeted py_compile;
13. parent and nested git diff --check;
14. protected-path SHA-256 comparison;
15. the complete repository suite exactly once after focused suites pass.

Do not run a live PTY workflow.

## Documentation

Add exactly one report:

docs/governance/G31_24G_R04_R04_R08_CONSUMED_REPLACEMENT_REQUEST_TO_EXISTING_CERTIFIED_WORKER_SELECTION_BINDING.md

Document baseline evidence, exact reuse, consumption-to-selection sequence,
selection identity, Replay, fail-closed evidence, common-entry and adapter
boundaries, forbidden zero calls, change size, validation, governance, protected
state, exact Git status, progress, verdict, and exactly one next state with a complete
bounded prompt.

Do not stage or commit. Preserve all pre-existing protected paths byte-for-byte.

## Success verdict

Return exactly:

G31_CONSUMED_REPLACEMENT_REQUEST_TO_EXISTING_CERTIFIED_WORKER_SELECTION_BINDING_OPERATIONAL

only if the exact consumed request reaches exactly one existing certified Worker
selection, Replay reconstructs, invalid or broadened evidence fails closed, adapters
remain neutral, and all forbidden downstream owners remain unreachable.

Otherwise return exactly:

G31_CONSUMED_REPLACEMENT_REQUEST_TO_EXISTING_CERTIFIED_WORKER_SELECTION_BINDING_BLOCKED

and identify the first exact deterministic blocker. Do not report partial success.
```
