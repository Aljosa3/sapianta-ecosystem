# Generation 31-24G-R04-R04-R10B R09B Lineage to Assignment Request Hash Contract Compatibility Transition

Status: completed bounded lineage-only compatibility transition; stopped
before Worker Assignment.

Date: 2026-07-23

Deterministic verdict:

`G31_ASSIGNMENT_REQUEST_HASH_COMPATIBILITY_OPERATIONAL`

Resolved blocker:

`R09B_COMPATIBILITY_LINEAGE_OMITTED_FROM_ASSIGNMENT_REQUEST_HASH_CONTRACT`

## Constitutional scope

This generation treats G0-G30 Platform Core and accepted G31 R05, R06, R07,
R08, R08A, R08B, R08C, R09A, R09B, and R10A as immutable certified
baselines.

It changes only the deterministic hash projection used by the existing Worker
Assignment request validator. The exact typed R09B compatibility lineage is
now included in that projection, matching the canonical request hash created
and reconstructed by the existing invocation-request owner.

It does not create an Assignment, change Assignment selection or lifecycle
behavior, project a Worker artifact, modify Common Entry, dispatch or invoke a
Worker, invoke a Provider, execute a command, open a target, mutate a
repository, modify a registry, or generate certification evidence. No live
PTY or mutation workflow was run.

## Accepted baseline

The work began from:

- branch: `master`;
- HEAD: `ea8265c2bbcde04b6cf03363a1d93517a9a3aa32`;
- HEAD subject:
  `docs(governance): audit worker assignment operational readiness`;
- R09B verdict:
  `G31_R08C_TO_EXISTING_INVOCATION_REQUEST_COMPATIBILITY_OPERATIONAL`;
- R10A verdict:
  `G31_WORKER_ASSIGNMENT_ARCHITECTURE_BLOCKED`;
- verified blocker:
  `R09B_COMPATIBILITY_LINEAGE_OMITTED_FROM_ASSIGNMENT_REQUEST_HASH_CONTRACT`;
- request artifact family:
  `WORKER_INVOCATION_REQUEST_ARTIFACT_V1`;
- typed lineage:
  `AUTHENTICATED_REPLACEMENT_SELECTION_LINEAGE_V1`.

The six modified runtime-evidence/ledger paths and three empty marker paths
predated R10B. Their hashes were recorded before implementation and remain
unchanged.

## Exact implementation

Exactly one existing production symbol changed:

- `aigol.runtime.worker_assignment_runtime._request_hash`.

The assignment-side request hash previously covered:

```text
base invocation-request identity and scope
  + optional g31_lineage
```

It now covers:

```text
base invocation-request identity and scope
  + optional g31_lineage
  + optional compatibility_lineage
```

The added projection is the same conditional canonical field projection
already used by
`aigol.runtime.worker_invocation_request_runtime._request_hash`:

```python
**(
    {"compatibility_lineage": request["compatibility_lineage"]}
    if request.get("compatibility_lineage") else {}
),
```

No public function, helper, constant, class, module, artifact family, Replay
family, registry, authority profile, Worker identity, capability, lifecycle
state, or presentation contract was added.

## Why this is lineage-only

The changed function does not:

- validate or select a Worker;
- call `assign_worker_from_invocation_request`;
- call `default_worker_registry_for_request`;
- name `FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER`;
- name `REPLACE_EXISTING_TEXT_FILE`;
- create Assignment evidence;
- write Assignment Replay;
- advance `worker_assigned`;
- authorize dispatch, invocation, command execution, or mutation.

It only makes the assignment-side integrity calculation cover the immutable
lineage already present in the certified request.

The older generic request and accepted G31 `g31_lineage` contracts are
unchanged. Their hash fields remain exactly as before.

## Identity continuity

The accepted R09B request continues to preserve:

| Required identity | Exact source |
|---|---|
| authorization identity/hash | exact R05 actor-bound mutation authorization retained by R06/R07 |
| authenticated request identity/hash | exact R06 request |
| single-use consumption identity | exact R07 authorization hash and consumption reconstruction |
| Worker selection identity/hash | exact R08C `RESOURCE_SELECTION_ARTIFACT_V1` |
| selection context identity/hash | exact R08C consumed-request context |
| checked certification identity/hash | accepted R08B report |
| invocation-request identity/hash | exact R09B request and artifact hashes |

The request owner still computes the canonical request hash. R10B does not
rehash, rewrite, or replace the request. It merely reproduces the same value
when the Assignment request validator performs its existing integrity check.

Focused evidence proves:

```text
assignment._request_hash(request)
  == invocation_request._request_hash(request)
  == request["request_hash"]
```

for the exact reconstructed R09B request.

## Replay continuity

The existing R09B request reconstructor remains the owner of parent Replay
validation. It requires and reconstructs:

```text
R05 mutation authorization
  -> R06 authenticated replacement request
  -> R07 single-use consumption
  -> R08B certified registry and selection evidence
  -> R08C Selection Replay
  -> R09B four-step invocation-request Replay
  -> STOP before Assignment
```

R10B does not add a Replay event. The compatibility lineage remains inside the
existing invocation-request artifact and is covered by:

- the request hash;
- the request artifact hash;
- the immutable invocation-request Replay wrapper hashes;
- reconstruction equality against R05-R08C source evidence.

Removal or substitution of the compatibility lineage changes the
assignment-side canonical hash and fails before Assignment.

## Fail-closed evidence

The focused R10B suite proves that the exact R09B request satisfies the
existing Assignment request hash contract.

It also proves rejection when any of these already-hashed lineage elements is
removed or changed:

- the complete compatibility lineage;
- lineage type;
- authenticated request identity;
- single-use consumption identity;
- selected Worker identity;
- checked selection-certification hash.

Each tampered artifact was rehashed at the outer artifact level while retaining
the original request hash. The Assignment request validator rejected every
case with:

```text
worker assignment failed closed: invocation request hash mismatch
```

No test invoked `assign_worker_from_invocation_request`, created Assignment
Replay, or wrote replacement content.

## Common Entry and authority boundary

Common Entry was not modified. The accepted R09B continuation remains:

```text
Human
  -> Common Entry
  -> Canonical Decision
  -> Mutation Authorization
  -> Authenticated Request
  -> Single-use Consumption
  -> Certified Worker Selection
  -> Certified Invocation Request
  -> STOP before Assignment
```

The successful R10B hash validation retains:

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

AiCLI remains a transport and owns no hash, lineage, request, Assignment,
Worker, Provider, command, or mutation semantics.

## Assignment behavior unchanged

No behavior in these existing Assignment stages changed:

- invocation-request Replay reconstruction;
- duplicate Assignment detection;
- Worker artifact validation;
- Worker compatibility filtering;
- zero-candidate or ambiguity rejection;
- Assignment evidence and classification;
- Assignment artifact and result creation;
- Assignment Replay persistence or reconstruction;
- post-Assignment stop flags;
- Assignment presentation.

The production file changed because it owns the downstream request-integrity
mirror. The change does not execute or broaden Assignment.

R10A's later observation remains outside R10B: the existing default Worker
artifact projection does not yet consume the typed R09B compatibility lineage.
R10B does not bypass, repair, or reinterpret that separate next boundary.

## Change size

Scoped R10B delta before this report:

| Category | Files | Insertions | Deletions |
|---|---:|---:|---:|
| Production | 1 modified | 4 | 0 |
| Tests | 1 new | 93 | 0 |
| Registries | 0 | 0 | 0 |
| Certification evidence | 0 | 0 | 0 |
| Documentation | 1 new | 375 | 0 |

Modified production symbol:

- `_request_hash`: includes the already-certified optional
  `compatibility_lineage` in deterministic request-integrity calculation.

New production symbols: none.

