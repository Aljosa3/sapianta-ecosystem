# Generation 31-24G-R04-R04-R08B Bounded Filesystem Replace Worker Selection Certification

Status: completed bounded registry admission and existing-model selection
certification; stopped before R07 binding or downstream execution.

Date: 2026-07-22

Deterministic verdict:

`G31_FILESYSTEM_REPLACE_WORKER_SELECTION_CERTIFIED`

Exactly one next state:

`G31_24G_R04_R04_R08C_CONSUMED_REPLACEMENT_REQUEST_TO_CERTIFIED_WORKER_SELECTION_BINDING_REQUIRED`

## Constitutional scope

This generation treats Generation 30, accepted G31 common-entry and R05-R07
results, the R08 blocked report, and the accepted R08A audit as immutable
baselines. It admits and certifies exactly one already-existing Worker and one
exact capability in the existing unified resource registry:

```text
resource_id = FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER
resource_version = G8_12_EXISTING_FILE_MUTATION_IMPLEMENTATION_V1
resource_category = WORKER
role_type = WORKER_ROLE
capability = REPLACE_EXISTING_TEXT_FILE
authority_profile = WORKER_AUTHORIZED_TASK_ONLY
domain = NATIVE_DEVELOPMENT
```

No R07 request or consumption evidence was bound. No common-entry
continuation, assignment, dispatch, Worker invocation, Provider invocation,
command execution, target opening, repository mutation, restoration, rollback,
or recovery owner was called by the R08B transition. No dedicated R08B live
PTY or mutation workflow was run.

## Accepted baseline

The work began from:

- branch: `master`;
- HEAD: `aaff05d0ba7d37253594952feb645d093c05bcd4`;
- HEAD subject:
  `docs(governance): audit filesystem replace worker selection compatibility`;
- R08A verdict: `READY_FOR_BOUNDED_SELECTION_CERTIFICATION`;
- R08A primary cause: `missing registration`;
- R08A blocker:
  `FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER_CERTIFIED_SELECTION_REGISTRATION_ABSENT`.

The nine previously declared protected paths were present before R08B and were
not modified or normalized by this work.

## Minimality proof

The smallest legitimate repair required no new architecture.

1. The existing `default_resource_registry` data shape can represent the exact
   Worker, capability, role, domain, trust, lifecycle, and authority profile.
2. The unchanged `select_unified_resource` eligibility rules select that exact
   entry when authorization is present and fail closed otherwise.
3. The existing selection-certification generator already supports immutable
   incremental roots through `_next_cert_root`; `CERT-000001` therefore did not
   need rewriting.
4. The existing selection Replay artifact family and reconstructor already
   preserve the selected identity, registry hash, role, capability, domain, and
   stop flags.
5. Three existing production files were the exact maximum necessary surface:
   registry and generic Replay validation, certification generation and
   validation, and the pre-existing checked-certification consumer.

No production file or artifact family was added. The implementation introduces
one validation symbol in the existing certification owner, not a new subsystem.

## Exact reuse

The registry entry cites the accepted bounded Worker lineage:

- `G8_12_EXISTING_FILE_MUTATION_IMPLEMENTATION_V1`;
- `G8_12A_EXISTING_FILE_MUTATION_ARCHITECTURE_REVIEW_V1`;
- `G8_99_GENERATION_8_RUNTIME_ADOPTION_CERTIFICATION_REVIEW_V1`;
- `G31_24G_R04_R04_R02_EXISTING_REPLACE_OWNER_ATOMICITY_CONSUMPTION_AND_RECOVERY_HARDENING`.

The generated certification report retains R05, R06, and R07 as upstream
lineage references only. None was reconstructed, rewritten, consumed, or
continued during certification.

The existing contracts reused unchanged are:

- `WORKER_ROLE`;
- `WORKER_AUTHORIZED_TASK_ONLY`;
- `RESOURCE_SELECTION_ARTIFACT_V1` and its status and diagnostics families;
- `select_unified_resource`;
- `reconstruct_unified_resource_selection_replay`;
- canonical serialization and `replay_hash`;
- immutable JSON writes;
- `WORKER_SELECTION_CERTIFICATION_REPORT_V1` and its existing generator layout.

## Registry admission

Exactly one canonical resource entry was added. It has exactly one role
binding, one capability, and one domain. It has no alias, generic capability
projection, Provider role, assignment profile, dispatch authority, invocation
authority, or mutation authority.

