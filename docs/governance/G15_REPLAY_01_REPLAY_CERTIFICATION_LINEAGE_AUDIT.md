# G15-REPLAY-01 - Replay Certification Lineage Audit

Status: audit complete.

Milestone: Generation 15 replay certification lineage audit.

Scope: audit only. No production code, runtime behavior, AiCLI behavior, replay semantics, governance semantics, provider behavior, worker behavior, or certification behavior is changed by this artifact.

## 1. Knowledge Reuse Audit

This audit reused the existing Generation 14 and Generation 15 runtime path instead of introducing a parallel certification model.

Reused Platform Core runtime components:

- `aigol/cli/aigol_cli.py::_continue_worker_request_to_replay_certification`
  - Owns the runtime continuation sequence from worker request through replay certification.
  - Calls worker assignment, worker dispatch, worker invocation, execution-candidate bridge, external worker task packaging, provider adapter, external result acceptance, result validation, and replay certification.
- `aigol/runtime/worker_invocation_to_execution_candidate_bridge_runtime.py`
  - Owns reconstruction of worker invocation replay lineage before a governed worker execution candidate can be created.
  - Validates invocation, dispatch, assignment, worker request, authorization, and dry-run candidate lineage.
- `aigol/runtime/result_validation_runtime.py`
  - Owns deterministic validation of completed governed worker execution results.
  - Requires completed worker execution, preserved replay lineage, replay references, replay hashes, validation evidence, and fail-closed preservation before certification readiness.
- `aigol/runtime/replay_certification_runtime.py`
  - Owns replay certification for validated execution results.
  - Requires a completed `RESULT_VALIDATION_ARTIFACT_V1` with `ready_for_replay_certification`, preserved replay lineage, fail-closed evidence, deterministic validation, replay references, replay hashes, and validation evidence.
- `.runtime/aicli/AICLI-REFERENCE-SESSION/TURN-000010/certified_development_continuation/worker_lifecycle_continuation`
  - Supplies observed replay evidence for assignment, dispatch, invocation, and execution-candidate bridge stopping condition.
- `tests/test_replay_certification_runtime_v1.py`
  - Proves replay certification completes when result validation is valid and fails closed when readiness or artifact type is invalid.
- `tests/test_result_validation_runtime_v1.py`
  - Proves result validation gates replay certification readiness on governed execution result lineage.
- `tests/test_worker_invocation_to_execution_candidate_bridge_runtime_v1.py`
  - Proves the invocation-to-execution-candidate bridge succeeds when replay lineage is reconstructable and fails closed when prerequisites are invalid.

No duplicate replay certification, replay-lineage, runtime certification, worker invocation, dispatch, or governance evidence logic was created.

## 2. Architectural Review

Replay certification is not the first component after worker invocation. The Platform Core runtime path is staged:

1. Worker invocation request is created after governed execution authorization.
2. Worker assignment is recorded.
3. Worker dispatch is recorded.
4. Worker invocation is recorded.
5. Worker invocation is bridged into a governed worker execution candidate.
6. External worker task packaging is prepared.
7. External worker provider adapter is invoked.
8. External worker result package is accepted.
9. Governed execution result is validated.
10. Validated replay is certified.

The replay certification owner is `aigol/runtime/replay_certification_runtime.py`.

The runtime continuation caller is `aigol/cli/aigol_cli.py::_continue_worker_request_to_replay_certification`.

The replay-lineage prerequisite immediately blocking certification is upstream of replay certification. It occurs in `aigol/runtime/worker_invocation_to_execution_candidate_bridge_runtime.py::_load_invocation_lineage`, before result validation and before replay certification can be reached.

Generation 14 ownership boundaries remain intact:

- Platform Core owns runtime continuation, replay lineage, result validation, replay certification, governance evidence, and fail-closed behavior.
- Worker runtime stages own worker assignment, dispatch, and invocation artifacts.
- AiCLI remains outside this audit scope and does not own replay certification, replay lineage, provider invocation, worker execution, approval semantics, or runtime orchestration.

## 3. Replay Certification Analysis

