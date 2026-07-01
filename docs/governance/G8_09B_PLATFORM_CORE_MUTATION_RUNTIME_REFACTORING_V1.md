# G8-09B Platform Core Mutation Runtime Refactoring V1

Status: Platform Core mutation runtime refactored.

Final verdict: PLATFORM_CORE_MUTATION_RUNTIME_REFACTORED

## 1. Executive Summary

G8-09B refactors the first governed mutation runtime after the G8-09A architecture review found responsibility leakage around, but not inside, the filesystem Worker.

The filesystem Worker remained correctly bounded as a Worker Platform execution component. The surrounding mutation runtime, however, had accumulated responsibilities that belong to existing certified Platform Core owners:

- OCS candidate construction;
- Governance approval and authorization artifacts;
- Replay persistence and reconstruction;
- validation evidence;
- rollback metadata.

This milestone realigns those responsibilities without adding runtime capabilities, redesigning Platform Core, or creating a new authority layer.

The mutation runtime now coordinates existing Platform Core responsibilities and delegates owned work to Platform Core modules. It does not directly mutate files, authorize execution, persist replay, reconstruct replay, create candidates, create approvals, validate mutation evidence, or own rollback metadata.

## 2. Responsibility Ownership Matrix

| Responsibility | Canonical Owner | Refactored Location | Mutation Runtime Role |
| --- | --- | --- | --- |
| Candidate creation | OCS | `aigol/runtime/platform_core_ocs_mutation_candidate.py` | Delegates and consumes candidate artifact. |
| Candidate validation | OCS | `aigol/runtime/platform_core_ocs_mutation_candidate.py` | Calls validation before workflow coordination. |
| Human approval artifact | Governance | `aigol/runtime/platform_core_governance_mutation_authorization.py` | Delegates and consumes approval artifact. |
| Approval validation | Governance | `aigol/runtime/platform_core_governance_mutation_authorization.py` | Calls validation before authorization. |
| Authorization creation | Governance | `aigol/runtime/platform_core_governance_mutation_authorization.py` | Requests governed authorization record. |
| Replay persistence | Replay | `aigol/runtime/platform_core_replay_mutation_evidence.py` | Requests replay step persistence. |
| Replay reconstruction | Replay | `aigol/runtime/platform_core_replay_mutation_evidence.py` | Re-exports reconstruction for compatibility. |
| Pre-mutation state validation | Existing validation capability | `aigol/runtime/platform_core_mutation_validation.py` | Requests validation artifact. |
| Post-mutation validation | Existing validation capability | `aigol/runtime/platform_core_mutation_validation.py` | Requests validation artifact. |
| Rollback metadata | Platform Core rollback metadata capability | `aigol/runtime/platform_core_mutation_rollback.py` | Requests rollback metadata artifact. |
| Worker request construction | Worker Platform boundary | `aigol/workers/filesystem_worker.py` | Delegates request creation to Worker Platform API. |
| File mutation execution | Worker Platform | `aigol/workers/filesystem_worker.py` | Invokes Worker Platform only after authorization. |
| Completion summary assembly | Mutation runtime coordinator | `aigol/runtime/first_mutating_worker_runtime.py` | Coordinates final capture and non-authoritative summary. |

## 3. Delegation Map

The refactored workflow is:

```text
first_mutating_worker_runtime
  -> platform_core_ocs_mutation_candidate
  -> platform_core_governance_mutation_authorization
  -> platform_core_mutation_validation
  -> platform_core_replay_mutation_evidence
  -> filesystem_worker
  -> platform_core_mutation_validation
  -> platform_core_mutation_rollback
  -> platform_core_replay_mutation_evidence
```

The coordinator retains only sequence coordination:

1. validate candidate and approval;
2. resolve governed workspace through validation helpers;
3. request Governance authorization;
4. request Worker Platform request construction;
5. request Replay persistence;
6. invoke the Worker Platform;
7. request validation and rollback metadata;
8. record completion evidence.

## 4. Dependency Graph

```text
Human / ACLI Next
        |
        v
PGSP / Platform Core session
        |
        v
Mutation Runtime Coordinator
        |
        +--> OCS candidate helpers
        |
        +--> Governance approval and authorization helpers
        |
        +--> Replay mutation evidence helpers
        |
        +--> Platform Core validation helpers
        |
        +--> Worker Platform filesystem Worker
        |
        +--> Platform Core rollback metadata helpers
        |
        v
Replay-visible completion capture
```

No edge gives the coordinator authority over Governance, Replay, OCS, or Worker execution.

## 5. Architectural Responsibility Realignment