The registry authority profile remains unchanged:

```text
can_execute_authorized_task = true
can_propose = false
can_dispatch = false
can_authorize = false
can_govern = false
can_mutate_replay = false
can_mutate_governance = false
can_invoke_provider = false
can_invoke_worker = false
```

Registry hash continuity is:

```text
old registry hash = sha256:74ad406cfde8b5c8d19005d29d8d513a5eea88bbe45e3379d8972a2f8892de5a
new registry hash = sha256:74357af9a2ba666d73241381e5a4c24ac7687e41b67efe6746cb86d3ac6e7d64
```

The registry validator now rejects a supplied stale or substituted
`registry_hash`. This is required because the selector accepts caller-supplied
registries for deterministic probes. It does not change eligibility policy.

## Incremental certification

The existing generator was incrementally extended. The accepted
`CERT-000001` remains byte-for-byte present and reconstructs all seven original
scenarios. The generator created `CERT-000002` with the original seven
scenarios plus exactly one new scenario:

```text
scenario_id = WSG-008
coverage = filesystem_replace_worker_selection
required_capability = REPLACE_EXISTING_TEXT_FILE
selected_worker = FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER
expected_status = SELECTED
```

WSG-008 invokes the existing unified selector against the canonical registry,
writes its existing two-step selection Replay below the scenario root, and
reconstructs that Replay. It does not manufacture a selection artifact from a
request field.

The checked certification hashes are:

```text
CERT-000001 report artifact hash = sha256:c38b21efede2314fb7cdb8f6bb8a74ee5f4a1d1c3adf46992471684734a94155
CERT-000002 report artifact hash = sha256:03cbf0fc4e8ae562ffe25235aff1c7a6fbd559c23fc8c4fad48e15a1c56b1b45
CERT-000002 coverage hash = sha256:00f1c088d18e8518b36be183633ab4f247067a2cff421fe96f780703eebb6c20
CERT-000002 evidence hash = sha256:8992246ca515a08f02ee73c042e5e57bbd707f79cf0dcd8aff212625a10a19d0
CERT-000002 Replay package hash = sha256:8304f3b76113b1712b04430ada4e3d406eecf6fe5b40f8c8546d9cf44f4d9c6a
WSG-008 selection hash = sha256:09775d0955ca575a1dc9152a5407945b67206e6e8a4bb6f09c26a17e71342882
WSG-008 selection Replay hash = sha256:8d76c0b0791e2a8d0fc2b908b0123d4afc6600719ee237522f8053a04661ae61
```

The report verdict is `WORKER_SELECTION_CERTIFIED`. Its registry hash equals
the new canonical registry hash, and its exact certified-resource hash is
validated against the canonical resource body.

`runtime/` is ignored by repository policy. `CERT-000002` therefore remains a
local generated evidence directory unless explicitly force-added by the
operator. It contains 70 JSON files and 70 canonical one-line JSON records.
No accepted `CERT-000001` file was rewritten.

## Replay and fail-closed evidence

The exact positive selection reconstructs two ordered immutable wrappers. The
generic reconstructor now requires the exact two-file set as well as the
existing ordering, wrapper-hash, artifact-hash, returned-reference, and
selection-hash checks. Removal, duplication, reordering, or substitution fails
closed.

Focused evidence proves rejection before selection for:

- changed Worker identity or version;
- changed capability or role;
- missing Worker authorization;
- wrong domain, lifecycle, trust, or authority profile;
- changed certification lineage;
- duplicate registration;
- stale registry hash;
- substituted registry not covered by certification;
- false, stale, hash-invalid, or lineage-substituted certification;
- `CODEX`, `IMPLEMENTATION_ASSISTANCE`, and broader preferred-resource
  substitution;
- an ambiguous competing exact candidate;
- removed, duplicated, reordered, or substituted selection Replay.

The public `validate_worker_selection_certification_v1` function centralizes
the report, registry-hash, exact-resource, and exact-resource-hash validation.
The G31-11B consumer now loads `CERT-000002` through that owner. This eliminated
duplicated checks and kept its production module below the accepted 480-line
minimality ceiling at 478 lines.

## Authority and stop boundary

The exact selected artifact and its reconstruction retain:

```text
worker_assigned = false
worker_dispatched = false
provider_invoked = false
worker_invoked = false
execution_requested = false
command_executed = false
repository_mutated = false
```

