# 1. Implementation Summary

Generation: G55-03

Report identity:
G55_03_CONVERSATION_WORKING_MEMORY_RUNTIME_IMPLEMENTATION_REPORT_V1

Reporting date: 2026-07-31

Constitutional baseline:
CONVERSATION_WORKING_MEMORY_IMPLEMENTATION_READY

Implementation contracts:

- G48 Constitutional Evidence Reporting Standard V1
- G55-01 Development Governance Conversation Boundary Architecture Audit
- G55-02 Conversation Working Memory Constitutional Implementation Readiness
  Audit
- Platform Core Capability Constitution V1
- existing Replay, Authorization, Worker, PCBV31, G31, G35, Completion Adapter,
  Human Interface, Conversation Boundary, Project Services, Objective
  Inference, Development Governance, and Capability Selection contracts

Objective:

Implement the standalone Conversation Working Memory runtime as an isolated,
mutable, non-authoritative Platform Core facility. This generation does not
integrate CWM with any constitutional execution owner.

Implementation scope:

- Added the exact
  `PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_RUNTIME_V1` runtime identity and
  `PLATFORM_CORE_HUMAN_INTENT_CONVERSATION` runtime owner.
- Added bounded structured state, deterministic canonical persistence,
  workspace/session isolation, monotonic revisions, atomic replacement,
  locking, SHA-256 integrity validation, TTL expiration, cleanup, and restart
  recovery.
- Added placeholder schema support for `COMMITTING` and `COMMITTED` while
  preventing this runtime from entering those states.
- Added focused deterministic tests for all required state, lifecycle,
  persistence, recovery, isolation, corruption, permission, concurrency, and
  constitutional-boundary requirements.

Modified modules:

- `aigol/runtime/platform_core_conversation_working_memory_runtime.py`:
  standalone CWM runtime.
- `tests/test_g55_03_conversation_working_memory_runtime.py`: focused CWM
  runtime unit and boundary tests.
- `docs/governance/G55_03_CONVERSATION_WORKING_MEMORY_RUNTIME_IMPLEMENTATION_REPORT_V1.md`:
  this G48 implementation report.

Intentionally unchanged modules:

- Platform Core Conversation Boundary, Admission Coordinator, Project
  Services, Objective Inference, Development Governance, and Capability
  Selection.
- Human Interface Runtime and AiCLI.
- Replay, Authorization, Workers, Completion Adapter, PCBV31, G31, and G35.
- Every existing constitutional artifact, capability identity, and execution
  protocol.

Architectural boundaries preserved:

- The runtime imports only the shared fail-closed error type from existing
  runtime code.
- Working state is stored below `.platform-core-working/conversation`, outside
  certified Replay artifact paths.
- State declares no constitutional, Replay, Authorization, Worker, Objective,
  or capability-routing authority.
- No entry point in an existing execution pipeline imports or invokes CWM.

# 2. Code Evidence

## Runtime Architecture

The public runtime identity and owner are:

```python
PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_RUNTIME_V1 = (
    "PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_RUNTIME_V1"
)
PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_SCHEMA_V1 = (
    "PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_SCHEMA_V1"
)
PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_OWNER = (
    "PLATFORM_CORE_HUMAN_INTENT_CONVERSATION"
)
```

Source:
`aigol/runtime/platform_core_conversation_working_memory_runtime.py`.

The complete public runtime surface supports:

- create;
- load;
- validate;
- bounded update;
- atomic replacement;
- cleanup;
- restart recovery; and
- path-safe state-location inspection.

No run, route, authorize, execute, replay, dispatch, or Objective API exists.

## State Model

The non-authority boundary is part of every stored state:

```python
_BOUNDARY_FIELDS = {
    "runtime_owner": PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_OWNER,
    "constitutional_artifact": False,
    "constitutional_authority": False,
    "replay_visible": False,
    "authorization_eligible": False,
    "worker_eligible": False,
    "objective_creation_supported": False,
    "capability_routing_supported": False,
}
```

