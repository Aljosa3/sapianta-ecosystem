# Generation 31-24G-R04-R04-R08C Consumed Replacement Request to Certified Existing Worker Selection Binding

Status: completed bounded application binding; stopped before Worker assignment
or every later execution stage.

Date: 2026-07-22

Deterministic verdict:

`G31_CONSUMED_REPLACEMENT_REQUEST_TO_CERTIFIED_EXISTING_WORKER_SELECTION_BINDING_OPERATIONAL`

Exactly one next state:

`G31_24G_R04_R04_R09A_FILESYSTEM_REPLACE_WORKER_ASSIGNMENT_COMPATIBILITY_AUDIT_REQUIRED`

## Constitutional scope

This generation treats Generation 30, accepted G31 Common Entry, R05, R06,
R07, the R08 blocked report, the R08A audit, and the accepted R08B selection
certification as immutable baselines.

It adds only the application binding that reconstructs the exact R07 request
and consumption evidence, validates the exact R08B registry and checked
certification, submits an immutable context to the existing unified selector,
reconstructs the existing Selection Replay, and returns the selected identity
through the existing common entry.

It does not change the R08B registry, selection certification, selector rules,
artifact families, Replay families, Worker identity, capability, authority
profile, or domain. It does not create an invocation request or reach Worker
assignment, dispatch, invocation, Provider invocation, command execution,
target opening, repository mutation, restoration, rollback, or recovery. No
live PTY or mutation workflow was run.

## Accepted baseline

The work began from:

- branch: `master`;
- HEAD: `22c976b45dd5cb3212572448f9f00d278d4e85d9`;
- HEAD subject:
  `feat(runtime): certify filesystem replace worker selection`;
- R08B verdict: `G31_FILESYSTEM_REPLACE_WORKER_SELECTION_CERTIFIED`;
- certified Worker:
  `FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER`;
- certified capability: `REPLACE_EXISTING_TEXT_FILE`;
- certified registry hash:
  `sha256:74357af9a2ba666d73241381e5a4c24ac7687e41b67efe6746cb86d3ac6e7d64`;
- certification report hash:
  `sha256:03cbf0fc4e8ae562ffe25235aff1c7a6fbd559c23fc8c4fad48e15a1c56b1b45`.

The six modified runtime-evidence paths and three empty marker paths were
present before R08C. Their hashes were recorded before implementation and were
not changed or normalized by this generation.

## First required R08B closure gate

Before any R08C production edit, the four tests that failed during R08B's one
complete-suite run were executed by exact node identity:

```text
tests/test_g31_10_confirmed_grounded_execution_authorization_binding.py::test_minimality_and_no_copied_helpers
tests/test_replay_reproducibility_certification_v1.py::test_replay_reproducibility_certifies_governed_path
tests/test_replay_reproducibility_certification_v1.py::test_replay_reproducibility_report_answers_reviewer_question
tests/test_replay_reproducibility_certification_v1.py::test_replay_reproducibility_replay_package_reconstructs
```

Result: **4 passed, 0 skipped, 0 failed** in **0.29 seconds**.

The original R08B causes were:

1. duplicated inline certification validation temporarily expanded the G31-10
   module to 501 lines, violating its 480-line minimality guard;
2. the initial eight-scenario reconstructor rejected immutable seven-scenario
   `CERT-000001` evidence in three Replay-reproducibility tests.

The committed R08B baseline contains the accepted closure: one public
certification validator, a 478-line G31-10 module, and explicit seven/eight
scenario reconstruction compatibility. R08C did not repair or alter R08B.

## Minimality proof

The bounded transition required two modified production files and no new
production file:

1. the existing existing-file Governance owner gained one public application
   binding that validates and projects R07 evidence into the existing selector;
2. the existing Common Entry mutation-approval continuation calls that binding,
   aggregates the returned state, and uses the existing selection presentation.

No selector, registry, certification generator, artifact family, Replay owner,
adapter path, alias, capability, Worker, assignment model, or execution owner
was added. The binding calls `select_unified_resource` directly; it does not
manufacture selection evidence from `request.worker_id`.

