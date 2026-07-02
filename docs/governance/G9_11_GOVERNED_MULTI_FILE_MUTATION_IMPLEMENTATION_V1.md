# G9-11 Governed Multi-File Mutation Implementation V1

Status: governed multi-file mutation implemented.

Final verdict: GOVERNED_MULTI_FILE_MUTATION_IMPLEMENTED

## 1. Executive Summary

G9-11 implements the smallest governed multi-file mutation capability by composing existing certified single-file mutation capabilities through a deterministic transaction envelope.

The implementation supports:

- multiple plaintext file operations in one governed transaction;
- certified single-file create operations;
- certified existing-file replacement operations;
- certified single-file patch operations;
- deterministic transaction candidate construction;
- explicit hash-bound human approval;
- Governance authorization;
- Worker Platform execution only;
- transaction Replay evidence;
- pre-transaction and post-transaction validation;
- transaction rollback metadata;
- fail-closed behavior.

The implementation does not introduce a new mutation subsystem or authority layer.

## 2. Implemented Runtime Surfaces

Implemented files:

```text
aigol/runtime/platform_core_multi_file_mutation_candidate.py
aigol/runtime/platform_core_multi_file_mutation_governance.py
aigol/runtime/platform_core_multi_file_mutation_replay.py
aigol/runtime/platform_core_multi_file_mutation_validation.py
aigol/runtime/multi_file_mutation_runtime.py
tests/test_g9_multi_file_mutation_runtime.py
```

The implementation reuses existing certified Worker Platform execution paths:

- `filesystem_worker.py` for create;
- `filesystem_replace_worker.py` for replace;
- `filesystem_patch_worker.py` for patch.

## 3. Transaction Envelope

The multi-file mutation runtime introduces a transaction envelope, not a new mutation authority.

Transaction candidate properties:

- exact ordered operation list;
- exact file set;
- per-file single-file candidate hash;
- per-file Worker identity and scope;
- per-file expected pre-hash when applicable;
- per-file expected post-hash;
- explicit no-Git, no-deployment, no-provider, no-dependency flags;
- deterministic ordering;
- Replay visibility.

The transaction envelope composes certified per-file operations and records transaction-level evidence around them.

## 4. Platform Core Coordination

Platform Core coordinates the transaction through:

```text
execute_governed_multi_file_mutation
```

Platform Core responsibilities:

- validate transaction candidate;
- validate hash-bound human approval;
- resolve the allowlisted workspace;
- perform pre-transaction validation;
- request Governance authorization;
- sequence per-file Worker execution deterministically;
- perform post-transaction validation;
- record rollback metadata;
- persist transaction Replay evidence;
- emit completion or fail-closed evidence.

Platform Core does not directly perform filesystem mutation.

## 5. Governance Integration

Human approval must bind the exact transaction candidate hash:

```text
confirm multi-file mutation <candidate_id> <candidate_hash>
```

Governance creates per-operation Worker authorization records from the approved transaction file set.

Governance does not:

- execute mutation;
- select files;
- plan operations;
- reconstruct Replay;
- authorize Git;
- authorize deployment;
- authorize provider invocation;
- authorize dependency installation;
- authorize automatic rollback.

## 6. Worker Platform Integration

Worker Platform execution remains per-file and bounded.

The multi-file runtime does not introduce a multi-file Worker authority.

Each operation invokes the existing certified Worker for that operation type:

| Operation | Worker |
| --- | --- |
| `create` | `FILESYSTEM_CREATE_WORKER` |
| `replace` | `FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER` |
| `patch` | `FILESYSTEM_SINGLE_FILE_CONTEXT_PATCH_WORKER` |

Workers do not plan, authorize, certify, reconstruct Replay, or operate Git, deployment, provider, or dependency surfaces.

## 7. Replay Integration

Transaction Replay steps:

```text
transaction_candidate_recorded
human_approval_recorded
governance_authorization_recorded
pre_transaction_validation_recorded
per_file_execution_recorded
post_transaction_validation_recorded
rollback_metadata_recorded
completion_recorded
```

Each per-file Worker also records its own bounded Worker-local replay evidence.

Replay remains append-only and owns transaction reconstruction.

## 8. Validation Integration

Pre-transaction validation confirms all operations are ready before any Worker executes:

- create targets must be absent;
- replace targets must match expected pre-hash;
- patch targets must match expected pre-hash and exact context occurrence;
- all targets remain inside the allowlisted workspace.

Post-transaction validation confirms:

- every expected resulting file hash is present;
- all per-file operations completed;
- no Git, deployment, provider, dependency, or automatic rollback behavior occurred.

If pre-transaction validation fails, no file operation is executed.

## 9. Rollback Metadata

The transaction records per-file rollback metadata:

- create rollback: delete created file if hash matches;
- patch rollback: restore prior complete content if current hash matches;
- replace rollback: marked as requiring complete prior content evidence before executable rollback.

The transaction does not execute rollback automatically.

Rollback execution remains separately governed and requires human approval.

## 10. Fail-Closed Behavior

The transaction fails closed when:

- transaction candidate is invalid;
- duplicate target paths are present;
- approval is missing or not hash-bound;
- Governance authorization is invalid;
- pre-transaction validation detects stale state;
- any Worker execution fails;
- post-transaction validation fails;
- Replay evidence cannot be persisted.

Partial execution is not automatically rolled back. Completed operation count is reported in fail-closed completion evidence if failure occurs after execution begins.

## 11. Architecture Preservation

Certified ownership boundaries are preserved:

| Owner | Responsibility |
| --- | --- |
| ACLI Next | Thin entrypoint; no transaction planning or execution authority. |
| Platform Core | Coordinates transaction lifecycle. |
| OCS | Owns deterministic transaction candidate construction. |
| Governance | Authorizes exact transaction scope. |
| Replay | Records and reconstructs transaction evidence. |
| Worker Platform | Executes bounded per-file operations only. |
| Architectural Health | May observe transaction evidence as advisory projection only. |

No Platform Core redesign occurred.

No mutation subsystem was introduced.

No new authority layer was introduced.

## 12. Validation Evidence

Validation performed:

```text
git diff --check
python -m py_compile aigol/runtime/platform_core_multi_file_mutation_candidate.py aigol/runtime/platform_core_multi_file_mutation_governance.py aigol/runtime/platform_core_multi_file_mutation_replay.py aigol/runtime/platform_core_multi_file_mutation_validation.py aigol/runtime/multi_file_mutation_runtime.py
python -m pytest tests/test_g9_multi_file_mutation_runtime.py
```

Validation result: clean.

Final verdict: GOVERNED_MULTI_FILE_MUTATION_IMPLEMENTED
