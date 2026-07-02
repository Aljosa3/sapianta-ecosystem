# G9-05 Governed Rollback Execution Specification V1

Status: governed rollback execution specified.

Final verdict: GOVERNED_ROLLBACK_EXECUTION_SPECIFIED

## 1. Executive Summary

G9-05 specifies the smallest safe governed rollback execution capability for AiGOL.

Generation 8 and Generation 9 certified governed mutation runtimes that produce rollback metadata, but executable rollback remained intentionally deferred. G9-02 identified governed rollback execution as the next highest-priority runtime capability after single-file patch-level mutation.

The certified next step is:

```text
Execute rollback for exactly one prior governed repository mutation
only when Replay can reconstruct the original mutation,
Governance authorizes the rollback candidate,
the current target state still matches the authorized rollback precondition,
and Worker Platform performs the restore operation.
```

This specification does not authorize multi-file rollback orchestration, Git remote operations, deployment rollback, provider invocation, package manager rollback, branch rollback, autonomous retry, or rollback of authority artifacts.

Governed rollback execution must remain:

- governed;
- replay-reconstructed;
- hash-bound;
- single-mutation only;
- single-target only for the first version;
- non-authority workspace only;
- validation-aware;
- fail-closed on conflict;
- coordinated by Platform Core;
- authorized by Governance;
- executed only by Worker Platform;
- evidenced by Replay;
- rendered by ACLI Next only as a thin entrypoint.

## 2. Allowed Rollback Scope

Allowed operation:

```text
EXECUTE_SINGLE_GOVERNED_MUTATION_ROLLBACK
```

Initial rollback scope:

| Field | Requirement |
| --- | --- |
| Prior mutation count | Exactly one prior governed mutation. |
| Target count | Exactly one target path. |
| Mutation families | Certified new-file creation, existing-file replacement, or single-file patch-level mutation when rollback metadata exists. |
| Workspace | Allowlisted non-authority workspace only. |
| Evidence basis | Replay-reconstructed prior mutation and rollback metadata. |
| Restore basis | Complete canonical pre-mutation artifact or equivalent rollback basis recorded by Replay. |
| Current-state precondition | Current target state must match the authorized post-mutation hash from the prior mutation. |
| Execution owner | Worker Platform only. |
| Coordination owner | Platform Core only. |
| Authorization owner | Governance only. |
| Evidence owner | Replay only. |

Allowed first-version rollback actions:

| Prior Mutation Type | Rollback Action |
| --- | --- |
| New-file creation | Delete the created file only if current file hash matches the authorized created-file hash and no directory deletion is required. |
| Existing-file full replacement | Restore complete original file content only if current file hash matches the authorized post-mutation hash. |
| Single-file patch mutation | Restore complete original file content only if current file hash matches the authorized post-mutation hash. |

The first version must not roll back:

- multiple files;
- partial transaction groups;
- Git commits;
- Git branches;
- remote repository state;
- deployments;
- dependency installations;
- authority-bearing artifacts;
- provider calls;
- runtime environment changes outside the one target file.

## 3. Rollback Request Model

The rollback request is not authority. It is human or interface input routed through Platform Core to certified owners.

Required request fields:

| Field | Requirement |
| --- | --- |
| `session_id` | Existing PGSP-governed session id. |
| `turn_id` | Current governed turn id. |
| `requested_operation` | Must equal `EXECUTE_SINGLE_GOVERNED_MUTATION_ROLLBACK`. |
| `prior_execution_id` | Identifier of the prior governed mutation execution. |
| `prior_replay_reference` | Replay reference for the prior mutation. |
| `rollback_metadata_hash` | Hash of the rollback metadata emitted by the prior mutation. |
| `target_relative_path` | Target path recorded by the prior mutation metadata. |
| `operator_intent` | Human-readable reason for rollback. |
| `validation_request` | Optional validation preference; not execution authorization. |

The request must not include:

- multiple prior execution ids;
- multiple target files;
- arbitrary file content;
- ad hoc restore payloads not reconstructed through Replay;
- shell commands;
- Git commands;
- deployment instructions;
- provider invocation instructions;
- implied approval.

