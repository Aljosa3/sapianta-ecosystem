# Generation 31-24G-R04-R04-R11A G31 Worker Assignment Operational Readiness Audit

Status: completed static constitutional audit; no Assignment or later
lifecycle owner was called.

Date: 2026-07-23

Deterministic verdict:

`G31_WORKER_ASSIGNMENT_OPERATIONAL_BLOCKED`

First deterministic constitutional blocker:

`R09B_CERTIFIED_SELECTION_LINEAGE_NOT_ACCEPTED_BY_DEFAULT_WORKER_ARTIFACT_PROJECTION`

## Constitutional scope

This audit treats G0-G30 Platform Core and accepted G31 R05, R06, R07, R08,
R08A, R08B, R08C, R09A, R09B, R10A, and R10B as immutable certified
baselines.

It asks only whether the existing Worker Assignment Runtime can accept the
certified R09B `WORKER_INVOCATION_REQUEST_ARTIFACT_V1`, now covered by the R10B
Assignment request-hash contract, while preserving the exact certified Worker
selection.

The audit made no production, test, registry, certification, Replay, runtime,
adapter, or constitutional change. It did not call Assignment, Dispatch,
Invocation, a Worker, a Provider, a command, a target-opening owner, or a
mutation owner. It generated no runtime or certification evidence. The only
repository addition is this report.

## Accepted baseline

The audit began from:

- branch: `master`;
- HEAD: `d156effc94b27bb057e330fa67db2248b1b15a96`;
- HEAD subject:
  `feat(runtime): bridge lineage into assignment request hash contract`;
- R09B verdict:
  `G31_R08C_TO_EXISTING_INVOCATION_REQUEST_COMPATIBILITY_OPERATIONAL`;
- R10A verdict: `G31_WORKER_ASSIGNMENT_ARCHITECTURE_BLOCKED`;
- R10B verdict:
  `G31_ASSIGNMENT_REQUEST_HASH_COMPATIBILITY_OPERATIONAL`;
- certified request family: `WORKER_INVOCATION_REQUEST_ARTIFACT_V1`;
- certified compatibility lineage:
  `AUTHENTICATED_REPLACEMENT_SELECTION_LINEAGE_V1`.

The certified execution spine reaches exactly:

```text
Human
  -> Common Entry
  -> Canonical Decision
  -> Mutation Authorization
  -> Authenticated Replacement Request
  -> Single-use Consumption
  -> Certified Existing Worker Selection
  -> Certified Invocation Request
  -> Assignment request-integrity validation
  -> stop
```

The six modified runtime-evidence/ledger paths and three empty marker paths
predated R11A and remained outside its scope.

## Deterministic determination

The existing Assignment request validator can now accept the certified R09B
request unchanged.

The existing default Worker-artifact projection cannot preserve the certified
Worker selection carried by that request.

This is the first blocker. The audit stops there.

R10B extended `aigol.runtime.worker_assignment_runtime._request_hash` to cover
the optional `compatibility_lineage`. Consequently:

```text
assignment._request_hash(r09b_request)
  == r09b_request.request_hash
```

and `_validate_request_artifact` accepts the immutable request, its authority
flags, and its R05-R09B lineage-bound hash.

The immediately following input projection is
`default_worker_registry_for_request`. It reads only:

```text
request.g31_lineage.resource_selection_artifact
```

The certified R09B request intentionally has:

```text
g31_lineage = null
compatibility_lineage.lineage_type =
  AUTHENTICATED_REPLACEMENT_SELECTION_LINEAGE_V1
compatibility_lineage.resource_selection_capture.resource_selection_artifact =
  exact R08C RESOURCE_SELECTION_ARTIFACT_V1
```

Because the projection does not inspect the typed compatibility lineage,
`selection` is deterministically `None` and the legacy fallback constructs:

```text
worker_id =
  AIGOL-WORKER-FILESYSTEM-REPLACE-EXISTING-TEXT-FILE-WORKER
worker_version = 1.0.0
declared_capabilities = [WORKER_ROLE]
capability_id = WORKER_ROLE
replay_reference = IN_MEMORY_REGISTERED_WORKER_CANDIDATE
```

