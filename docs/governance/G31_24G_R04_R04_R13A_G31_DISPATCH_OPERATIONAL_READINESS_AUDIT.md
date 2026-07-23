# Generation 31-24G-R04-R04-R13A G31 Dispatch Operational Readiness Audit

Status: completed static constitutional audit; no Dispatch or later lifecycle
owner was called.

Date: 2026-07-23

Deterministic verdict:

`G31_DISPATCH_OPERATIONAL_READY`

First deterministic constitutional blocker:

`NONE_BEFORE_EXISTING_CERTIFIED_WORKER_DISPATCH`

## Constitutional scope

This audit treats G0-G30 Platform Core and accepted G31 R05, R06, R07, R08,
R08A, R08B, R08C, R09A, R09B, R10A, R10B, R11A, R11B, R12A, and R12B as
immutable certified baselines.

It asks only whether the existing certified
`dispatch_assigned_worker` runtime can consume:

- the exact R12B `WORKER_ASSIGNMENT_ARTIFACT_V1`; and
- its exact reconstructed four-step Assignment Replay;

without a new Dispatch owner, entrypoint, authority model, artifact family,
Replay subsystem, Worker-specific branch, adapter call, Invocation, Worker
execution, Provider execution, command execution, or repository mutation path.

This audit changes no production file, test, runtime, registry, certification
evidence, Replay evidence, adapter, or protected path. It does not call
Assignment or Dispatch. The only repository addition is this report.

## Accepted baseline

The audit began from:

- branch: `master`;
- HEAD: `e502ddf0004ed5801edc0e5e8ade8a6cb66be954`;
- HEAD subject:
  `feat(runtime): bind common entry to certified assignment transition`;
- R12A verdict: `G31_WORKER_ASSIGNMENT_EXECUTION_READY`;
- R12B verdict: `G31_COMMON_ENTRY_TO_ASSIGNMENT_OPERATIONAL`;
- certified Assignment runtime:
  `AIGOL_WORKER_ASSIGNMENT_RUNTIME_V1`;
- certified Dispatch runtime:
  `AIGOL_WORKER_DISPATCH_RUNTIME_V1`;
- checked Dispatch certification:
  `governance/AIGOL_WORKER_DISPATCH_RUNTIME_CERTIFICATION.json`;
- Dispatch certification status: `CERTIFIED`.

The six modified runtime-evidence/ledger paths, three empty marker paths, and
three unstaged R12B baseline regression adjustments predated R13A. This audit
does not alter or reinterpret them.

## Plain-language determination

The existing certified Dispatch Runtime is operationally ready for the exact
R12B Assignment result.

R12B returns the same canonical Assignment artifact family and Replay family
that Dispatch already consumes. Static comparison finds no field, hash,
lineage, authority, state, role, packet, or stop-boundary mismatch.

The Dispatch runtime can:

1. reconstruct the exact R12B Assignment Replay;
2. require `WORKER_ASSIGNED`;
3. validate the exact recorded Assignment artifact;
4. compare the provided Assignment identity and hash with Replay;
5. reconstruct the exact R09B invocation-request Replay below Assignment;
6. validate request, authorization, execution-packet, Worker, chain, Replay,
   and authority continuity;
7. create the existing Dispatch evidence, classification, artifact, and result
   families;
8. persist and reconstruct the existing four-step Dispatch Replay; and
9. stop before Invocation, execution, result creation, or mutation.

No constitutional repair or compatibility translation is required.

## Existing certified Dispatch contract

The public owner is:

```text
aigol.runtime.worker_dispatch_runtime.dispatch_assigned_worker
```

It accepts:

- one deterministic Dispatch identity;
- one `WORKER_ASSIGNMENT_ARTIFACT_V1`;
- the exact Assignment Replay reference;
- one dispatching actor and timestamp; and
- one unused Dispatch Replay destination.

It returns:

- `WORKER_DISPATCH_EVIDENCE_ARTIFACT_V1`;
- `WORKER_DISPATCH_CLASSIFICATION_ARTIFACT_V1`;
- `WORKER_DISPATCH_ARTIFACT_V1`;
- `WORKER_DISPATCH_RESULT_ARTIFACT_V1`;
- one four-step Replay reference; and
- a canonical capture that stops before Worker Invocation.

The checked certification explicitly covers Assignment Replay
reconstruction, Assignment identity/hash continuity, invocation-request
lineage, authorization lineage, execution-packet lineage, Worker identity,
chain continuity, Replay continuity, authority continuity, dispatch
eligibility, role compatibility, and fail-closed behavior.

Its certified non-goals include no Worker Invocation, execution, result
creation, code generation, planned output creation, approval creation,
Governance mutation, or mutation of existing Replay.

## Exact R12B Assignment compatibility

### Artifact family and state

R12B returns the existing `WORKER_ASSIGNMENT_ARTIFACT_V1` produced by
`assign_worker_from_invocation_request`.

Its exact state satisfies every Dispatch precondition:

```text
artifact_type = WORKER_ASSIGNMENT_ARTIFACT_V1
assignment_status = WORKER_ASSIGNED
worker_state_after = ASSIGNED
worker_assigned = true
worker_dispatched = false
worker_invoked = false
execution_started = false
result_created = false
approval_created = false
governance_mutated = false
replay_mutated = false
replay_visible = true
```

### Required identities and hashes

The artifact contains every non-empty string required by Dispatch:

- Worker Assignment identity;
- exact Worker identity and Worker artifact hash;
- Worker family and role;
- invocation-request identity and artifact hash;
- authorization identity and hash;
- execution-packet identity and hash;
- canonical chain identity;
- assigning actor and timestamp.

The exact R12B Worker remains:

```text
worker_id = FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER
worker_family = FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER
worker_role = WORKER_ROLE
```

Dispatch has no branch for this Worker identity, CODEX, Provider identity,
replacement capability, or filesystem behavior. It treats Worker identity as
immutable evidence and applies the same generic Assignment checks.

### Replay family

R12B returns the existing ordered Assignment Replay:

```text
000_assignment_evidence_recorded.json
001_assignment_classification_recorded.json
002_assignment_artifact_recorded.json
003_assignment_result_recorded.json
```

Dispatch `_load_assignment_lineage`:

1. calls `reconstruct_worker_assignment_runtime_replay`;
2. requires `WORKER_ASSIGNED`;
3. verifies all four wrapper and artifact hashes;
4. validates the recorded Assignment artifact;
5. compares the provided Assignment identity and hash with the recorded
   artifact;
6. requires the Assignment result to cite the exact Assignment hash;
7. reconstructs the nested invocation-request Replay; and
8. checks Assignment, request, authorization, packet, chain, Replay, and
   authority continuity.

R12B already reconstructs the same Assignment Replay before returning from
Common Entry. Dispatch repeats validation at its own authority boundary; it
does not rewrite the parent Replay.

## Deterministic compatibility matrix

