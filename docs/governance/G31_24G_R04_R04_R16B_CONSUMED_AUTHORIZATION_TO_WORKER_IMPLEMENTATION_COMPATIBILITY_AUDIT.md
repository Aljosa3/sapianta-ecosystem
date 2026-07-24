# Generation 31-24G-R04-R04-R16B Consumed Authorization to Worker Implementation Compatibility Audit

Status: completed audit-only constitutional compatibility determination.

Date: 2026-07-24

Deterministic verdict:

`G31_CONSUMED_AUTHORIZATION_TO_WORKER_IMPLEMENTATION_COMPATIBILITY_STRATEGY_DEFINED`

Exactly one next state:

`G31_24G_R04_R04_R16C_CONSUMED_AUTHORIZATION_WORKER_CONTINUATION_IMPLEMENTATION_REQUIRED`

## Certified baseline and scope

G0-G30 and accepted Generation 31 evidence through R15F are treated as
constitutionally closed. R16A is the immediate accepted audit baseline:

- commit: `44645270528d566150e275850032a2040b16e287`;
- subject:
  `docs(governance): audit filesystem worker activation readiness`;
- R16A verdict:
  `G31_FILESYSTEM_REPLACE_WORKER_IMPLEMENTATION_ACTIVATION_BLOCKED`;
- R16A blocker:
  `R15F_CONSUMED_AUTHORIZATION_INCOMPATIBLE_WITH_EXISTING_FILESYSTEM_REPLACE_WORKER_EXECUTION_ENTRY`.

This audit inspected only consumed Authorization ownership, Worker ownership,
the existing V2 Replay, execution-packet continuity, authority continuity,
fail-closed behavior, and duplicate-consumption prevention. It did not inspect
or alter unrelated execution phases.

No Worker, Provider, runtime, command, target, result, restoration, rollback,
recovery, or repository mutation operation was executed.

## Ownership findings

### Consumed Authorization

Common Entry invokes the existing
`consume_authenticated_replace_authorization_v2` owner exactly once before
selection. That owner:

1. validates the immutable authenticated request;
2. reconstructs an exact request-only V2 Replay;
3. appends the immutable `AUTHORIZATION_CONSUMPTION_CLAIMED` event with
   `O_EXCL`;
4. reconstructs exactly `request -> consumption`; and
5. returns the request, authorization, consumption, and Replay identities.

Sequential duplication fails because the Replay is no longer request-only.
Concurrent duplication has one immutable destination and therefore only one
possible successful claimant.

The request's `authorization_consumed = false` field is an immutable
pre-consumption assertion inside the request hash. Consumed state is correctly
represented by the later Replay event and reconstruction; mutating the request
field is neither required nor permitted.

### Worker and Replay

The existing Filesystem Replace Worker owns the complete V2 event vocabulary:

```text
request
-> consumption
-> journal
-> started
-> atomic
-> result
-> completion / termination / rollback / recovery
```

The reconstructor already accepts a valid partial prefix, validates every
artifact identity and predecessor hash, rejects unexpected files, and rejects
reordered, duplicated, or branched Replay. The immutable event writer already
supports continuing the chain from a supplied predecessor wrapper hash.

The incompatibility is localized to the existing physical execution entry:
it requires the consumption destination to be absent, initializes its
predecessor to `None`, and writes `request` and `consumption` again before the
journal. The V2 Replay model itself does not require duplicate consumption.

### Execution packet and authority

The exact authenticated request and consumption reconstruction are retained in
the invocation request's certified compatibility lineage. The projected
execution packet is not a competing payload:

```text
packet_id = exact authenticated request_id
packet_hash = exact authenticated request_hash
target Worker = FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER
capability = REPLACE_EXISTING_TEXT_FILE
```

Assignment, Dispatch, Invocation, and the R15F Execution artifact preserve
that packet identity and hash, Worker identity and hash, Assignment-derived
capability, request lineage, and canonical chain. Common Entry also retains
the original authenticated request and exact consumption reconstruction.

The R15F Execution artifact grants no Provider authority and records only an
`AIGOL` start. Physical replacement remains owned by the existing Filesystem
Replace Worker. Consumption remains owned by the existing V2 consumption
owner. Replay append and reconstruction remain owned by the existing V2
Worker Replay owner.

No additional authority or payload is missing at this boundary.

## Constitutional compatibility analysis

