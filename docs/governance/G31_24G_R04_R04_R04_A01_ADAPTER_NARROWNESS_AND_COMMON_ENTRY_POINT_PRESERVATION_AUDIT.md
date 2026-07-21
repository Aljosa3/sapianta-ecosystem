# Generation 31-24G-R04-R04-R04-A01 — Adapter Narrowness and Common Entry-Point Preservation Audit

## Deterministic verdict

`G31_ADAPTER_NARROWNESS_DRIFT_DETECTED`

Plain-language conclusion: the low-level G31 owners remain canonical, fail-closed,
and reusable, but the production application sequence that connects them is not
exposed through the G0-G30-certified interface-neutral entry.  Starting in
G31-09, the reference AiCLI became the only production owner of the post-entry
state machine.  The uncommitted R04 delta extends that same AiCLI-owned state
machine through V2 candidate construction, V3 context preparation, decision
recording, Replay reconstruction, result aggregation, and presentation.  A REST,
Web, Speech, GUI/chat, or automation adapter cannot reach the same lifecycle by
calling one existing shared application transition; it must import AiCLI or copy
its sequencing and `runtime_result` conventions.  That is the architectural
failure the G14-30 contract expressly prohibited.

This verdict does not invalidate the individual decision, acceptance,
authorization, replacement, or Replay contracts.  It blocks committing R04 as
constitutionally compatible until the G31 application sequencing is extracted
into the existing interface-neutral Human Interface Runtime Entry owner.

## Baseline and audit boundary

- Branch: `master`.
- Full immutable HEAD: `4d5dbd94d16e258904ef250024284df1f8e3ef63`.
- HEAD subject: `docs(governance): audit hardened replace live reachability`.
- Required committed report:
  `docs/governance/G31_24G_R04_R04_R03_HARDENED_REPLACE_OWNER_LIVE_REACHABILITY_AUDIT.md`.
- Required committed verdict found:
  `G31_HARDENED_REPLACE_OWNER_LIVE_BINDING_REQUIRED`.
- No commit was created by this audit.
- No path was staged when the audit began.
- The parent worktree was intentionally dirty.  The only task-scope production
  delta was the known uncommitted R04 change to `aigol/cli/aicli.py`; its new
  focused test and report were also present and untracked.

Recent committed history at audit start:

```text
4d5dbd94 docs(governance): audit hardened replace live reachability
4c3493dc feat(governance): harden atomic existing-file replacement
3e622828 feat(governance): bind mutation authorization actor and replay
151c6442 docs(governance): record replace owner hardening blocker
40b890e1 docs(governance): audit replace mutation owner safety
b9213840 feat(governance): bind approved mutation decision to authorization
8069f65e fix(governance): reconstruct activation lineage for R01 candidate
8924a646 feat(governance): record replayed mutation decisions
5b22f16e docs(governance): audit R01 activation lineage compatibility
ba787435 feat(governance): bind accepted result to replayed candidate
```

This generation was read-only except for this report.  It did not invoke an
authorization, authenticated request, authorization consumption, Worker,
Provider, generated command, mutation, restoration, or recovery owner.  It did
not run a live PTY workflow.

## Initial dirty-worktree inventory

```text
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/diagnostic_evidence.json
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/governed_return.json
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/lineage.json
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/provider_stderr.txt
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/provider_stdout.txt
 M .runtime/aigol/ledger/governed_returns.jsonl
 M aigol/cli/aicli.py
?? WORKER_INVOCATION_ARTIFACT_V1
?? WORKER_INVOKED
?? docs/governance/G31_24G_R04_R04_R04_AICLI_V3_MUTATION_DECISION_TRANSPORT_BINDING.md
?? invocation
?? tests/test_g31_24g_r04_r04_r04_aicli_v3_mutation_decision_transport.py
```

No additional unexplained production change overlapped the audit.

## Protected and R04 pre-audit hashes