ACLI Next may capture the request and render summaries. It must not reconstruct Replay, authorize rollback, execute rollback, select an alternate rollback target, or synthesize missing rollback payloads.

## 4. Rollback Candidate

OCS owns rollback candidate formation.

The rollback candidate is deterministic proposal evidence, not execution authority.

Required candidate fields:

| Field | Requirement |
| --- | --- |
| `candidate_id` | Replay-visible candidate identifier. |
| `candidate_hash` | Hash over the normalized rollback candidate payload. |
| `operation` | `EXECUTE_SINGLE_GOVERNED_MUTATION_ROLLBACK`. |
| `prior_execution_id` | Prior governed mutation execution id. |
| `prior_mutation_type` | Certified mutation family. |
| `prior_replay_reference` | Replay reference used for reconstruction. |
| `rollback_metadata_hash` | Hash of the prior rollback metadata artifact. |
| `target_relative_path` | Canonical relative target path. |
| `target_workspace` | Allowlisted non-authority workspace id. |
| `authorized_current_hash` | Hash the current target must match before rollback. |
| `rollback_result_hash` | Expected hash after rollback execution. |
| `rollback_action` | One of the allowed rollback actions for the prior mutation family. |
| `canonical_restore_artifact_hash` | Hash of the complete restore artifact or deletion basis. |
| `validation_plan_ref` | Reference to proposed validation evidence or plan. |
| `prohibited_operations` | Explicit declaration of excluded operations. |

The rollback candidate must be derived from:

- Replay reconstruction of the prior mutation;
- prior rollback metadata;
- original canonical pre-mutation artifact when restoring content;
- authorized post-mutation hash when detecting conflict;
- current target path and workspace policy.

The candidate must not be derived from free-form user-provided restore content.

## 5. Preconditions

Required preconditions:

1. PGSP session exists.
2. Human rollback request is replay-visible.
3. Prior governed mutation has replay evidence.
4. Replay reconstructs the prior mutation successfully.
5. Prior mutation emitted rollback metadata.
6. Rollback metadata hash matches the request and reconstructed evidence.
7. Prior mutation target is exactly one path.
8. Target path is inside an allowlisted non-authority workspace.
9. Target path is not authority-bearing or prohibited.
10. OCS creates a rollback candidate from Replay evidence and rollback metadata.
11. Candidate declares exactly one rollback action.
12. Candidate contains authorized current-state hash and expected rollback result hash.
13. Human approval is explicit and bound to `candidate_id` and `candidate_hash`.
14. Governance authorizes the rollback candidate after validating approval and policy.
15. Replay root for the rollback turn is available and append-only.
16. Worker Platform validates Governance authorization before execution.
17. Current target state matches the candidate's authorized current-state precondition.
18. Rollback result can be validated against the expected rollback result hash.

If any precondition fails, rollback must fail closed before mutation.

## 6. Authorization Requirements

Human approval must be explicit and hash-bound.

Required approval phrase:

```text
confirm governed rollback execution <candidate_id> <candidate_hash>
```

Approval artifact must include:

- approval id;
- session id;
- turn id;
- candidate id;
- candidate hash;
- prior execution id;
- prior replay reference;
- rollback metadata hash;
- target relative path;
- rollback action;
- authorized current-state hash;
- expected rollback result hash;
- approving human identity;
- approval timestamp;
- explicit statement that approval does not authorize unrelated mutation, Git, deployment, provider invocation, or multi-file rollback.

Governance authorization must bind:

- rollback candidate hash;
- human approval hash;
- prior mutation replay reference;
- rollback metadata hash;
- authorized target path;
- authorized current-state hash;
- expected rollback result hash;
- allowed Worker Platform rollback action.

Human approval is necessary but not sufficient. Worker Platform execution requires Governance authorization.

## 7. Conflict Detection

Conflict detection is mandatory and must occur before any rollback write or deletion.

Conflict classes:

| Conflict | Detection Rule | Required Behavior |
| --- | --- | --- |
| Missing replay | Prior mutation replay reference cannot be reconstructed. | Fail closed; no rollback. |
| Missing rollback metadata | Prior mutation lacks rollback metadata. | Fail closed; no rollback. |
| Metadata mismatch | Requested rollback metadata hash differs from reconstructed metadata hash. | Fail closed; no rollback. |
| Unsupported mutation family | Prior mutation is not in the allowed family list. | Fail closed; no rollback. |
| Multi-target mutation | Prior mutation affected more than one target. | Fail closed; no rollback. |
| Path escape | Target canonical path is outside allowlisted workspace. | Fail closed; no rollback. |
| Prohibited path | Target is authority-bearing or prohibited. | Fail closed; no rollback. |
| Current hash mismatch | Current target hash differs from authorized post-mutation hash. | Fail closed; stale rollback candidate. |
| Missing created file | New-file rollback target is absent before deletion. | Fail closed; no rollback completion claim. |
| Unexpected target type | Target is symlink, directory, device, or special file. | Fail closed; no rollback. |
| Restore hash mismatch | Restored content hash differs from expected rollback result hash. | Fail closed; no completion claim. |
| Authorization mismatch | Governance authorization does not bind the candidate. | Fail closed; no rollback. |
| Replay write failure | Rollback evidence cannot be recorded. | Fail closed; no completion claim. |

The runtime must not attempt fuzzy recovery, alternate target selection, approximate matching, conflict resolution, Git reset, checkout, patch reversal from local diff, or autonomous retry.

## 8. Replay Interaction

Replay remains the evidence and reconstruction authority.

Required replay evidence:

- rollback request capture;
- prior mutation replay reference;
- prior mutation reconstruction result;
- rollback metadata reference and hash;
- rollback candidate;
- explicit human approval;
- Governance authorization;
- pre-rollback state evidence;
- Worker request;
- Worker execution result;
- post-rollback validation evidence;
- completion or fail-closed summary.

Replay must be able to reconstruct:

```text
prior mutation
-> rollback metadata
-> rollback candidate
-> approval
-> Governance authorization
-> Worker execution
-> post-rollback validation
-> completion summary
```

Rollback execution must not rewrite or erase prior mutation replay. Rollback is a new governed event appended to evidence history.

Missing Replay evidence blocks rollback completion claims.

## 9. Validation Interaction

Validation is required before completion.

Required validation checks:

| Check | Requirement |
| --- | --- |
| Prior reconstruction | Prior mutation replay reconstructs successfully. |
| Metadata binding | Rollback metadata binds to prior mutation evidence. |
| Current state | Current target hash equals authorized current-state hash before rollback. |
| Execution result | Worker-reported rollback result matches expected rollback result hash. |
| Filesystem result | Post-rollback filesystem state matches expected result. |
| Scope | No path outside the authorized target changed. |
| Prohibited operations | No Git, deployment, provider, package manager, or remote operation occurred. |

For restore rollbacks, validation operates on the complete restored file artifact. For delete-created-file rollbacks, validation records the absence of the created file and the absence hash or deletion evidence model defined by the Worker request.

Validation does not authorize rollback. It only records whether the authorized rollback completed as expected.

## 10. Rollback Execution Boundaries

Worker Platform owns rollback execution only.

Allowed Worker responsibilities:

- validate the Governance authorization record;
- validate rollback request schema;
- resolve the exact authorized target path;
- verify current target state;
- restore complete original content or delete the created file as authorized;
- verify post-rollback state;
- emit bounded execution evidence.

Worker Platform must not:

- choose rollback candidates;
- approve rollback;
- authorize rollback;
- reconstruct prior mutation Replay independently of Platform Core coordination;
- run Git;
- invoke providers;
- deploy;
- execute shell commands;
- mutate multiple files;
- modify authority artifacts;
- retry with modified inputs;
- synthesize restore content.

Platform Core coordinates the rollback flow and delegates execution to Worker Platform only after Governance authorization.

## 11. Fail-Closed Behavior

Rollback must fail closed when:

- prior Replay cannot be reconstructed;
- rollback metadata is missing or hash-mismatched;
- candidate evidence is missing;
- human approval is missing, ambiguous, or not hash-bound;
- Governance authorization is missing or does not bind the candidate;
- Worker Platform authorization validation fails;
- target path is outside allowlisted workspace;
- target path is prohibited or authority-bearing;
- current target state differs from authorized current-state hash;
- restore or deletion result does not match expected rollback result;
- validation evidence is missing;
- Replay evidence cannot be recorded;
- any stale, partial, conflicting, or ambiguous evidence is detected.

