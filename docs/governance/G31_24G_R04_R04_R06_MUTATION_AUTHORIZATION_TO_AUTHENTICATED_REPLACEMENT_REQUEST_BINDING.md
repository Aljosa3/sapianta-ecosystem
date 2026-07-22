# Generation 31-24G-R04-R04-R06 Mutation Authorization to Authenticated Replacement Request Binding

Status: operational bounded implementation.

Date: 2026-07-21

Verdict:

`G31_MUTATION_AUTHORIZATION_TO_AUTHENTICATED_REPLACEMENT_REQUEST_BINDING_OPERATIONAL`

Exactly one next state:

`G31_24G_R04_R04_R07_AUTHENTICATED_REPLACEMENT_REQUEST_TO_SINGLE_USE_AUTHORIZATION_CONSUMPTION_BINDING_REQUIRED`

## Constitutional scope

This implementation preserves the Generation 30 certified baseline, the repaired
Generation 31 common-entry architecture, and the accepted R05 mutation-authorization
boundary. It binds only an exact reconstructed APPROVED V3 authorization to the
existing authenticated replacement-request family and its existing hardened Replay
lifecycle.

It does not consume authorization, select or dispatch a Worker, invoke a Provider or
Worker, construct or execute a command, inspect a live target for execution, mutate a
repository, restore content, roll back content, or recover an interrupted mutation.
No live PTY workflow was run.

## Baseline evidence

- branch: `master`;
- baseline HEAD: `a597bdd7bda30776d48dce98a4b79f37e6681d47`;
- baseline subject: `feat(runtime): bind approved V3 decision to mutation authorization`;
- the committed R05 report contains
  `G31_CANONICAL_APPROVED_V3_DECISION_TO_MUTATION_AUTHORIZATION_BINDING_OPERATIONAL`;
- its sole next state is the R06 state implemented here;
- R01 and R05 governance reports remain byte-unchanged from HEAD;
- the parent index was empty and no commit was created.

The initial parent worktree contained only protected pre-existing state:

```text
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/diagnostic_evidence.json
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/governed_return.json
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/lineage.json
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/provider_stderr.txt
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/provider_stdout.txt
 M .runtime/aigol/ledger/governed_returns.jsonl
?? WORKER_INVOCATION_ARTIFACT_V1
?? WORKER_INVOKED
?? invocation
```

The nested repositories were clean before implementation:

- `sapianta-domain-credit` at `8615e1e...`;
- `sapianta_system` at `3183bab...`;
- `sapianta-domain-trading` at `d3038dc...`.

## Certified boundary and exact transition

Before R06:

```text
run_human_interface_runtime_entry
  -> exact APPROVED V3 mutation decision
  -> canonical mutation authorization
  -> actor-bound authorization Replay
  -> authentic authorization reconstruction
  -> presentation
  -> stop before request construction
```

After R06:

```text
run_human_interface_runtime_entry
  -> _continue_g31_application_transition
  -> _record_g31_mutation_decision
  -> _authorize_g31_mutation_decision
  -> authorize_g31_approved_existing_file_mutation
  -> reconstruct_g31_existing_file_mutation_authorization_binding
  -> bind_g31_mutation_authorization_actor_and_replay
  -> reconstruct_g31_mutation_authorization_actor_and_replay
  -> create_g31_authenticated_replace_request
  -> record_authenticated_replace_request_v2
  -> reconstruct_authenticated_replace_replay_v2
  -> _g31_application_result and canonical presentation
  -> stop before authorization consumption
```

The public application transition remains
`run_human_interface_runtime_entry`. The common entry sequences existing owners; it
does not reproduce their domain validation.

## Reused canonical owners