The certified selection instead requires:

```text
worker_id = FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER
worker_version = G8_12_EXISTING_FILE_MUTATION_IMPLEMENTATION_V1
resource_category = WORKER
worker_role = WORKER_ROLE
capability_id = REPLACE_EXISTING_TEXT_FILE
authority_profile = WORKER_AUTHORIZED_TASK_ONLY
domain = NATIVE_DEVELOPMENT
replay_reference = exact R08C Selection Replay
```

The two identities are not aliases and are not constitutionally
interchangeable.

## First blocking contract

The first blocking contract is the transition:

```text
certified WORKER_INVOCATION_REQUEST_ARTIFACT_V1
  -> exact WORKER_ARTIFACT_V1 Assignment candidate
```

The request side is compatible. The Worker-evidence side is not.

Repository-wide static inspection found no checked or canonical
`WORKER_ARTIFACT_V1` for
`FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER`. The exact Worker is present in:

- the unified selection registry;
- the R08B selection certification;
- the R08C selected artifact and Replay;
- the physical existing-file replacement Worker owner.

Those artifacts prove selection and implementation identity. None is itself a
`WORKER_ARTIFACT_V1`, and treating one as an Assignment candidate would bypass
the existing Assignment input contract.

The Assignment runtime's generic compatibility checks compare Worker family,
role, execution packet, allowed outputs, forbidden operations, availability,
and false authority flags. They do not restore the selected Worker identity,
version, capability, authority profile, or Selection Replay after the default
projection has discarded them.

The legacy synthetic artifact could therefore be structurally compatible while
representing a different Worker. Continuing to Assignment would create
lifecycle ambiguity rather than preserve the certified execution spine.

## Architectural analysis

### Directly compatible

The following existing contracts are directly reusable:

- R10B Assignment request-hash calculation;
- `_validate_request_artifact`;
- invocation-request Replay identity and hash validation;
- `WORKER_ARTIFACT_V1` structure;
- generic Worker availability and authority validation;
- generic family, role, packet, output, and forbidden-operation checks;
- Assignment evidence, classification, artifact, result, and Replay families;
- the post-Assignment stop before Dispatch;
- Common Entry as the application owner.

No new Assignment runtime, artifact family, registry, Replay subsystem,
authority model, or application entrypoint is required.

### Incompatible at the first edge

`default_worker_registry_for_request` has two existing branches:

1. a `g31_lineage` branch fixed to the older
   `CODEX / HYBRID_PROVIDER_WORKER` selection contract;
2. a legacy fallback that manufactures an in-memory Worker identity from the
   request's target family.

Neither branch consumes
`AUTHENTICATED_REPLACEMENT_SELECTION_LINEAGE_V1`.

Mapping the replacement Worker to CODEX would change Worker identity and
category. Using the fallback would replace its certified identity, version,
capability, authority metadata, and Replay reference. Supplying the R08C
selection artifact directly would bypass `WORKER_ARTIFACT_V1`. Each shortcut
is constitutionally invalid.

### Authority continuity

The R09B request remains non-authoritative:

```text
approval_created = false
worker_assigned = false
worker_dispatched = false
worker_invoked = false
execution_started = false
result_created = false
governance_mutated = false
replay_mutated = false
```

Its compatibility lineage preserves the exact authorization, authenticated
request, consumption, selection, registry, certification, and Replay
identities. R10B makes tampering with that lineage fail request-integrity
validation.

The blocker does not require new authority. It is an evidence-projection
omission between two existing contracts.

### Common Entry neutrality

The mutation continuation remains owned by
`run_human_interface_runtime_entry`. It stops after creating the certified
invocation request with `worker_assigned = false`.

AiCLI calls Common Entry and does not own the R05-R09B lineage transition,
Worker projection, Assignment, or later execution stages. No adapter field is
needed to close the blocker, and no adapter field may influence the Worker
identity.

