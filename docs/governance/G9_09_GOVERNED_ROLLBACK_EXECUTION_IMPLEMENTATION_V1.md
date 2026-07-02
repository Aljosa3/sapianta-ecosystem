# G9-09 Governed Rollback Execution Implementation V1

Status: governed rollback execution implemented.

Final verdict: GOVERNED_ROLLBACK_EXECUTION_IMPLEMENTED

## 1. Executive Summary

G9-09 implements the smallest safe governed rollback execution capability for AiGOL development mutations.

The implementation completes the governed lifecycle for exactly one previously governed mutation while preserving the certified Platform Core ownership model.

Implemented rollback modes:

- delete one file created by the first governed mutating Worker;
- restore one existing plaintext file after governed single-file patch mutation, using complete canonical restore content reconstructed from prior Replay evidence.

Existing-file full replacement rollback remains fail-closed unless prior Replay evidence contains complete original content. This preserves the certified canonical artifact model and prevents hash-only rollback reconstruction.

## 2. Implemented Runtime Surfaces

Implemented files:

```text
aigol/runtime/governed_rollback_runtime.py
aigol/runtime/platform_core_rollback_candidate.py
aigol/runtime/platform_core_rollback_governance.py
aigol/runtime/platform_core_rollback_replay.py
aigol/runtime/platform_core_rollback_validation.py
aigol/workers/filesystem_rollback_worker.py
tests/test_g9_governed_rollback_runtime.py
```

The runtime provides:

- deterministic rollback candidate construction from prior Replay evidence;
- hash-bound human approval;
- Governance authorization record creation;
- pre-rollback validation;
- bounded Worker Platform rollback execution;
- post-rollback validation;
- append-only rollback Replay evidence;
- deterministic rollback replay reconstruction;
- fail-closed handling for missing approval, hash conflicts, unsupported evidence, and Worker failure.

## 3. Platform Core Coordination

Platform Core coordinates rollback through `execute_governed_rollback`.

Platform Core responsibilities:

- validate the rollback candidate;
- validate human approval;
- resolve the allowlisted workspace;
- perform pre-rollback validation;
- request Governance authorization;
- create the bounded Worker request;
- invoke the rollback Worker;
- perform post-rollback validation;
- persist Replay evidence;
- return deterministic completion evidence.

Platform Core does not execute filesystem mutation directly.

## 4. Rollback Candidate Model

Rollback candidates are created by:

```text
create_governed_rollback_candidate
```

The candidate is deterministic and includes:

- prior mutation type;
- prior replay reference;
- prior replay hash;
- rollback metadata hash;
- target path;
- rollback action;
- authorized current hash;
- expected rollback result hash;
- restore content when complete canonical restore content is available;
- explicit prohibition flags for multi-target rollback, orchestration, Git, branch manipulation, deployment, provider invocation, dependency rollback, and automatic rollback.

Supported prior mutation types:

| Prior Mutation Type | Rollback Behavior |
| --- | --- |
| `first_mutating_worker` | Delete the created file if current hash matches. |
| `single_file_patch_mutation` | Restore complete prior file content if current hash matches. |
| `existing_file_mutation` | Fail closed unless complete original content evidence exists. |

## 5. Governance Integration

Governance remains the authorization authority.

Human approval must use the exact hash-bound confirmation:

```text
confirm governed rollback execution <candidate_id> <candidate_hash>
```

Approval alone does not execute rollback. Governance produces the authorization record consumed by the Worker Platform.

Governance does not:

- execute rollback;
- reconstruct Replay;
- perform validation;
- approve automatically;
- authorize Git, branch, deployment, provider, dependency, or multi-target rollback behavior.

## 6. Worker Platform Integration

The rollback Worker is:

```text
FILESYSTEM_SINGLE_TARGET_ROLLBACK_WORKER
```

The Worker accepts only:

```text
AUTHORIZED_SINGLE_TARGET_ROLLBACK_REQUEST_V1
```

Worker actions:

- `DELETE_CREATED_FILE_IF_HASH_MATCHES`;
- `RESTORE_ORIGINAL_CONTENT_IF_CURRENT_HASH_MATCHES_AUTHORIZED_POST_HASH`.

The Worker performs execution only. It does not plan, authorize, certify, mutate Replay, invoke providers, operate Git, manipulate branches, deploy, or perform dependency rollback.

## 7. Replay Integration

Rollback Replay is append-only and reconstructable.

Replay steps:

```text
rollback_candidate_recorded
human_approval_recorded
governance_authorization_recorded
pre_rollback_validation_recorded
worker_request_recorded
worker_result_recorded
post_rollback_validation_recorded
completion_recorded
```

Worker Replay is separately recorded and linked through deterministic hashes.

Replay remains the evidence and reconstruction authority.

## 8. Validation Interaction

Pre-rollback validation confirms:

- target path remains inside the allowlisted workspace;
- current target state is regular plaintext when required;
- current hash matches the authorized post-mutation hash;
- exactly one rollback target is in scope.

Post-rollback validation confirms:

- Worker execution occurred;
- expected rollback result hash was produced;
- target absence or restored content matches the rollback candidate;
- no Git, branch, deployment, provider, dependency, or automatic rollback behavior occurred.

## 9. Fail-Closed Behavior

Rollback fails closed when:

- rollback candidate evidence is invalid;
- prior Replay evidence is missing or unsupported;
- complete restore content is unavailable;
- human approval is absent or not hash-bound;
- Governance authorization is invalid;
- current target hash conflicts with authorized rollback state;
- Worker execution fails;
- post-rollback validation fails;
- Replay evidence cannot be persisted.

Fail-closed completion evidence is replay-visible and reports no repository mutation.

## 10. Architecture Preservation

Certified ownership boundaries are preserved:

| Owner | Responsibility |
| --- | --- |
| ACLI Next | Thin human entrypoint; no rollback execution added here. |
| Platform Core | Coordinates rollback lifecycle. |
| OCS | Owns deterministic rollback candidate formation. |
| Governance | Authorizes rollback. |
| Replay | Records and reconstructs rollback evidence. |
| Worker Platform | Executes the bounded rollback action only. |
| Architectural Health | May observe rollback evidence as advisory projection only. |

No new authority layer was introduced.

No Platform Core replacement occurred.

No rollback engine authority was introduced.

## 11. Validation Evidence

Validation performed:

```text
git diff --check
python -m py_compile aigol/runtime/governed_rollback_runtime.py aigol/runtime/platform_core_rollback_candidate.py aigol/runtime/platform_core_rollback_governance.py aigol/runtime/platform_core_rollback_replay.py aigol/runtime/platform_core_rollback_validation.py aigol/workers/filesystem_rollback_worker.py
python -m pytest tests/test_g9_governed_rollback_runtime.py
```

Validation result: clean.

Final verdict: GOVERNED_ROLLBACK_EXECUTION_IMPLEMENTED