| Responsibility | Existing owner |
|---|---|
| APPROVED V3 decision and Replay | `aigol.runtime.human_decision_runtime` |
| mutation authorization construction and reconstruction | `aigol.runtime.platform_core_existing_file_governance` |
| authorization actor and Replay binding | `aigol.runtime.platform_core_existing_file_governance` |
| candidate and provenance validation | `aigol.runtime.platform_core_existing_file_mutation_candidate` |
| authenticated request construction | `create_g31_authenticated_replace_request` |
| request schema and identity validation | `validate_authenticated_replace_request_v2` |
| deterministic request Replay destination | `g31_replace_destinations` |
| hardened lifecycle event persistence | existing `_persist_v2_event` owner |
| request lifecycle reconstruction | `reconstruct_authenticated_replace_replay_v2` |
| lifecycle sequencing and presentation | common Human Interface runtime entry service |
| terminal transport and rendering | AiCLI or another Human Interface adapter |

One public request-only recorder,
`record_authenticated_replace_request_v2`, was added beside the existing hardened
request validator, event writer, and reconstructor. It introduces no artifact family
and no Replay subsystem. It validates the existing request, rejects any pre-existing
lifecycle evidence, persists only the existing `request` event with
`REQUEST_VALIDATED`, reconstructs that event through the existing owner, and verifies
the exact request, authorization, event order, and count.

## Authenticated request contract

The existing request type remains:

`AUTHORIZED_REPLACE_EXISTING_FILE_REQUEST_V2`

The request binds the following canonical evidence:

- request ID and hash;
- canonical authorization actor;
- complete authorization record, ID, hash, status, scope, and Worker identity;
- authorization Replay reference and hash;
- actor-Replay and R02 authorization-binding hashes;
- candidate ID, artifact hash, Replay hash, and provenance-binding hash;
- APPROVED V3 decision ID, hash, outcome, scope, actor, and Replay hash;
- session ID and root;
- repository identity and root;
- repository-grounding and implementation-manifest hashes;
- exact existing-file replacement operation;
- workspace-relative target path;
- expected preimage SHA-256 and source-content hash;
- postimage SHA-256 and replacement-content hash;
- immutable preimage and replacement bytes;
- source and replacement modes;
- deterministic lifecycle destinations;
- explicit false values for consumption, Worker invocation, Provider invocation,
  command execution, and repository mutation.

The request hash covers all of those fields. Terminal prompt, slash-command,
interface name, and presentation text are never projected into the request.

## Replay and evidence mapping

Authorization remains reconstructed from its existing three-wrapper
`G31_MUTATION_AUTHORIZATION_REPLAY_V1` chain. Request Replay is written beneath the
existing deterministic destination:

```text
<session-root>/G31_EXISTING_FILE_REPLACE_V2/<authorization-hash>/
  000_request.json
```

R06 writes exactly one existing hardened lifecycle event:

```text
event_key: request
event_type: REQUEST_VALIDATED
previous_replay_hash: null
```

The wrapper binds the request hash, authorization identity and Replay hash, actor,
candidate, decision, repository, grounding, target, preimage, postimage, and modes.
`reconstruct_authenticated_replace_replay_v2` first revalidates the complete request,
then verifies artifact and wrapper hashes, exact event identity, predecessor order,
and the request hash carried by Replay.

The reconstructed R06 state contains:

- `authenticated_replacement_request`;
- `authenticated_replacement_request_reconstruction`;
- request ID and hash;
- request Replay reference and hash;
- `replace_request_created: True`;
- `authorization_consumed: False`;
- all downstream execution and mutation flags false.

## APPROVED, REJECTED, and unauthorized behavior

APPROVED:

```text
exact V3 APPROVED decision
  -> one authorization and actor Replay
  -> one authenticated request
  -> one request Replay event
  -> canonical presentation
  -> terminal stop
```

REJECTED:

```text
exact V3 REJECTED decision
  -> recorded terminal decision
  -> zero authorization calls
  -> zero request-construction calls
  -> zero request Replay events
```

Missing or unreconstructible authorization:

```text
authorization reconstruction failure
  -> fail closed
  -> zero request-construction or recorder calls
  -> zero request Replay events
```

Proposal approval remains distinct from execution authorization, and the V3 mutation
decision remains distinct from single-use authorization consumption.

## Fail-closed evidence

