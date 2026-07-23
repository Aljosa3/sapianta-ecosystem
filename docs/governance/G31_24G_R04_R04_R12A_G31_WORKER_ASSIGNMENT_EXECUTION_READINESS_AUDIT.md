# Generation 31-24G-R04-R04-R12A G31 Worker Assignment Execution Readiness Audit

Status: completed static constitutional audit; no Assignment or later
lifecycle owner was called.

Date: 2026-07-23

Deterministic verdict:

`G31_WORKER_ASSIGNMENT_EXECUTION_READY`

First deterministic constitutional blocker:

`NONE_BEFORE_EXISTING_CERTIFIED_WORKER_ASSIGNMENT`

## Constitutional scope

This audit treats G0-G30 Platform Core and accepted G31 R05, R06, R07, R08,
R08A, R08B, R08C, R09A, R09B, R10A, R10B, R11A, and R11B as immutable
certified baselines.

It asks only whether the existing certified
`assign_worker_from_invocation_request` runtime can consume:

- the exact certified R09B `WORKER_INVOCATION_REQUEST_ARTIFACT_V1`;
- its exact reconstructed invocation-request Replay; and
- the exact R11B projected `WORKER_ARTIFACT_V1`;

without a new Assignment owner, Worker selection path, registry, authority
model, artifact family, Replay subsystem, adapter path, Dispatch, Invocation,
Worker execution, Provider execution, command execution, or repository
mutation path.

This audit changes no production file, test, registry, certification evidence,
Replay evidence, runtime behavior, or protected path. It does not call
Assignment. The only repository addition is this report.

## Accepted baseline

The audit began from:

- branch: `master`;
- HEAD: `af99cde2b175ce5625c422e882978aa5179ecead`;
- HEAD subject:
  `feat(runtime): preserve certified worker lineage during artifact projection`;
- R10B verdict:
  `G31_ASSIGNMENT_REQUEST_HASH_COMPATIBILITY_OPERATIONAL`;
- R11A verdict: `G31_WORKER_ASSIGNMENT_OPERATIONAL_BLOCKED`;
- R11B verdict:
  `G31_WORKER_ARTIFACT_PROJECTION_COMPATIBILITY_OPERATIONAL`;
- certified Assignment runtime:
  `AIGOL_WORKER_ASSIGNMENT_RUNTIME_V1`;
- checked Assignment certification:
  `governance/AIGOL_WORKER_ASSIGNMENT_RUNTIME_CERTIFICATION.json`;
- Assignment certification status: `CERTIFIED`.

The six modified runtime-evidence/ledger paths and three empty marker paths
predated R12A. Their hashes were captured before the audit.

## Plain-language determination

The existing certified Assignment Runtime is operationally ready for the
certified G31 replacement-Worker lineage.

R10B closed the request-hash incompatibility. R11B closed the Worker-artifact
projection incompatibility. Static comparison now finds no remaining mismatch
between the two certified inputs and the Assignment runtime's public
preconditions.

The runtime can:

1. validate the exact invocation request and its artifact hash;
2. recompute the R10B lineage-inclusive request hash;
3. reconstruct the exact R09B four-step request Replay;
4. reject a repeated Assignment for the same request identity or hash;
5. validate one exact R11B `WORKER_ARTIFACT_V1`;
6. recognize that artifact as the sole compatible Worker;
7. create the existing Assignment evidence, classification, Assignment, and
   result families;
8. persist and reconstruct the existing four-step Assignment Replay; and
9. stop with Dispatch, Invocation, and execution false.

No new execution path is required. A later operational generation needs only
to connect the already-existing Common Entry mutation continuation to these
already-existing public functions.

## Certified Assignment contract

The relevant public owner is:

```text
aigol.runtime.worker_assignment_runtime.assign_worker_from_invocation_request
```

It accepts:

- one Assignment identity;
- one `WORKER_INVOCATION_REQUEST_ARTIFACT_V1`;
- the exact invocation-request Replay reference;
- bounded `WORKER_ARTIFACT_V1` registry evidence;
- one assigning actor and timestamp; and
- one unused Assignment Replay destination.

It returns:

- `WORKER_ASSIGNMENT_EVIDENCE_ARTIFACT_V1`;
- `WORKER_ASSIGNMENT_CLASSIFICATION_ARTIFACT_V1`;
- `WORKER_ASSIGNMENT_ARTIFACT_V1`;
- `WORKER_ASSIGNMENT_RESULT_ARTIFACT_V1`;
- one four-step Replay reference; and
- a canonical capture that stops before Dispatch.

The checked certification explicitly covers request Replay reconstruction,
authorization, packet, candidate, handoff, chain, Replay, authority and hash
continuity, one compatible Worker, family, role, execution packet, allowed
outputs, forbidden operations, Assignment evidence, and the Assignment
artifact.

Its certified non-goals include no Dispatch, Worker invocation, execution,
result creation, approval creation, Governance mutation, or mutation of
existing Replay.