| Path | Initial SHA-256 |
| --- | --- |
| `.runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/diagnostic_evidence.json` | `a626a69a8020bc730876119c52701a94de9ab6e4772cc64c1f5d017296650203` |
| `.runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/governed_return.json` | `e82f47c0c13678725993b21e2af2e0437edccaed324f861a7b58e77d7f8e787d` |
| `.runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/lineage.json` | `07b95505521e70f51cdddecc1057fd3a208b198445693c9a8da1e996df5799dd` |
| `.runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/provider_stderr.txt` | `d47a06d59aba2814c3fb7460049fc2ccbfc834196c956d6c6558e8be8b079e24` |
| `.runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/provider_stdout.txt` | `a73a499e2e9133c03d7babfd5c4dec7967f31e2bfb354ea9dd41df0a15c08cb3` |
| `.runtime/aigol/ledger/governed_returns.jsonl` | `dbc7b63f2a17c50c43bbb4fde4f44c1dbae8d25d550fb6b4d4daa14e17126161` |
| `WORKER_INVOCATION_ARTIFACT_V1` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `WORKER_INVOKED` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `invocation` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `aigol/cli/aicli.py` | `76611464b24e7d2d5c8ad7f01f1cbb821a193dfff411729e2e4c6b85bec8044c` |
| `tests/test_g31_24g_r04_r04_r04_aicli_v3_mutation_decision_transport.py` | `02f687d5db5ef8681bde847a052cd13201c2d2c57ab7a7573448212c7ecaaf5b` |
| `docs/governance/G31_24G_R04_R04_R04_AICLI_V3_MUTATION_DECISION_TRANSPORT_BINDING.md` | `503d93f4f0893df4fed54f9514fd9d3fb7bf82157e730731ec3d520e27ef2a19` |

## Files and evidence inspected

Production and tests were inspected by symbol and call topology, including:

- `aigol/cli/aicli.py` at HEAD and in the working tree;
- `aigol/cli/aigol_cli.py` and `aigol/acli_next/conversational.py`;
- `aigol/runtime/human_interface_runtime_entry_service.py`;
- `aigol/runtime/platform_core_project_services.py`;
- `aigol/runtime/platform_presentation_layer.py`;
- `aigol/runtime/human_decision_runtime.py`;
- the G31 authorization, Worker selection/assignment/dispatch/invocation,
  execution-candidate, governed-execution, CODEX activation/result/validation,
  task-review, disposable-validation, acceptance-prerequisite,
  generated-content-acceptance, existing-file-candidate, authorization, request,
  hardened replacement, and recovery owners referenced in the call graph;
- G14-22, G14-30, G14-31, G14-38A, G14-40, G19-05, G19-06, G30 closure,
  G31-04 through G31-24G-R04-R04-R03 reports and their focused tests;
- the exact uncommitted R04 test and report.

Git history and blame were used to distinguish an accepted historical claim
from the current production topology.  Reports were not treated as overriding
source or caller evidence.

## Recovered G0-G30 certified contract

The baseline is proven, not inferred.  G14-30 introduced one literal common
entry function:

```text
aigol.runtime.human_interface_runtime_entry_service
  ::run_human_interface_runtime_entry(...)
```

Its module docstring calls it the shared Platform Core entry boundary for human
interfaces, and its public docstring says it enters the certified runtime from
any Unified Human Interface.  G14-30 states that the service is
interface-independent and that future Web, Android, iOS, Voice, REST, Desktop,
and other interfaces can delegate to it without copying runtime logic.  G14-31
then certified both reference AiCLI and AiGOL Next through that exact symbol and
found the downstream runtime path equivalent.

The certified dependency and ownership direction was:

```text
transport adapter
-> run_human_interface_runtime_entry
-> Platform Core Project Services and governed conversation runtime
-> canonical artifacts, Replay, and presentation
-> adapter rendering
```

G14-40 removed the remaining adapter-authored approval/fail-closed semantics;
Platform Core owns conversation state, approval summaries, failure
explanations, clarification, and next-step guidance.  G19-06 added the public
`present_platform_response` / `validate_platform_presentation` normalization
surface so Human Interfaces can render common fields without understanding
service internals.  G30 closed on thin, operation-neutral Human Interfaces and
separate Governance, Provider, Worker, Replay, and mutation authority.

### Allowed adapter responsibilities

- collect bytes or UI events from the transport;
- implement compose buffers, terminal commands, widgets, accessibility, and
  connection mechanics;
- translate one contextual UI action into one interface-neutral application
  request;
- cache a canonical pending result only for transport continuity;
- render canonical presentation fields without inventing semantics;
- return canonical results to the transport.

### Forbidden adapter responsibilities

- select and order canonical workflow owners;
- create decision, authorization, Worker, acceptance, mutation, or recovery
  evidence directly;
- reconstruct Replay as the condition for choosing the next application step;
- own the only aggregate lifecycle state or pending-state semantics;
- derive canonical Replay destinations and artifact identities;
- require another adapter to understand an adapter-private result dictionary;
- embed transport identity or syntax where an interface-neutral actor/action is
  required;
- bypass the common entry because the low-level callees are individually
  reusable.

## G31 interface-change inventory and origin