## Minimal constitutional repair

The smallest bounded repair is lineage-only and Worker-neutral:

1. extend the existing `default_worker_registry_for_request` projection to
   recognize the already-certified
   `AUTHENTICATED_REPLACEMENT_SELECTION_LINEAGE_V1`;
2. reuse the invocation-request owner's existing lineage validation rather
   than copy its authorization, request, consumption, selection,
   certification, or Replay checks;
3. project one existing `WORKER_ARTIFACT_V1` from the exact selected resource,
   preserving:
   - selected Worker identity and version;
   - resource category, role, capability, authority profile, and domain;
   - exact Selection Replay reference;
   - request execution packet;
   - allowed outputs and forbidden operations;
   - all false authority and execution flags;
4. fail closed for missing, ambiguous, stale, substituted, or mismatched typed
   lineage;
5. stop before calling `assign_worker_from_invocation_request`.

The repair must not:

- branch on the filesystem-replacement Worker identity;
- add an alias, synthetic Worker, or broad capability;
- modify the certified unified registry or R08B evidence;
- change the R09B request or R10B hash;
- create a second Worker registry or Assignment owner;
- execute Assignment or any later lifecycle stage.

After that bounded projection is separately proven, a later operational
transition may submit the unchanged request plus the exact projected
`WORKER_ARTIFACT_V1` to the existing Assignment owner through Common Entry.
That later transition is outside R11A.

## Static validation

Validation deliberately excluded every test or command that would call
Assignment, write lifecycle Replay, generate certification evidence, dispatch,
invoke, execute, open a mutation target, or mutate the repository.

Exact results:

| Validation | Passed | Skipped | Failed |
|---|---:|---:|---:|
| R09B/R10B source-only compatibility boundaries | 2 | 0 | 0 |
| R06/R07 AiCLI and Common Entry import boundaries | 2 | 0 | 0 |
| Constitutional layer contracts and layer model | 7 | 0 | 0 |
| Governance conformance tests | 5 | 0 | 0 |

Additional read-only checks:

- in-memory source compilation: passed for the Assignment,
  invocation-request, and Common Entry owners;
- parent `git diff --check`: passed;
- all three nested repository `git diff --check` checks: passed;
- repository search found no exact replacement-Worker
  `WORKER_ARTIFACT_V1`;
- full repository suite: not run for this static audit;
- Assignment runtime: not called;
- runtime Replay or certification generation: not run;
- live PTY, Dispatch, Invocation, Worker, Provider, command, and mutation
  workflows: not run.

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
`promotion_gate_v02` and `check_layer_freeze`. R11A neither repairs nor
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

The only scoped R11A change is this governance report. No production, test,
registry, Replay, certification, or protected path was changed. Nothing was
staged and no commit was created.

The report contains 384 lines after recording this final state.

Exact final `git status --short`:

```text
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/diagnostic_evidence.json
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/governed_return.json
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/lineage.json
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/provider_stderr.txt
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/provider_stdout.txt
 M .runtime/aigol/ledger/governed_returns.jsonl
?? WORKER_INVOCATION_ARTIFACT_V1
?? WORKER_INVOKED
?? docs/governance/G31_24G_R04_R04_R11A_G31_WORKER_ASSIGNMENT_OPERATIONAL_READINESS_AUDIT.md
?? invocation
```

## Deterministic verdict

`G31_WORKER_ASSIGNMENT_OPERATIONAL_BLOCKED`

First deterministic constitutional blocker:

`R09B_CERTIFIED_SELECTION_LINEAGE_NOT_ACCEPTED_BY_DEFAULT_WORKER_ARTIFACT_PROJECTION`

The existing Assignment request validator accepts the certified Assignment
Request unchanged, but the immediately following default Worker-artifact
projection discards its typed certified selection lineage and substitutes a
different synthetic Worker. The existing Worker Assignment Runtime is
therefore not operationally ready for this execution spine.

R11A stops at this first blocker. No Assignment or repair was implemented.