The implementation modifies fewer than the permitted three production files.
No helper was copied from R05-R08B, and no new hash, serialization, immutable
write, registry, or Replay helper was created. Existing public validation,
hashing, selection, reconstruction, and presentation functions are reused.

## Exact R07-to-selector projection

The new
`bind_consumed_g31_authenticated_replace_worker_selection` function accepts:

- the exact authenticated R06/R07 request;
- the exact reconstructed actor-bound mutation authorization;
- the exact reconstructed R07 single-use consumption;
- one temporary or session-local destination for existing Selection Replay.

Before selection it:

1. validates the immutable request;
2. reconstructs the request and consumption Replay through
   `reconstruct_authenticated_replace_replay_v2`;
3. requires exactly `request -> consumption` and no later event;
4. validates request, authorization, actor, session, candidate, decision,
   target, preimage, consumption identity, request-stage Replay, and full
   parent Replay continuity;
5. loads the existing checked `CERT-000002` report;
6. validates it against the exact canonical registry through
   `validate_worker_selection_certification_v1`;
7. requires the accepted R08B registry and report hashes and exact resource
   body;
8. constructs one immutable selector context; and
9. calls the existing unified selector with the exact certified vocabulary.

The selector input is exactly:

```text
workflow_type = NATIVE_DEVELOPMENT
required_capability = REPLACE_EXISTING_TEXT_FILE
requested_role_type = WORKER_ROLE
domain_id = NATIVE_DEVELOPMENT
worker_authorization_required = true
minimum_trust = HIGH
preferred_resource_id = FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER
```

The request Worker identity is only validated and supplied as a preferred exact
identity. Eligibility, ambiguity handling, result creation, persistence, and
selection authority remain solely with `select_unified_resource`.

## Immutable selection context

The context is a non-canonical-artifact selector input using the existing
context reference/hash fields. It preserves:

- context type and deterministic context identity;
- Worker identity and exact G8-12 Worker version;
- operation/capability, role, authority profile, and domain;
- Worker-authorization requirement;
- repository and session identity;
- decision identity and hash;
- authorization identity and hash;
- authenticated request identity and hash;
- consumption identity and exact consumption-event wrapper hash;
- full request/consumption Replay hash;
- target path, preimage, postimage, source and replacement content hashes, and
  source/replacement modes;
- exact predecessor ordering;
- parent Replay reference and hash;
- certified registry hash and checked certification report hash.

The context identity is deterministically derived from the immutable request
identity. Its hash is canonical `replay_hash(context)`. The Selection artifact
must cite both that exact identity and hash. Terminal prompts, slash commands,
display Worker fields, adapter names, and other UI fields are not projected.

## Exact selection result

The existing selector returned and Replay reconstructed:

```text
selection_status = RESOURCE_SELECTION_SUCCEEDED
selected_resource_id = FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER
selected_resource_version = G8_12_EXISTING_FILE_MUTATION_IMPLEMENTATION_V1
selected_role_type = WORKER_ROLE
required_capability = REPLACE_EXISTING_TEXT_FILE
selected_authority_profile = WORKER_AUTHORIZED_TASK_ONLY
registry_hash = sha256:74357af9a2ba666d73241381e5a4c24ac7687e41b67efe6746cb86d3ac6e7d64
provider_invoked = false
worker_invoked = false
dispatch_requested = false
execution_requested = false
```

The binding rejects any result that does not match those exact values or the
immutable context identity/hash.

## Parent-child Replay continuity

The parent chain remains the accepted R05-R07 chain:

```text
exact APPROVED V3 decision
  -> exact mutation authorization and actor-bound Replay
  -> exact authenticated replacement request Replay
  -> exact single-use consumption Replay
```

R08C does not rewrite, repeat, or consume any parent event. It records only the
existing two-wrapper unified Selection Replay below a separate deterministic
selection destination. The child context contains the request identity/hash,
consumption identity/event hash, complete parent Replay reference/hash, and
R08B registry/report hashes.

`reconstruct_unified_resource_selection_replay` then validates the exact
two-file set, order, wrapper hashes, artifact hashes, returned reference,
selection hash, registry hash, selected identity, role, capability, and stop
flags. Removal, duplication, reordering, or substitution fails closed.

