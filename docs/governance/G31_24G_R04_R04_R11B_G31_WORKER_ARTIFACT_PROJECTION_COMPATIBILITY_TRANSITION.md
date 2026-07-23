# Generation 31-24G-R04-R04-R11B G31 Worker Artifact Projection Compatibility Transition

Status: completed minimal Worker-neutral compatibility transition; stopped
before live Worker Assignment.

Date: 2026-07-23

Deterministic verdict:

`G31_WORKER_ARTIFACT_PROJECTION_COMPATIBILITY_OPERATIONAL`

Resolved blocker:

`R09B_CERTIFIED_SELECTION_LINEAGE_NOT_ACCEPTED_BY_DEFAULT_WORKER_ARTIFACT_PROJECTION`

## Constitutional scope

This generation treats G0-G30 Platform Core and accepted G31 R05, R06, R07,
R08, R08A, R08B, R08C, R09A, R09B, R10A, R10B, and R11A as immutable
certified baselines.

It changes only the existing
`aigol.runtime.worker_assignment_runtime.default_worker_registry_for_request`
projection. When an already-certified
`AUTHENTICATED_REPLACEMENT_SELECTION_LINEAGE_V1` is present, that projection
now creates one existing `WORKER_ARTIFACT_V1` from the exact selected resource
rather than using the legacy synthetic fallback.

It does not select a Worker, change the unified registry, change the Assignment
runtime, create an Assignment, dispatch or invoke a Worker, invoke a Provider,
execute a command, open a mutation target, mutate a target repository,
generate certification evidence, or add a Replay or artifact family.

## Accepted baseline

The work began from:

- branch: `master`;
- HEAD: `e55296ac226b1c96d2624e0a887e5fcdb3358e54`;
- HEAD subject:
  `docs(governance): audit worker assignment operational readiness`;
- R10B verdict:
  `G31_ASSIGNMENT_REQUEST_HASH_COMPATIBILITY_OPERATIONAL`;
- R11A verdict: `G31_WORKER_ASSIGNMENT_OPERATIONAL_BLOCKED`;
- R11A blocker:
  `R09B_CERTIFIED_SELECTION_LINEAGE_NOT_ACCEPTED_BY_DEFAULT_WORKER_ARTIFACT_PROJECTION`;
- input family: `WORKER_INVOCATION_REQUEST_ARTIFACT_V1`;
- output family: `WORKER_ARTIFACT_V1`;
- typed lineage:
  `AUTHENTICATED_REPLACEMENT_SELECTION_LINEAGE_V1`.

The six modified runtime-evidence/ledger paths and three empty marker paths
predated R11B. Their hashes were captured before implementation.

## Minimal implementation

One production file was modified:

`aigol/runtime/worker_assignment_runtime.py`

The existing `default_worker_registry_for_request` now distinguishes three
existing input states:

1. typed certified compatibility lineage;
2. the accepted older `g31_lineage` path;
3. the legacy request-only fallback.

Only the first state is new. The other two remain behaviorally unchanged.

The new internal `_certified_compatibility_worker_projection` function:

- requires exactly one typed lineage and rejects ambiguous simultaneous
  `g31_lineage`;
- reads the already-created `RESOURCE_SELECTION_ARTIFACT_V1`;
- verifies its public artifact hash;
- compares the selection to the request, authenticated request, selection
  context, registry identity, certification identity, and stop flags;
- returns the exact selected artifact, Selection Replay reference, and
  metadata required by the existing Worker artifact;
- has no Worker identity, capability, CODEX, Provider, Dispatch, Invocation,
  command, or mutation branch.

It does not query a registry, score candidates, choose among resources, or
create selection evidence. Selection authority remains exclusively upstream.

## Exact projection

The certified R08C/R09B lineage projects:

| Existing Worker field | Certified source |
|---|---|
| `worker_id` | `selection.selected_resource_id` |
| `worker_version` | `selection.selected_resource_version` |
| `worker_type` / `worker_family` | invocation request `target_worker_family` |
| `worker_roles` | `selection.selected_role_type` |
| `capability_id` | `selection.required_capability` |
| `declared_capabilities` | exact capability plus existing request role |
| `selected_resource_category` | selected resource category |
| `selected_authority_profile` | selected authority profile |
| `selected_domain_id` | selected domain |
| `selection_artifact_hash` | exact Selection artifact hash |
| `selection_context_reference/hash` | exact Selection context |
| `selection_registry_hash` | exact certified registry hash |
| `worker_selection_certification_hash` | exact R08B report hash |
| `replay_reference` | exact R08C Selection Replay reference |
| `compatible_execution_packets` | exact authenticated request identity |
| `allowed_outputs` | existing invocation-request outputs |
| `forbidden_operations` | existing invocation-request prohibitions |

For the accepted replacement Worker, the projected identity is:

```text
worker_id = FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER
worker_version = G8_12_EXISTING_FILE_MUTATION_IMPLEMENTATION_V1
resource_category = WORKER
worker_role = WORKER_ROLE
capability_id = REPLACE_EXISTING_TEXT_FILE
authority_profile = WORKER_AUTHORIZED_TASK_ONLY
domain = NATIVE_DEVELOPMENT
```

No synthetic `AIGOL-WORKER-*` identity is created when the typed certified
lineage is present.

## Existing artifact and runtime preservation

The output remains the existing `WORKER_ARTIFACT_V1`:

- no schema or artifact-family constant changed;
- the existing canonical hash covers all projected metadata;
- availability remains `AVAILABLE`;
- trust boundary remains `LOCAL_BOUNDED_WORKER`;
- supported request type remains `WORKER_INVOCATION_REQUEST`;
- request packet, allowed-output, and forbidden-operation compatibility retain
  their existing meanings;
- all authority and execution flags remain false.

The Assignment owner and its evidence, classification, assignment, result, and
Replay functions were not modified.

The older G31 CODEX projection continues to return its accepted identity,
version, category, role, and authority profile. The request-only fallback
continues to exist only for request families without certified selection
lineage.

## Fail-closed behavior

The focused suite proves rejection before Assignment for:

- changed selected Worker identity;
- changed Worker version;
- changed capability;
- changed resource category;
- changed authority profile;
- changed domain;
- missing Selection Replay reference;
- changed certification hash;
- a prior `worker_assigned = true` state;
- ambiguous simultaneous typed and older G31 lineage.

The projection also requires:

- successful selection state in the artifact and capture;
- request, selected resource, and context Worker identity continuity;
- role continuity;
- authenticated operation/capability continuity;
- context identity and hash continuity;
- registry and certification continuity;
- Worker authorization present;
- Provider, Worker, Dispatch, Assignment, execution, command, and repository
  mutation states false.

Invalid evidence creates no Worker artifact and does not call Assignment.

## Authority and lifecycle boundary

The successful compatibility result is only one available Worker artifact:

```text
worker_assigned = false
worker_dispatched = false
worker_invoked = false
execution_performed = false
completion_recorded = false
governance_authority = false
approval_authority = false
proposal_authority = false
provider_authority = false
self_authorization = false
replay_mutation_authority = false
```

The focused R11B tests call only the projection. They assert that no
`worker-assignment` destination exists and that the authenticated replacement
target remains unchanged.

The requested complete suite and existing G31-12B regressions include ordinary
temporary-fixture tests of the pre-existing Assignment runtime. No R11B
production continuation called Assignment, no live application Assignment was
performed, and no repository runtime Replay or mutation artifact was created
by this transition.

## Common Entry and registry continuity

Common Entry was not modified. The accepted R09B continuation still stops
after the certified invocation request with `worker_assigned = false`.

AiCLI remains a transport and presentation adapter. No Worker projection,
selection, Assignment, or execution authority moved to an adapter.

The unified selection registry, R08B certification evidence, passive ERR
registry, and all other registry owners remain byte-for-byte outside the R11B
delta.

## Production symbols

New internal production symbol:

- `_certified_compatibility_worker_projection`: validates and returns the exact
  typed selected-resource projection without selecting or assigning.

Modified production symbol:

- `default_worker_registry_for_request`: uses the typed projection when
  certified compatibility lineage is present and otherwise retains its two
  existing branches.

Imported existing constant:

- `AUTHENTICATED_REPLACEMENT_SELECTION_LINEAGE_V1`.

No helper algorithm was copied and no new public runtime surface was added.

## Change size

Before this report, the scoped delta was:

| Category | Files | Insertions | Deletions |
|---|---:|---:|---:|
| Production | 1 modified | 107 | 4 |
| Tests | 1 new | 157 | 0 |
| Registry/certification/Replay evidence | 0 | 0 | 0 |

The production additions are validation and metadata projection inside the
single existing owner. No production file or artifact family was added.

## Validation

Focused validation ran before the complete suite:

| Validation command group | Passed | Skipped | Failed |
|---|---:|---:|---:|
| Final focused R11B projection suite | 13 | 0 | 0 |
| R09B and R10B compatibility regressions | 21 | 0 | 0 |
| Existing G31 selection-to-assignment regressions | 14 | 0 | 0 |
| R05-R11B certified-spine group | 132 | 0 | 0 |
| Common Entry and constitutional layer checks | 23 | 0 | 0 |
| Governance tests | 5 | 0 | 0 |

The first focused invocation returned 12 passed and one failed assertion
because the legacy test helper returns a selection capture rather than its
nested artifact. That test-only lookup was corrected. A subsequent accidental
edit of the analogous positive assertion produced two test-only lookup
failures; both assertions were corrected before the final 13-test focused
pass. No production repair followed either assertion failure.

Targeted `py_compile` passed for:

- `aigol/runtime/worker_assignment_runtime.py`;
- `tests/test_g31_24g_r04_r04_r11b_worker_artifact_projection_compatibility.py`.

Parent and all three nested `git diff --check` checks passed.

The complete repository suite ran exactly once and returned:

```text
6787 passed, 4 skipped, 0 failed in 4445.06s (1:14:05)
```

No second complete-suite invocation was run.

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
`promotion_gate_v02` and `check_layer_freeze`. R11B neither repairs nor
reinterprets them.

## Protected and nested state

All protected SHA-256 values equal the pre-R11B baseline:

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

## Git state

The scoped R11B change contains one modified production file, one new focused
test file, and this governance report. Nothing was staged and no commit was
created.

## Deterministic verdict

`G31_WORKER_ARTIFACT_PROJECTION_COMPATIBILITY_OPERATIONAL`

The existing default Worker registry projection now preserves the exact
certified Selection lineage in one existing `WORKER_ARTIFACT_V1`, creates no
synthetic Worker identity when that lineage is present, remains Worker-neutral,
and stops before live Assignment.