The state contains the required runtime/schema versions, workspace and session
identities and hashes, revision, lifecycle, topic, entities, inferred intent,
confirmed facts, assumptions, unresolved ambiguity, confidence, discarded
interpretations, context references, candidate Objective snapshot and digest,
timestamps, expiration, and commitment placeholder.

The validator accepts exactly the declared schema. It rejects unexpected or
missing fields, malformed revisions, non-canonical identities, invalid
lifecycles, unbounded values, invalid timestamps, boundary changes, and
integrity mismatch.

Top-level constitutional and execution identity fields including
`artifact_hash`, `artifact_type`, `replay_hash`, `replay_identity`,
`replay_reference`, `objective_id`, `authorization_id`, and
`worker_request_id` are forbidden. Candidate snapshots recursively reject the
same identity keys.

No artifact hash or Replay identity exists.

## Lifecycle Implementation

Lifecycle constants support:

```text
ABSENT
  -> EXPLORING
  -> CANDIDATE_READY
  -> COMMITTING     placeholder only
  -> COMMITTED      placeholder only
```

Creation always stores revision-zero `EXPLORING` state. This runtime permits
only `EXPLORING` and `CANDIDATE_READY` mutation. `CANDIDATE_READY` requires a
non-empty candidate Objective snapshot with a matching deterministic digest.

Attempts to enter `COMMITTING` or `COMMITTED` through update or replacement
fail with:

```text
commit lifecycle is reserved for a future commitment runtime
```

The validator recognizes the two placeholder states so a future versioned
commitment runtime can adopt the prepared schema. No commitment transition or
Objective creation is implemented here.

## Persistence Implementation

State is stored at:

```text
<runtime-root>/.platform-core-working/conversation/
  <sha256(workspace-identity)>/
    <sha256(session-identity)>/
      state.json
```

Raw workspace and session values never form path components. The workspace
identity is canonicalized, and both requested identities must match the
validated state.

State serialization uses sorted, compact, ASCII JSON with non-finite numbers
rejected. State is capped at 65,536 bytes, candidate snapshots at 16,384
bytes, collections at 64 items, collection entries at 512 characters, and
free text at 4,096 characters.

Atomic replacement is implemented as:

```python
descriptor, temporary_name = tempfile.mkstemp(
    prefix=".state.",
    suffix=".tmp",
    dir=path.parent,
)
os.fchmod(descriptor, stat.S_IRUSR | stat.S_IWUSR)
with os.fdopen(descriptor, "wb", closefd=True) as handle:
    descriptor = -1
    handle.write(data)
    handle.flush()
    os.fsync(handle.fileno())
os.replace(temporary_name, path)
temporary_name = None
os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)
_fsync_directory(path.parent)
```

Owned directories are forced to mode `0700`; state and lock files are forced
to mode `0600`.

## Recovery Implementation

`load_conversation_working_memory_state` returns `None` only when state is
absent. It otherwise validates:

- safe regular-file storage;
- maximum byte size;
- UTF-8 and JSON structure;
- exact schema;
- workspace and session ownership;
- integrity;
- lifecycle;
- bounds; and
- expiration.

Expired direct loads fail closed. Restart recovery deterministically validates
the same state, removes an expired state, and returns `None`. Corrupt state is
never reconstructed, silently discarded, or converted into constitutional
evidence.

Cleanup validates integrity and ownership before deletion. An optional
expected revision prevents stale cleanup. Cleanup produces no artifact or
lineage record.

## Locking and Revision Control

All store operations acquire an exclusive lock on:

```text
<runtime-root>/.platform-core-working/conversation/.cwm.lock
```

The global CWM lock serializes create, load, update, replacement, recovery,
expiration cleanup, and explicit cleanup. This favors deterministic safety
over parallel write throughput in the standalone V1 runtime.

Every update:

1. reloads and validates current state while holding the lock;
2. rejects expiration;
3. requires the exact expected revision;
4. increments the revision by exactly one;
5. validates the complete replacement; and
6. atomically replaces the state file.

Two concurrent callers using the same expected revision produce one successful
update and one deterministic stale-revision rejection.

## Integrity Validation

