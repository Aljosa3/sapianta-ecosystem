# G8-09A First Mutating Worker Architecture Review V1

Status: Worker Platform responsibility leakage detected.

Final verdict: WORKER_PLATFORM_RESPONSIBILITY_LEAKAGE_DETECTED

## 1. Executive Summary

G8-09 successfully implemented the first governed mutating Worker as a narrow create-only file operation.

The actual Worker Platform execution component remains bounded:

```text
aigol/workers/filesystem_worker.py
```

It validates an authorized request, creates exactly one file, records Worker replay, and does not own OCS, Governance, provider invocation, Git, commits, deployment, or autonomous orchestration.

However, the new Platform Core runtime:

```text
aigol/runtime/first_mutating_worker_runtime.py
```

centralizes several responsibilities that should belong to distinct Platform Core owner surfaces before mutation capabilities expand:

- OCS-style mutation candidate construction;
- human approval artifact construction;
- Governance authorization creation;
- Replay wrapper persistence and reconstruction;
- post-mutation validation artifact construction;
- rollback metadata construction;
- execution completion assembly.

This is not ACLI Next leakage. ACLI Next remains unaffected and thin.

The concern is internal Platform Core responsibility concentration around the first mutation path. The implementation is safe for the first narrow create-only Worker, but additional mutation capabilities should not be added until these responsibilities are decomposed into owner helpers, following the G8-06D correction pattern.

## 2. Ownership Review

| Responsibility | Current location | Correct owner | Assessment |
| --- | --- | --- | --- |
| Create one file after authorized request | `aigol/workers/filesystem_worker.py` | Worker Platform | Correct. |
| Validate Worker request shape and scope | `aigol/workers/filesystem_worker.py` | Worker Platform | Correct. |
| Write target file | `aigol/workers/filesystem_worker.py` | Worker Platform | Correct. |
| Worker replay capture | `aigol/workers/filesystem_worker.py` | Worker Platform / Replay evidence | Acceptable for Worker-local replay. |
| Mutation candidate construction | `first_mutating_worker_runtime.py` | OCS | Leakage. |
| Human approval artifact construction | `first_mutating_worker_runtime.py` | Governance / human decision boundary | Leakage. |
| Governance authorization record creation | `first_mutating_worker_runtime.py` | Governance | Leakage. |
| Pre-mutation state evidence | `first_mutating_worker_runtime.py` | Replay / Worker Platform boundary | Acceptable temporarily; should delegate. |
| Post-mutation validation artifact | `first_mutating_worker_runtime.py` | Validation / Replay / Worker Platform | Leakage if expanded. |
| Rollback metadata construction | `first_mutating_worker_runtime.py` | Governance / Worker Platform / Replay | Leakage if expanded. |
| Replay persistence and reconstruction | `first_mutating_worker_runtime.py` | Replay | Leakage if expanded. |
| Completion assembly | `first_mutating_worker_runtime.py` | Platform Core coordinator | Acceptable. |
| Interface capture and rendering | No ACLI Next mutation route added | ACLI Next | Correct. |

## 3. Dependency Analysis

Current dependency shape:

```text
first_mutating_worker_runtime.py
  |
  +--> authorization_record.py
  |
  +--> filesystem_worker.py
  |
  +--> transport/serialization.py
```

The dependency shape reuses existing certified surfaces and does not introduce a new external mechanism.

The issue is that `first_mutating_worker_runtime.py` combines OCS, Governance, Replay, validation, rollback, and coordinator duties in one runtime module.

Recommended dependency shape:

```text
Platform Core mutation coordinator
  |
  +--> OCS mutation candidate helper
  |
  +--> Governance mutation approval and authorization helper
  |
  +--> Worker Platform filesystem create Worker
  |
  +--> Replay mutation evidence helper
  |
  +--> Validation helper
  |
  +--> Rollback metadata helper
```

This mirrors the G8-06D execution planning service refactor and prevents the mutation coordinator from becoming a second OCS/Governance/Replay layer.

## 4. Authority Review

Governance remains the authority at the conceptual boundary:

- explicit human approval is required;
- approval is bound to candidate hash;
- Governance authorization record is required;
- Worker cannot self-authorize;
- provider cannot authorize;
- replay cannot authorize;
- the mutation fails closed without approval.

Concern:

The runtime module constructs the approval artifact and authorization record directly. That is safe for the first isolated operation, but if extended it would make the mutation runtime a Governance authoring surface.

Required correction before expansion:

- move approval artifact construction into a Governance helper;
- move authorization record creation into a Governance mutation authorization service;
- keep the mutation runtime as coordinator only.

## 5. Replay Review

Replay evidence is present and reconstructable:

- candidate;
- approval;
- authorization;
- Worker request;
- pre-mutation state;
- Worker result;
- validation;
- rollback metadata;
- completion.

Replay remains append-only and hash-bound.

Concern:

The mutation runtime owns replay wrapper persistence and reconstruction directly. This is acceptable for a single proof milestone, but should be moved into a Replay mutation evidence helper before broader mutation support.

Required correction before expansion:

- move `REPLAY_STEPS`, replay persistence, and replay reconstruction to a Replay-owned mutation evidence helper;
- keep Worker-local replay reconstruction in `filesystem_worker.py`;
- keep coordinator replay references only in the mutation coordinator.

## 6. Worker Platform Boundary Review

The Worker Platform boundary is preserved in the concrete Worker:

| Boundary | Result |
| --- | --- |
| Worker validates authorization scope | Preserved. |
| Worker validates operation is `CREATE_FILE` | Preserved. |
| Worker validates filename-only target | Preserved. |
| Worker prevents overwrite | Preserved. |
| Worker writes exactly one file | Preserved. |
| Worker records Worker-local replay | Preserved. |
| Worker avoids provider invocation | Preserved. |
| Worker avoids Git, commit, deployment | Preserved. |
| Worker does not create approval | Preserved. |
| Worker does not create authorization | Preserved. |
| Worker does not orchestrate | Preserved. |

The leakage is not inside `filesystem_worker.py`.

The leakage is in the Platform Core mutation runtime surrounding the Worker, where owner-specific responsibilities are currently centralized.

## 7. OCS Review

OCS should own mutation candidate construction.

Current issue:

`create_first_mutating_worker_candidate` creates an OCS-style candidate directly inside the mutation runtime.

Recommendation:

Move candidate construction into:

```text
aigol/runtime/platform_core_ocs_mutation_preview.py
```

or equivalent existing OCS owner surface.

The mutation runtime should consume an OCS-produced candidate instead of constructing one.

## 8. Governance Review

Governance should own:

- approval artifact construction;
- authorization artifact construction;
- approval-to-candidate binding;
- mutation authorization status;
- authorization scope and expiry policy.

Current issue:

`create_first_mutating_worker_approval` and inline `create_authorization_record(...)` calls are in the mutation runtime.

Recommendation:

Move these into:

```text
aigol/runtime/platform_core_governance_mutation_authorization.py
```

or equivalent existing Governance owner surface.

The mutation runtime should receive validated Governance authorization evidence.

## 9. ACLI Next Review

ACLI Next remains thin.

No ACLI Next route, rendering logic, command parser, or adapter was extended to own mutation policy or execution behavior in G8-09.

Future ACLI Next mutation support must:

- capture human request;
- render candidate and authorization summaries;
- capture structured confirmation;
- delegate all mutation behavior to Platform Core;
- present replay identifiers;
- avoid direct file writing or policy decisions.

## 10. Recommendations

Before expanding mutation capabilities, implement:

```text
G8_09B_FIRST_MUTATING_WORKER_BOUNDARY_REFACTORING_V1
```

Recommended refactoring:

1. Move mutation candidate construction to OCS owner helper.
2. Move human approval artifact construction to Governance helper.
3. Move mutation authorization record creation to Governance helper.
4. Move replay wrapper persistence and reconstruction to Replay helper.
5. Move post-mutation validation artifact construction to validation/Replay helper.
6. Move rollback metadata construction to Governance/Worker Platform helper.
7. Keep `first_mutating_worker_runtime.py` as coordinator only.
8. Preserve `aigol/workers/filesystem_worker.py` as the Worker execution component.
9. Add boundary tests proving the coordinator delegates owner-specific responsibilities.

Do not expand mutation to existing-file edits, multi-file patches, validation command execution, Git, commits, or deployment until this boundary refactoring is complete.

## 11. Validation Evidence

Validation performed:

```text
git diff --check
```

Validation result: clean.

## 12. Final Determination

The first mutating Worker execution component remains properly bounded as Worker Platform execution.

Responsibility leakage is detected in the Platform Core mutation runtime surrounding the Worker. The current implementation is safe for the first narrow create-only proof, but it should be refactored before mutation capabilities are expanded.

Final verdict: WORKER_PLATFORM_RESPONSIBILITY_LEAKAGE_DETECTED
