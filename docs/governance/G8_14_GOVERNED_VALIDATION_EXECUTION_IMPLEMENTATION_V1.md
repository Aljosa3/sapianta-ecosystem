# G8-14 Governed Validation Execution Implementation V1

Status: governed validation execution implemented.

Final verdict: GOVERNED_VALIDATION_EXECUTION_IMPLEMENTED

## 1. Executive Summary

G8-14 implements the smallest governed validation execution capability specified by G8-13.

The implemented operation is:

```text
RUN_SINGLE_ALLOWLISTED_VALIDATION_COMMAND
```

The implementation supports only:

- one allowlisted validation command per execution;
- fixed argv from a static allowlist;
- non-shell execution;
- timeout-bound execution;
- bounded stdout/stderr capture;
- explicit human approval;
- Governance authorization;
- Worker Platform execution;
- Replay evidence generation;
- validation result normalization;
- fail-closed behavior.

The implementation does not add Git, commits, deployment, provider invocation, package installation, network access, arbitrary shell execution, or ACLI Next authority.

## 2. Implemented Runtime Surfaces

Files added:

- `aigol/runtime/platform_core_validation_allowlist.py`
- `aigol/runtime/platform_core_validation_candidate.py`
- `aigol/runtime/platform_core_validation_governance.py`
- `aigol/runtime/platform_core_validation_result.py`
- `aigol/runtime/platform_core_validation_replay.py`
- `aigol/runtime/governed_validation_runtime.py`
- `aigol/workers/validation_command_worker.py`
- `tests/test_g8_governed_validation_runtime.py`

The implementation follows the certified Platform Core ownership model:

- OCS-shaped helper owns validation candidate artifacts.
- Governance-shaped helper owns approval and authorization artifacts.
- Worker Platform owns validation command execution.
- Replay helper owns evidence persistence and reconstruction.
- Result helper owns validation result normalization.
- Runtime coordinator owns only workflow sequencing and completion capture.

## 3. Validation Scope

Allowed validation execution:

| Field | Implemented behavior |
| --- | --- |
| Command count | Exactly one. |
| Command source | Static allowlist. |
| Arguments | Exact argv vector from allowlist. |
| Shell | Not used. |
| Timeout | Required and enforced by Worker. |
| Output capture | stdout/stderr captured with hashes and bounded excerpts. |
| Exit code | Captured exactly. |
| Git | Not performed. |
| Commit | Not created. |
| Deployment | Not performed. |
| Provider | Not invoked. |
| Package install | Not performed. |
| Network | Not authorized. |

Implemented allowlist entries:

- `PY_COMPILE_G8_VALIDATION_TARGETS`
- `PYTHON_VALIDATION_FAILS_FOR_TEST`
- `PYTHON_VALIDATION_TIMEOUT_FOR_TEST`

The latter two exist to certify failure and timeout behavior.

## 4. Governance Integration

Human approval is explicit and candidate-hash-bound:

```text
confirm validation <candidate_id> <candidate_hash>
```

Governance authorization uses the existing authorization record implementation and authorizes only:

```text
RUN_ALLOWLISTED_VALIDATION_COMMAND
```

Approval and authorization artifacts explicitly do not authorize:

- Git;
- commits;
- deployment;
- provider invocation;
- package installation;
- network access;
- additional Worker dispatch.

Human approval remains admissibility evidence. It does not authorize execution by itself.

## 5. Worker Platform Integration

The Worker Platform integration is implemented by:

```text
aigol/workers/validation_command_worker.py
```

The Worker:

1. validates request schema;
2. validates Governance authorization;
3. validates command id against the allowlist;
4. resolves exact argv;
5. rejects shell execution;
6. validates working directory containment;
7. executes the command with timeout;
8. captures exit code;
9. captures stdout and stderr hashes;
10. records bounded stdout and stderr excerpts;
11. records timeout and validation status;
12. records Worker-side replay evidence.

The Worker does not choose commands, authorize itself, run Git, create commits, deploy, call providers, install packages, or dispatch other Workers.

## 6. Replay Integration