Fail-closed output must include:

- error class;
- failed checkpoint;
- prior execution id;
- prior replay reference if available;
- rollback candidate id if available;
- rollback metadata hash if available;
- statement that rollback did not complete;
- statement whether any filesystem mutation occurred;
- recommended next safe action;
- governance review route if required.

Completion must not be claimed when rollback evidence is incomplete.

## 12. ACLI Next Interaction

ACLI Next remains a thin entrypoint.

Allowed ACLI Next responsibilities:

- capture rollback request;
- display rollback candidate summary;
- capture explicit human confirmation;
- render fail-closed or completion summary returned by Platform Core;
- display Replay reference.

ACLI Next must not:

- reconstruct prior mutation Replay;
- build rollback candidates independently;
- authorize rollback;
- dispatch Workers directly;
- write files;
- run Git;
- modify rollback metadata;
- decide that rollback succeeded.

## 13. Prohibited Operations

The first governed rollback execution capability must not implement:

- multi-file rollback orchestration;
- rollback of transaction groups;
- rollback of Git commits;
- Git push, pull, fetch, branch, merge, rebase, checkout, reset, or remote interaction;
- deployment rollback;
- package manager rollback;
- provider invocation rollback;
- authority artifact rollback;
- hidden shell execution;
- autonomous retry;
- rollback based on local unverified diffs;
- rollback that rewrites Replay history.

## 14. Acceptance Criteria

Governed rollback execution is acceptable when:

1. A rollback request model exists.
2. OCS can form a deterministic rollback candidate from Replay and rollback metadata.
3. Human approval is explicit and hash-bound.
4. Governance authorization binds the rollback candidate and prior mutation evidence.
5. Worker Platform executes only the authorized rollback action.
6. Current-state hash conflict blocks rollback.
7. Replay records rollback request, candidate, approval, authorization, Worker result, validation, and completion.
8. Validation confirms post-rollback state.
9. Prior mutation Replay is append-only and not rewritten.
10. Rollback completion is fail-closed on missing, stale, partial, or conflicting evidence.
11. ACLI Next remains a thin capture/render adapter.
12. No Git remote operation, deployment rollback, provider invocation, multi-file rollback, or authority artifact mutation is introduced.

## 15. Implementation Readiness Assessment

| Area | Readiness | Notes |
| --- | --- | --- |
| Rollback metadata | Ready enough | New-file, existing-file, and patch mutation paths emit rollback metadata. |
| Replay reconstruction | Ready enough | Prior mutation replay helpers already validate mutation evidence. |
| Governance authorization | Ready pattern | Existing mutation and validation authorization patterns can be reused. |
| Worker Platform execution | Ready for minimal extension | New Worker should execute only one authorized rollback action. |
| Validation | Ready pattern | Existing mutation validation can be extended to rollback state checks. |
| ACLI Next | Ready | Thin capture/render behavior is sufficient. |
| Multi-file rollback | Not ready | Requires transaction semantics and separate certification. |
| Git/deployment rollback | Not ready | Out of scope for this capability. |

Implementation readiness: ready for smallest single-mutation rollback implementation.

## 16. Validation Strategy

Documentation-only specification validation:

```text
git diff --check
```

Future implementation validation:

- `git diff --check`;
- `python -m py_compile` for changed Python modules;
- targeted rollback runtime tests;
- replay reconstruction test;
- current-hash conflict fail-closed test;
- missing rollback metadata fail-closed test;
- unauthorized rollback fail-closed test;
- no-Git/no-deployment/no-provider assertion test.

## 17. Final Determination

The smallest governed rollback execution capability is specified.

Rollback execution should begin with exactly one prior governed mutation, exactly one target, Replay-reconstructed rollback metadata, explicit human approval, Governance authorization, Worker Platform execution, validation, and append-only Replay evidence.

Final verdict: GOVERNED_ROLLBACK_EXECUTION_SPECIFIED

## 18. Validation Evidence

Validation performed:

```text
git diff --check
```

Validation result: clean.

Final verdict: GOVERNED_ROLLBACK_EXECUTION_SPECIFIED