Focused tests prove rejection before request recording for substitution of:

- authorization ID or authorization Replay hash;
- actor, repository, or session;
- decision outcome or decision Replay;
- candidate identity or candidate Replay;
- grounding or provenance;
- target path;
- expected preimage content;
- replacement content.

The request recorder rejects an exact duplicate and a conflicting request identity
when any lifecycle evidence already exists. A tampered `REQUEST_VALIDATED` wrapper
fails reconstruction. No invalid input partially records or authenticates a request.

## Adapter independence and presentation

The in-memory adapter calls only `run_human_interface_runtime_entry` and imports no
AiCLI code. It reaches the same request ID, request hash, Replay path, lifecycle state,
and canonical presentation as any other adapter.

Static evidence confirms:

- AiCLI calls the common entry;
- AiCLI contains no request constructor, validator, recorder, reconstructor,
  authorization-consumption, hardened-execution, or recovery call;
- canonical runtime and Worker modules do not import `aigol.cli`;
- the in-memory adapter copies no low-level sequencing;
- interface-only state does not enter canonical request identity.

Canonical presentation states the authorization ID, status, actor, target, request
ID and hash, request Replay hash, request-created status, and the stop before
authorization consumption and Worker selection.

## Authority and downstream boundary

Focused spies prove zero calls to:

- `execute_g31_authenticated_replace`;
- `recover_g31_authenticated_replace`;
- `execute_filesystem_replace_request`;
- `_execute_authenticated_replace_v2`;
- `_recover_authenticated_replace_v2`;
- live-target opening;
- atomic restoration.

Only the request event key was persisted. No consumption, journal, started, atomic,
result, rollback, recovery, completion, or termination event exists. There was no
additional CODEX Worker or Provider invocation, no command construction or execution,
and no repository mutation.

## Change size and minimality

Production changes before this report:

| File | Insertions | Deletions | Reason |
|---|---:|---:|---|
| `aigol/runtime/human_interface_runtime_entry_service.py` | 35 | 3 | Sequence existing request owners, retain lifecycle state, and present the bounded stop. |
| `aigol/workers/filesystem_replace_worker.py` | 25 | 1 | Expose the existing request event writer as a request-only recorder and return request Replay identity from reconstruction. |

Total production delta: **60 insertions, 4 deletions across two files**.

Exactly one new production symbol was introduced:

- `record_authenticated_replace_request_v2` — validate, exclusively record, and
  reconstruct only the existing authenticated request-stage Replay event.

Modified existing production symbols:

- `reconstruct_authenticated_replace_replay_v2` — adds request ID and Replay
  reference to its existing reconstruction result;
- `_authorize_g31_mutation_decision` — sequences existing construction and recording
  owners and retains their evidence;
- `_continue_g31_application_transition` — presents the request and truthful stop.

No helper logic was copied. Existing hashing, path validation, authorization
validation, immutable event persistence, and Replay reconstruction remain owned by
their original modules.

Test changes before this report total **463 insertions and 9 deletions**:

- one 408-line focused R06 test module;
- bounded fixture and expectation updates in three existing R01/R04/R05 tests.

The documentation delta is exactly this 612-line report. The focused test file is justified by the 29 required positive, terminal,
fail-closed, adapter-neutrality, Replay, and zero-reachability assertions. No new
runtime module or top-level framework was added. Total scoped delta is **1,135 insertions and 13 deletions**.

## Validation

Distinct focused command results:

- focused R06: **19 passed, 0 skipped, 0 failed**;
- R05 authorization regression: **11 passed, 0 skipped, 0 failed**;
- R01 common-entry and adapter regression: **4 passed, 0 skipped, 0 failed**;
- existing authenticated request-owner regression: **31 passed, 0 skipped, 0 failed**;
- relevant candidate, V3 decision, authorization, and Replay lineage in full-suite
  XML: **28 passed, 0 skipped, 0 failed**;
- G0-G30 Human Interface, AiCLI, presentation, and G30 operational group:
  **88 passed, 0 skipped, 0 failed**;
