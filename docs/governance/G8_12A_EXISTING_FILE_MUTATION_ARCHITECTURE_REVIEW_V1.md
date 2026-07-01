# G8-12A Existing File Mutation Architecture Review V1

Status: existing file mutation architecture confirmed.

Final verdict: EXISTING_FILE_MUTATION_ARCHITECTURE_CONFIRMED

## 1. Executive Summary

G8-12A reviews the existing-file mutation implementation introduced by G8-12.

The implementation preserves the certified Platform Core ownership model:

- ACLI Next remains a thin entrypoint.
- Platform Core coordinates the mutation workflow.
- OCS owns mutation candidate artifacts.
- Governance owns approval and authorization artifacts.
- Worker Platform owns file mutation execution.
- Replay owns evidence persistence and reconstruction.
- Validation owns pre- and post-mutation checks.
- Rollback metadata is generated as evidence only and does not execute rollback.

No new authority layer was introduced.

No responsibility leakage requiring architectural realignment was detected.

## 2. Review Scope

Reviewed implementation surfaces:

- `aigol/runtime/existing_file_mutation_runtime.py`
- `aigol/workers/filesystem_replace_worker.py`
- `aigol/runtime/platform_core_existing_file_mutation_candidate.py`
- `aigol/runtime/platform_core_existing_file_governance.py`
- `aigol/runtime/platform_core_existing_file_replay.py`
- `aigol/runtime/platform_core_existing_file_validation.py`
- `aigol/runtime/platform_core_existing_file_rollback.py`
- `tests/test_g8_existing_file_mutation_runtime.py`
- `docs/governance/G8_12_EXISTING_FILE_MUTATION_IMPLEMENTATION_V1.md`

Reviewed lineage:

- G8-11 existing-file mutation specification;
- G8-12 existing-file mutation implementation;
- G8-09B mutation runtime responsibility realignment;
- G8-09C first mutating Worker certification.

## 3. Ownership Matrix

| Responsibility | Certified owner | Implementation location | Review result |
| --- | --- | --- | --- |
| Workflow coordination | Platform Core coordinator | `existing_file_mutation_runtime.py` | Confirmed. Coordinates delegated services only. |
| Candidate creation | OCS | `platform_core_existing_file_mutation_candidate.py` | Confirmed. Candidate construction is outside coordinator and ACLI Next. |
| Candidate validation | OCS | `platform_core_existing_file_mutation_candidate.py` | Confirmed. Validates scope, flags, path, and replacement hash. |
| Human approval | Governance | `platform_core_existing_file_governance.py` | Confirmed. Approval is explicit and candidate-hash-bound. |
| Authorization creation | Governance | `platform_core_existing_file_governance.py` | Confirmed. Reuses existing authorization record implementation. |
| Worker request validation | Worker Platform | `filesystem_replace_worker.py` | Confirmed. Worker validates request and authorization before execution. |
| File replacement execution | Worker Platform | `filesystem_replace_worker.py` | Confirmed. Worker performs the only repository mutation. |
| Replay persistence | Replay | `platform_core_existing_file_replay.py` | Confirmed. Replay helper owns append-only writes and wrapper hashes. |
| Replay reconstruction | Replay | `platform_core_existing_file_replay.py` and Worker replay API | Confirmed. Reconstruction is outside coordinator. |
| Pre/post validation | Validation capability | `platform_core_existing_file_validation.py` | Confirmed. Hash and path checks are delegated. |
| Rollback metadata | Rollback metadata capability | `platform_core_existing_file_rollback.py` | Confirmed. Metadata only, no rollback execution. |
| Human interface | ACLI Next | No new ACLI mutation code | Confirmed. ACLI Next remains thin. |

## 4. Existing-File Mutation Coordinator Review

The coordinator performs only sequence coordination:

1. validate OCS candidate;
2. validate Governance approval;
3. resolve repository and allowlisted workspace through validation helpers;
4. collect pre-mutation validation evidence;
5. request Governance authorization;
6. create Worker request through Worker Platform API;
7. persist Replay evidence through Replay helper;
8. invoke Worker Platform execution;
9. request post-mutation validation;
10. request rollback metadata;
11. assemble completion capture.

The coordinator does not:

- create authorization records directly;
- persist replay JSON directly;
- reconstruct replay directly;
- perform file writes directly;
- validate request authority itself;
- call providers;
- run Git;
- create commits;
- deploy;
- mutate multiple files.

Coordinator boundary: confirmed.

## 5. Filesystem Replace Worker Review

The filesystem replace Worker owns execution only.

Worker responsibilities are bounded to:

- validate an authorized replace request;
- validate authorization record scope and Worker id;
- validate target path containment;
- validate target exists and is a regular file;
- read current plaintext content;
- compute and compare pre-mutation hash;
- replace file content;
- verify post-mutation hash;
- record Worker-side replay evidence.

The Worker does not:

- create candidates;
- authorize itself;
- own Governance decisions;
- own Platform Core orchestration;
- own provider invocation;
- run shell commands;
- run Git;
- create commits;
- deploy;
- dispatch additional Workers.

Worker Platform execution boundary: confirmed.

## 6. OCS Candidate Handling Review

Candidate handling is isolated in `platform_core_existing_file_mutation_candidate.py`.

The candidate artifact records:

- operation;
- Worker id and scope;
- allowlisted workspace;
- target path;
- expected pre-mutation hash;
- replacement content hash;
- single-file and full-replacement constraints;
- explicit false flags for Git, commit, deployment, provider invocation, and additional Worker dispatch.

OCS responsibility is represented without granting execution authority.

OCS boundary: confirmed.

## 7. Governance Review

Governance owns:

- explicit human approval artifact;
- candidate-hash-bound confirmation phrase;
- validation of approval continuity;
- authorization record creation;
- authorization record validation through the existing authorization implementation.

Approval is not treated as execution authorization by itself.

The authorization scope is limited to:

```text
FILESYSTEM_REPLACE_EXISTING_TEXT_FILE
```

Governance boundary: confirmed.

## 8. Replay Review

Replay owns mutation evidence persistence and reconstruction.

The Replay helper records nine ordered artifacts:

- mutation candidate;
- human approval;
- Governance authorization;
- Worker request;
- pre-mutation state;
- Worker result;
- post-mutation validation;
- rollback metadata;
- completion summary.

Replay reconstruction verifies:

- replay ordering;
- wrapper hashes;
- artifact hashes;
- candidate/approval continuity;
- authorization continuity;
- Worker request continuity;
- pre-hash continuity;
- Worker old/new hash continuity;
- validation status;
- rollback original hash;
- completion linkage.

Replay boundary: confirmed.

## 9. Validation Review

Validation is delegated to `platform_core_existing_file_validation.py`.

Validation confirms:

- target remains inside the allowlisted workspace;
- target exists before mutation;
- target is a regular UTF-8 plaintext file;
- pre-mutation hash matches the candidate;
- post-mutation hash matches the replacement content;
- Worker old/new hashes match candidate expectations;
- exactly one file was mutated;
- no Git, commit, deployment, or provider invocation occurred.

Validation boundary: confirmed.

## 10. Rollback Metadata Review

Rollback metadata is delegated to `platform_core_existing_file_rollback.py`.

The rollback artifact records:

- target path;
- original content hash;
- authorized post-mutation hash;
- rollback operation description;
- rollback authorization requirement;
- automatic rollback prohibition;
- delete-file and delete-directory prohibitions.

Rollback execution is not implemented.

Rollback metadata boundary: confirmed.

## 11. ACLI Next Thin Entrypoint Review

G8-12 does not add ACLI Next mutation authority.

ACLI Next remains allowed to:

- capture requests;
- render summaries;
- capture explicit confirmation;
- present replay identifiers.

ACLI Next still must not:

- compute candidates;
- authorize mutation;
- construct Worker requests;
- write files;
- own Replay;
- run Git;
- invoke providers.

Thin entrypoint boundary: confirmed.

## 12. Authority And Prohibited Surface Review

The implementation explicitly preserves:

- no provider invocation;
- no Git operation;
- no commit creation;
- no deployment;
- no multi-file mutation;
- no arbitrary shell execution;
- no ACLI Next execution authority;
- no Worker self-authorization;
- no Governance execution;
- no Replay authorization.

No new authority layer was detected.

## 13. Architectural Risks

Residual risks are bounded and should be watched in future phases:

| Risk | Mitigation |
| --- | --- |
| Coordinator grows into orchestration owner | Keep OCS candidate formation and Worker selection outside the coordinator. |
| Worker gains planning behavior | Worker APIs must continue accepting only authorized requests. |
| Validation expands into Governance | Validation may produce evidence but must not decide admissibility. |
| Replay helper becomes policy authority | Replay must reconstruct and verify evidence, not authorize execution. |
| ACLI Next adds local mutation UX logic | ACLI Next should delegate all mutation behavior to Platform Core. |
| Future patch support becomes broad editing engine too early | Specify and certify narrowly before any patch-based mutation. |

No immediate refactoring is required.

## 14. Recommendations

Recommended next steps:

- certify the existing-file mutation implementation after this architecture review;
- add a focused certification review before broadening mutation scope;
- keep rollback execution separate from rollback metadata;
- specify governed validation-command execution as the next practical workflow bridge;
- keep Git and commit capabilities out of mutation Workers until separately specified.

## 15. Validation Evidence

Validation performed:

```text
git diff --check
```

Prior implementation validation retained as review evidence:

```text
python -m py_compile aigol/workers/filesystem_replace_worker.py aigol/runtime/existing_file_mutation_runtime.py aigol/runtime/platform_core_existing_file_mutation_candidate.py aigol/runtime/platform_core_existing_file_governance.py aigol/runtime/platform_core_existing_file_validation.py aigol/runtime/platform_core_existing_file_rollback.py aigol/runtime/platform_core_existing_file_replay.py tests/test_g8_existing_file_mutation_runtime.py
python -m pytest tests/test_g8_existing_file_mutation_runtime.py tests/test_g8_first_mutating_worker_runtime.py tests/test_repository_mutation_worker_runtime_v1.py
```

Validation result:

```text
22 passed
```

## 16. Final Determination

The existing-file mutation implementation preserves certified Platform Core ownership boundaries.

Worker Platform owns execution only, Platform Core coordinates, Governance remains authority, Replay remains the evidence system, and ACLI Next remains a thin entrypoint.

Final verdict: EXISTING_FILE_MUTATION_ARCHITECTURE_CONFIRMED