| Generation / commit | Effective application transition | Current owner | Common-entry status |
| --- | --- | --- | --- |
| G31-04 `01e6239e` through G31-08 `d18b0efd` | approved durable work -> payload -> grounding -> pending execution review | canonical entry plus governed conversation runtime | Preserved/compatible extension |
| G31-09 `14f1f616` | pending execution review -> distinct human decision + Replay | `aicli._record_contextual_execution_decision` | First proven bypass |
| G31-10 `e5e8fa87` through G31-16B `02995b8f` | authorization -> selection -> request -> assignment -> dispatch -> invocation -> governed execution evidence | same AiCLI helper | Duplicated application orchestration |
| G31-17B `eb0c7eb7` through G31-22B `c20a2817` | activation decision -> CODEX call -> result capture -> validation -> outcome review/decision | AiCLI helpers and loop | Duplicated application orchestration |
| G31-24D R02 `10b13103` through R04 `c85453d3` | disposable review/decision/execution -> acceptance prerequisites | AiCLI helpers and loop | Duplicated application orchestration |
| G31-24D `a5d30c2a` and G31-24E `6e7c7ed7` | content decision -> Replay -> generated-content acceptance | AiCLI loop | Decision/Replay/application sequencing leak |
| G31-24G R01 `ba787435`, repaired by `8069f65e` | accepted content -> activation reconstruction -> V2 candidate + Replay | AiCLI loop | Candidate/Replay/application sequencing leak |
| Uncommitted R04 | V2 candidate -> V3 context -> exact decision -> Replay reconstruction -> presentation | AiCLI loop | Extends the same bypass |

The first violated boundary is therefore not speculative and is not introduced
only by the current delta.  At commit `14f1f6167692196159ee404ca6fe260b31ffe937`,
AiCLI gained `_record_contextual_execution_decision`, directly called
`bind_distinct_human_execution_decision`, chose session/Replay destinations,
and merged authoritative continuation fields into its private `runtime_result`.
The common entry was extended only to project the pending review artifact; it
was not extended to accept and process the decision.  Every later direct G31
continuation accumulated behind that adapter-local branch.

## Exact R04 working-tree delta

The R04 production delta is 109 additions and one changed line in
`aigol/cli/aicli.py`.  It introduces:

| Delta | Responsibility | Classification |
| --- | --- | --- |
| `pending_mutation_decision_context` | caches a canonical pending context | Permitted only as transport cache |
| EOF/pending/session/exit handling | terminal continuity | Adapter translation, but coupled to application state names |
| exact raw uppercase `APPROVED | REJECTED` parsing | contextual transport vocabulary | Permitted adapter translation |
| activation reconstruction and grounding extraction | proves application lineage before the decision | Canonical workflow and Replay sequencing |
| `record_existing_file_mutation_decision` call | creates the V3 authoritative decision | Common-entry bypass |
| `reconstruct_existing_file_mutation_decision_replay` call | validates Replay to advance the lifecycle | Replay orchestration leak |
| `runtime_result.update(...)` with decision and stop-state truth | sole aggregate application progression | Authoritative lifecycle-state leak |
| direct V3 renderer selection and terminal prompt | selects semantic result/context presentation | Presentation-selection leak |
| post-acceptance candidate creation/reconstruction | selects the next canonical owner and Replay path | Existing G31 orchestration leak expanded by R04 |
| V3 context preparation and Replay destination derivation | creates pending application state | Common-entry bypass |
| `HUMAN_OPERATOR_VIA_AICLI` in the decision/context subject | transport identity enters canonical evidence/hash | Transport-specific evidence leak |

The exact R04 sequence is in `run_reference_uhi_session` itself:

```text
prepare_existing_file_mutation_decision_context
-> parse exact APPROVED or REJECTED
-> reconstruct_codex_worker_activation_binding
-> record_existing_file_mutation_decision
-> reconstruct_existing_file_mutation_decision_replay
-> mutate runtime_result aggregate
-> render_existing_file_mutation_decision
-> stop before authorization
```

No public symbol in `human_interface_runtime_entry_service.py`, another
application service, or a versioned common-entry family exposes this sequence.
The low-level functions are reusable, but a second adapter must know their exact
order, full argument projection, Replay directories, aggregate keys, and stop
flags.  That is copied application logic, not adapter replacement.

## Current production call graph

