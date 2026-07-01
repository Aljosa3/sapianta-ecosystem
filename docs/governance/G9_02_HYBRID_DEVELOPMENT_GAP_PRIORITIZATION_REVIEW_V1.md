# G9-02 Hybrid Development Gap Prioritization Review V1

Status: hybrid development priorities established.

Final verdict: HYBRID_DEVELOPMENT_PRIORITIES_ESTABLISHED

## 1. Executive Summary

G9-01 confirmed that ACLI Next is the canonical governed development entrypoint, but a hybrid Codex/Terminal workflow remains necessary for unsupported development tasks.

This review prioritizes the remaining runtime gaps by their ability to reduce manual Codex/Terminal usage while preserving certified Platform Core architecture.

The highest-priority capability is:

```text
governed patch-level editing of exactly one existing file
```

Rationale:

- it addresses the most frequent daily development operation;
- it builds directly on certified existing-file mutation;
- it reduces manual file editing more than Git push, deployment, or dependency management;
- it can be implemented before multi-file transactions;
- it keeps mutation scope bounded enough for Governance, Replay, rollback metadata, validation, and Worker Platform execution.

Recommended roadmap:

1. Governed single-file patch-level editing.
2. Governed rollback execution.
3. Governed multi-file mutation envelope.
4. Broader governed validation execution.
5. Governed Git branch and push workflow.
6. Governed dependency management.
7. Governed deployment.

This sequence maximizes day-to-day workflow replacement without skipping architectural safety gates.

## 2. Prioritization Criteria

Each remaining gap is evaluated against:

| Criterion | Meaning |
| --- | --- |
| Development frequency | How often ordinary AiGOL development requires the capability. |
| Architectural dependency | Which certified owners must participate before implementation. |
| Implementation complexity | Expected runtime and test complexity. |
| Risk | Risk to repository integrity, replay continuity, governance authority, or release discipline. |
| Manual reduction | Expected reduction in hybrid Codex/Terminal usage. |

Priority levels:

| Priority | Meaning |
| --- | --- |
| P0 | Should be implemented next or immediately after the next capability. |
| P1 | Important near-term capability after P0 foundations exist. |
| P2 | Useful but should wait for stronger mutation, validation, or release foundations. |
| Deferred | Should remain manual until prior runtime layers are certified. |

## 3. Gap Evaluation Matrix

| Gap | Development Frequency | Architectural Dependency | Complexity | Risk | Manual Reduction | Priority |
| --- | --- | --- | --- | --- | --- | --- |
| Patch-level editing | Very high | Existing-file mutation, OCS candidate handling, Governance authorization, Replay evidence, Worker Platform execution, rollback metadata | Medium | Medium | Very high | P0 |
| Rollback execution | Medium | Existing rollback metadata, Governance authorization, Replay reconstruction, Worker Platform execution | Medium | High | High for safe adoption | P0 |
| Multi-file mutation | Very high | Patch-level mutation, OCS multi-candidate planning, Governance authorization, Replay transaction evidence, rollback execution | High | High | Very high | P0 |
| Broader validation execution | High | Existing validation Worker, command allowlist, Governance authorization, Replay result model | Medium | Medium | High | P0 |
| Git push / branch / remote workflows | Medium | Local commit runtime, release discipline, remote boundary governance, Replay evidence | High | High | Medium to high | P1 |
| Dependency management | Medium | Validation expansion, package manager policy, multi-file mutation, lockfile integrity, Governance authorization | High | High | Medium | P2 |
| Deployment | Low to medium | Release discipline, Git remote workflow, environment authority, rollback execution, Replay release evidence | Very high | Very high | Medium | Deferred |

## 4. Gap Reviews

### 4.1 Patch-Level Editing

Current state:

- Existing-file mutation can replace the complete contents of exactly one existing plaintext file.
- Day-to-day development usually requires smaller patch or hunk edits.

Why the gap remains:

- Full-file replacement is safer to certify initially, but inefficient and risky for iterative development.
- Patch-level mutation requires stronger file integrity, pre-hash, context matching, conflict detection, rollback, and post-hash evidence.

Canonical owners:

- OCS owns patch candidate formation and proposal.
- Governance owns approval and authorization.
- Worker Platform applies the patch.
- Replay records pre-state, patch intent, post-state, hashes, conflicts, and completion evidence.
- Platform Core coordinates.
- ACLI Next captures and renders only.