Integrity uses local canonical JSON and SHA-256:

```text
integrity_algorithm = SHA256_CANONICAL_JSON
integrity_checksum = sha256(<canonical state without integrity_checksum>)
```

The checksum protects mutable storage integrity only. It is not named or used
as an artifact hash, Replay hash, constitutional identity, authorization
identity, or execution identity.

Corrupt JSON, invalid UTF-8, checksum mismatch, identity mismatch, schema
drift, invalid revision, invalid lifecycle, non-finite confidence, excessive
TTL, excessive storage, duplicate collection values, and forbidden nested
identity fields fail closed.

## Unit Test Results

Required CWM suite:

```text
python -m pytest -q \
  tests/test_g55_03_conversation_working_memory_runtime.py

17 passed in 0.18s
```

Final focused and adjacent constitutional regression:

```text
python -m pytest -q \
  tests/test_g55_03_conversation_working_memory_runtime.py \
  tests/test_g49_02_platform_core_conversation_boundary.py \
  tests/test_g54_09_platform_core_admission_precedence.py \
  tests/test_g21_02_platform_project_objective_inference.py \
  tests/test_g47_r01_objective_task_intake_compatibility.py

50 passed in 2.26s
```

Additional validation:

```text
python -m py_compile \
  aigol/runtime/platform_core_conversation_working_memory_runtime.py \
  tests/test_g55_03_conversation_working_memory_runtime.py

PASS
```

```text
git diff --check

PASS
```

The CWM suite covers creation, deterministic load, restart recovery, atomic
replacement, revision increments, stale writers, concurrent writers,
corruption, invalid JSON, session/workspace isolation, copied-state rejection,
integrity, cleanup, expiration, TTL extension, bounded state, bounded candidate
snapshots, permissions, path traversal resistance, placeholder lifecycle
states, duplicate creation, and prohibited downstream imports.

## Constitutional Boundary Verification

The runtime does not import or invoke:

- Platform Project Objective Inference;
- Platform Core Conversation Boundary;
- Admission Coordinator;
- Platform Core Project Services;
- Development Governance;
- Capability Selection;
- Replay;
- Authorization;
- Workers;
- Completion Adapter;
- PCBV31;
- G31;
- G35;
- Human Interface Runtime; or
- AiCLI.

No existing runtime imports CWM. Therefore the addition cannot create an
Objective, route a capability, authorize execution, dispatch a Worker, mutate
Replay, or enter PCBV31.

# 3. Constitutional Self-Assessment

## Verified

- The exact required runtime identity and owner are implemented.
- All required mutable state fields are present and validated.
- No constitutional artifact identity or Replay identity is created.
- State creation, load, validation, update, atomic replacement, cleanup,
  expiration, and restart recovery are implemented.
- Workspace and session values are isolated by canonical identity and
  path-safe hashes.
- Monotonic optimistic revision control is deterministic.
- Global locking makes concurrent same-revision updates fail closed.
- Temporary-file replacement, file synchronization, directory
  synchronization, and owner-only modes are implemented.
- Integrity corruption and malformed storage fail closed.
- TTL and all in-state collections and payloads are bounded.
- Commit lifecycle values are placeholders only; no commitment logic exists.
- Replay, Authorization, Workers, Completion Adapter, PCBV31, G31, G35,
  AiCLI, and every existing pipeline owner remain unchanged.
- The complete 17-test CWM suite and 50-test focused/adjacent set pass.
- `git diff --check` is clean.

## Not Verified

- Objective Commitment Gate behavior is not implemented or tested.
- Objective V2, Conversation Boundary V2, Admission Coordinator, Project
  Services V2, and HIR integration are not implemented.
- Replay exclusion is verified structurally and by negative imports; no future
  integrated Replay scanner exists to test against CWM yet.
- Authorization and Worker exclusion are verified structurally and through
  unchanged adjacent tests; no integrated CWM route exists.
- Multi-process crash testing during the exact `os.replace` instruction was
  not performed.
- `fcntl` locking is certified only for the repository's Unix-like runtime
  environment.