## Exact input compatibility

### Invocation request

The R09B request has the exact family and state required by Assignment:

```text
artifact_type = WORKER_INVOCATION_REQUEST_ARTIFACT_V1
request_status = WORKER_INVOCATION_REQUEST_CREATED
worker_assigned = false
worker_dispatched = false
worker_invoked = false
execution_started = false
```

R10B makes the Assignment-local `_request_hash` cover the complete typed
`compatibility_lineage`. The request hash therefore agrees with the canonical
invocation-request owner without deleting or translating any R05-R09B
identity.

`_validate_invocation_request` also reconstructs the existing request Replay,
requires the same request identity and hash, and validates the immutable
recorded request wrapper.

### Worker artifact

R11B produces exactly one existing `WORKER_ARTIFACT_V1`:

```text
worker_id = FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER
worker_version = G8_12_EXISTING_FILE_MUTATION_IMPLEMENTATION_V1
worker_family = FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER
worker_role = WORKER_ROLE
capability_id = REPLACE_EXISTING_TEXT_FILE
state = AVAILABLE
replay_visible = true
```

The artifact preserves the exact selected category, authority profile, domain,
Selection artifact hash, context identity/hash, registry hash, certification
hash, and Selection Replay reference.

It also projects the exact Assignment compatibility inputs:

| Assignment check | R11B projected value |
|---|---|
| Worker family | exact request `target_worker_family` |
| Worker role | exact request `worker_role` |
| compatible packet | exact request `execution_packet_reference` |
| allowed outputs | exact request `allowed_outputs` |
| forbidden operations | exact request `forbidden_operations` |
| availability | `AVAILABLE` |
| artifact integrity | canonical `artifact_hash` |
| authority | every prohibited authority flag false |

No synthetic Worker identity is used when the certified lineage is present.

### Bounded registry input

`default_worker_registry_for_request` returns a one-element list for the typed
certified lineage.

`_select_compatible_worker` therefore sees:

- one candidate;
- one hash-valid Worker artifact;
- one compatible family;
- one compatible role;
- one compatible packet;
- compatible allowed outputs;
- compatible forbidden operations; and
- no competing eligible candidate.

The zero-candidate and multiple-compatible-candidate fail-closed paths remain
available but are not activated by the exact certified input.

## Deterministic compatibility matrix

| Transition | Status | Existing owner | Determination |
|---|---|---|---|
| R09B request -> Assignment request validator | `COMPATIBLE` | `_validate_request_artifact` | R10B hash covers typed lineage; pre-Assignment flags and required fields match |
| Request -> request Replay reconstruction | `COMPATIBLE` | `_validate_invocation_request` | identity, artifact hash, request hash, and four-step Replay reconstruct |
| Request -> duplicate-Assignment guard | `COMPATIBLE` | `_worker_invocation_request_already_assigned` | exact request identity/hash can be checked without rewriting upstream evidence |
| R11B artifact -> Worker artifact validator | `COMPATIBLE` | `_validate_worker_artifact` | exact type, hash, availability, strings, lists, visibility, and authority flags match |
| Worker artifact -> request compatibility | `COMPATIBLE` | `_validate_worker_compatibility` | family, role, packet, outputs, and forbidden operations match |
| Candidate set -> one Worker | `COMPATIBLE` | `_select_compatible_worker` | exactly one compatible projected candidate |
| Inputs -> Assignment evidence | `COMPATIBLE` | `_evidence_artifact` | request, authorization, packet, Worker and Replay identities are representable |
| Evidence -> classification | `COMPATIBLE` | `_classification_artifact` | all five compatibility booleans are true |
| Classification -> Assignment artifact | `COMPATIBLE` | `_assignment_artifact` | existing artifact preserves Worker, request, authorization, packet and chain |
| Assignment -> Assignment Replay | `COMPATIBLE` | `_persist_step` and reconstructor | existing ordered four-step Replay and nested request Replay checks apply |
| Assignment -> Dispatch boundary | `STOP_SUPPORTED` | post-Assignment flags | assigned true; dispatched, invoked and execution-started false |

No row requires a compatibility wrapper, alias, new registry, or second
Assignment owner.

## Replay continuity

The immutable parent chain remains:

```text
Canonical Decision
  -> Mutation Authorization
  -> Authenticated Replacement Request
  -> Single-use Consumption
  -> Certified Worker Selection
  -> Certified Invocation Request
  -> projected WORKER_ARTIFACT_V1
```

The existing Assignment evidence records:

- canonical chain identity;
- invocation-request identity, artifact hash, and Replay reference;
- authorization identity and hash;
- execution packet identity and hash;
- target domain;
- candidate and handoff references;
- Worker identity and artifact hash; and
- true lineage, Replay, and authority continuity checks.

The Assignment artifact then binds the evidence and classification hashes,
request identity/hash, Worker identity/hash, authorization, execution packet,
domain, outputs, prohibitions, validations, actor, timestamp, and canonical
chain.