## Common-entry and adapter ownership

`run_human_interface_runtime_entry` remains the only public application
transition. The existing mutation-approval continuation now invokes the R08C
binding after R07 consumption and before any assignment path.

The in-memory adapter and AiCLI continuation both reached the same canonical
selection status, Worker identity, role, capability, parent context, and stop
flags. AiCLI calls only Common Entry and contains no calls to the R08C binding,
selector, registry, certification validator, or R07 reconstructor.

Existing Canonical Presentation renders the certified selection result. The
small existing mutation lifecycle summary now truthfully states
`Worker Selection Reached: True`. No adapter received selection, registry,
capability, authorization, Replay, or lifecycle authority.

## Fail-closed evidence

Focused tests prove rejection before successful selection for:

- missing or changed consumption evidence;
- a duplicated consumption wrapper;
- changed consumption identity, authorization hash, request hash,
  request-stage Replay hash, parent Replay hash, consumption status, or prior
  Worker-selection flag;
- missing or stale authorization reconstruction;
- changed decision, authorization, repository, session, target, replacement
  content, replacement bytes, request identity, or request hash;
- `CODEX`, `CLAUDE_CODE`, alias, `IMPLEMENTATION_ASSISTANCE`, or
  `FILESYSTEM_INSPECTION` substitution;
- changed Worker version;
- stale registry hash, substituted registry, or duplicate exact candidate;
- missing, false, hash-invalid, or lineage-substituted R08B certification;
- removed, duplicated, reordered, or substituted Selection Replay;
- changed Selection context hash or Selection artifact body.

Invalid parent or certification evidence is rejected before the selector and
writes no Selection Replay. Existing selector fail-closed evidence selects no
resource. No invalid case creates assignment, dispatch, invocation, command,
target-open, mutation, restoration, rollback, or recovery evidence.

## Authority and stop boundary

The successful capture states only that the exact certified Worker is selected:

```text
worker_selected = true
worker_assigned = false
worker_dispatched = false
provider_invoked = false
worker_invoked = false
execution_requested = false
command_executed = false
target_opened = false
repository_mutated = false
restoration_started = false
rollback_started = false
recovery_started = false
```

Focused spies remained zero for invocation-request creation, assignment,
dispatch, Worker invocation, Worker execution, Provider execution, command
execution, target opening, filesystem replacement, restoration, rollback, and
recovery. No live PTY, Worker, Provider, command, or mutation workflow ran.

## Production symbols and responsibilities

New production symbols:

- `R08B_REGISTRY_HASH`: pins the accepted certified registry identity;
- `R08B_CERTIFICATION_HASH`: pins the accepted checked report identity;
- `R08B_CERTIFICATION_PATH`: identifies the accepted checked report through
  the existing evidence layout;
- `bind_consumed_g31_authenticated_replace_worker_selection`: validates exact
  R07/R08B continuity, projects the immutable context, invokes the existing
  selector, reconstructs Selection Replay, and enforces the assignment stop.

Modified production symbols:

- `_authorize_g31_mutation_decision`: calls the binding after the accepted R07
  consumption and aggregates selection state and Replay reference;
- `_continue_g31_application_transition`: truthfully presents that selection
  was reached and delegates detail rendering to the existing canonical
  selection presentation.

No production helper or algorithm was duplicated. Immutable identity literals
appear only where independent request, certification, selection, and test
layers must compare the same accepted values.

## Change size

The final scoped R08C delta is:

| Category | Files | Insertions | Deletions |
|---|---:|---:|---:|
| Production | 2 modified | 241 | 5 |
| Tests | 1 modified, 1 new | 417 | 2 |
| Registry/certification evidence | 0 | 0 | 0 |
| Documentation | 1 new | 625 | 0 |

Production-file justification:

- `platform_core_existing_file_governance.py` is the existing owner of the
  R05-R07 authorization/request evidence and therefore the smallest owner for
  its selection projection;
- `human_interface_runtime_entry_service.py` is the existing public Common
  Entry continuation and canonical lifecycle aggregator.

Test-file justification:

- the R07 regression assertion now acknowledges the permitted new selection
  boundary while retaining every later stop assertion;
- the new focused R08C file proves positive common-entry behavior, adapter
  neutrality, exact identity continuity, fail-closed behavior, Replay tamper
  rejection, and zero downstream calls.

No production file, registry record, certification artifact, or Replay family
was added or regenerated.

## Validation

Validation ran in the required order.

| Validation group | Passed | Skipped | Failed |
|---|---:|---:|---:|
| Pre-implementation R08B closure gate | 4 | 0 | 0 |
| Focused R08C exact-selection success | 2 | 0 | 0 |
| Focused R08C fail-closed and tamper | 32 | 0 | 0 |
| R05-R07 regressions | 63 | 0 | 0 |
| R08B certification and G31 selection regressions | 48 | 0 | 0 |
| Unified selector and Selection Replay | 21 | 0 | 0 |
| Common-entry and adapter-neutrality | 5 | 0 | 0 |
| Architecture and import boundaries | 28 | 0 | 0 |
| Human Interface and G30 common-entry compatibility | 21 | 0 | 0 |
| Governance tests | 5 | 0 | 0 |

The full focused R08C file also passed **35 passed, 0 skipped, 0 failed**.
Targeted `py_compile` passed for both modified production files and both touched
test files. Parent `git diff --check` and all three nested repository
`git diff --check` checks passed.

The complete repository suite ran exactly once after all focused groups were
green and returned:

```text
6753 passed, 4 skipped, 0 failed in 4409.38s (1:13:29)
```

No full-suite failure or targeted closure repair occurred, and no second full
suite was run.

## Governance result

The read-only conformance engine remains:

`PARTIALLY_CONFORMANT`

- checks passed: 18;
- checks failed: 2;
- critical violations: 0;
- deterministic: true;
- fail-closed: true;
- read-only: true;
- report hash:
  `0790499ee53f9a82e15225e15eff1c2637b7e60523fa38be0c921281abe4cbea`.

The two known hook findings remain visible and unchanged: the root expected and
installed hooks are missing, and the system pre-commit hook lacks
`promotion_gate_v02` and `check_layer_freeze`. R08C neither repairs nor
reinterprets them.

## Protected and nested state

All protected SHA-256 values equal the pre-R08C baseline:

| Protected path | SHA-256 |
|---|---|
| `diagnostic_evidence.json` | `a626a69a8020bc730876119c52701a94de9ab6e4772cc64c1f5d017296650203` |
| `governed_return.json` | `e82f47c0c13678725993b21e2af2e0437edccaed324f861a7b58e77d7f8e787d` |
| `lineage.json` | `07b95505521e70f51cdddecc1057fd3a208b198445693c9a8da1e996df5799dd` |
| `provider_stderr.txt` | `d47a06d59aba2814c3fb7460049fc2ccbfc834196c956d6c6558e8be8b079e24` |
| `provider_stdout.txt` | `a73a499e2e9133c03d7babfd5c4dec7967f31e2bfb354ea9dd41df0a15c08cb3` |
| `governed_returns.jsonl` | `dbc7b63f2a17c50c43bbb4fde4f44c1dbae8d25d550fb6b4d4daa14e17126161` |
| each protected marker | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

The nested repositories remain clean at their accepted commits:

- `sapianta-domain-credit`:
  `8615e1e290471a67e4e764c6ab2138340bc7936f`;
- `sapianta_system`:
  `3183bab71f8f30397c0309dd2e6d846d14a11f66`;
- `sapianta-domain-trading`:
  `d3038dc4ba36ffbaee9161172b4c852e8e6acbda`.

## Git state and scoped commit commands

The six modified runtime-evidence paths and three marker paths predate R08C and
are excluded from its scoped implementation delta. Nothing is staged and no
commit was created.

Exact final `git status --short`:

```text
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/diagnostic_evidence.json
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/governed_return.json
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/lineage.json
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/provider_stderr.txt
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/provider_stdout.txt
 M .runtime/aigol/ledger/governed_returns.jsonl
 M aigol/runtime/human_interface_runtime_entry_service.py
 M aigol/runtime/platform_core_existing_file_governance.py
 M tests/test_g31_24g_r04_r04_r07_authenticated_request_consumption.py
?? WORKER_INVOCATION_ARTIFACT_V1
?? WORKER_INVOKED
?? docs/governance/G31_24G_R04_R04_R08C_CONSUMED_REPLACEMENT_REQUEST_TO_CERTIFIED_EXISTING_WORKER_SELECTION_BINDING.md
?? invocation
?? tests/test_g31_24g_r04_r04_r08c_consumed_request_certified_worker_selection.py
```

No command below was executed:

```bash
git add aigol/runtime/platform_core_existing_file_governance.py
git add aigol/runtime/human_interface_runtime_entry_service.py
git add tests/test_g31_24g_r04_r04_r07_authenticated_request_consumption.py
git add tests/test_g31_24g_r04_r04_r08c_consumed_request_certified_worker_selection.py
git add docs/governance/G31_24G_R04_R04_R08C_CONSUMED_REPLACEMENT_REQUEST_TO_CERTIFIED_EXISTING_WORKER_SELECTION_BINDING.md
git commit -m "feat(runtime): bind consumed replacement request to certified Worker selection"
```

## Progress and verdict

Evidence-scoped planning estimates are:

- Generation 31 no-copy/paste governed-development lifecycle: **99.98%**;
- whole project toward the current bounded Product 1 and governed-development
  objective: **98.14%**.

These are not production-readiness, certification, or regulatory-compliance
claims. R08C operationally reaches exact certified selection only. Existing
assignment compatibility, later lifecycle progression, physical execution,
validation, certification, and Product 1 release remain separately governed.

Deterministic verdict:

`G31_CONSUMED_REPLACEMENT_REQUEST_TO_CERTIFIED_EXISTING_WORKER_SELECTION_BINDING_OPERATIONAL`

Exactly one next state:

`G31_24G_R04_R04_R09A_FILESYSTEM_REPLACE_WORKER_ASSIGNMENT_COMPATIBILITY_AUDIT_REQUIRED`

## Complete bounded G31-24G-R04-R04-R09A prompt

