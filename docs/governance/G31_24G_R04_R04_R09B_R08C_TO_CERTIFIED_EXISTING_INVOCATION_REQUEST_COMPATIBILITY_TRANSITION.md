# Generation 31-24G-R04-R04-R09B R08C to Certified Existing Invocation Request Compatibility Transition

Status: completed bounded lineage compatibility transition; stopped before
Worker assignment and all later execution stages.

Date: 2026-07-22

Deterministic verdict:

`G31_R08C_TO_EXISTING_INVOCATION_REQUEST_COMPATIBILITY_OPERATIONAL`

Resolved blocker:

`R08C_AUTHENTICATED_REPLACEMENT_LINEAGE_NOT_ACCEPTED_BY_CERTIFIED_WORKER_INVOCATION_REQUEST_CONTRACT`

## Constitutional scope

This generation treats G0-G30 Platform Core and accepted G31 R05-R09A as
immutable baselines. It adds only the typed lineage translation needed for the
exact reconstructed R05-R08C replacement lineage to produce the existing
`WORKER_INVOCATION_REQUEST_ARTIFACT_V1` family through Common Entry.

The transition does not change Assignment, any registry, selection
certification, the R05 authorization, R06 request, R07 consumption, or R08C
selection. It does not dispatch or invoke a Worker, invoke a Provider, execute
a command, open a mutation target, mutate a repository, restore, roll back, or
recover. It generated no checked runtime certification evidence and ran no
live PTY or mutation workflow.

## Accepted baseline

The work began from:

- branch: `master`;
- HEAD: `2fc59ec1`;
- HEAD subject:
  `docs(governance): audit filesystem replace worker assignment compatibility`;
- R08C verdict:
  `G31_CONSUMED_REPLACEMENT_REQUEST_TO_CERTIFIED_EXISTING_WORKER_SELECTION_BINDING_OPERATIONAL`;
- R09A verdict:
  `G31_FILESYSTEM_REPLACE_WORKER_ASSIGNMENT_ARCHITECTURE_BLOCKED`;
- verified first blocker:
  `R08C_AUTHENTICATED_REPLACEMENT_LINEAGE_NOT_ACCEPTED_BY_CERTIFIED_WORKER_INVOCATION_REQUEST_CONTRACT`.

The six modified runtime-evidence paths and three empty marker paths predated
R09B. Their hashes were recorded before implementation and remain unchanged.

## Exact implementation

The existing invocation-request owner now accepts one additional typed source
lineage:

`AUTHENTICATED_REPLACEMENT_SELECTION_LINEAGE_V1`

The new public transition
`create_authenticated_replacement_worker_invocation_request` accepts only:

- the exact authenticated R06 request;
- the exact reconstructed R07 consumption;
- the exact R08C certified selection capture and Selection Replay;
- the checked R08B selection-certification reference;
- request identity, actor, timestamp, and a session-local Replay destination.

It independently reconstructs request/consumption Replay and Selection Replay,
validates the checked certification against the unchanged canonical registry,
and compares the selected resource, capability, role, authority profile,
version, domain, context, registry, and certification identities. Only then
does it project the evidence into the existing four-artifact invocation-request
pipeline.

The projection is selected-evidence driven. It contains no branch on
`FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER`, `REPLACE_EXISTING_TEXT_FILE`,
`CODEX`, or another Worker identity. The only new discriminator is the
authenticated replacement request family. The selected Worker identity and
operation are read from reconstructed evidence and must equal the authenticated
request.

## Existing contract reuse

The implementation reuses unchanged:

- `validate_authenticated_replace_request_v2`;
- `reconstruct_authenticated_replace_replay_v2`;
- `default_resource_registry`;
- `validate_worker_selection_certification_v1`;
- `reconstruct_unified_resource_selection_replay`;
- `WORKER_INVOCATION_REQUEST_EVIDENCE_ARTIFACT_V1`;
- `WORKER_INVOCATION_REQUEST_CLASSIFICATION_ARTIFACT_V1`;
- `WORKER_INVOCATION_REQUEST_ARTIFACT_V1`;
- `WORKER_INVOCATION_REQUEST_RESULT_ARTIFACT_V1`;
- the existing four-step invocation-request Replay writer;
- canonical serialization, hashing, immutable writes, and presentation;
- `run_human_interface_runtime_entry` as the public application transition.

No new artifact family, registry, selector, authorization owner,
certification owner, Replay subsystem, assignment owner, Worker, Provider, or
adapter path was introduced.

## Exact lineage translation