Replay evidence records eight ordered artifacts:

| Index | Artifact |
| --- | --- |
| 0 | Validation candidate |
| 1 | Human approval |
| 2 | Governance authorization |
| 3 | Worker request |
| 4 | Pre-execution state |
| 5 | Worker result |
| 6 | Validation result |
| 7 | Completion summary |

Replay reconstruction verifies:

- wrapper ordering;
- wrapper hashes;
- artifact hashes;
- candidate-to-approval continuity;
- authorization-to-candidate continuity;
- Worker request-to-authorization continuity;
- command id and argv hash continuity;
- Worker result-to-validation result continuity;
- completion linkage.

Missing or conflicting replay evidence blocks success claims.

## 7. Validation Result Recording

Validation result status values implemented:

| Status | Meaning |
| --- | --- |
| `VALIDATION_PASSED` | Command exited with expected exit code. |
| `VALIDATION_FAILED` | Command completed with non-success exit code. |
| `VALIDATION_TIMED_OUT` | Command exceeded authorized timeout. |
| `VALIDATION_BLOCKED` | Preconditions failed before execution. |

The result artifact records:

- command id;
- argv hash;
- exit code;
- timed-out flag;
- stdout hash;
- stderr hash;
- bounded stdout excerpt;
- bounded stderr excerpt;
- truncation flags;
- Worker replay hash;
- prohibited-operation flags set to false.

Validation result recording does not certify release readiness by itself.

## 8. Failure And Timeout Handling

Fail-closed behavior is implemented for:

- unallowlisted command id;
- missing approval;
- unbound confirmation phrase;
- missing or invalid authorization;
- working directory escape;
- replay artifact collision;
- Worker request mismatch;
- Worker execution exception.

Timeout behavior is implemented as a validation result:

```text
VALIDATION_TIMED_OUT
```

Non-zero command exit is implemented as:

```text
VALIDATION_FAILED
```

Non-zero exit is not treated as infrastructure failure.

## 9. Architecture Review

The implementation preserves certified boundaries:

| Boundary | Result |
| --- | --- |
| ACLI Next | No new local validation execution authority. |
| Platform Core | Coordinates validation workflow through a thin runtime coordinator. |
| OCS | Owns validation candidate artifacts. |
| Governance | Owns approval and authorization artifacts. |
| Worker Platform | Owns command execution. |
| Replay | Owns evidence persistence and reconstruction. |
| Validation result | Owns result normalization, not Governance decisions. |

No new authority layer was introduced.

## 10. Targeted Tests

Targeted tests cover:

- successful allowlisted validation execution;
- replay reconstruction;
- non-zero exit recorded as `VALIDATION_FAILED`;
- timeout recorded as `VALIDATION_TIMED_OUT`;
- missing approval fail-closed behavior;
- unbound confirmation rejection;
- unallowlisted command rejection;
- no shell, Git, commit, deployment, provider surface.

Regression tests for existing-file mutation and first mutating Worker remain passing.

## 11. Validation Evidence

Validation performed:

```text
git diff --check
python -m py_compile aigol/workers/validation_command_worker.py aigol/runtime/governed_validation_runtime.py aigol/runtime/platform_core_validation_allowlist.py aigol/runtime/platform_core_validation_candidate.py aigol/runtime/platform_core_validation_governance.py aigol/runtime/platform_core_validation_result.py aigol/runtime/platform_core_validation_replay.py tests/test_g8_governed_validation_runtime.py
python -m pytest tests/test_g8_governed_validation_runtime.py tests/test_g8_existing_file_mutation_runtime.py tests/test_g8_first_mutating_worker_runtime.py tests/test_repository_mutation_worker_runtime_v1.py
```

Validation result:

```text
29 passed
```

## 12. Final Determination

The smallest governed validation execution capability has been implemented.

Validation execution is allowlisted, non-shell, timeout-bound, replay-visible, Governance-authorized, Worker-executed, and bounded to validation result evidence.

Final verdict: GOVERNED_VALIDATION_EXECUTION_IMPLEMENTED
