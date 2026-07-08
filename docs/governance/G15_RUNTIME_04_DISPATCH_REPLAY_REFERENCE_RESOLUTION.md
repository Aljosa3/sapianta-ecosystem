# G15-RUNTIME-04 - Dispatch Replay Reference Resolution

Status: implemented.

Milestone: Generation 15 runtime replay reference resolution.

Scope: deterministic correction to Worker Invocation to Execution Candidate replay reference resolution. No replay certification semantics, governance semantics, worker ownership, Human Interface behavior, approval behavior, or provider behavior were changed.

## 1. Knowledge Reuse Audit

This milestone reused the existing Platform Core runtime and replay lineage path.

Reused components:

- `aigol/runtime/worker_invocation_to_execution_candidate_bridge_runtime.py`
  - Existing owner of Worker Invocation to Execution Candidate replay reconstruction.
  - Existing `_resolve_replay_reference` helper reused as the single resolution boundary.
- `aigol/runtime/worker_dispatch_runtime.py`
  - Existing owner of Worker Dispatch replay artifacts, including `000_dispatch_evidence_recorded.json`.
- `aigol/runtime/worker_invocation_runtime.py`
  - Existing owner of Worker Invocation artifacts and invocation evidence containing `worker_dispatch_replay_reference`.
- `aigol/runtime/result_validation_runtime.py`
  - Existing downstream owner of governed execution result validation and replay certification readiness.
- `aigol/runtime/replay_certification_runtime.py`
  - Existing downstream owner of replay certification.
- `tests/test_worker_invocation_to_execution_candidate_bridge_runtime_v1.py`
  - Existing bridge test surface extended with a repository-relative `.runtime/...` replay reference regression.

No alternate replay path, duplicate replay certification mechanism, duplicate worker dispatch lookup, or Human Interface-owned replay logic was introduced.

## 2. Architectural Review

The architectural owner of this correction is Platform Core, specifically the Worker Invocation to Execution Candidate bridge.

The bridge reconstructs replay lineage in this order:

1. Worker invocation replay.
2. Worker dispatch replay.
3. Worker assignment replay.
4. Worker invocation request replay.
5. Execution authorization replay.
6. Execution-ready dry-run replay.

The failure identified by G15-REPLAY-01 occurred at step 2. The dispatch evidence existed, but the replay reference was repository-relative and was resolved as if it were relative to the invocation replay directory.

The correction keeps responsibilities unchanged:

- Worker Dispatch continues to produce dispatch replay evidence.
- Worker Invocation continues to record the dispatch replay reference.
- The execution-candidate bridge continues to reconstruct lineage.
- Result Validation remains downstream.
- Replay Certification remains downstream and unchanged.
- AiCLI remains outside replay lineage ownership.

## 3. Replay Reference Resolution Review

Previous behavior:

- Absolute replay references resolved directly.
- All non-absolute replay references resolved relative to `anchor.parent`.
- Repository-relative references such as `.runtime/aicli/.../worker_dispatch` were therefore resolved under the invocation replay directory parent.
- That produced duplicated path construction and failed lookup of `000_dispatch_evidence_recorded.json`.

Corrected behavior:

- Absolute replay references still resolve directly.
- Repository-relative runtime references beginning with `.runtime` or `runtime` resolve from the process working directory.
- Other relative references continue to resolve relative to `anchor.parent`.

This preserves existing anchor-relative behavior while adding deterministic handling for repository-relative runtime replay references.

Fail-closed behavior is preserved. If the resolved repository-relative path does not contain valid replay artifacts, existing `load_json`, wrapper hash validation, artifact hash validation, and bridge failure capture still fail closed.

## 4. Implementation Summary

Modified `_resolve_replay_reference` in `aigol/runtime/worker_invocation_to_execution_candidate_bridge_runtime.py`.

The helper now treats replay references whose first path part is `.runtime` or `runtime` as repository-relative replay references and resolves them from the current working directory. It leaves absolute paths and existing anchor-relative paths unchanged.

Added a regression test in `tests/test_worker_invocation_to_execution_candidate_bridge_runtime_v1.py`.

The test builds a relative `.runtime/aicli/.../worker_lifecycle_continuation` replay chain, invokes a worker, and verifies that the execution-candidate bridge:

- resolves the repository-relative dispatch replay reference,
- generates the execution candidate,
- preserves replay lineage,
- carries dispatch source identity,
- records replay references and replay hashes.

## 5. Validation Summary

Validation commands required:

- `python -m py_compile`
- `python -m pytest -q`
- `git diff --check`

Validation results:

- Focused regression: `python -m pytest tests/test_worker_invocation_to_execution_candidate_bridge_runtime_v1.py -q` passed: `3 passed in 0.30s`.
- `python -m py_compile aigol/runtime/worker_invocation_to_execution_candidate_bridge_runtime.py tests/test_worker_invocation_to_execution_candidate_bridge_runtime_v1.py aigol/runtime/worker_dispatch_runtime.py aigol/runtime/worker_invocation_runtime.py aigol/runtime/replay_certification_runtime.py` passed.
- Full regression: `python -m pytest -q` passed: `5823 passed, 4 skipped in 140.49s`.
- `git diff --check` passed.

## 6. Regression Test Summary

New regression:

- `test_worker_invocation_bridge_resolves_repository_relative_dispatch_replay_reference`

Regression purpose:

- Reproduce the `.runtime/aicli/.../worker_dispatch` replay reference shape observed in runtime evidence.
- Prove the bridge no longer constructs a duplicated repository-relative path.
- Prove execution-candidate generation can proceed with replay lineage preserved.

Existing regression coverage remains active:

- Bridge succeeds with valid invocation replay lineage.
- Bridge fails closed without explicit human approval.
- Replay certification remains separately tested and unchanged.

## 7. Files Modified

Production:

- `aigol/runtime/worker_invocation_to_execution_candidate_bridge_runtime.py`

Tests:

- `tests/test_worker_invocation_to_execution_candidate_bridge_runtime_v1.py`

Governance:

- `docs/governance/G15_RUNTIME_04_DISPATCH_REPLAY_REFERENCE_RESOLUTION.md`

## 8. Boundary Confirmation

No Human Interface behavior changed.

No AiCLI replay ownership was introduced.

No replay certification semantics changed.

No governance semantics changed.

No worker ownership changed.

No provider behavior changed.

No alternate replay path was introduced.

Platform Core remains the owner of replay lineage reconstruction, result validation, replay certification, runtime continuation, and fail-closed behavior.

## 9. Governance Report

Governance classification:

`DISPATCH_REPLAY_REFERENCE_RESOLUTION_RESTORED`

Prior stopping condition:

`runtime artifact missing: 000_dispatch_evidence_recorded.json`

Corrected condition:

Repository-relative `.runtime/...` dispatch replay references resolve to the existing dispatch replay artifact instead of being nested under the invocation replay directory parent.

Replay certification ownership:

Preserved. This milestone does not alter `aigol/runtime/replay_certification_runtime.py`.

Replay lineage:

Preserved. The bridge can now reconstruct the existing dispatch replay artifact from the recorded invocation evidence and continue toward downstream runtime stages using existing lineage gates.

Fail-closed posture:

Preserved. Invalid references, missing artifacts, invalid wrappers, hash mismatches, approval failures, and invalid lineage still fail closed through the existing bridge behavior.

Generation 14 architectural invariants remain unchanged.