The selection artifact does not itself contain assignment or command fields;
the certification evidence and test assertions preserve those later states as
unreached. No target path was opened and no replacement bytes were written.

## Production symbols and responsibilities

New production symbol:

- `validate_worker_selection_certification_v1`: validates an existing checked
  report against the exact canonical registry and replacement-resource body.

Modified production symbols:

- `DEFAULT_RESOURCES`: adds the one exact Worker entry;
- `_validate_registry`: rejects a stale supplied registry hash;
- `reconstruct_unified_resource_selection_replay`: rejects extra or missing
  Replay files;
- `SCENARIOS`: adds WSG-008;
- `WORKER_DECLARATIONS`: adds the exact existing deterministic Worker
  declaration;
- `run_worker_selection_certification_v1`: validates registry identity, runs
  the real selector for WSG-008, and binds registry/resource hashes;
- `reconstruct_worker_selection_replay`: remains backward compatible with the
  accepted seven-scenario `CERT-000001` and reconstructs eight-scenario
  `CERT-000002`;
- `_assertions`: requires exact replacement-Worker selection coverage;
- `WORKER_SELECTION_CERTIFICATION_PATH`: advances the existing consumer from
  `CERT-000001` to `CERT-000002`;
- `select_authorized_grounded_worker`: validates the checked report against the
  exact current registry before its unchanged G31-11B selection;
- `reconstruct_authorized_grounded_worker_selection`: proves the same
  certification continuity during reconstruction.

No helper logic was copied. Exact identity strings occur in registry data,
certification assertions, and tests because those independent evidence layers
must compare the same immutable values; they are not duplicated algorithms.

## Change size

Before this report, the scoped delta was:

| Category | Files | Insertions | Deletions |
|---|---:|---:|---:|
| Production | 3 modified | 192 | 12 |
| Tests | 2 modified, 1 new | 279 | 11 |
| Generated certification evidence | 70 new ignored JSON files | 70 | 0 |

Production-file justification:

- `unified_resource_selection_runtime.py`: the only canonical registry and
  selection-Replay owner;
- `worker_selection_certification_v1.py`: the only existing certification
  generator and now the centralized report validator;
- `confirmed_grounded_execution_authorization_binding.py`: the existing
  checked-certification consumer contained a hard-coded `CERT-000001` path and
  required registry/report continuity.

No production file was added. The focused R08B test file contains 267 lines.
The generated evidence contains 70 canonical JSON lines. This 569-line report
is the only new governance document.

## Validation

Validation ran in the required order, with the full repository suite invoked
exactly once after the initial focused suites passed.

| Validation group | Passed | Skipped | Failed |
|---|---:|---:|---:|
| Focused R08B | 26 | 0 | 0 |
| Existing Worker-selection certification | 5 | 0 | 0 |
| Unified selector and registry | 21 | 0 | 0 |
| G31-11B selection regressions, downstream AiCLI continuation excluded | 16 | 1 | 0 |
| Architecture and import-boundary tests | 18 | 0 | 0 |
| Governance tests | 5 | 0 | 0 |
| Post-full targeted minimality and Replay-reproducibility closure | 5 | 0 | 0 |
| Final combined R08B, certification, selector, and registry regression | 52 | 0 | 0 |

Targeted `py_compile` passed for all three production files and all three
touched test files. Parent `git diff --check` and all three nested repository
`git diff --check` checks passed.

The complete repository suite was run exactly once and returned:

```text
6714 passed, 4 skipped, 4 failed in 4414.51s (1:13:34)
```

The four failures were fully identified:

1. the G31-10 480-line minimality guard observed the first duplicated inline
   certification checks at 501 lines;
2. three replay-reproducibility tests observed that the current reconstructor
   initially required eight scenarios when reading immutable seven-scenario
   `CERT-000001`.

The implementation was then reduced to one central validation function, the
G31-10 module returned to 478 lines, and reconstruction gained explicit
seven/eight-scenario compatibility. All four previously failing tests passed in
the five-test targeted closure command. The final 52-test focused group and
the final 16-test G31-11B group also passed. The full suite was not invoked a
second time because this generation explicitly permits exactly one complete
repository-suite invocation. This limitation is recorded rather than hidden.

No dedicated R08B live PTY, mutation workflow, Worker execution, or Provider
execution was run; the required complete repository suite remained an ordinary
test invocation over its existing temporary fixtures.

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