```text
AiCLI input/composition
-> prepare_unified_human_interface_project_context
-> proposal presentation and first /approve
-> run_human_interface_runtime_entry                         SHARED ENTRY
   -> approved durable-work consumption / Platform Core runtime
   -> Worker payload and repository grounding
   -> execution-authorization review
-> return pending review to AiCLI                            SHARED ENTRY STOPS
-> AiCLI _record_contextual_execution_decision
   -> human execution decision + Replay
   -> execution authorization
   -> certified Worker selection
   -> invocation request -> assignment -> dispatch -> invocation
   -> execution candidate -> governed execution evidence
-> AiCLI activation pending state and third /approve
   -> CODEX activation -> transport -> result capture -> semantic validation
   -> task-outcome review
-> AiCLI task decision
   -> task decision + Replay
   -> disposable validation review
-> AiCLI disposable decision
   -> decision + Replay -> disposable execution + reconstruction
   -> G31-23B acceptance prerequisites + reconstruction
-> AiCLI content decision
   -> V2 content decision + reconstruction
   -> generated-content acceptance + reconstruction
   -> activation reconstruction / repository grounding
   -> V2 existing-file candidate + reconstruction
-> uncommitted R04 AiCLI V3 pending state
   -> exact APPROVED or REJECTED
   -> V3 decision + Replay reconstruction
   -> specialized result rendering
-> STOP before mutation authorization
```

Compatible but unreachable owners remain outside this production route:

```text
authorize_g31_approved_existing_file_mutation
-> reconstruct_g31_existing_file_mutation_authorization_binding
-> bind_g31_mutation_authorization_actor_and_replay
-> reconstruct_g31_mutation_authorization_actor_and_replay
-> create_g31_authenticated_replace_request
-> execute_g31_authenticated_replace / recover_g31_authenticated_replace
-> durable consumption / hardened replacement / restoration / recovery
```

Availability of those owners does not repair the shared-entry bypass.

## Transition ownership

| Transition | Artifact/state owner | Replay owner | Presentation owner | Production sequencer |
| --- | --- | --- | --- | --- |
| ingress/project intent | Platform Core Project Services | Project Services | Human Conversation Experience / canonical presentation | shared entry and adapter pre-entry calls |
| proposal approval to G31-08 review | Platform Core/governed conversation | each canonical owner | Platform Core projections | shared entry |
| G31-09 decision through governed execution evidence | canonical low-level owners | each low-level owner | specialized runtime renderers | AiCLI only |
| CODEX activation/result/validation | activation, Worker-result, validation owners | each low-level owner | specialized renderers | AiCLI only |
| task outcome and disposable validation | task-review and disposable owners | each low-level owner | specialized renderers | AiCLI only |
| prerequisites/content acceptance | prerequisite, human-decision, acceptance owners | each low-level owner | specialized renderers | AiCLI only |
| V2 candidate | candidate owner | candidate owner | candidate renderer | AiCLI only |
| R04 V3 decision | human-decision owner | human-decision owner | V3 renderer selected by AiCLI | AiCLI only |
| mutation authorization/request/physical lifecycle | Governance / Platform Core / hardened Worker | their existing Replay owners | existing specialized renderers where present | no production caller |

Canonical artifact authority remains in the low-level owners.  Application
orchestration authority, however, is effectively in AiCLI because only AiCLI
knows how and when to call those owners.  Authority flags saying
`aicli_authorizes=false` do not negate that topological fact.

## AiCLI direct-call inventory

### Certified/shared service calls

| Direct call | Classification |
| --- | --- |
| `prepare_unified_human_interface_project_context` | existing shared Platform Core pre-entry/context service |
| `record_unified_human_interface_workspace_state` | existing shared Platform Core persistence service |
| `guided_development_clarification` | compatibility presentation over Platform Core clarification |
| `run_human_interface_runtime_entry` | the one certified shared application entry |

### G31 direct orchestration calls

The following are all called directly from AiCLI rather than one shared G31
application transition:

- `bind_distinct_human_execution_decision`;
- `authorize_confirmed_grounded_execution_decision` and
  `select_authorized_grounded_worker`;
- `create_worker_invocation_request`, `default_worker_registry_for_request`,
  `assign_worker_from_invocation_request`, `dispatch_assigned_worker`, and
  `invoke_dispatched_worker`;
- `project_g31_invocation_to_execution_candidate` and
  `project_g31_candidate_to_governed_execution`;
- CODEX synthesis preflight, activation review/activation/reconstruction,
  result capture, and semantic validation;
- task-outcome review preparation/reconstruction, decision recording, and
  decision reconstruction;
- disposable-patch review preparation/reconstruction, human-decision recording,
  execution, and outcome reconstruction;
- replacement-acceptance prerequisite binding/reconstruction;
- V2 content context preparation, decision recording/reconstruction, generated
  content acceptance, and acceptance reconstruction;
- V2 existing-file candidate creation/reconstruction;
- uncommitted R04 V3 context preparation, decision recording, and Replay
  reconstruction.