Replay certification is implemented as a deterministic Platform Core runtime in `aigol/runtime/replay_certification_runtime.py`.

The certification entrypoint is `certify_validated_replay`.

Certification is allowed only when all of these prerequisites are true:

- Artifact type is `RESULT_VALIDATION_ARTIFACT_V1`.
- Validation status is `RESULT_VALIDATION_COMPLETED`.
- `replay_lineage_preserved` is true.
- `fail_closed_preserved` is true.
- `deterministic_validation_preserved` is true.
- `ready_for_replay_certification` is true.
- Certification readiness requires replay certification and does not allow premature improvement-loop entry.
- Source worker execution and source worker execution hash are present.
- Replay references and replay hashes are present.
- Validation evidence is present, hash-valid, lineage-valid, and governance-valid.
- Certification itself does not invoke workers, providers, governance mutation, or validation result mutation.

The certification runtime is therefore intentionally fail-closed. If any prerequisite is absent, invalid, or lineage-broken, it emits a failed certification artifact rather than certifying an incomplete runtime chain.

Implementation readiness finding:

- Replay certification implementation exists.
- Replay certification replay reconstruction exists.
- Positive certification path is covered by tests.
- Fail-closed paths are covered by tests.
- No missing replay certification implementation was found in `replay_certification_runtime.py`.

## 4. Replay Lineage Analysis

Observed runtime evidence stops before result validation and before replay certification.

Observed evidence present for `TURN-000010`:

- `worker_assignment/000_assignment_evidence_recorded.json`
- `worker_assignment/001_assignment_classification_recorded.json`
- `worker_assignment/002_assignment_artifact_recorded.json`
- `worker_assignment/003_assignment_result_recorded.json`
- `worker_dispatch/000_dispatch_evidence_recorded.json`
- `worker_dispatch/001_dispatch_classification_recorded.json`
- `worker_dispatch/002_dispatch_artifact_recorded.json`
- `worker_dispatch/003_dispatch_result_recorded.json`
- `worker_invocation/000_invocation_evidence_recorded.json`
- `worker_invocation/001_invocation_classification_recorded.json`
- `worker_invocation/002_invocation_artifact_recorded.json`
- `worker_invocation/003_invocation_result_recorded.json`
- `worker_execution_candidate/001_worker_invocation_execution_candidate_recorded.json`
- `worker_execution_candidate/002_worker_invocation_execution_candidate_returned.json`

Observed evidence absent for `TURN-000010`:

- `result_validation/`
- `replay_certification/`

The worker invocation evidence records:

- `worker_invoked: true`
- `worker_dispatched: true`
- `worker_dispatch_replay_reference: .runtime/aicli/AICLI-REFERENCE-SESSION/TURN-000010/certified_development_continuation/worker_lifecycle_continuation/worker_dispatch`

The dispatch evidence exists at:

- `.runtime/aicli/AICLI-REFERENCE-SESSION/TURN-000010/certified_development_continuation/worker_lifecycle_continuation/worker_dispatch/000_dispatch_evidence_recorded.json`

The execution-candidate bridge nevertheless fails closed with:

- `candidate_status: FAILED_CLOSED`
- `certification_status: FAILED_CLOSED`
- `failure_reason: runtime artifact missing: 000_dispatch_evidence_recorded.json`
- `replay_lineage_preserved: false`
- `ready_for_governed_worker_execution: false`
- `execution_requested: false`
- `provider_invoked: false`
- `worker_executed: false`
- `replay_references: []`
- `replay_hashes: []`

The deterministic cause is replay reference resolution in the execution-candidate bridge:

- `_load_invocation_lineage` reads `worker_dispatch_replay_reference` from invocation evidence.
- `_resolve_replay_reference` treats every non-absolute replay reference as relative to `anchor.parent`.
- The observed reference begins with `.runtime/...`, which is repository-relative, not invocation-directory-relative.
- Resolving that repository-relative string against the invocation replay directory parent creates an invalid duplicated path.
- The bridge then attempts to read `000_dispatch_evidence_recorded.json` from that invalid path and fails closed.