Candidate creation no longer belongs to the mutation runtime. The candidate artifact is created and validated by an OCS-shaped Platform Core module.

Human approval artifacts no longer belong to the mutation runtime. They are created and validated through a Governance-shaped Platform Core module.

Authorization creation no longer occurs inside the coordinator. The coordinator requests a governed authorization record from the Governance helper, which reuses the existing authorization record implementation.

Replay persistence and reconstruction no longer occur inside the coordinator. Replay wrapper creation, append-only writes, replay ordering, hash verification, and reconstruction are delegated to the Replay mutation evidence helper.

Validation artifacts no longer belong to the coordinator. Pre-mutation state, allowlisted workspace checks, target resolution, and post-mutation validation are delegated to the validation helper.

Rollback metadata no longer belongs to the coordinator. Hash-bound rollback metadata is delegated to the rollback helper. The helper creates metadata only; it does not perform rollback.

Worker invocation remains exclusively Worker Platform execution. The coordinator creates no files directly and performs no Git, commit, deployment, provider, or write-capable dispatch behavior outside the Worker Platform.

## 6. Platform Core Reuse Analysis

The refactor preserves reuse-first behavior:

- Governance authorization reuses `aigol/authorization/authorization_record.py`.
- Worker execution reuses `aigol/workers/filesystem_worker.py`.
- Replay persistence reuses canonical runtime serialization helpers.
- Candidate, approval, validation, and rollback helpers use hash-bound artifacts compatible with existing replay reconstruction.
- ACLI Next remains unaffected and continues consuming Platform Core behavior through the existing runtime route.

No new orchestration engine, Governance authority, Replay authority, Worker Platform, or capability registry was introduced.

## 7. Governance Impact

Governance impact: improved.

Governance-owned decisions are no longer locally assembled inside the mutation coordinator. Human approval evidence and authorization record creation now live behind a Governance-shaped Platform Core boundary.

The coordinator cannot authorize execution by itself. It can only request a validated authorization artifact before delegating to the Worker Platform.

## 8. Replay Impact

Replay impact: improved.

Replay persistence and reconstruction are no longer local coordinator responsibilities. The Replay mutation evidence helper owns:

- append-only replay step writes;
- replay step ordering;
- wrapper hash verification;
- artifact hash verification;
- mutation replay reconstruction.

Replay remains the evidence system. The coordinator only presents replay references and asks Replay helpers to record evidence.

## 9. Validation Impact

Validation impact: improved.

Pre-mutation state and post-mutation validation are delegated to the validation helper. This prevents the coordinator from becoming the validation authority and keeps validation artifacts reusable by future interfaces and Platform Core flows.

Targeted tests now include a boundary assertion that the coordinator does not directly create authorization records, persist replay JSON, reconstruct replay, define candidate creation, or define validation and rollback artifact ownership.

## 10. Implementation Notes

Files added:

- `aigol/runtime/platform_core_ocs_mutation_candidate.py`
- `aigol/runtime/platform_core_governance_mutation_authorization.py`
- `aigol/runtime/platform_core_replay_mutation_evidence.py`
- `aigol/runtime/platform_core_mutation_validation.py`
- `aigol/runtime/platform_core_mutation_rollback.py`

Files updated:

- `aigol/runtime/first_mutating_worker_runtime.py`
- `tests/test_g8_first_mutating_worker_runtime.py`

Compatibility preserved:

- existing public imports for `create_first_mutating_worker_candidate`;
- existing public imports for `create_first_mutating_worker_approval`;
- existing public imports for `reconstruct_first_mutating_worker_replay`;
- existing execution API for `execute_first_mutating_worker`;
- existing Worker Platform behavior;
- existing replay artifact count and reconstruction behavior.

## 11. Validation Evidence

Validation performed:

```text
git diff --check
python -m py_compile aigol/runtime/first_mutating_worker_runtime.py aigol/runtime/platform_core_ocs_mutation_candidate.py aigol/runtime/platform_core_governance_mutation_authorization.py aigol/runtime/platform_core_mutation_validation.py aigol/runtime/platform_core_mutation_rollback.py aigol/runtime/platform_core_replay_mutation_evidence.py tests/test_g8_first_mutating_worker_runtime.py
python -m pytest tests/test_g8_first_mutating_worker_runtime.py tests/test_repository_mutation_worker_runtime_v1.py
```

Validation result:

```text
15 passed
```

## 12. Final Determination

The mutation runtime has been refactored into a thin coordination layer over existing certified Platform Core responsibilities.

It does not introduce a second OCS, Governance system, Replay system, Worker Platform, or capability registry.

Final verdict: PLATFORM_CORE_MUTATION_RUNTIME_REFACTORED