These calls are canonical workflow sequencing or duplicated application
orchestration.  Direct calls to their `render_*` functions consume owner text,
but AiCLI still owns presentation selection and adds state-dependent semantic
instructions outside the canonical presentation layer.

AiCLI does not directly call the later G31 mutation authorization, actor/Replay
binder, authenticated request, hardened replace, or recovery owners.  There is
no R04 mutation reachability and no new physical-write edge.

## AiCLI state-ownership analysis

The compose buffer, input-line queue, transcript mechanics, and terminal exit
handling are legitimate adapter state.  A pending canonical artifact can also
be cached by an adapter without becoming authoritative.

The following state is not merely a cache:

- `runtime_result` is the only complete aggregate of the G31 lifecycle after
  the shared entry returns;
- `pending_execution_review`, `pending_activation_review`,
  `pending_task_outcome_review`, `pending_disposable_patch_validation_review`,
  `pending_content_acceptance_context`, and R04
  `pending_mutation_decision_context` select which canonical owner is legal to
  call next;
- AiCLI constructs Replay destinations and extracts nested lineage from
  `runtime_result`;
- AiCLI writes progression truth such as `worker_selected`, `result_accepted`,
  `mutation_decision_approved`, and all downstream stop flags;
- no interface-neutral application result can be passed to the same entry for
  the next action.

Individual artifacts remain authoritative in their owners, but the lifecycle
graph and aggregate state are authoritative only in AiCLI.  A future adapter
must understand these private fields and reproduce the branching.  This is
canonical lifecycle-state leakage.

## Dependency direction and evidence purity

- Relevant domain/runtime owners do not import `aigol.cli.aicli`; the static
  Python module dependency remains mostly adapter-to-runtime.
- Some certification/support runtimes import the historical `aigol_cli` command
  surface, but none supplies a shared G31 application transition and none cures
  this finding.
- `human_interface_runtime_entry_service` does not import AiCLI and remains a
  valid extraction host.
- Canonical Platform presentation does not depend on slash commands.
- The actual call graph nevertheless becomes
  `adapter -> many runtime owners` after G31-08 instead of
  `adapter -> shared application transition -> runtime owners`.
- `HUMAN_OPERATOR_VIA_AICLI` is bound into decision/candidate subjects and
  hashes.  A non-AiCLI adapter cannot produce hash-identical evidence while
  truthfully naming its own transport, and cannot reuse the AiCLI label without
  recording false provenance.
- R04 creates no terminal-only field in the V3 artifact vocabulary, but its
  actor and destination derivation are transport-bound at the call site.

## Adapter replaceability matrix

| Adapter | Same common entry for full G31 | Same pending/result presentation | Submit V3 action without copied sequence | Same semantic/hash evidence | Avoid AiCLI/runtime_result internals | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| Current AiCLI | No; common entry stops at G31-08 | Yes, locally selected | Yes, because it contains the sequence | Only for AiCLI actor | No | Operational but architecturally non-narrow |
| REST/API | No | No shared G31 application response | No | No | No | Not replaceable |
| Web | No | No shared G31 application response | No | No | No | Not replaceable |
| Speech | No | No shared G31 application response | No | No | No | Not replaceable |
| GUI/chat | No | No shared G31 application response | No | No | No | Not replaceable |
| Automation | No | No shared G31 application response | No | No | No | Not replaceable |

All hypothetical adapters could call the individual public owners, but doing so
would reproduce `run_reference_uhi_session` sequencing.  The audit definition
therefore requires a failure for all ten replaceability criteria: none can use
one shared application entry, receive/submit the same canonical pending action,
avoid AiCLI imports and private state, preserve evidence hashing, and continue
G31 without a parallel workflow implementation.

## G0-G30 versus current G31

| Boundary | Current classification | Evidence |
| --- | --- | --- |
| one common entry through G31-08 | Preserved | both primary interfaces call `run_human_interface_runtime_entry` |
| post-G31-08 application continuation | Common-entry bypass | only AiCLI sequences it |
| low-level decision/Replay authority | Compatible extension | canonical owners validate and persist artifacts |
| application sequencing | Narrow-adapter regression / duplicated orchestration | AiCLI helpers and loop own order and branching |
| aggregate lifecycle state | Authority leak | `runtime_result` and pending flags are the only continuation state |
| presentation semantics | Presentation leak | specialized renderer selection and prompts occur in AiCLI |
| actor/evidence purity | Transport-specific evidence leak | `HUMAN_OPERATOR_VIA_AICLI` is hash-bound |
| later mutation owners | Preserved but unreachable | no production authorization/request/replace caller |
| Python import direction | Mostly preserved | relevant runtime owners do not import AiCLI |