```text
# Generation 31-24G-R04-R04-R09A
# Filesystem Replace Worker Assignment Compatibility Audit

Treat Generation 30, accepted G31 Common Entry and R05-R07 results, R08 and
R08A, the accepted R08B selection certification, and the accepted R08C
selection binding as immutable certified baselines.

R08C verdict:

G31_CONSUMED_REPLACEMENT_REQUEST_TO_CERTIFIED_EXISTING_WORKER_SELECTION_BINDING_OPERATIONAL

Required state:

G31_24G_R04_R04_R09A_FILESYSTEM_REPLACE_WORKER_ASSIGNMENT_COMPATIBILITY_AUDIT_REQUIRED

## Objective

Perform an AUDIT_ONLY repository-evidence assessment of whether the exact R08C
RESOURCE_SELECTION_ARTIFACT_V1 for
FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER can reach the existing certified
Worker-assignment owner without changing its Worker identity, capability,
authorization, request, consumption, registry, certification, or Selection
Replay lineage.

Identify the smallest legitimate next transition or the first exact
deterministic blocker. Do not implement assignment or mutate runtime behavior.

## Required inspection

Inspect and compare:

- the exact R08C selection capture, context, and Selection Replay;
- the R05-R07 authorization, request, and consumption identities;
- the R08B registry entry and checked selection certification;
- existing WORKER_INVOCATION_REQUEST_ARTIFACT_V1 contracts and reconstructors;
- existing WORKER_ARTIFACT_V1 registry/validation contracts;
- assign_worker_from_invocation_request and Worker-assignment Replay;
- G31-12B's selection-to-assignment projection and its CODEX-specific limits;
- replacement-Worker capability, allowed-output, forbidden-operation,
  availability, and authority evidence;
- common-entry aggregation, Canonical Presentation, and adapter boundaries;
- later dispatch and invocation contracts only to establish the assignment
  stop boundary.

Search all assignment registries and certification evidence before declaring
an identity, role, packet, capability, or operation absent.

## Required determinations

Classify every necessary assignment input as:

- already implemented and directly reusable;
- present but requiring a bounded exact projection;
- absent and requiring bounded registration or certification;
- incompatible with the immutable R05-R08C identity;
- downstream work outside assignment scope.

Determine exactly:

1. whether an existing WORKER_ARTIFACT_V1 can represent the exact replacement
   Worker and operation without aliasing it to CODEX or another Worker;
2. whether the existing invocation-request family can preserve the consumed
   request and Selection Replay as immutable parent evidence without granting
   invocation authority;
3. whether the existing assignment owner accepts the exact Worker category,
   role, capability, allowed outputs, forbidden operations, and authority;
4. whether any registry or checked certification addition is required before
   a live assignment binding;
5. whether assignment Replay can retain the exact R08C parent context and
   reconstruct without rewriting R05-R08C evidence;
6. whether a later successful assignment can stop before dispatch, invocation,
   Provider execution, command execution, target opening, or mutation;
7. the first exact blocker and smallest bounded next generation.

## Fail-closed rules

Do not recommend:

- mapping the replacement Worker to CODEX, CLAUDE_CODE, a generic
  implementation Worker, an inspection capability, or an alias;
- treating request.worker_id or selected_resource_id as an assignment artifact;
- bypassing invocation-request or assignment validation;
- changing or repeating R05 authorization, R06 request recording, R07
  consumption, R08B certification, or R08C selection;
- creating a second assignment owner, registry, Worker identity, capability,
  certification system, Replay subsystem, or common-entry path;
- assignment, dispatch, Worker or Provider invocation, command execution,
  target opening, repository mutation, restoration, rollback, or recovery.

If exact Worker registration or assignment certification is absent, identify
the first exact missing artifact and propose only one bounded certification or
registration generation. Do not bundle the later operational assignment.

## Authority boundary

This is read-only audit work. It must retain:

worker_selected = true
worker_assigned = false
worker_dispatched = false
provider_invoked = false
worker_invoked = false
execution_requested = false
command_executed = false
target_opened = false
repository_mutated = false
restoration_started = false
rollback_started = false
recovery_started = false

Do not call the common-entry R08C continuation, invocation-request creation,
assignment, dispatch, invocation, Worker, Provider, command, target-open,
mutation, restoration, rollback, or recovery owners. Use read-only inspection
and temporary validation probes only.

## Minimal-change rule

Make no production or test change. Add exactly one governance audit report.
If an exact existing-function assignment binding is already possible, document
the minimal projection and its required focused evidence; do not implement it.
If certification or registry work is required, separate that work from the
later binding.

## Validation

Run relevant existing R08C, invocation-request, Worker artifact/registry,
assignment, assignment Replay, architecture, import-boundary, and Governance
tests. Run the read-only conformance engine, targeted py_compile, parent and
nested git diff --check, and protected-path SHA-256 comparison.

Do not run the complete repository suite, live PTY, Worker, Provider, command,
or mutation workflow for this AUDIT_ONLY generation unless deterministic
repository evidence makes it necessary.

## Documentation

Add exactly one report:

docs/governance/G31_24G_R04_R04_R09A_FILESYSTEM_REPLACE_WORKER_ASSIGNMENT_COMPATIBILITY_AUDIT.md

Document accepted baseline evidence, complete contract inventory, exact
compatibility matrix, identity and Replay continuity, authority boundary,
smallest safe next change, rejected shortcuts, validation, Governance,
protected state, exact Git status, progress, one deterministic verdict, and
exactly one next state with a complete bounded prompt.

Do not stage or commit. Preserve all protected paths byte-for-byte.

## Required verdict

Return exactly one:

READY_FOR_DIRECT_EXISTING_FILESYSTEM_REPLACE_WORKER_ASSIGNMENT_BINDING
READY_FOR_BOUNDED_FILESYSTEM_REPLACE_WORKER_ASSIGNMENT_CERTIFICATION
BLOCKED_BY_MISSING_FILESYSTEM_REPLACE_WORKER_ASSIGNMENT_EVIDENCE
BLOCKED_BY_INCOMPATIBLE_CERTIFIED_ASSIGNMENT_ARCHITECTURE

Do not report partial success.
```
