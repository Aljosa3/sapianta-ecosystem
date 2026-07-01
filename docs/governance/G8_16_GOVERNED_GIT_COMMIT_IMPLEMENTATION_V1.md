# G8-16 Governed Git Commit Implementation V1

Status: governed Git commit implemented.

Final verdict: GOVERNED_GIT_COMMIT_IMPLEMENTED

## 1. Executive Summary

G8-16 implements the smallest governed local Git commit capability specified by G8-15.

The implementation supports only:

```text
one local Git commit
from exactly the authorized file set
after successful governed validation
after explicit human approval
after Governance authorization
through Worker Platform execution
with Replay-visible evidence
```

The implementation does not add Git push, fetch, pull, clone, remote mutation, branch creation, branch switching, merge, rebase, reset, revert, tag, deployment, provider invocation, package installation, arbitrary shell execution, or ACLI Next execution authority.

## 2. Implemented Runtime Surfaces

Implemented files:

- `aigol/runtime/platform_core_git_commit_candidate.py`
- `aigol/runtime/platform_core_git_commit_governance.py`
- `aigol/runtime/platform_core_git_commit_result.py`
- `aigol/runtime/platform_core_git_commit_replay.py`
- `aigol/runtime/governed_git_commit_runtime.py`
- `aigol/workers/git_commit_worker.py`
- `tests/test_g8_governed_git_commit_runtime.py`

The implementation follows the Generation 8 responsibility split:

- OCS-shaped helper owns commit candidate artifacts.
- Governance helper owns approval and authorization artifacts.
- Platform Core coordinator owns workflow coordination.
- Worker Platform owns Git execution.
- Replay helper owns evidence persistence and reconstruction.
- Result helper owns commit result and rollback metadata normalization.

## 3. Supported Commit Scope

Allowed operation:

```text
CREATE_SINGLE_GOVERNED_LOCAL_GIT_COMMIT
```

Supported staged content model:

```text
EXPLICIT_FILE_SET_STAGED_BY_COMMIT_WORKER
```

Supported change types:

| Change Type | Status |
| --- | --- |
| `ADD_TEXT_FILE` | Implemented. |
| `REPLACE_TEXT_FILE` | Implemented. |

Commit execution requires:

- repository identity;
- current branch name;
- expected pre-commit `HEAD`;
- exact authorized file set;
- expected file content hashes;
- successful governed validation artifact;
- explicit hash-bound human approval;
- Governance authorization;
- Worker Platform Git execution;
- Replay root;
- commit metadata.

## 4. OCS Candidate Integration

The OCS-shaped candidate helper is:

```text
aigol/runtime/platform_core_git_commit_candidate.py
```

It creates and validates `GIT_COMMIT_CANDIDATE_ARTIFACT_V1`.

Candidate artifacts bind:

- candidate id;
- session id;
- repository id;
- branch name;
- expected `HEAD`;
- exact file set;
- file set hash;
- commit message hash;
- author hash;
- successful validation artifact hash;
- Worker id and scope;
- prohibited operation flags.

Candidate creation fails closed unless the validation artifact is a passed governed validation result.

## 5. Governance Integration

The Governance helper is:

```text
aigol/runtime/platform_core_git_commit_governance.py
```

Human approval requires:

```text
confirm governed git commit <candidate_id> <candidate_hash>
```

The approval artifact records the candidate hash, repository id, branch, expected `HEAD`, file set hash, commit message hash, author hash, validation artifact hash, and explicit non-authorization for push, remote interaction, branch management, merge, rebase, checkout, reset, deployment, provider invocation, and additional Worker dispatch.

Governance authorization uses the existing authorization record implementation and authorizes only:

| Field | Value |
| --- | --- |
| Worker id | `GOVERNED_LOCAL_GIT_COMMIT_WORKER` |
| Scope | `CREATE_GOVERNED_LOCAL_GIT_COMMIT` |

Human approval remains evidence for Governance. It does not execute Git by itself.

## 6. Worker Platform Integration

The Git Worker is:

```text
aigol/workers/git_commit_worker.py
```

The Worker:

1. validates the Worker request schema;
2. validates Governance authorization;
3. verifies repository root containment;
4. verifies current branch;
5. verifies current `HEAD`;
6. rejects unexpected staged content;
7. verifies authorized file paths and content hashes;
8. rejects path traversal and binary content;
9. verifies `ADD_TEXT_FILE` targets are untracked;
10. verifies `REPLACE_TEXT_FILE` targets are tracked;
11. stages only the exact authorized file set;
12. verifies staged paths exactly match authorization;
13. creates one local commit with approved metadata;
14. records commit hash and post-commit `HEAD`;
15. records Worker-side Replay evidence.