Priority finding:

Patch-level editing should be implemented first. It provides the largest immediate reduction in manual Codex/Terminal use while remaining narrow enough to certify as an extension of existing-file mutation.

### 4.2 Rollback Execution

Current state:

- Rollback metadata exists for governed mutations.
- Runtime rollback execution is not certified.

Why the gap remains:

- Executing rollback is itself a mutation.
- It must not bypass Governance, Replay, OCS, or Worker Platform boundaries.

Canonical owners:

- Governance authorizes rollback.
- Replay reconstructs rollback basis and evidence.
- Worker Platform executes the rollback action.
- OCS proposes rollback candidate when needed.
- Platform Core coordinates.

Priority finding:

Rollback execution should follow patch-level editing before broad multi-file mutation. This makes later mutation expansion safer and reduces operator dependence on manual recovery.

### 4.3 Multi-File Mutation

Current state:

- New-file and existing-file mutation are certified only for one file at a time.

Why the gap remains:

- Real implementation frequently spans tests, runtime code, documentation, and fixtures.
- Multi-file mutation requires transaction semantics, all-file authorization, conflict detection, partial failure handling, rollback evidence, and validation sequencing.

Canonical owners:

- OCS owns multi-file candidate grouping and dependency ordering.
- Governance authorizes the exact file set and mutation scope.
- Replay records per-file evidence and transaction-level evidence.
- Worker Platform performs bounded file operations.
- Platform Core coordinates the transaction.

Priority finding:

Multi-file mutation is a P0 capability, but it should follow single-file patch-level editing and rollback execution. Implementing it before patch and rollback would increase blast radius too quickly.

### 4.4 Broader Validation Execution

Current state:

- Governed validation supports exactly one allowlisted non-shell validation command.

Why the gap remains:

- Real development commonly requires more than one validation command, such as whitespace checks, compilation, targeted tests, and replay reconstruction checks.
- Validation suite selection can accidentally become a new local authority if not owned by OCS/Governance.

Canonical owners:

- OCS proposes validation plan.
- Governance authorizes the validation suite.
- Worker Platform executes each allowlisted command.
- Replay records command, timeout, stdout/stderr bounds, exit code, and result evidence.
- Platform Core coordinates sequencing.

Priority finding:

Broader validation execution remains P0 because it reduces manual terminal usage after edits. It should follow or accompany multi-file mutation so validation can cover the actual change set.

### 4.5 Git Push / Branch / Remote Workflows

Current state:

- Governed local Git commit is certified.
- Branch creation, branch switching, push, fetch, pull, merge, rebase, remote interaction, and pull request creation are not certified.

Why the gap remains:

- Remote Git operations cross repository boundaries and interact with release discipline.
- Branch and push workflows require stronger provenance, remote target verification, and release governance.

Canonical owners:

- Governance authorizes Git remote operations.
- Worker Platform executes Git commands.
- Replay records branch state, remote target, commit hash, command results, and fail-closed evidence.
- Release discipline remains a separate governed concern.
- Platform Core coordinates.

Priority finding:

Git remote workflows are P1. They should not precede patch-level editing, rollback, multi-file mutation, and broader validation because pushing poorly governed changes would amplify existing gaps.

### 4.6 Dependency Management

Current state:

- Package installation and dependency updates are outside certified validation and mutation scope.

Why the gap remains:

- Dependency updates may execute package managers, alter lockfiles, change transitive runtime behavior, and require broader validation.
- Package installation may involve network access and external trust boundaries.

Canonical owners:

- Governance authorizes dependency operations.
- OCS proposes dependency update intent and validation requirements.
- Worker Platform executes only certified package-manager actions.
- Replay records package input, lockfile changes, command evidence, and validation results.
- EPP or provider boundaries may apply if external registries or provider analysis are used.

Priority finding:

Dependency management is P2. It requires multi-file mutation, broader validation, and stronger external boundary policy first.

### 4.7 Deployment

Current state:

- Deployment remains intentionally outside current governed development workflow certification.

Why the gap remains:

- Deployment affects server/runtime environments, release discipline, rollback, evidence retention, and operational safety.
- It has higher blast radius than repository mutation or local Git.

Canonical owners:

- Governance authorizes deployment.
- Release discipline owns release readiness policy.
- Worker Platform executes deployment only through certified actions.
- Replay records deployment evidence and rollback references.
- Platform Core coordinates.

