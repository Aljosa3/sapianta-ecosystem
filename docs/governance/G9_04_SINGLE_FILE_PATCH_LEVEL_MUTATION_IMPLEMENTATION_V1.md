# G9-04 Single File Patch-Level Mutation Implementation V1

Status: single-file patch-level mutation implemented.

Final verdict: SINGLE_FILE_PATCH_LEVEL_MUTATION_IMPLEMENTED

## 1. Executive Summary

G9-04 implements the governed single-file patch-level mutation specified by G9-03 and constrained by G9-03A.

The implementation supports only:

- one existing plaintext file;
- one exact context-bound replacement;
- exactly-once old text matching;
- pre-hash verification;
- deterministic construction of the complete resulting file;
- post-hash verification;
- explicit human approval;
- Governance authorization;
- Worker Platform execution;
- Replay evidence;
- rollback metadata;
- validation interaction;
- fail-closed behavior.

Patch form remains intent-level and candidate-level. The canonical execution artifact remains the complete resulting file.

## 2. Implemented Runtime Surfaces

| Surface | File | Ownership |
| --- | --- | --- |
| OCS patch candidate helper | `aigol/runtime/platform_core_patch_mutation_candidate.py` | OCS candidate formation. |
| Governance approval and authorization helper | `aigol/runtime/platform_core_patch_mutation_governance.py` | Governance approval and authorization. |
| Patch Worker | `aigol/workers/filesystem_patch_worker.py` | Worker Platform execution only. |
| Replay helper | `aigol/runtime/platform_core_patch_mutation_replay.py` | Replay evidence and reconstruction. |
| Validation helper | `aigol/runtime/platform_core_patch_mutation_validation.py` | Complete-artifact validation evidence. |
| Rollback metadata helper | `aigol/runtime/platform_core_patch_mutation_rollback.py` | Rollback-ready metadata only. |
| Platform Core coordinator | `aigol/runtime/single_file_patch_mutation_runtime.py` | Thin coordination over certified owners. |
| Targeted tests | `tests/test_g9_single_file_patch_mutation_runtime.py` | Runtime boundary and fail-closed coverage. |

## 3. Canonical Artifact Preservation

The implementation preserves the G9-03A determination:

```text
Patch-level mutation is intent-only.
The complete resulting file is the canonical execution artifact.
```

The Worker constructs the complete resulting file before writing and verifies its hash against the authorized expected post-hash. Replay and validation record complete resulting file evidence.

## 4. Prohibited Operations

The implementation does not support:

- multi-file patching;
- multiple hunks;
- arbitrary search/replace;
- regular expressions;
- fuzzy matching;
- Git operations;
- commits;
- deployment;
- provider invocation;
- package installation;
- additional Worker dispatch.

## 5. Validation Evidence

Validation performed:

```text
git diff --check
python -m py_compile aigol/workers/filesystem_patch_worker.py aigol/runtime/platform_core_patch_mutation_candidate.py aigol/runtime/platform_core_patch_mutation_governance.py aigol/runtime/platform_core_patch_mutation_validation.py aigol/runtime/platform_core_patch_mutation_rollback.py aigol/runtime/platform_core_patch_mutation_replay.py aigol/runtime/single_file_patch_mutation_runtime.py
python -m pytest tests/test_g9_single_file_patch_mutation_runtime.py
```

Validation result: clean.

Final verdict: SINGLE_FILE_PATCH_LEVEL_MUTATION_IMPLEMENTED