The Worker does not:

- choose files autonomously;
- run broad staging commands;
- push;
- fetch;
- pull;
- clone;
- mutate remotes;
- create or switch branches;
- merge;
- rebase;
- reset;
- revert;
- deploy;
- invoke providers;
- run arbitrary shell commands;
- dispatch additional Workers.

Git execution uses argument-vector `subprocess.run` calls with `shell=False`.

## 7. Replay Integration

Replay evidence is owned by:

```text
aigol/runtime/platform_core_git_commit_replay.py
```

Replay records ten ordered artifacts:

| Step | Evidence |
| --- | --- |
| 0 | Commit candidate. |
| 1 | Human approval. |
| 2 | Validation evidence. |
| 3 | Governance authorization. |
| 4 | Worker request. |
| 5 | Pre-execution state. |
| 6 | Worker result. |
| 7 | Commit result. |
| 8 | Rollback metadata. |
| 9 | Completion. |

Replay reconstruction verifies:

- candidate hash;
- approval-to-candidate binding;
- validation evidence hash;
- authorization-to-candidate binding;
- Worker request authorization binding;
- expected `HEAD` continuity;
- commit result continuity;
- rollback metadata continuity;
- completion-to-result binding;
- prohibited remote/deployment surfaces remain false.

## 8. Commit Metadata

Commit metadata is candidate-bound and approval-bound.

Implemented metadata:

- subject;
- optional body;
- author name;
- author email;
- committer policy using authorized author metadata;
- candidate id;
- authorization id;
- Replay reference through artifacts.

The Worker sets author and committer identity for the local commit through Git environment variables. It does not mutate Git config.

## 9. Rollback Interaction

Rollback metadata is produced by:

```text
aigol/runtime/platform_core_git_commit_result.py
```

Rollback metadata records:

- pre-commit `HEAD`;
- created commit hash;
- branch name;
- authorized file set;
- file set hash;
- recommendation for manual governed review before revert or reset.

Rollback execution is not implemented. The Git Worker does not run reset or revert.

## 10. Fail-Closed Behavior

The runtime fails closed on:

- missing approval;
- unbound approval text;
- missing successful validation evidence;
- validation evidence hash mismatch;
- missing Governance authorization;
- repository root mismatch;
- branch mismatch;
- `HEAD` mismatch;
- unexpected staged content;
- authorized file missing;
- authorized file hash mismatch;
- tracked/untracked change type mismatch;
- staged path mismatch;
- prohibited Worker request fields;
- Git command failure;
- Replay write failure.

Failure summaries preserve the specific failed checkpoint where available and explicitly report that no push, remote interaction, branch management, deployment, or provider invocation occurred.

## 11. Boundary Compliance

| Boundary | Implementation Result |
| --- | --- |
| ACLI Next | No new ACLI execution authority. |
| Platform Core | Coordinates commit workflow through a thin runtime coordinator. |
| OCS | Owns commit candidate artifacts. |
| Governance | Owns approval and authorization artifacts. |
| Worker Platform | Owns Git execution. |
| Replay | Owns evidence persistence and reconstruction. |
| Validation | Successful governed validation artifact is required before commit candidate acceptance. |
| Rollback | Metadata only; no rollback execution. |
| Remote Git | Absent. |
| Deployment | Absent. |
| Provider invocation | Absent. |

## 12. Targeted Test Coverage

Targeted tests cover:

- successful governed local commit with Replay reconstruction;
- authorized existing-file replacement commit;
- missing human approval fail-closed behavior;
- `HEAD` conflict fail-closed behavior;
- unexpected staged content fail-closed behavior;
- prohibited Worker request surface rejection;
- failed validation rejection before candidate creation.

Test file:

```text
tests/test_g8_governed_git_commit_runtime.py
```

## 13. Validation Evidence

Validation performed:

```text
git diff --check
python -m py_compile aigol/workers/git_commit_worker.py aigol/runtime/governed_git_commit_runtime.py aigol/runtime/platform_core_git_commit_candidate.py aigol/runtime/platform_core_git_commit_governance.py aigol/runtime/platform_core_git_commit_result.py aigol/runtime/platform_core_git_commit_replay.py tests/test_g8_governed_git_commit_runtime.py
python -m pytest tests/test_g8_governed_git_commit_runtime.py
```

Validation result: clean.

## 14. Final Determination

The smallest governed local Git commit capability has been implemented.

The implementation creates exactly one local commit from an explicitly authorized file set after successful governed validation, explicit human approval, Governance authorization, Worker Platform Git execution, and Replay-visible evidence generation.

Final verdict: GOVERNED_GIT_COMMIT_IMPLEMENTED