No second constitutional blocker exists within the audited boundary. The
certified spine already retains all identities and inputs needed to prove:

- exact single-use consumption;
- exact Worker and capability;
- exact authenticated request and execution packet;
- exact session, repository, target, preimage, postimage, content, and mode
  bindings;
- exact R15F Execution start and parent lineage; and
- absence of Provider, command, result, and prior repository-mutation
  authority.

The minimum constitutional adaptation is one consumed-authorization
continuation contract inside the existing Filesystem Replace Worker ownership
boundary. A later implementation must:

1. accept the exact immutable authenticated request, its exact consumed
   reconstruction, and the exact R15F Execution artifact/reconstruction;
2. validate the R15F Worker, capability, request/execution-packet, chain, and
   start-only authority continuity before target access;
3. reconstruct the existing V2 Replay and require exactly
   `request -> consumption`, with the exact request hash, authorization
   identity/hash, consumption identity, Replay hash, and last wrapper hash;
4. treat the existing consumption event as a mandatory prerequisite, never
   call the consumption owner again, and never rewrite either predecessor;
5. continue the existing V2 chain at `journal` using the existing
   consumption wrapper hash as `previous_replay_hash`;
6. retain the existing target, preimage, clean-repository, journal,
   atomic-replacement, verification, restoration, recovery, and terminal
   semantics; and
7. fail closed before target access if any execution or consumption evidence
   differs, if any post-consumption event already exists, or if the immutable
   journal destination loses a concurrent append race.

This adaptation extends the already-certified path after R15F. It does not
move consumption into Worker activation, change a certified parent, create a
second consumption event, add a Replay family, introduce a Provider or command
runner, or create a new mutation owner.

The existing fresh-lifecycle execution behavior may remain available only for
its already-certified callers. The G31 continuation must use the consumed
entry contract and may not fall back to the fresh-lifecycle path.

## Fail-closed boundary

The continuation is admissible only from the single exact V2 prefix:

```text
REQUEST_VALIDATED
-> AUTHORIZATION_CONSUMPTION_CLAIMED
-> STOP
```

Missing consumption, a changed identity or hash, request-only Replay,
duplicate/branched Replay, any journal or later event, a mismatched R15F
Execution artifact, Provider authority, a different Worker or capability, or
a second activation attempt must fail before the target is opened.

After the first immutable `journal` append succeeds, the existing Worker
recovery and termination semantics remain authoritative. No new recovery
owner is required.

## Validation and repository preservation

Static inspection covered:

- the authenticated request validator;
- request Replay creation and single-use consumption;
- V2 Replay reconstruction and immutable event append;
- the existing fresh-lifecycle Worker execution entry;
- the public existing-file governance execution entry;
- authenticated request projection into the execution packet;
- Assignment, Dispatch, Invocation, and R15F Execution continuity; and
- Common Entry's retained request, consumption, and execution captures.

Targeted `python -m py_compile` passed for all inspected production modules.
Parent `git diff --check` and all three nested-repository
`git diff --check` checks passed.

The nested repositories remain at:

- `sapianta-domain-credit`:
  `8615e1e290471a67e4e764c6ab2138340bc7936f`;
- `sapianta_system`:
  `3183bab71f8f30397c0309dd2e6d846d14a11f66`;
- `sapianta-domain-trading`:
  `d3038dc4ba36ffbaee9161172b4c852e8e6acbda`.

The six protected hashes equal the accepted baseline:

| Protected path | SHA-256 |
| --- | --- |
| `diagnostic_evidence.json` | `21546ed151c165c6364aa914d892c34b117ef1ab664ae09d8e2c2a5327bcc8df` |
| `governed_return.json` | `ee57877ceea7d85bd9e3bb29aca64f3637384a7346a5b6a4c4f922c87cb2bcf7` |
| `lineage.json` | `8c47abb9a7c238c9f527e54dd88aa304edbca03b97ea630a4907b4ef139b3a08` |
| `provider_stderr.txt` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `provider_stdout.txt` | `f2fec907b48e7162211f26bbe94352d40f4f6c4380ab3aa4256d072b7c602f30` |
| `governed_returns.jsonl` | `71b085174a274b870617c21810d9a496421985675ae0945f4b56bd3afe7b1118` |

No production, test, Replay, protected, or nested-repository file was changed.
Nothing was staged or committed. This governance report is the sole R16B
artifact.