The two known hook findings remain visible and unchanged. R08B neither repairs
nor reinterprets them.

## Protected and nested state

All protected SHA-256 values equal the pre-R08B baseline:

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

## Git state and commit commands

The six modified runtime-evidence paths and three marker paths predate R08B and
are excluded from its scoped implementation delta. `CERT-000002` is hidden by
the repository's `/runtime/` ignore rule and must be force-added if the checked
evidence is committed.

Exact final `git status --short`:

```text
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/diagnostic_evidence.json
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/governed_return.json
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/lineage.json
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/provider_stderr.txt
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/provider_stdout.txt
 M .runtime/aigol/ledger/governed_returns.jsonl
 M aigol/runtime/confirmed_grounded_execution_authorization_binding.py
 M aigol/runtime/unified_resource_selection_runtime.py
 M aigol/runtime/worker_selection_certification_v1.py
 M tests/test_g31_11b_authorized_existing_worker_selection_binding.py
 M tests/test_worker_selection_certification_v1.py
?? WORKER_INVOCATION_ARTIFACT_V1
?? WORKER_INVOKED
?? docs/governance/G31_24G_R04_R04_R08B_BOUNDED_FILESYSTEM_REPLACE_WORKER_SELECTION_CERTIFICATION.md
?? invocation
?? tests/test_g31_24g_r04_r04_r08b_filesystem_replace_worker_selection_certification.py
```

No command below was executed:

```bash
git add aigol/runtime/unified_resource_selection_runtime.py
git add aigol/runtime/worker_selection_certification_v1.py
git add aigol/runtime/confirmed_grounded_execution_authorization_binding.py
git add tests/test_worker_selection_certification_v1.py
git add tests/test_g31_11b_authorized_existing_worker_selection_binding.py
git add tests/test_g31_24g_r04_r04_r08b_filesystem_replace_worker_selection_certification.py
git add docs/governance/G31_24G_R04_R04_R08B_BOUNDED_FILESYSTEM_REPLACE_WORKER_SELECTION_CERTIFICATION.md
git add -f runtime/worker_selection_certification_v1/CERT-000002
git commit -m "feat(runtime): certify filesystem replacement Worker selection"
```

Nothing was staged and no commit was created.

## Progress and verdict

Evidence-scoped planning estimates are:

- Generation 31 no-copy/paste governed-development lifecycle: **99.975%**;
- whole project toward the current bounded Product 1 and governed-development
  objective: **98.12%**.

These are not production-readiness or regulatory-compliance claims. R08B
certifies selection eligibility only. Live R07-to-selection binding,
replacement-Worker assignment compatibility, later lifecycle progression,
physical execution, validation, certification, and Product 1 release remain
separately governed.

Deterministic verdict:

`G31_FILESYSTEM_REPLACE_WORKER_SELECTION_CERTIFIED`

Exactly one next state:

`G31_24G_R04_R04_R08C_CONSUMED_REPLACEMENT_REQUEST_TO_CERTIFIED_WORKER_SELECTION_BINDING_REQUIRED`

## Complete bounded G31-24G-R04-R04-R08C prompt