- architecture and import-boundary group: **23 passed, 0 skipped, 0 failed**;
- Governance tests: **5 passed, 0 skipped, 0 failed**;
- all Generation 31 tests represented in the authoritative full-suite XML:
  **490 passed, 0 skipped, 0 failed**;
- targeted `py_compile`: passed;
- parent `git diff --check`: passed;
- all nested repository `git diff --check` commands: passed;
- complete repository suite: **6,660 passed, 1 skipped, 0 failed** in
  **4,539.48 seconds (1:15:39)**.

Focused counts overlap the complete suite and must not be added together. The sole
full-suite skip is the opt-in real OpenAI provider certification test, which requires
`AIGOL_RUN_REAL_OPENAI_PROVIDER_CALL=1` and an API key. No live Provider call was
attempted.

## Governance result

The read-only conformance engine remains:

`PARTIALLY_CONFORMANT`

- checks passed: 18;
- checks failed: 2;
- critical violations: 0;
- deterministic: true;
- fail-closed: true;
- read-only: true;
- report hash: `0790499ee53f9a82e15225e15eff1c2637b7e60523fa38be0c921281abe4cbea`.

The two known findings remain unchanged: missing root expected/installed pre-commit
hooks, and missing `promotion_gate_v02` plus `check_layer_freeze` tokens in the system
hook. R06 does not hide or repair this hook drift.

## Protected state and nested repositories

Protected SHA-256 values remained exact after implementation and validation:

| Protected path | SHA-256 |
|---|---|
| `diagnostic_evidence.json` | `a626a69a8020bc730876119c52701a94de9ab6e4772cc64c1f5d017296650203` |
| `governed_return.json` | `e82f47c0c13678725993b21e2af2e0437edccaed324f861a7b58e77d7f8e787d` |
| `lineage.json` | `07b95505521e70f51cdddecc1057fd3a208b198445693c9a8da1e996df5799dd` |
| `provider_stderr.txt` | `d47a06d59aba2814c3fb7460049fc2ccbfc834196c956d6c6558e8be8b079e24` |
| `provider_stdout.txt` | `a73a499e2e9133c03d7babfd5c4dec7967f31e2bfb354ea9dd41df0a15c08cb3` |
| `governed_returns.jsonl` | `dbc7b63f2a17c50c43bbb4fde4f44c1dbae8d25d550fb6b4d4daa14e17126161` |
| each protected marker | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

All three nested repositories remain clean. Nothing is staged, and no commit was
created.

## Progress estimate

Evidence-scoped estimates only:

- Generation 31 no-copy/paste governed-development lifecycle: **99.96%**;
- whole project toward the current bounded Product 1 and governed-development
  objective: **98.0%**.

These are planning estimates, not certification or production-readiness claims. The
remaining immediate gap is the single-use consumption transition; execution,
mutation, validation, certification, and product-release work remain separately
governed.

## Scoped commit commands

No command below was executed:

```bash
git add aigol/runtime/human_interface_runtime_entry_service.py
git add aigol/workers/filesystem_replace_worker.py
git add tests/test_g31_24g_r04_r04_r04_aicli_v3_mutation_decision_transport.py
git add tests/test_g31_24g_r04_r04_r04_r01_common_entry_adapter_repair.py
git add tests/test_g31_24g_r04_r04_r05_canonical_v3_to_mutation_authorization.py
git add tests/test_g31_24g_r04_r04_r06_mutation_authorization_to_authenticated_request.py
git add docs/governance/G31_24G_R04_R04_R06_MUTATION_AUTHORIZATION_TO_AUTHENTICATED_REPLACEMENT_REQUEST_BINDING.md
git commit -m "feat(runtime): bind mutation authorization to authenticated request"
```

## Deterministic verdict

`G31_MUTATION_AUTHORIZATION_TO_AUTHENTICATED_REPLACEMENT_REQUEST_BINDING_OPERATIONAL`