Duplicated helper logic: none added. R10B extends the pre-existing mirrored
field projection with the canonical field already established by R09B; it does
not add another hash function.

## Validation

Validation ran in the required order.

| Validation group | Passed | Skipped/Deselected | Failed |
|---|---:|---:|---:|
| Focused R10B exact hash, tamper, and stop-boundary tests | 8 | 0 | 0 |
| Existing Assignment and invocation-request hash regressions | 25 | 0 | 0 |
| R05-R09B certified-spine regressions | 137 | 0 | 0 |
| Existing G31-12B request-to-Assignment regressions, live downstream test excluded | 13 | 1 deselected | 0 |
| Common Entry, Human Interface, operational-entry, and layer boundaries | 25 | 0 | 0 |
| Governance conformance tests | 5 | 0 | 0 |

Targeted `py_compile` passed for:

- `aigol/runtime/worker_assignment_runtime.py`;
- `tests/test_g31_24g_r04_r04_r10b_assignment_request_hash_compatibility.py`.

Parent `git diff --check` and all three nested repository
`git diff --check` checks passed before the complete suite.

The complete repository suite was invoked exactly once after all focused gates
passed:

```text
6774 passed, 4 skipped, 0 failed in 4439.60s (1:13:59)
```

No repair was required and no second complete-suite run occurred.

No live PTY, Worker, Provider, command, target-open, mutation, restoration,
rollback, recovery, registry mutation, or certification generation workflow
was run.

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

The two known hook findings remain visible and unchanged:

- the root expected and installed pre-commit hooks are missing;
- the system pre-commit hook lacks `promotion_gate_v02` and
  `check_layer_freeze`.

R10B neither repairs nor reinterprets them.

## Protected and nested state

The protected paths retained their pre-R10B SHA-256 values:

| Protected path | SHA-256 |
|---|---|
| `diagnostic_evidence.json` | `a626a69a8020bc730876119c52701a94de9ab6e4772cc64c1f5d017296650203` |
| `governed_return.json` | `e82f47c0c13678725993b21e2af2e0437edccaed324f861a7b58e77d7f8e787d` |
| `lineage.json` | `07b95505521e70f51cdddecc1057fd3a208b198445693c9a8da1e996df5799dd` |
| `provider_stderr.txt` | `d47a06d59aba2814c3fb7460049fc2ccbfc834196c956d6c6558e8be8b079e24` |
| `provider_stdout.txt` | `a73a499e2e9133c03d7babfd5c4dec7967f31e2bfb354ea9dd41df0a15c08cb3` |
| `governed_returns.jsonl` | `dbc7b63f2a17c50c43bbb4fde4f44c1dbae8d25d550fb6b4d4daa14e17126161` |
| each protected marker | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

The nested repositories remained clean at their accepted commits:

- `sapianta-domain-credit`:
  `8615e1e290471a67e4e764c6ab2138340bc7936f`;
- `sapianta_system`:
  `3183bab71f8f30397c0309dd2e6d846d14a11f66`;
- `sapianta-domain-trading`:
  `d3038dc4ba36ffbaee9161172b4c852e8e6acbda`.

Nothing was staged and no commit was created.

## Remaining bounded observation

R10B resolves only the verified hash-contract blocker. The accepted request
now passes assignment-side integrity validation, but the existing default
Worker artifact projection still reads the older `g31_lineage` rather than
the typed R09B compatibility lineage.

That separate boundary must be audited or repaired without:

- inventing a synthetic Worker identity;
- mapping to CODEX or a broad capability;
- modifying the certified selection registry;
- generating certification evidence;
- adding Worker-specific Assignment policy;
- executing Assignment or any later lifecycle stage.

## Deterministic verdict

`G31_ASSIGNMENT_REQUEST_HASH_COMPATIBILITY_OPERATIONAL`

The exact certified R09B invocation request now satisfies the existing
Assignment Request Hash contract, tampered lineage fails closed, all accepted
identity and Replay evidence remains intact, and execution stops before
Assignment.
