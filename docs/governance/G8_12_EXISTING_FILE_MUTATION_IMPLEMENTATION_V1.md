# G8-12 Existing File Mutation Implementation V1

Status: existing file mutation implemented.

Final verdict: EXISTING_FILE_MUTATION_IMPLEMENTED

## 1. Executive Summary

G8-12 implements the smallest governed mutation of an existing repository file as specified by G8-11.

The implemented operation is:

```text
REPLACE_SINGLE_EXISTING_TEXT_FILE_IN_GOVERNED_WORKSPACE
```

The implementation supports only:

- full-content replacement of exactly one existing plaintext file;
- target files inside an allowlisted non-authority workspace;
- pre-mutation hash verification;
- post-mutation hash verification;
- explicit human approval;
- Governance authorization;
- Worker Platform execution;
- Replay evidence generation;
- validation evidence;
- rollback metadata;
- fail-closed conflict detection.

The implementation does not add Git, commit creation, deployment, provider invocation, multi-file mutation, arbitrary shell execution, authority artifact modification, or ACLI Next authority.

## 2. Implemented Runtime Surfaces

Files added:

- `aigol/workers/filesystem_replace_worker.py`
- `aigol/runtime/existing_file_mutation_runtime.py`
- `aigol/runtime/platform_core_existing_file_mutation_candidate.py`
- `aigol/runtime/platform_core_existing_file_governance.py`
- `aigol/runtime/platform_core_existing_file_validation.py`
- `aigol/runtime/platform_core_existing_file_rollback.py`
- `aigol/runtime/platform_core_existing_file_replay.py`
- `tests/test_g8_existing_file_mutation_runtime.py`

The implementation follows the G8-09B responsibility model:

- OCS-shaped helper owns candidate creation and validation.
- Governance-shaped helper owns approval and authorization creation.
- Worker Platform owns file mutation execution.
- Replay helper owns replay persistence and reconstruction.
- Validation helper owns pre- and post-mutation validation evidence.
- Rollback helper owns rollback metadata.
- Runtime coordinator owns only workflow sequencing and completion capture.

## 3. Mutation Scope

Allowed mutation:

| Field | Implemented behavior |
| --- | --- |
| Operation | Replace one existing plaintext file. |
| File count | Exactly one. |
| Target path | Relative path under allowlisted workspace. |
| Workspace | Defaults to `runtime/governed_mutation_workspace`. |
| Existing file requirement | Target must exist and be a regular file. |
| Encoding | UTF-8 plaintext, no null bytes. |
| Size | Replacement and target content are bounded to 64 KiB. |
| Precondition | Current target hash must match candidate expected hash. |
| Postcondition | Resulting target hash must match candidate replacement hash. |
| Git | Not performed. |
| Commit | Not created. |
| Deployment | Not performed. |
| Provider | Not invoked. |

The Worker fails closed if the target is missing, escapes the workspace, is a symlink, is not a regular file, is not plaintext UTF-8, or has a stale hash.

## 4. Governance Integration

Human approval is explicit and candidate-hash-bound:

```text
confirm existing-file mutation <candidate_id> <candidate_hash>
```

Governance authorization uses the existing authorization record implementation and authorizes only:

```text
FILESYSTEM_REPLACE_EXISTING_TEXT_FILE
```

The approval artifact and authorization record explicitly do not authorize:

- Git;
- commit creation;
- deployment;
- provider invocation;
- additional Worker dispatch.

Human approval remains admissibility evidence. It does not authorize mutation by itself.

## 5. Worker Platform Integration

The Worker Platform integration is implemented by:

```text
aigol/workers/filesystem_replace_worker.py
```

The Worker accepts an authorized replace request and:

1. validates request schema;
2. validates Governance authorization;
3. validates target path containment;
4. validates target existence and regular-file status;
5. reads current plaintext content;
6. verifies current hash against the expected pre-mutation hash;
7. writes replacement content;
8. verifies resulting hash;
9. records Worker-side replay evidence.

The Worker does not authorize itself, call providers, run shell commands, run Git, create commits, deploy, select additional Workers, or mutate multiple files.

## 6. Replay Integration

