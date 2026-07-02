# G11-08 Governed Git Remote Workflow Implementation V1

Status: governed Git remote workflow implemented.

Final verdict: GOVERNED_GIT_REMOTE_WORKFLOW_IMPLEMENTED

## 1. Executive Summary

G11-07 specified Git remote workflow as a bounded Worker Platform capability.

G11-08 implements the first governed Git Remote Worker without redesigning Platform Core, ACLI Next, Worker Platform, Governance, Replay, Platform Digital Twin, or Architectural Health.

Implemented scope:

- remote inspection;
- remote verification;
- branch verification;
- protected branch verification;
- fetch;
- fast-forward-only pull support;
- push;
- credential reference boundary handling;
- execution result reporting;
- failure reporting;
- Replay reconstruction.

The implementation does not authorize Git operations by itself and does not perform orchestration. Git remote execution occurs only through an authorized Worker-facing request.

## 2. Governed Development Workflow Compliance

This implementation follows:

```text
Capability Discovery
->
Existing Capability Audit
->
Reuse
->
Canonicalization
->
Minimal Extension
->
Implementation
->
Architectural Health Review
->
Architecture Review
->
Certification
```

Current phase:

```text
Implementation
```

Architecture review and certification remain future steps.

## 3. Mandatory Capability Audit

| Capability | Existing Certified State | Implementation Decision |
| --- | --- | --- |
| Platform Core | Certified orchestration authority. | Reused conceptually; no Platform Core routing code changed. |
| ACLI Next | Certified human interface. | Not modified. |
| Worker Platform | Certified bounded execution model. | Reused for Git Remote Worker request, execution, and failure boundaries. |
| Existing Worker registration | Certified worker identity pattern. | Git Remote Worker uses a canonical worker id and scope. |
| Existing Worker dispatch | Certified replay-visible dispatch model. | Not changed; implementation is Worker execution surface only. |
| Governance | Certified authorization authority. | Reused through existing authorization records. |
| Replay | Certified evidence and reconstruction authority. | Reused through immutable ordered artifacts and replay hashes. |
| Platform Digital Twin | Canonical evidence projection. | Not modified; Git Remote evidence is projection-ready. |
| Architectural Health | Deterministic advisory framework. | Not modified; implementation exposes evidence for future review. |
| Local Git runtime | Certified local commit Worker exists. | Reused design pattern; not modified or expanded. |
| Validation runtime | Certified governed validation exists. | Referenced by validation artifact hash; validation logic not duplicated. |
| Validation suites | Certified broader validation suite exists. | Not duplicated. |
| Rollback runtime | Certified rollback exists for supported repository mutations. | Recovery references recorded; no automatic remote rollback. |
| Execution runtime | Existing Worker execution patterns. | Reused. |

Audit finding:

```text
The missing behavior was bounded Git remote execution and replay evidence.
```

## 4. Implemented Runtime Surfaces

Implemented files:

- `aigol/workers/git_remote_worker.py`
- `aigol/runtime/platform_core_git_remote_governance.py`
- `tests/test_g11_governed_git_remote_worker.py`

The implementation provides:

- Governance authorization helper for the Git Remote Worker;
- Worker-facing authorized request creation;
- request validation;
- remote URL fingerprint verification;
- branch verification;
- expected local and remote `HEAD` verification;
- protected branch authorization check;
- credential reference evidence without credential replay;
- bounded Git execution using argument vectors and `shell=False`;
- ordered Worker replay artifacts;
- deterministic replay reconstruction;
- targeted tests using local temporary Git remotes.

## 5. Git Remote Worker Identity

Canonical Worker id:

```text
GOVERNED_GIT_REMOTE_WORKER
```

Canonical authorization scope:

```text
BOUNDED_GIT_REMOTE_OPERATION
```

Supported operations:

- `REMOTE_INSPECTION`
- `FETCH`
- `PULL`
- `PUSH`

The Worker does not support:

- arbitrary shell commands;
- raw Git commands;
- merge operations;
- rebase operations;
- force push;
- tag operations;
- deployment;
- provider invocation;
- Replay mutation;
- orchestration requests.

## 6. Governance Integration

Governance integration is implemented by:

```text
aigol/runtime/platform_core_git_remote_governance.py
```

The helper creates a standard governed authorization record bound to:

- Worker id: `GOVERNED_GIT_REMOTE_WORKER`
- scope: `BOUNDED_GIT_REMOTE_OPERATION`

Worker request creation requires a valid authorization record.

Protected branches require explicit protected branch authorization before request creation succeeds.

The Worker does not approve or authorize itself.

## 7. Replay Integration

The Git Remote Worker records three ordered replay steps:

| Step | Evidence |
| --- | --- |
| 0 | Authorized Git remote request. |
| 1 | Git remote pre-state. |
| 2 | Git remote execution result or fail-closed result. |

Replay captures:

- requested operation;
- authorization id and hash;
- repository id;
- remote name;
- remote URL fingerprint;
- local branch;
- remote branch;
- expected local and remote state;
- credential reference;
- validation artifact hash;
- rollback reference;
- execution argv hash;
- bounded stdout and stderr;
- exit code;
- local and remote post-state;
- failure reason when fail-closed.

Replay reconstruction is provided by:

```text
reconstruct_git_remote_worker_replay
```

## 8. Validation Integration

The Git Remote Worker does not duplicate validation logic.

Validation integration is represented by:

- required `validation_artifact_hash` on the authorized request;
- pre-operation branch and remote verification;
- working tree cleanliness requirement for pull and push;
- replay-visible result evidence for post-operation validation.

Future Platform Core coordination should bind the `validation_artifact_hash` to governed validation suite evidence before dispatching the Worker.

## 9. Rollback And Recovery Integration

The implementation records a `rollback_reference` on the authorized request.

The Worker does not:

- automatically reset;
- automatically force push;
- automatically delete branches;
- automatically revert remote state;
- execute recovery without separate authorization.

Remote recovery remains a future separately governed capability.

## 10. Authentication Boundary

The Worker records:

- credential reference;
- credential value not recorded;
- credential hash not recorded.

Credential values are never printed or persisted by the Worker.

The first implementation supports local temporary remotes in tests without network credentials.

## 11. Responsibility Verification

| Component | Verification |
| --- | --- |
| ACLI Next | Not modified. |
| Platform Core | Not modified; orchestration remains outside Worker. |
| Worker Platform | Owns Git remote execution surface. |
| Governance | Owns authorization record creation. |
| Replay | Owns ordered evidence and reconstruction. |
| Platform Digital Twin | Not modified; evidence remains projection-ready. |
| Architectural Health | Not modified; future review can consume replay evidence. |
| Git Remote Worker | Executes exact authorized Git operation only. |

Responsibility verification result:

```text
No responsibility movement detected.
```

## 12. Targeted Tests

Targeted tests verify:

- governed push to a local bare remote;
- replay reconstruction;
- remote inspection without remote mutation;
- fetch without remote mutation;
- protected branch request fail-closed behavior;
- forbidden request surface rejection;
- Governance authorization scope binding.

The tests use local temporary Git remotes and do not require network access.

## 13. Final Determination

Governed Git remote workflow has been implemented as a bounded Worker Platform capability.

The implementation preserves Platform Core orchestration, Governance authorization, Replay evidence, ACLI Next thin-interface boundaries, and Worker Platform execution ownership.

Final verdict: GOVERNED_GIT_REMOTE_WORKFLOW_IMPLEMENTED

## 14. Validation Evidence

Validation performed:

```text
git diff --check
python -m py_compile aigol/workers/git_remote_worker.py aigol/runtime/platform_core_git_remote_governance.py
python -m pytest tests/test_g11_governed_git_remote_worker.py tests/test_g8_governed_git_commit_runtime.py tests/test_worker_runtime_v1.py
```

Validation result: clean.

Final verdict: GOVERNED_GIT_REMOTE_WORKFLOW_IMPLEMENTED