## First violation and smallest safe repair boundary

First violation:

```text
G31-09 commit 14f1f6167692196159ee404ca6fe260b31ffe937
aigol/cli/aicli.py::_record_contextual_execution_decision
```

The smallest safe architectural repair is a bounded extraction, not a redesign:

1. Extend the existing certified owner
   `aigol.runtime.human_interface_runtime_entry_service` with a versioned,
   interface-neutral application-transition entry (or a versioned member of
   the existing `run_human_interface_runtime_entry` symbol family).
2. Move the current G31 ordering, lineage projection, Replay reconstruction,
   aggregate state, pending-action selection, and stop-state composition behind
   that entry from the first G31-09 decision through reconstructed V3 decision
   presentation.
3. Accept an interface-neutral action envelope containing canonical session,
   actor, action vocabulary, timestamp, and prior application state.  Transport
   adapters translate `/approve`, `/accept`, exact uppercase text, buttons, HTTP
   requests, or speech intents into that envelope; transport syntax must not
   enter canonical hashes.
4. Return a canonical application result containing the authoritative state,
   pending action, canonical evidence identities, Replay identity, and
   presentation.  AiCLI may cache and render it but may not inspect nested
   captures to choose low-level callees.
5. Preserve every existing artifact family, hash algorithm, Replay owner,
   low-level owner, APPROVED/REJECTED behavior, and stop before mutation
   authorization.
6. Prove the same transition through a minimal in-memory non-AiCLI adapter that
   imports no CLI module and contains no copied workflow sequence.

Transport-only behavior that may remain in AiCLI includes composing requests,
mapping terminal commands to interface-neutral actions, terminal prompts and
wrapping, keyboard/EOF handling, transcript display, and caching the returned
canonical pending action.

R04 should not be committed as-is.  Its low-level calls and tests are valuable
behavioral evidence for the extraction, but the sequencing must move behind the
common application boundary first.

## Validation

Focused final-state validation:

| Evidence group | Result |
| --- | --- |
| G14-22 reference UHI, G14-30 common entry, G14-40 conversation ownership, and G19-06 canonical presentation | 33 passed, 0 failed, 0 skipped, 0 deselected in 1.12 seconds |
| Exact uncommitted R04 AiCLI V3 transport suite | 4 passed, 0 failed, 0 skipped, 0 deselected in 391.68 seconds |
| G31-09 decision, G31-18 result capture, G31-24D content decision, G31-24E acceptance, G31-24G R01 candidate, and R02 mutation-decision suites | 50 passed, 0 failed, 0 skipped, 0 deselected in 1096.14 seconds |
| Governance conformance tests | 5 passed, 0 failed, 0 skipped, 0 deselected in 0.03 seconds |

Distinct focused total: 92 passed, 0 failed, 0 skipped, 0 deselected.

Targeted `py_compile` passed for AiCLI, the common-entry service, human-decision
runtime, canonical presentation, V2 candidate, existing-file Governance, and
the R04 focused test.  Static symbol/caller and import-direction scans completed
without an execution side effect.  They proved that the relevant runtime owners
do not import AiCLI, that no common-entry symbol calls the R04 V3 sequence, and
that AiCLI is the sole production caller for most post-G31-08 transitions.

Governance engine result:

```text
status: PARTIALLY_CONFORMANT
checks_passed: 18
checks_failed: 2
critical_violations: 0
deterministic: true
fail_closed: true
read_only: true
report_hash: 0790499ee53f9a82e15225e15eff1c2637b7e60523fa38be0c921281abe4cbea
```

The two visible findings are unchanged: the expected/installed root pre-commit
hooks are missing, and the `sapianta_system` hook lacks
`promotion_gate_v02` / `check_layer_freeze`.  This audit does not conceal or
upgrade partial conformance.

Parent `git diff --check` passed.  The untracked audit report was checked with
`git diff --no-index --check /dev/null <report>`; the expected exit status was
one because the file is new, and there was no whitespace-error output.  Parent
and all nested-repository diff checks passed.

The full repository suite and live PTY workflow were not run because focused
evidence is consistent with the committed certifications and the finding is a
static production-topology defect.

## Repository preservation and nested repositories

All nine protected SHA-256 values exactly matched their initial values.  The
three pre-existing R04 subject hashes also matched byte-for-byte:

```text
aigol/cli/aicli.py
  76611464b24e7d2d5c8ad7f01f1cbb821a193dfff411729e2e4c6b85bec8044c
tests/test_g31_24g_r04_r04_r04_aicli_v3_mutation_decision_transport.py
  02f687d5db5ef8681bde847a052cd13201c2d2c57ab7a7573448212c7ecaaf5b
docs/governance/G31_24G_R04_R04_R04_AICLI_V3_MUTATION_DECISION_TRANSPORT_BINDING.md
  503d93f4f0893df4fed54f9514fd9d3fb7bf82157e730731ec3d520e27ef2a19
```

No production or test file was edited by A01.  This report is the sole file
created by the audit.  HEAD remained
`4d5dbd94d16e258904ef250024284df1f8e3ef63`; nothing is staged and no commit was
created.  Focused tests wrote only below pytest temporary directories.  No
authorization, request, consumption, Worker, Provider, command, mutation,
restoration, recovery, completion, or termination evidence was created in the
source repository.

Exact final parent status:

```text
## master...origin/master [ahead 65]
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/diagnostic_evidence.json
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/governed_return.json
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/lineage.json
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/provider_stderr.txt
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/provider_stdout.txt
 M .runtime/aigol/ledger/governed_returns.jsonl
 M aigol/cli/aicli.py
?? WORKER_INVOCATION_ARTIFACT_V1
?? WORKER_INVOKED
?? docs/governance/G31_24G_R04_R04_R04_A01_ADAPTER_NARROWNESS_AND_COMMON_ENTRY_POINT_PRESERVATION_AUDIT.md
?? docs/governance/G31_24G_R04_R04_R04_AICLI_V3_MUTATION_DECISION_TRANSPORT_BINDING.md
?? invocation
?? tests/test_g31_24g_r04_r04_r04_aicli_v3_mutation_decision_transport.py
```

Nested repositories are clean:

- `sapianta-domain-credit`: `main...origin/main`;
- `sapianta_system`:
  `feature/governance-evolution-loop...origin/feature/governance-evolution-loop [ahead 2]`;
- `sapianta-domain-trading`: `main...origin/main`.

## Evidence-scoped progress

Functional conversational reachability remains approximately 99.92%, because
R04 reaches and reconstructs the V3 decision and still stops before
authorization.  Architecture-safe G31 integration is estimated at 98.9% until
the existing lifecycle is reachable through the certified common entry.  The
whole project remains approximately 97.7% complete on the same evidence scope.
No percentage implies authorization or physical mutation readiness.

## Exactly one next state

`G31_COMMON_ENTRY_POINT_AND_NARROW_ADAPTER_ARCHITECTURE_REPAIR_REQUIRED`

## Complete bounded next Codex prompt