Replay evidence records nine ordered artifacts:

| Index | Artifact |
| --- | --- |
| 0 | Mutation candidate |
| 1 | Human approval |
| 2 | Governance authorization |
| 3 | Worker request |
| 4 | Pre-mutation state |
| 5 | Worker result |
| 6 | Post-mutation validation |
| 7 | Rollback metadata |
| 8 | Completion summary |

Replay reconstruction verifies:

- wrapper ordering;
- wrapper hashes;
- artifact hashes;
- candidate-to-approval linkage;
- authorization-to-candidate linkage;
- worker request-to-authorization linkage;
- pre-mutation hash continuity;
- Worker old/new hash continuity;
- validation status;
- rollback original hash;
- completion linkage.

Missing or conflicting replay evidence blocks success claims.

## 7. Validation

Validation confirms:

- target stayed inside allowlisted workspace;
- target existed before mutation;
- target exists after mutation;
- target was plaintext UTF-8;
- pre-mutation hash matched candidate expectation;
- post-mutation hash matched replacement content;
- exactly one file was mutated;
- no Git operation occurred;
- no commit was created;
- no deployment occurred;
- no provider was invoked.

Hash conflict fails closed before mutation.

## 8. Rollback Metadata

Rollback metadata records:

- target path;
- target relative path;
- original content hash;
- authorized post-mutation hash;
- rollback operation description;
- authorization requirement for rollback;
- automatic rollback disabled;
- delete-file and delete-directory operations prohibited.

Rollback execution is not implemented in this milestone.

## 9. Fail-Closed Behavior

Fail-closed behavior is implemented for:

- missing human approval;
- unbound human confirmation;
- missing target file;
- target path traversal;
- target escaping workspace;
- symlink or non-regular-file target;
- stale pre-mutation hash;
- replacement hash mismatch;
- replay artifact collision;
- Worker execution failure;
- validation failure.

Failure capture is replay-visible where replay remains available and reports that no repository mutation occurred.

## 10. Architecture Review

The implementation preserves certified boundaries:

| Boundary | Result |
| --- | --- |
| ACLI Next | Remains a thin entrypoint; no direct mutation authority added. |
| Platform Core | Coordinates workflow through a runtime coordinator. |
| OCS | Owns existing-file mutation candidate artifacts. |
| Governance | Owns approval and authorization artifacts. |
| Worker Platform | Owns file replacement execution. |
| Replay | Owns replay persistence and reconstruction. |
| Validation | Owns pre/post mutation validation evidence. |
| Rollback | Owns rollback metadata only, not rollback execution. |

No new authority layer was introduced.

## 11. Targeted Tests

Targeted tests cover:

- successful replacement of one existing file;
- replay reconstruction;
- rollback metadata presence;
- explicit hash-bound human approval;
- fail-closed missing approval;
- fail-closed stale hash conflict;
- fail-closed missing target;
- path traversal rejection;
- unbound confirmation rejection;
- no provider, Git, commit, or deployment surface.

Regression tests for the first mutating Worker remain passing.

## 12. Validation Evidence

Validation performed:

```text
git diff --check
python -m py_compile aigol/workers/filesystem_replace_worker.py aigol/runtime/existing_file_mutation_runtime.py aigol/runtime/platform_core_existing_file_mutation_candidate.py aigol/runtime/platform_core_existing_file_governance.py aigol/runtime/platform_core_existing_file_validation.py aigol/runtime/platform_core_existing_file_rollback.py aigol/runtime/platform_core_existing_file_replay.py tests/test_g8_existing_file_mutation_runtime.py
python -m pytest tests/test_g8_existing_file_mutation_runtime.py tests/test_g8_first_mutating_worker_runtime.py tests/test_repository_mutation_worker_runtime_v1.py
```

Validation result:

```text
22 passed
```

## 13. Final Determination

The smallest governed existing-file mutation has been implemented.

The mutation remains bounded, governed, replay-visible, rollback-aware, validation-backed, and restricted to a single existing plaintext file inside an allowlisted non-authority workspace.

Final verdict: EXISTING_FILE_MUTATION_IMPLEMENTED