The exact reconstructed authorization now creates and records exactly one canonical
authenticated replacement request through the common entry. REJECTED and
unauthorized paths create none. Replay reconstructs and rejects tampering,
authorization remains unconsumed, adapters remain neutral, and all forbidden
downstream owners remain unreachable.

Exactly one next state:

`G31_24G_R04_R04_R07_AUTHENTICATED_REPLACEMENT_REQUEST_TO_SINGLE_USE_AUTHORIZATION_CONSUMPTION_BINDING_REQUIRED`

## Complete bounded G31-24G-R04-R04-R07 prompt

```text
# Generation 31-24G-R04-R04-R07
# Authenticated Replacement Request to Single-Use Authorization Consumption Binding

Treat Generation 30 and accepted G31 common-entry, R05, and R06 results as immutable
certified baselines.

R06 verdict:

G31_MUTATION_AUTHORIZATION_TO_AUTHENTICATED_REPLACEMENT_REQUEST_BINDING_OPERATIONAL

Required state:

G31_24G_R04_R04_R07_AUTHENTICATED_REPLACEMENT_REQUEST_TO_SINGLE_USE_AUTHORIZATION_CONSUMPTION_BINDING_REQUIRED

## Objective

Bind exactly one authentic R06 replacement request and its exact reconstructed
mutation authorization to the existing single-use authorization-consumption owner.

Produce either:

1. one immutable consumption claim and reconstructed Replay state bound to the exact
   request and authorization; or
2. a deterministic fail-closed state when the request, authorization, lifecycle, or
   evidence is invalid.

Stop before Worker selection, Worker dispatch, Provider invocation, command
execution, repository mutation, restoration, rollback, or recovery.

## Required reuse

First inspect and document the existing contracts for:

- `AUTHORIZED_REPLACE_EXISTING_FILE_REQUEST_V2` validation;
- request-stage Replay recording and reconstruction;
- authorization records and actor-bound authorization Replay;
- deterministic hardened lifecycle destinations;
- the existing consumption event and exclusive immutable writer;
- duplicate and concurrent consumption rejection;
- common-entry lifecycle aggregation and Canonical Presentation.

Reuse those contracts. Do not create a new authorization, request, consumption,
locking, Replay, Worker, command, or mutation subsystem.

## Required lifecycle

Demonstrate through `run_human_interface_runtime_entry`:

exact reconstructed APPROVED V3 decision
  -> exact reconstructed mutation authorization
  -> exact reconstructed authenticated replacement request
  -> validate request-stage Replay is the sole predecessor
  -> claim the exact authorization exactly once through the existing immutable
     consumption event
  -> reconstruct request and consumption Replay
  -> aggregate canonical lifecycle state and presentation
  -> stop before Worker selection or dispatch

The consumption identity must equal the exact authorization hash and must be bound to
the exact request hash, actor, repository, session, decision, candidate, grounding,
provenance, target, expected preimage, replacement content, and request Replay.

R06 request recording must not be repeated. R05 authorization owners must not be
reinvoked except through an existing explicit reconstruction contract.

## Single-use and fail-closed requirements

Reject before consumption readiness when:

- the request or request Replay is absent, reordered, duplicated, stale, or tampered;
- authorization ID, hash, status, scope, actor, or Replay differs;
- repository, session, decision, candidate, grounding, provenance, target,
  preimage, replacement content, mode, or lifecycle destination differs;
- request-stage Replay is not the sole exact predecessor;
- consumption already exists;
- a competing or conflicting consumption claim exists;
- lifecycle evidence exists after the expected request-only boundary;
- terminal, UI, or adapter fields attempt to influence canonical identity;
- consumption would implicitly select, dispatch, or invoke a Worker, invoke a
  Provider, execute a command, or mutate a repository.

Invalid evidence must not partially consume authorization. Concurrent claims must
have exactly one immutable winner and all other attempts must fail closed.

## Common-entry and adapter boundaries

Keep `run_human_interface_runtime_entry` as the public application transition.
AiCLI may transport and render only. It must not call request, Replay, consumption,
Worker, Provider, command, mutation, restoration, rollback, or recovery owners.

Prove the same transition with a non-AiCLI in-memory adapter and prove that terminal
display fields do not affect consumption identity.

## Forbidden downstream reachability

Do not:

- select, assign, or dispatch a Worker;
- invoke a Worker or Provider;
- open the target for mutation;
- construct or execute a shell command;
- write replacement bytes;
- mutate the repository;
- persist journal, started, atomic, result, completion, termination, rollback, or
  recovery events;
- perform restoration, rollback, or recovery.

Do not run a live PTY workflow.

## Minimal-change rule

Prefer an existing-function binding. Modify at most three production files. Add no
new artifact family or Replay subsystem. If the existing consumption contract cannot
consume the already-recorded R06 request event without broad execution changes, stop
and report the first exact blocker instead of implementing a parallel owner.

Report exact production, test, and documentation line counts; every new production
symbol and responsibility; every modified production symbol; and any duplicated
helper logic.

## Tests

Prove at minimum:

- exact R06 request and authorization yield one immutable consumption claim;
- authorization changes from unconsumed to consumed only at this stage;
- REJECTED, missing, or unreconstructible request paths consume nothing;
- exact request-stage Replay is required and retained unchanged;
- duplicate sequential consumption fails closed;
- two concurrent claims have exactly one winner;
- altered authorization, actor, repository, session, decision, candidate, grounding,
  provenance, target, expected state, replacement content, mode, destination, request
  hash, or Replay fails before consumption;
- conflicting lifecycle evidence fails closed;
- terminal and UI fields do not affect canonical identity;
- a non-AiCLI adapter reaches the same result;
- AiCLI owns no consumption semantics;
- Worker, Provider, command, target-open, mutation, restoration, rollback, and
  recovery spies remain zero;
- request Replay plus consumption Replay reconstruct and reject reordering,
  substitution, duplication, or removal;
- R01, R05, R06, and existing hardened request-owner tests remain compatible.

Use pytest temporary session roots for all new Replay writes.

## Validation

Run in order and report exact pass, skip, and fail counts for:

1. focused R07 tests;
2. R06 request-binding tests;
3. R05 authorization tests;
4. R01 common-entry and adapter tests;
5. existing hardened request and consumption tests;
6. relevant decision, candidate, authorization, and Replay tests;
7. relevant G0-G30 Human Interface neutrality and presentation tests;
8. affected downstream G31 compatibility tests;
9. architecture and import-boundary tests;
10. Governance tests and the read-only conformance engine;
11. targeted py_compile;
12. parent and nested git diff --check;
13. protected-path SHA-256 comparison;
14. the complete repository suite exactly once after focused suites pass.

Do not run a live PTY workflow.

## Documentation

Add exactly one report:

docs/governance/G31_24G_R04_R04_R07_AUTHENTICATED_REPLACEMENT_REQUEST_TO_SINGLE_USE_AUTHORIZATION_CONSUMPTION_BINDING.md

Document baseline evidence, exact reuse, request-to-consumption sequence, single-use
identity, Replay, concurrency, fail-closed evidence, common-entry and adapter
boundaries, forbidden zero calls, change size, validation, governance, protected
state, exact Git status, progress, verdict, and exactly one next state with a complete
bounded prompt.

Do not stage or commit. Preserve all pre-existing protected paths byte-for-byte.

## Success verdict

Return exactly:

G31_AUTHENTICATED_REPLACEMENT_REQUEST_TO_SINGLE_USE_AUTHORIZATION_CONSUMPTION_BINDING_OPERATIONAL

only if one exact request consumes one exact authorization exactly once, Replay
reconstructs, concurrent or duplicate attempts fail closed, adapters remain neutral,
and all forbidden downstream owners remain unreachable.

Otherwise return exactly:

G31_AUTHENTICATED_REPLACEMENT_REQUEST_TO_SINGLE_USE_AUTHORIZATION_CONSUMPTION_BINDING_BLOCKED

and identify the first exact deterministic blocker. Do not report partial success.
```