| Transition | Status | Existing owner | Determination |
|---|---|---|---|
| R12B capture -> Assignment artifact | `COMPATIBLE` | Common Entry aggregation | exact existing artifact and Replay reference are exposed |
| Artifact type -> Dispatch validator | `COMPATIBLE` | `_validate_assignment_artifact` | canonical Assignment family matches |
| Assignment status/state -> eligibility | `COMPATIBLE` | `_validate_assignment_artifact` | `WORKER_ASSIGNED` and `ASSIGNED` match |
| Assignment flags -> authority continuity | `COMPATIBLE` | `_assignment_authority_continuity` | assigned true; every later authority flag false |
| Provided artifact -> recorded artifact | `COMPATIBLE` | `_load_assignment_lineage` | exact identity and artifact hash are preserved |
| Assignment Replay -> reconstruction | `COMPATIBLE` | Assignment reconstructor | existing four-step Replay reconstructs |
| Assignment -> request Replay | `COMPATIBLE` | invocation-request reconstructor | exact R09B identity/status reconstruct |
| Request/authorization/packet/chain | `COMPATIBLE` | `_load_assignment_lineage` | all hashes and references remain continuous |
| Worker identity/family/role | `COMPATIBLE` | evidence and classification owners | exact values project without aliasing |
| Assignment -> Dispatch artifacts | `COMPATIBLE` | existing evidence/classification/artifact/result owners | all required values are representable |
| Dispatch -> Dispatch Replay | `COMPATIBLE` | `_persist_step` and Dispatch reconstructor | existing ordered four-step Replay applies |
| Dispatch -> Invocation boundary | `STOP_SUPPORTED` | post-Dispatch flags | dispatched true; invoked/executed/result-created false |

No row requires a compatibility wrapper, registry lookup, alias, new
authority grant, or second Dispatch owner.

## Replay continuity

The immutable parent chain remains:

```text
Canonical Decision
  -> Mutation Authorization
  -> Authenticated Replacement Request
  -> Single-use Consumption
  -> Certified Existing Worker Selection
  -> Certified Invocation Request
  -> projected WORKER_ARTIFACT_V1
  -> certified Worker Assignment
```

The existing Dispatch evidence records:

- canonical chain identity;
- Assignment identity, artifact hash, and Replay reference;
- invocation-request identity and hash;
- authorization identity and hash;
- execution-packet identity and hash;
- target domain;
- Worker identity, hash, family, and role; and
- exact lineage-continuity checks.

The Dispatch artifact then binds the evidence and classification hashes,
Assignment identity/hash, request identity/hash, authorization, packet,
domain, Worker identity/hash, outputs, prohibitions, validations, actor,
timestamp, and chain.

`reconstruct_worker_dispatch_replay` verifies:

- exact wrapper ordering and hashes;
- all four Dispatch artifact hashes;
- evidence-to-classification continuity;
- classification-to-Dispatch continuity;
- Dispatch-to-result continuity;
- chain agreement;
- Assignment identity/hash agreement;
- the complete nested Assignment Replay; and
- the post-Dispatch authority boundary.

No R05-R12B artifact or Replay event must be repeated, rewritten, consumed
again, or reauthorized.

## Authority and stop boundary

The certified successful Dispatch contract changes only:

```text
worker_dispatched: false -> true
dispatch_requested: false -> true
```

It preserves:

```text
approval_created = false
worker_assigned = true
worker_invoked = false
execution_started = false
result_created = false
governance_mutated = false
replay_mutated = false
```

The Dispatch source contains no Worker invocation call, Worker execution call,
result-creation call, human-approval creation, Governance mutation,
subprocess, or network-request surface.

The canonical Dispatch summary explicitly states:

```text
No Worker has been invoked, executed, or produced results.
```

Worker Invocation remains a distinct downstream transition and is outside
R13A.

## Common Entry neutrality

`run_human_interface_runtime_entry` remains the public application owner.

The R12B mutation continuation currently stops after verified Assignment with
`worker_dispatched = false`. That stop is correct for the accepted baseline
and was not changed by this audit.

The same Common Entry service already imports `worker_dispatch_runtime` and
uses `dispatch_assigned_worker` in its existing certified G31 lifecycle path.
A later operational transition can reuse that established call pattern inside
the R12B mutation continuation. It does not require an adapter-owned call,
parallel entrypoint, new Dispatch owner, or Worker-specific dispatch logic.

Because Common Entry already holds the exact Assignment capture and Replay
reference, the later binding should pass those values directly. It should not
search the filesystem with `find_latest_domain_worker_assignment` or
reconstruct identity from display fields.

AiCLI remains transport and presentation only.

## Minimal operational transition