The existing invocation-request schema retains its established field names.
The typed compatibility lineage makes their source semantics explicit and
prevents an authenticated request from being silently represented as an
ordinary execution-ready packet.

| Existing request field | Exact R05-R08C source |
|---|---|
| `chain_id` | canonical R08C selection-context hash |
| `authorization_reference` | R05 mutation authorization ID retained by R06 |
| `authorization_hash` | exact actor-bound R05 authorization hash retained by R06/R07 |
| `execution_ready_reference` | R08C selection-context identity |
| `execution_ready_hash` | exact R08C selection-context hash |
| `execution_candidate_reference` | exact R08C selection ID |
| `execution_candidate_hash` | exact R08C selection artifact hash |
| `execution_packet_reference` | exact authenticated R06 request ID |
| `execution_packet_hash` | exact authenticated R06 request hash |
| `approval_reference/hash` | exact approved V3 mutation-decision identity/hash |
| `target_worker_family` | reconstructed selected resource ID |
| `worker_role` | reconstructed selected role |
| `target_domain` | reconstructed selection domain |
| `allowed_outputs` | exact authenticated target path |

The complete authenticated request, consumption reconstruction, canonicalized
selection capture, selection context, request/consumption Replay identity,
Selection Replay identity, certification reference, and certification hash are
stored inside `compatibility_lineage`. The existing request hash now covers
that entire lineage. This is an immutable parent translation, not a second
authorization or execution packet.

The bounded classification records only validation and prohibition terms:
authenticated-request Replay, single-use-consumption Replay, certified
Selection Replay, preimage and replacement hashes, Provider invocation,
shell-command execution, and mutation outside the authenticated target. It
does not grant Assignment, dispatch, invocation, command, or mutation
authority.

## Replay continuity and tamper result

Creation requires:

```text
R05 actor-bound mutation authorization
  -> R06 authenticated replacement request
  -> R07 single-use authorization consumption
  -> R08B checked selection certification and registry
  -> R08C certified Worker selection
  -> existing four-step Worker invocation-request Replay
  -> STOP before Assignment
```

The invocation-request reconstructor now selects the parent reconstructor by
the explicit typed lineage. For this path it reconstructs both R07 and R08C,
reloads and validates the checked R08B report, rebuilds the canonical
compatibility lineage, and requires byte-semantic equality with the lineage
covered by the request hash.

It also requires the exact four-file invocation-request Replay set. Focused
tests prove fail-closed behavior for removed, duplicated, reordered, or
substituted request Replay and for changed request, consumption, selection,
context, certification, or session evidence. Invalid input records no request
artifact and cannot partially satisfy the transition.

## Common Entry and interface neutrality

The R08C branch in `_authorize_g31_mutation_decision` calls the new request
owner after certified selection, aggregates its existing capture, and returns
with `worker_assigned = false`. Canonical Presentation uses the existing
`render_worker_invocation_request_summary` and explicitly states that
Assignment was not reached.

AiCLI remains a transport. It contains no call to the compatibility owner,
request validator, request/consumption reconstructor, selector,
certification validator, Assignment, dispatch, invocation, command, or
mutation owner. The focused non-AiCLI adapter reaches the transition only
through `run_human_interface_runtime_entry`.

Terminal, display, and adapter fields are absent from the compatibility
lineage and do not affect request identity.

## Authority boundary

The successful transition retains:

```text
worker_selected = true
worker_invocation_request_created = true
worker_assigned = false
worker_dispatched = false
provider_invoked = false
worker_invoked = false
execution_started = false
command_executed = false
repository_mutated = false
```

Focused spies remained zero for Assignment, dispatch, invocation, physical
replacement, target opening, and command execution. The request artifact is
explicitly non-authoritative. It preserves prior authority; it does not create
or consume authority.

## Production symbols and responsibilities

New production symbols:

- `AUTHENTICATED_REPLACEMENT_SELECTION_LINEAGE_V1`: typed discriminator for
  the accepted parent lineage;
- `create_authenticated_replacement_worker_invocation_request`: public
  pre-Assignment compatibility transition;
- `_create_request_from_lineage`: shares the existing four-artifact creation
  and persistence path between the original and compatibility entries;
- `_load_authenticated_replacement_selection_lineage`: reconstructs and
  validates request, consumption, selection, certification, session, Replay,
  and authority continuity without choosing a Worker;
- `_project_authenticated_replacement_lineage`: translates validated parent
  identities into the existing invocation-request fields.

Modified production symbols:

- `create_worker_invocation_request`: delegates artifact creation to the
  shared existing-family helper; its accepted execution-authorization behavior
  is unchanged;
- `reconstruct_worker_invocation_request_replay`: requires the exact file set
  and reconstructs the explicit compatibility lineage when present;
- `_request_artifact`: includes the typed compatibility lineage when supplied;
- `_validate_request_artifact`: rejects ambiguous or authority-inconsistent
  compatibility lineage;
- `_request_hash`: covers the complete compatibility lineage;
- `_authorize_g31_mutation_decision`: calls and aggregates the request
  transition after R08C selection and returns before Assignment;
- `_continue_g31_application_transition`: renders the existing request summary
  and truthful Assignment stop.

No helper was copied from R05-R08C. Existing public validators,
reconstructors, hash functions, immutable writers, and renderers are reused.

## Change size

Before this report, the scoped R09B delta was:

| Category | Files | Insertions | Deletions |
|---|---:|---:|---:|
| Production | 2 modified | 450 | 35 |
| Tests | 1 new | 247 | 0 |
| Registries/certification evidence | 0 | 0 | 0 |

Production-file justification:

- `worker_invocation_request_runtime.py` is the existing certified owner of
  request artifacts, classification, validation, persistence, and Replay;
- `human_interface_runtime_entry_service.py` is the existing Common Entry
  sequencer and canonical lifecycle aggregator.

The production size is driven by complete reconstruction and fail-closed
comparison of two immutable parent Replay chains. No production file or
abstraction was added, and Assignment was not modified.

## Validation

Validation ran with focused suites first. The complete repository suite was
then invoked exactly once.

| Validation group | Passed | Skipped/Deselected | Failed |
|---|---:|---:|---:|
| Focused R09B compatibility, Common Entry, tamper, and zero-downstream tests | 13 | 0 | 0 |
| Existing invocation-request regressions | 13 | 0 | 0 |
| R05-R08C regressions | 124 | 0 | 0 |
| Common Entry, Human Interface, architecture, and layer boundaries | 38 | 0 | 0 |
| Existing G31-12B request/assignment compatibility, live downstream test excluded | 13 | 1 deselected | 0 |
| Governance tests | 5 | 0 | 0 |

Targeted `py_compile` passed for both modified production files and the new
focused test. Parent `git diff --check` and all three nested repository
`git diff --check` checks passed.

The complete repository suite ran exactly once and returned:

```text
6766 passed, 4 skipped, 0 failed in 4431.92s (1:13:51)
```

No second complete-suite invocation was run.

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

The known hook findings remain visible and unchanged. R09B neither repairs nor
reinterprets them.

## Protected and nested state

All protected SHA-256 values equal the pre-R09B baseline:

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

Nothing is staged and no commit was created. The six modified evidence paths
and three markers predate R09B and are excluded from its scoped delta.

Exact final `git status --short`:

```text
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/diagnostic_evidence.json
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/governed_return.json
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/lineage.json
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/provider_stderr.txt
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/provider_stdout.txt
 M .runtime/aigol/ledger/governed_returns.jsonl
 M aigol/runtime/human_interface_runtime_entry_service.py
 M aigol/runtime/worker_invocation_request_runtime.py
?? WORKER_INVOCATION_ARTIFACT_V1
?? WORKER_INVOKED
?? docs/governance/G31_24G_R04_R04_R09B_R08C_TO_CERTIFIED_EXISTING_INVOCATION_REQUEST_COMPATIBILITY_TRANSITION.md
?? invocation
?? tests/test_g31_24g_r04_r04_r09b_r08c_invocation_request_compatibility.py
```

No command below was executed:

```bash
git add aigol/runtime/worker_invocation_request_runtime.py
git add aigol/runtime/human_interface_runtime_entry_service.py
git add tests/test_g31_24g_r04_r04_r09b_r08c_invocation_request_compatibility.py
git add docs/governance/G31_24G_R04_R04_R09B_R08C_TO_CERTIFIED_EXISTING_INVOCATION_REQUEST_COMPATIBILITY_TRANSITION.md
git commit -m "feat(runtime): bind R08C lineage to existing invocation request"
```

## Remaining boundary and verdict

R09B ends with one reconstructed existing invocation request and no Assignment.
The existing Assignment registry and exact replacement-Worker assignment
evidence remain unchanged and downstream. They are not interpreted as part of
this compatibility verdict.

Deterministic verdict:

`G31_R08C_TO_EXISTING_INVOCATION_REQUEST_COMPATIBILITY_OPERATIONAL`