`reconstruct_worker_assignment_runtime_replay` verifies:

- wrapper ordering and hashes;
- all four artifact hashes;
- evidence-to-classification continuity;
- classification-to-Assignment continuity;
- Assignment-to-result continuity;
- canonical chain agreement;
- invocation-request hash agreement;
- nested invocation-request Replay reconstruction; and
- the post-Assignment authority boundary.

No R05-R11B artifact or Replay event must be repeated, rewritten, or
reauthorized.

## Authority and stop boundary

The existing successful Assignment contract changes only:

```text
worker_assigned: false -> true
worker_state: AVAILABLE -> ASSIGNED
```

It preserves:

```text
approval_created = false
worker_dispatched = false
worker_invoked = false
execution_started = false
result_created = false
governance_mutated = false
replay_mutated = false
```

The Assignment runtime source contains no Worker dispatch call, Worker
invocation call, result-creation call, human-approval creation, Governance
mutation, subprocess, or network request surface.

The canonical Assignment summary explicitly states that no Worker has been
dispatched, invoked, or executed.

## Common Entry neutrality

`run_human_interface_runtime_entry` remains the public application owner.

The mutation continuation currently stops after the certified R09B invocation
request with `worker_assigned = false`. That stop is correct for the accepted
baseline and was not changed by this audit.

The same Common Entry service already imports the Assignment runtime and uses
both:

```text
default_worker_registry_for_request
assign_worker_from_invocation_request
```

in its existing certified G31 Assignment path. A future mutation-lineage
operational transition can reuse that established call pattern inside the
existing continuation. It does not require an adapter-owned call or a parallel
entrypoint.

AiCLI remains transport and presentation only.

## Minimal operational transition

No constitutional repair is required.

The smallest later operational generation should:

1. remain inside the existing Common Entry mutation continuation;
2. reconstruct or retain the exact R09B invocation-request capture;
3. call `default_worker_registry_for_request` once;
4. call `assign_worker_from_invocation_request` once with the exact request,
   request Replay, projected one-element Worker evidence, deterministic
   Assignment identity, actor, timestamp, and unused temporary/session-local
   Replay destination;
5. reconstruct the returned Assignment Replay;
6. aggregate and render the existing Assignment capture; and
7. stop before Dispatch.

That future generation must prove zero calls to Dispatch, Invocation, Worker,
Provider, command, target-open, mutation, restoration, rollback, and recovery
owners.

It must not change R05-R11B evidence, the Assignment runtime, the Worker
artifact, a registry, the Assignment artifact family, or AiCLI authority.

## Rejected shortcuts

The audit rejects:

- calling Assignment from AiCLI;
- mapping the Worker to CODEX or a synthetic identity;
- bypassing request or Worker artifact validation;
- passing a Selection artifact as a Worker artifact;
- using ERR lookup instead of the exact R11B projected Worker;
- adding Worker-specific Assignment policy;
- modifying the certified Assignment runtime without an observed blocker;
- combining Assignment with Dispatch or Invocation;
- rewriting or repeating authorization or consumption; and
- treating readiness as proof that Assignment has already occurred.

## Static validation

Validation intentionally excluded every test or command that would call the
Assignment owner or write lifecycle Replay.

Exact results:

| Validation | Passed | Skipped | Failed |
|---|---:|---:|---:|
| R09B-R11B source-only compatibility and neutrality | 3 | 0 | 0 |
| Assignment authority and existing-binding source checks | 2 | 0 | 0 |
| Constitutional layer contracts and model | 7 | 0 | 0 |
| Governance tests | 5 | 0 | 0 |

Additional read-only checks:

- in-memory source compilation passed for the Assignment,
  invocation-request, and Common Entry owners;
- parent `git diff --check`: passed;
- all three nested repository `git diff --check` checks: passed;
- complete repository suite: not run for this static audit;
- live Assignment: not called;
- runtime Replay or certification generation: not run;
- Dispatch, Invocation, Worker, Provider, command, target-open, and mutation
  workflows: not run.

The accepted R11B baseline already records its exactly-once full-suite result:

```text
6787 passed, 4 skipped, 0 failed
```

R12A does not repeat that suite.

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
`promotion_gate_v02` and `check_layer_freeze`. R12A neither repairs nor
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

The only scoped R12A change is this governance report. No production, test,
registry, certification, Replay, runtime, adapter, or protected path was
changed. Nothing was staged and no commit was created.

## Deterministic verdict

`G31_WORKER_ASSIGNMENT_EXECUTION_READY`

The existing certified Assignment Runtime can consume the exact certified
R09B request and R11B `WORKER_ARTIFACT_V1`, preserve identity, authority and
Replay continuity, produce the existing bounded Assignment lifecycle, and stop
before Dispatch without a new execution path.

R12A certifies readiness only. No Assignment occurred.