```text
# Generation 31-24G-R04-R04-R04-A02 — Common Entry-Point and Narrow Adapter Architecture Repair

Repository: /home/pisarna/work/sapianta
Executor: Codex
Reasoning effort: High

Required baseline:
- committed HEAD must still contain
  docs/governance/G31_24G_R04_R04_R03_HARDENED_REPLACE_OWNER_LIVE_REACHABILITY_AUDIT.md
  with G31_HARDENED_REPLACE_OWNER_LIVE_BINDING_REQUIRED;
- the uncommitted R04 subject files must be present at these exact SHA-256 values:
  - aigol/cli/aicli.py = 76611464b24e7d2d5c8ad7f01f1cbb821a193dfff411729e2e4c6b85bec8044c
  - tests/test_g31_24g_r04_r04_r04_aicli_v3_mutation_decision_transport.py = 02f687d5db5ef8681bde847a052cd13201c2d2c57ab7a7573448212c7ecaaf5b
  - docs/governance/G31_24G_R04_R04_R04_AICLI_V3_MUTATION_DECISION_TRANSPORT_BINDING.md = 503d93f4f0893df4fed54f9514fd9d3fb7bf82157e730731ec3d520e27ef2a19;
- the A01 report must contain G31_ADAPTER_NARROWNESS_DRIFT_DETECTED.

Stop and report the exact blocker if the committed baseline, R04 hashes, or A01
verdict differ. Preserve all nine protected paths. Do not stage or commit.

Objective:
Restore the exact G0-G30 dependency direction by extracting the canonical G31
application state machine from aigol/cli/aicli.py into the existing certified
interface-neutral owner:

  aigol/runtime/human_interface_runtime_entry_service.py

Implement one versioned public application-transition entry, or a versioned
extension of run_human_interface_runtime_entry, that owns G31 sequencing from
the first post-G31-08 pending execution decision through canonical reconstructed
V3 APPROVED or REJECTED result presentation. It must reuse every existing
decision, authorization, Worker, activation, validation, review, disposable,
acceptance, candidate, Replay, hashing, and presentation owner. Do not create a
parallel artifact, decision, Replay, router, authorization, Worker, mutation,
rollback, or recovery system.

The common transition must accept interface-neutral session/application state
and an interface-neutral human action envelope. It must return one canonical
application result containing authoritative lifecycle state, exact pending
action, canonical presentation, evidence/Replay identities, and false
downstream mutation flags. Transport syntax such as /approve, /accept, terminal
EOF, button names, HTTP fields, or speech text must remain outside canonical
hashes. Bind a truthful human actor independently of adapter brand; preserve
existing actor semantics through an explicitly versioned compatible projection
if changing the currently hash-bound HUMAN_OPERATOR_VIA_AICLI value would alter
accepted artifacts.

Reduce AiCLI to transport duties:
- compose/terminal input and output;
- contextual mapping from current commands or exact R04 text to the neutral
  action envelope;
- one call to the common transition per application action;
- rendering/caching the returned canonical result and pending action;
- keyboard, EOF, help, and transcript mechanics.

AiCLI must no longer directly select or sequence G31 decision, Replay,
authorization, Worker selection/assignment/dispatch/invocation, execution,
activation, result capture, validation, task-review, disposable-validation,
acceptance, candidate, or V3 owners. It must not derive Replay destinations or
inspect nested runtime_result captures to choose the next low-level call.

Preserve current semantics and evidence:
- all existing G31 positive, rejection, ambiguous-input, duplicate, tamper,
  cross-session, and stop states;
- exact R04 APPROVED and REJECTED semantics;
- existing artifact families, versions, hashes, Replay order, and owner
  authority;
- CODEX remains WORKER_ROLE only and Provider authority remains absent;
- V1/V2 compatibility;
- no new authorization or physical-write reachability.

Mandatory stop:
After reconstructed V3 decision presentation:
  human_mutation_decision_recorded=true
  mutation_decision_approved=true|false
  mutation_authorized=false
  authorization_actor_bound=false
  authorization_replay_recorded=false
  authorization_consumed=false
  replace_request_created=false
  worker_invoked=false beyond the one already-certified CODEX lifecycle
  provider_invoked=false
  command_executed=false
  repository_mutated=false
  main_repository_mutated=false

Do not call authorize_g31_approved_existing_file_mutation,
bind_g31_mutation_authorization_actor_and_replay,
create_g31_authenticated_replace_request, execute_g31_authenticated_replace,
recover_g31_authenticated_replace, authorization consumption, replacement,
restoration, recovery, completion, or termination owners.

Replaceability proof:
Add a minimal in-memory non-AiCLI adapter fixture. It must import no aigol.cli
module, contain no copied G31 owner sequence, call the same common transition,
receive the same canonical pending presentation, submit APPROVED and REJECTED
through the same application contract, and obtain evidence identical in
semantics and hashing for the same neutral actor/session inputs. Prove AiCLI and
the in-memory adapter differ only in transport parsing/rendering.

Scope:
- maximum 3 production files;
- prefer moving/extracting existing logic over rewriting it;
- no new top-level artifact family, router, authorization owner, or workflow;
- one focused common-entry/adapter test module plus minimal updates to existing
  tests whose imports must move;
- one governance report:
  docs/governance/G31_24G_R04_R04_R04_A02_COMMON_ENTRY_POINT_AND_NARROW_ADAPTER_ARCHITECTURE_REPAIR.md.

Validation:
Run G14 common-entry/UHI/presentation tests, all affected G31 interface tests,
the R04 focused suite, the in-memory adapter proof, architecture/import-boundary
checks, Governance tests/engine, targeted py_compile, parent/nested
git diff --check, protected and R04-subject hash accounting, and exact status.
All execution or filesystem fixtures must use pytest temporary directories and
temporary Git repositories. Do not run a live PTY workflow. Run the full suite
only if focused evidence conflicts with committed certification.

Return exactly one verdict:
- G31_COMMON_ENTRY_POINT_AND_NARROW_ADAPTER_ARCHITECTURE_REPAIR_OPERATIONAL
- G31_COMMON_ENTRY_POINT_AND_NARROW_ADAPTER_ARCHITECTURE_REPAIR_BLOCKED

If operational, return exactly one next state:
G31_24G_R04_R04_R05_CANONICAL_APPROVED_V3_DECISION_TO_MUTATION_AUTHORIZATION_BINDING_REQUIRED

That later authorization transition must remain UI-independent and must stop
before authenticated request construction, authorization consumption, Worker
dispatch, or mutation.
```