No constitutional repair is required.

The smallest later operational generation should:

1. remain inside the existing Common Entry mutation continuation;
2. retain the exact verified R12B Assignment capture and reconstruction;
3. call `dispatch_assigned_worker` once with:
   - `<worker_assignment_id>:DISPATCH`;
   - the exact `worker_assignment_artifact`;
   - the exact Assignment Replay reference;
   - the existing bounded Governance actor and timestamp; and
   - one unused deterministic session-local Dispatch Replay destination;
4. require `WORKER_DISPATCHED`;
5. call `reconstruct_worker_dispatch_replay` once;
6. verify Dispatch identity, Assignment identity/hash, Worker identity,
   request, chain, Replay, and stop flags;
7. aggregate and render the existing Dispatch capture; and
8. return immediately before Worker Invocation.

That future generation must prove zero calls to Invocation, Worker, Provider,
governed execution, command, target-open, mutation, restoration, rollback, and
recovery owners.

It must not modify R05-R12B evidence, the Assignment runtime, Dispatch runtime,
artifact families, registry, selector, Worker implementation, or AiCLI.

## Rejected shortcuts

The audit rejects:

- calling Dispatch from AiCLI;
- using `request.worker_id` or `selected_resource_id` as a Dispatch artifact;
- mapping the Worker to CODEX, CLAUDE_CODE, a Provider, or an alias;
- bypassing Assignment Replay reconstruction;
- using filesystem discovery when the exact Assignment capture is available;
- adding replacement-Worker-specific Dispatch policy;
- creating a second Dispatch owner or Replay family;
- modifying the certified Dispatch runtime without an observed blocker;
- combining Dispatch with Worker Invocation or execution;
- rewriting or repeating upstream authorization or consumption; and
- treating readiness as evidence that Dispatch already occurred.

## Static validation

Validation intentionally excluded every test or command that would call the
Assignment or Dispatch owner or write lifecycle Replay.

Exact results:

| Validation | Passed | Skipped | Failed |
|---|---:|---:|---:|
| Dispatch authority and source-boundary checks | 1 | 0 | 0 |
| R10B-R12B source-only compatibility and neutrality | 3 | 0 | 0 |
| Constitutional layer and authority contracts | 10 | 0 | 0 |
| Governance tests | 5 | 0 | 0 |

Additional read-only checks:

- in-memory source compilation passed for the Dispatch, Assignment, and Common
  Entry owners;
- parent `git diff --check`: passed;
- all three nested repository `git diff --check` checks: passed;
- complete repository suite: not run for this static audit;
- live Assignment or Dispatch: not called;
- runtime Replay or certification generation: not run;
- Invocation, Worker, Provider, command, target-open, and mutation workflows:
  not run.

The accepted R12B baseline records its exactly-once complete-suite result:

```text
6791 passed, 3 skipped, 0 failed in 4180.08s (1:09:40)
```

R13A does not repeat that suite.

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

The two known hook findings remain visible and unchanged: the root expected
and installed hooks are missing, and the system pre-commit hook lacks
`promotion_gate_v02` and `check_layer_freeze`. R13A neither repairs nor
reinterprets them.

## Protected and nested state

The protected SHA-256 values remain:

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

The only scoped R13A change is this governance report. No production, test,
runtime, registry, certification, Replay, adapter, or protected path was
changed.

The six protected runtime-evidence/ledger changes, three empty markers, and
three R12B baseline regression adjustments predate this audit. Nothing was
staged and no commit was created.

## Deterministic verdict

`G31_DISPATCH_OPERATIONAL_READY`

The existing certified Dispatch Runtime can consume the exact R12B Assignment
artifact and Replay, preserve Worker, request, authorization, packet, chain,
authority, hash, and Replay continuity, construct the existing bounded
Dispatch lifecycle, and stop before Invocation without introducing a new
execution path.

R13A certifies readiness only. No Dispatch occurred.