Priority finding:

Deployment is deferred. It should wait until rollback execution, Git remote workflow, release evidence, and validation suite execution are certified.

## 5. Prioritized Implementation Roadmap

### Phase 1: Single-File Patch-Level Mutation

Objective:

```text
replace manual patch application and reduce Codex/Terminal file-editing dependence
```

Scope:

- exactly one existing plaintext file;
- context-bound patch or hunk replacement;
- pre-hash and post-hash verification;
- conflict detection;
- rollback metadata;
- explicit human approval;
- Governance authorization;
- Worker Platform execution;
- Replay evidence.

Expected manual reduction: very high.

### Phase 2: Governed Rollback Execution

Objective:

```text
make certified mutation recovery executable through the governed path
```

Scope:

- rollback exactly one prior governed mutation;
- hash-bound rollback basis;
- Governance authorization;
- Worker Platform execution;
- Replay reconstruction evidence;
- fail-closed conflict behavior.

Expected manual reduction: high, especially for operator confidence and adoption safety.

### Phase 3: Multi-File Mutation Envelope

Objective:

```text
allow coherent development changes spanning multiple authorized files
```

Scope:

- exact authorized file set;
- per-file patch or replacement operations;
- transaction-level evidence;
- partial failure handling;
- rollback plan;
- validation prerequisites;
- Replay evidence.

Expected manual reduction: very high.

### Phase 4: Broader Governed Validation Suites

Objective:

```text
replace manual terminal validation for common development loops
```

Scope:

- multiple allowlisted non-shell commands;
- timeout and output bounds per command;
- ordered validation plan;
- result aggregation;
- Replay evidence;
- Governance authorization.

Expected manual reduction: high.

### Phase 5: Governed Git Remote Workflow

Objective:

```text
extend local governed commit toward controlled branch and push operations
```

Scope:

- branch status and creation only after authorization;
- push to authorized remote/branch only;
- no merge or rebase in first phase;
- Replay evidence for remote target and command result;
- release discipline linkage.

Expected manual reduction: medium to high.

### Phase 6: Governed Dependency Management

Objective:

```text
bring dependency updates into governed mutation and validation flow
```

Scope:

- allowlisted package manager actions;
- lockfile integrity checks;
- network and registry policy;
- mandatory validation suite;
- replay-visible dependency evidence.

Expected manual reduction: medium.

### Phase 7: Governed Deployment

Objective:

```text
govern release and server/runtime activation
```

Scope:

- release evidence;
- deployment authorization;
- environment targeting;
- rollback readiness;
- Replay evidence;
- no uncontrolled server mutation.

Expected manual reduction: medium, but high operational risk.

## 6. Recommended First Capability

The first implementation after this review should be:

```text
G9_03_GOVERNED_PATCH_LEVEL_MUTATION_SPECIFICATION_V1
```

Recommended verdict target:

```text
PATCH_LEVEL_MUTATION_SPECIFIED
```

Why this comes first:

- it targets the most frequent manual development bottleneck;
- it extends an already certified existing-file mutation capability;
- it is narrower and safer than multi-file mutation;
- it creates the primitive needed for later multi-file changes;
- it avoids remote Git, deployment, dependency, and package-manager risk;
- it preserves the G9-00 methodology.

## 7. Architecture Preservation Requirements

All roadmap items must continue applying:

```text
Reuse
-> Canonicalization
-> Extension
```

Required invariants:

- ACLI Next remains a thin entrypoint.
- Platform Core coordinates.
- OCS owns candidate and proposal formation.
- Governance owns approval and authorization.
- Replay owns evidence and reconstruction.
- Worker Platform owns execution.
- Platform Digital Twin and Architectural Health remain deterministic projections.
- No new authority layer is introduced.
- No Platform Core replacement occurs.

## 8. Final Determination

The hybrid development gaps are now prioritized.

The highest-value next capability is governed single-file patch-level editing, followed by rollback execution, multi-file mutation, broader validation, Git remote workflow, dependency management, and deployment.

This roadmap maximizes reduction of manual Codex/Terminal usage while preserving certified Platform Core ownership boundaries.

Final verdict: HYBRID_DEVELOPMENT_PRIORITIES_ESTABLISHED

## 9. Validation Evidence

Validation performed:

```text
git diff --check
```

Validation result: clean.

Final verdict: HYBRID_DEVELOPMENT_PRIORITIES_ESTABLISHED