The missing replay-lineage prerequisite is not physical dispatch evidence production. Dispatch evidence exists. The missing prerequisite is a reconstructable dispatch replay reference at the path resolution boundary used by the worker invocation to execution-candidate bridge.

## 5. Root Cause Analysis

Root cause classification:

`WORKER_INVOCATION_EXECUTION_CANDIDATE_DISPATCH_REPLAY_REFERENCE_RESOLUTION_GAP`

Deterministic stopping condition:

`runtime artifact missing: 000_dispatch_evidence_recorded.json`

Stopping component:

`aigol/runtime/worker_invocation_to_execution_candidate_bridge_runtime.py::_load_invocation_lineage`

Fail-closed stage:

Worker invocation to execution candidate bridge.

Downstream effect:

- No valid worker execution candidate is produced.
- No external worker task package is produced.
- No external worker result is accepted.
- No governed execution result is available.
- Result validation is not reached.
- Replay certification is not reached.

This means replay certification does not complete because it never receives a valid completed `RESULT_VALIDATION_ARTIFACT_V1`. That absence is correct. Certifying without a validated result would violate replay-lineage and fail-closed constraints.

Audit answers:

1. Replay certification owner: `aigol/runtime/replay_certification_runtime.py`.
2. Missing replay-lineage prerequisite: reconstructable dispatch evidence lineage from invocation evidence into the execution-candidate bridge.
3. Replay certification fail-closed behavior: intentional.
4. Proof artifact: `worker_execution_candidate/001_worker_invocation_execution_candidate_recorded.json` records `FAILED_CLOSED`, `replay_lineage_preserved: false`, and `runtime artifact missing: 000_dispatch_evidence_recorded.json`.
5. Replay certification implementation completeness: complete for its documented contract and covered by tests.
6. Replay lineage intentional incompleteness: not an intended final state; it is intentionally treated as incomplete until the upstream replay reference is reconstructable.
7. Missing production implementation: replay certification itself is not missing. The remaining production implementation gap is upstream replay-reference binding/resolution for the worker invocation to execution-candidate bridge.

## 6. Validation Summary

Validation commands required for this milestone:

- `python -m py_compile`
- `python -m pytest -q`
- `git diff --check`

Validation result:

- `python -m py_compile aigol/cli/aigol_cli.py aigol/runtime/replay_certification_runtime.py aigol/runtime/result_validation_runtime.py aigol/runtime/worker_invocation_to_execution_candidate_bridge_runtime.py aigol/runtime/worker_dispatch_runtime.py aigol/runtime/worker_invocation_runtime.py` passed.
- `python -m pytest -q` passed: `5822 passed, 4 skipped in 139.52s`.
- `git diff --check` passed.

## 7. Boundary Confirmation

No Human Interface responsibility changes are required or proposed.

No Platform Core responsibility moves into AiCLI.

No replay certification semantics move into worker runtime, provider runtime, AiCLI, approval handling, or Canonical Semantic Artifact generation.

No production code was modified by this audit.

Replay certification remains Platform Core-owned and fail-closed.

Replay lineage remains Platform Core-owned and evidence-backed.

Worker dispatch and invocation remain worker lifecycle runtime-owned.

AiCLI remains a thin Human Interface.

## 8. Governance Report

Governance verdict:

`REPLAY_CERTIFICATION_BLOCKED_BY_UPSTREAM_REPLAY_REFERENCE_LINEAGE`

Certification verdict:

`REPLAY_CERTIFICATION_IMPLEMENTED_AND_CORRECTLY_FAIL_CLOSED`

Implementation readiness:

- Replay certification runtime: ready for valid result-validation input.
- Result validation runtime: ready for valid governed worker execution result input.
- Worker invocation to execution candidate bridge: implemented, but observed runtime reveals a replay reference resolution gap for repository-relative replay references.

Required future correction:

`G15-REPLAY-02` or equivalent should address the upstream replay-reference binding/resolution gap in the worker invocation to execution-candidate bridge. The correction should preserve replay immutability, maintain deterministic reconstruction, and avoid moving any replay semantics into AiCLI or provider code.

This milestone does not implement that correction.

Generation 14 ownership boundaries remain unchanged.