```text
# Generation 31-24G-R04-R04-R08C
# Consumed Replacement Request to Certified Filesystem Replace Worker Selection Binding

Treat Generation 30, accepted G31 common-entry and R05-R07 results, the R08
blocked report, R08A audit, and R08B certification as immutable certified
baselines.

R08B verdict:

G31_FILESYSTEM_REPLACE_WORKER_SELECTION_CERTIFIED

Required state:

G31_24G_R04_R04_R08C_CONSUMED_REPLACEMENT_REQUEST_TO_CERTIFIED_WORKER_SELECTION_BINDING_REQUIRED

## Objective

Bind exactly one reconstructed R07 single-use consumption claim and its exact
authenticated replacement request to the now-certified existing unified
Worker-selection owner.

Produce either one immutable RESOURCE_SELECTION_ARTIFACT_V1 bound to the exact
R07 request, authorization, consumption, canonical registry, and R08B
certification, or a deterministic fail-closed state.

Stop before Worker assignment, dispatch, invocation, Provider invocation,
command execution, target opening, repository mutation, restoration, rollback,
or recovery.

## Required reuse

Reuse without redesign:

- reconstruct_authenticated_replace_replay_v2;
- the exact R07 request and single-use consumption identity;
- default_resource_registry and its R08B exact Worker entry;
- validate_worker_selection_certification_v1 and CERT-000002;
- select_unified_resource and reconstruct_unified_resource_selection_replay;
- G31 common-entry aggregation, Human Conversation Experience, and Canonical
  Presentation.

Do not create a selector, registry, request, authorization, consumption,
capability, policy, Replay, Worker, Provider, command, mutation, alias, or
compatibility subsystem. Do not modify R05-R07 or R08B evidence.

## Required lifecycle

Demonstrate through run_human_interface_runtime_entry:

exact reconstructed APPROVED V3 decision
  -> exact reconstructed mutation authorization
  -> exact reconstructed authenticated replacement request
  -> exact reconstructed single-use consumption claim
  -> exact R08B checked certification and canonical registry
  -> existing unified selector with preferred exact Worker identity
  -> immutable selection evidence and Replay
  -> canonical lifecycle aggregation and presentation
  -> stop before assignment

Project exactly:

workflow_type = NATIVE_DEVELOPMENT
required_capability = REPLACE_EXISTING_TEXT_FILE
requested_role_type = WORKER_ROLE
domain_id = NATIVE_DEVELOPMENT
worker_authorization_required = true
preferred_resource_id = FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER

The selection context identity and hash must bind the exact R07 consumption,
request, and authorization lineage. R05 authorization, R06 request recording,
R07 consumption, and R08B certification must be reconstructed or validated,
not repeated.

## Fail-closed requirements

Reject before selection when request, consumption, authorization,
certification, registry, Worker identity or version, operation, role, domain,
authority, lifecycle, trust, target, expected state, replacement content,
mode, destination, context hash, or Replay differs. Reject missing, stale,
duplicated, reordered, substituted, ambiguous, or later-stage lifecycle
evidence. Terminal, UI, or adapter fields must not influence canonical
selection identity. Invalid evidence must select nothing and must not alter the
R05-R07 chain.

## Common-entry and authority boundaries

Keep run_human_interface_runtime_entry as the public application transition.
AiCLI may transport and render only. Prove the same result through one
non-AiCLI in-memory adapter and prove display fields do not affect identity.

Retain worker_assigned, worker_dispatched, provider_invoked, worker_invoked,
execution_requested, command_executed, and repository_mutated as false. Do not
call assignment, dispatch, invocation, Provider, command, target-open,
mutation, restoration, rollback, or recovery owners. Do not run a live PTY.

## Minimal-change rule

Prefer one existing-function binding. Modify at most three production files.
Add no artifact family or Replay subsystem. If R07 evidence cannot reach the
existing selector through an exact bounded projection, stop and report the
first deterministic blocker rather than adding a parallel owner.

## Tests and validation

Prove positive exact binding; exact request/consumption/certification/registry
continuity; no repeat consumption; invalid, stale, broadened, ambiguous, or
tampered evidence fails before selection; selection Replay reconstructs and
rejects removal, duplication, reordering, or substitution; adapter and AiCLI
neutrality; all downstream spies remain zero; and R01, R05-R07, R08B, unified
selector, and existing selection regressions remain compatible.

Use pytest temporary session roots. Run focused suites first, then Governance,
py_compile, parent and nested git diff --check, protected SHA-256 comparison,
and the complete repository suite exactly once only after focused suites pass.
Do not run a live PTY or mutation workflow.

## Documentation

Add exactly one report:

docs/governance/G31_24G_R04_R04_R08C_CONSUMED_REPLACEMENT_REQUEST_TO_CERTIFIED_WORKER_SELECTION_BINDING.md

Document exact reuse, projection, identity and hash continuity, Replay,
fail-closed evidence, common-entry and adapter neutrality, zero downstream
calls, change size, validation, Governance, protected state, exact Git status,
progress, one verdict, and exactly one next state with a complete bounded
prompt.

Do not stage or commit. Preserve all protected paths byte-for-byte.

## Required verdict

Return exactly one:

G31_CONSUMED_REPLACEMENT_REQUEST_TO_CERTIFIED_WORKER_SELECTION_BINDING_OPERATIONAL
G31_CONSUMED_REPLACEMENT_REQUEST_TO_CERTIFIED_WORKER_SELECTION_BINDING_BLOCKED

Do not report partial success.
```