- Cleanup means logical removal; forensic erasure by the underlying filesystem
  is not claimed.
- An optional full-repository test run was stopped without observed failures
  at 39 percent because unrelated integration tests were exceptionally slow.
  It is not used as certification evidence; the complete required CWM suite
  and selected adjacent regression set passed.

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| Runtime identity and owner | Runtime constants | Direct import and state assertions | PASS |
| Complete state model | Exact schema and create result | Create/validate tests | PASS |
| Create and load | Public APIs | Deterministic create/load test | PASS |
| Update and revision increment | Update API | Revision and atomic-inode test | PASS |
| Stale revision rejection | Expected-revision gate | Sequential stale test | PASS |
| Concurrent update rejection | Global lock plus revision gate | Two-thread same-revision test | PASS |
| Atomic replacement | Temporary write, fsync, replace | Atomic update and public replacement tests | PASS |
| Integrity validation | SHA-256 canonical checksum | Tamper and corruption tests | PASS |
| Session isolation | Hashed session path plus validator | Isolation and copied-state test | PASS |
| Workspace isolation | Canonical workspace hash plus validator | Isolation and copied-state test | PASS |
| Owner-only permissions | Directory/file mode enforcement | Mode assertions | PASS |
| Path safety | Hashed identity components | Traversal-input test | PASS |
| Bounded storage | Size, collection, text, snapshot, TTL caps | Oversize and bound tests | PASS |
| Cleanup | Validated unlink plus revision guard | Cleanup test | PASS |
| Expiration | Explicit observed time and TTL | Expiration/recovery test | PASS |
| Restart recovery | Persistent validated state | Recovery equality test | PASS |
| Corruption rejection | Parse/schema/integrity gates | Invalid JSON and tamper tests | PASS |
| Lifecycle support | Constants, validator, mutable transition gate | Candidate and placeholder tests | PASS |
| Commit logic absent | Reserved-state rejection | COMMITTING update rejection | PASS |
| No constitutional identity | Exact schema and forbidden fields | State and nested identity tests | PASS |
| Replay exclusion | Storage root, flags, negative imports | Boundary test and source inspection | PASS |
| Authorization exclusion | Flags and negative imports | Boundary test and adjacent regression | PASS |
| Worker exclusion | Flags and negative imports | Boundary test and adjacent regression | PASS |
| Existing pipeline unchanged | No existing runtime file modified | 33 adjacent tests within 50-test set | PASS |
| Complete CWM unit suite | Focused pytest command | 17 tests | PASS |
| Repository formatting | Repository diff | `git diff --check` | PASS |

# 5. Repository Mutation Summary

Modified files:

- `aigol/runtime/platform_core_conversation_working_memory_runtime.py`:
  added isolated CWM state, persistence, validation, lifecycle, recovery,
  locking, revision, expiration, cleanup, bounds, and non-authority flags.
- `tests/test_g55_03_conversation_working_memory_runtime.py`: added 17 focused
  deterministic runtime tests.
- `docs/governance/G55_03_CONVERSATION_WORKING_MEMORY_RUNTIME_IMPLEMENTATION_REPORT_V1.md`:
  added this G48 evidence report.

Unchanged subsystems:

- Replay behavior: unchanged.
- Authorization behavior: unchanged.
- Worker behavior and lifecycle: unchanged.
- PCBV31 behavior and identity: unchanged.
- Completion Adapter: unchanged.
- G31 and G35: unchanged.
- AiCLI and Human Interface Runtime: unchanged.
- Conversation Boundary, Project Services, Objective Inference, Development
  Governance, Capability Selection, and Admission: unchanged.

API compatibility:

- No existing public API was changed.
- The CWM API is additive and has no existing caller.

Boundary preservation:

- The new state is mutable working data, not an immutable constitutional or
  Replay artifact.
- No execution authority, routing authority, Objective authority, or
  downstream semantic responsibility was added.

Unrelated pre-existing changes:

- None observed at the start of G55-03.

# 6. Certification Verdict

CONVERSATION_WORKING_MEMORY_RUNTIME_ESTABLISHED
