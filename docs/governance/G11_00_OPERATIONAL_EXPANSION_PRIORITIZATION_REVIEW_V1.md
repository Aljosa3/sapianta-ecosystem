# G11-00 Operational Expansion Prioritization Review V1

Status: operational expansion priorities established.

Final verdict: OPERATIONAL_EXPANSION_PRIORITIES_ESTABLISHED

## 1. Executive Summary

Generation 10 certified ACLI Next as the canonical operational development interface and confirmed that AiGOL has transitioned from building the governed development platform to using the governed development platform to evolve itself.

Generation 11 should therefore focus on operational expansion, not architectural redesign.

Strategic finding:

```text
Generation 11 should reduce remaining hybrid operation by extending certified Platform Core capabilities into bounded operational domains.
```

Recommended implementation order:

1. Governed Git remote workflow.
2. Governed dependency management.
3. Governed deployment readiness.
4. Governed deployment implementation.
5. Governed environment operations for recurring operational patterns.

This sequence maximizes reduction of manual copy/paste, terminal use, and external Codex dependence while preserving certified ownership boundaries.

## 2. Current Certified Platform Assessment

Generation 11 begins from a certified architectural foundation.

Certified foundation:

| Capability | Certified Role |
| --- | --- |
| Platform Core | Coordinates certified development workflows and capability composition. |
| UBTR | Preserves deterministic bounded task routing and governed execution semantics. |
| OCS | Owns candidate and proposal formation. |
| Governance | Owns approval, authorization, admissibility, and certification. |
| Replay | Owns evidence, execution history, and reconstruction. |
| Worker Platform | Executes bounded authorized operations. |
| Platform Digital Twin | Projects canonical architectural evidence. |
| Architectural Health | Produces deterministic advisory findings only. |
| Governed Development Workflow | Provides the canonical development process. |
| ACLI Next | Serves as the canonical human development entrypoint. |
| Daily Operational Dashboard | Presents Platform Core operational state without taking authority. |
| Primary ACLI Next Development Operation | Establishes ACLI Next as the default day-to-day development interface. |

These capabilities remain the architectural baseline for Generation 11.

No Generation 11 capability should replace them.

## 3. Remaining Operational Capability Inventory

The remaining roadmap items are operational extensions that reduce hybrid development.

| Capability | Expected Operational Value | Hybrid Reduction | Complexity | Architectural Risk | Certified Reuse |
| --- | --- | --- | --- | --- | --- |
| Governed Git remote workflow | Very high | High reduction of terminal and manual copy/paste after local work | High | High if remote authority is unclear | Reuses governed Git commit, Governance, Replay, Worker execution, ACLI Next dashboard |
| Governed dependency management | High | Medium to high reduction of terminal work for package and lockfile changes | High | High because package managers, registries, and lockfiles affect runtime behavior | Reuses multi-file mutation, validation suites, Governance, Replay, Worker execution |
| Governed deployment readiness | Medium to high | Medium reduction of manual release preparation | High | Very high if environment authority is not certified first | Reuses release discipline, validation suites, rollback, Replay, Governance |
| Governed deployment implementation | Medium | Medium reduction of deployment terminal work | Very high | Very high because it activates runtime environments | Depends on deployment readiness, Git remote workflow, release evidence, rollback |
| Governed environment operations | Variable | Medium for recurring setup, credential, OS, or infrastructure tasks | Medium to very high | High if generalized too early | Reuses Worker allowlists, Governance authorization, Replay evidence, ACLI Next hybrid guidance |
| Unsupported investigation capture | Medium | Low to medium reduction of context loss | Medium | Low if capture remains evidence-only | Reuses Replay summaries, ACLI Next guidance, Platform Core operational snapshots |

The highest-priority operational gap is Git remote workflow because governed local development and local Git commit already exist, while remote publication still forces a terminal handoff.

## 4. Prioritization Methodology

Capabilities are prioritized against the following criteria:

1. Operational impact.
2. Reduction of hybrid workflow.
3. Reuse of certified Platform Core capabilities.
4. Architectural simplicity.
5. Low responsibility leakage risk.
6. Deterministic composition.
7. Replay continuity.
8. Governance continuity.

Implementation difficulty is not ignored, but it is not the sole priority driver.

A capability is preferred when it:

- removes a common manual transition;
- composes existing certified owners;
- preserves explicit human approval;
- remains replay-visible;
- can fail closed;
- has bounded execution scope;
- does not introduce new authority.

## 5. Capability Reviews

### 5.1 Governed Git Remote Workflow

Current gap:

- Local governed Git commit is certified.
- Remote push, fetch, pull, branch switching, branch creation, merge, rebase, and pull request creation remain outside certified scope.

Operational value: very high.

Hybrid reduction:

- reduces terminal use after governed local changes;
- reduces copy/paste around branch status and remote targets;
- reduces manual release-registry handoff;
- keeps publication intent visible to ACLI Next.

Certified reuse:

- governed Git commit evidence;
- Governance authorization;
- Replay command result evidence;
- Worker Platform command execution;
- Platform Core coordination;
- ACLI Next dashboard presentation.

Architectural risk:

- remote operations cross repository boundaries;
- branch and remote target authority must be explicit;
- fetch, pull, merge, and rebase can change local state in complex ways.

Priority finding:

Git remote workflow should be implemented first, beginning with the smallest safe scope:

```text
authorized push to an explicitly approved remote and branch
```

Branch creation or pull request creation may follow only after remote-target evidence and branch-state policy are certified.

### 5.2 Governed Dependency Management

Current gap:

- Dependency installation and update operations remain outside certified mutation and validation scope.

Operational value: high.

Hybrid reduction:

- reduces terminal use for package manager commands;
- reduces manual lockfile inspection;
- improves replay visibility for dependency-driven changes.

Certified reuse:

- multi-file mutation;
- validation suites;
- rollback metadata;
- Governance authorization;
- Worker Platform allowlisted execution;
- Replay evidence.

Architectural risk:

- package managers may access registries;
- lockfiles can change broad dependency behavior;
- transitive updates may alter runtime behavior outside the immediately visible change set.

Priority finding:

Dependency management should follow Git remote workflow. It should begin with bounded dependency review and lockfile-aware update candidates, not unrestricted package-manager execution.

### 5.3 Governed Deployment Readiness

Current gap:

- Deployment remains intentionally outside certified governed development operation.

Operational value: medium to high.

Hybrid reduction:

- reduces manual release preparation;
- improves visibility of release readiness;
- prepares deployment for certification without activating runtime environments prematurely.

Certified reuse:

- release discipline artifacts;
- validation suites;
- rollback evidence;
- Replay reconstruction;
- Governance authorization;
- Platform Digital Twin evidence.

Architectural risk:

- deployment crosses release, environment, runtime activation, and rollback boundaries;
- readiness must not be confused with execution.

Priority finding:

Deployment readiness should precede deployment implementation. It should certify release evidence, target environment policy, rollback readiness, and validation prerequisites before any deployment execution is introduced.

### 5.4 Governed Deployment Implementation

Current gap:

- No certified governed deployment execution exists.

Operational value: medium.

Hybrid reduction:

- reduces terminal deployment activity;
- reduces manual transfer between release certification and runtime activation.

Certified reuse:

- deployment readiness;
- Git remote workflow;
- dependency evidence;
- validation suites;
- rollback execution;
- Governance;
- Worker Platform;
- Replay.

Architectural risk:

- very high, because deployment mutates active environments;
- environment authority and rollback semantics must be certified before execution.

Priority finding:

Deployment implementation should remain after deployment readiness and should be narrow, fail-closed, target-bound, and fully replay-visible.

### 5.5 Governed Environment Operations

Current gap:

- Some OS, infrastructure, credential, filesystem, and environment actions remain outside certified Worker Platform coverage.

Operational value: variable.

Hybrid reduction:

- high for repeated setup or operational tasks;
- low for rare exceptional investigations.

Certified reuse:

- ACLI Next hybrid guidance;
- Worker command allowlists;
- Governance authorization;
- Replay evidence;
- Platform Core operational snapshots.

Architectural risk:

- high if generalized into broad shell authority;
- lower if limited to repeated, observed, narrow operational patterns.

Priority finding:

Environment operations should not be generalized early. Generation 11 should canonicalize only repeated operational patterns supported by evidence from actual hybrid use.

### 5.6 Unsupported Investigation Capture

Current gap:

- Some investigations may still require ChatGPT, Codex, terminal, or manual inspection.

Operational value: medium.

Hybrid reduction:

- improves continuity but does not eliminate the external action itself.

Certified reuse:

- ACLI Next dashboard;
- Replay summaries;
- Governance disclosure;
- Platform Core operational state.

Architectural risk:

- low if capture remains evidence-only;
- high if capture is treated as governed execution.

Priority finding:

Investigation capture is useful but should not outrank Git remote workflow or dependency management. It can be incorporated as part of hybrid-operation evidence improvements.

## 6. Recommended Implementation Order

### Phase 1: Governed Git Remote Workflow

Objective:

```text
replace manual terminal publication for certified local governed development
```

Dependencies:

- governed local Git commit;
- Governance authorization;
- Replay command evidence;
- Worker Platform execution;
- ACLI Next operational dashboard.

Expected operational benefit: very high.

Expected hybrid reduction: high.

Expected architectural impact: bounded extension if remote and branch targets are explicit, authorized, and replay-visible.

Recommended first scope:

- inspect branch and remote state;
- authorize exact remote and branch;
- push an existing local commit;
- record command result and remote target;
- fail closed on mismatch.

### Phase 2: Governed Dependency Management Readiness And Minimal Execution

Objective:

```text
bring dependency changes into governed mutation and validation flow
```

Dependencies:

- multi-file mutation;
- validation suites;
- lockfile evidence;
- Governance authorization;
- Replay evidence;
- Worker Platform allowlisted package actions.

Expected operational benefit: high.

Expected hybrid reduction: medium to high.

Expected architectural impact: manageable if package manager actions are allowlisted and lockfile changes are explicitly authorized.

Recommended first scope:

- dependency intent review;
- package and version target declaration;
- lockfile-aware evidence;
- mandatory validation suite;
- no broad package-manager shell access.

### Phase 3: Governed Deployment Readiness

Objective:

```text
certify deployment prerequisites without activating runtime environments
```

Dependencies:

- release discipline;
- Git remote workflow;
- validation suites;
- rollback readiness;
- Replay release evidence;
- Governance authorization.

Expected operational benefit: medium to high.

Expected hybrid reduction: medium.

Expected architectural impact: low to medium if readiness remains evidence and certification only.

Recommended first scope:

- release evidence review;
- environment target declaration;
- validation prerequisite review;
- rollback readiness review;
- no deployment execution.

### Phase 4: Governed Deployment Implementation

Objective:

```text
execute deployment only through certified, authorized, replay-visible operations
```

Dependencies:

- deployment readiness certification;
- environment authority policy;
- rollback execution;
- release evidence;
- Worker Platform deployment action allowlist.

Expected operational benefit: medium.

Expected hybrid reduction: medium.

Expected architectural impact: high, requiring narrow scope and architecture review.

Recommended first scope:

- one approved environment target;
- one approved deployment action;
- pre-validation and post-validation;
- rollback reference;
- fail-closed execution.

### Phase 5: Governed Environment Operations

Objective:

```text
canonicalize repeated external environment actions as governed operations where evidence supports recurring need
```

Dependencies:

- pilot evidence;
- Worker Platform allowlists;
- Governance authorization;
- Replay evidence;
- ACLI Next hybrid-operation status.

Expected operational benefit: variable.

Expected hybrid reduction: medium for repeated tasks.

Expected architectural impact: variable; low only when operations remain narrow and evidence-backed.

Recommended first scope:

- repeated environment checks;
- deterministic status commands;
- bounded setup verification;
- no broad shell or credential authority.

## 7. Expected Reduction Of Hybrid Development

Expected reduction sequence:

| Phase | Primary Hybrid Reduction |
| --- | --- |
| Git remote workflow | Reduces terminal use after local governed commits and reduces manual publication handoff. |
| Dependency management | Reduces terminal package-manager usage and manual lockfile review. |
| Deployment readiness | Reduces manual release-preparation and environment-readiness copy/paste. |
| Deployment implementation | Reduces direct deployment terminal activity. |
| Environment operations | Reduces repeated exceptional OS, infrastructure, and setup transitions. |

Generation 11 should measure success by:

- fewer manual terminal transitions;
- fewer manual copy/paste loops;
- more operations initiated through ACLI Next;
- more complete Replay evidence;
- fewer unsupported hybrid exceptions;
- no ownership boundary drift.

## 8. Architectural Verification

Every Generation 11 capability must preserve the certified architecture.

Required invariants:

- ACLI Next remains the human interaction layer.
- Platform Core coordinates only.
- OCS owns candidate and proposal formation.
- Governance authorizes and certifies only.
- Replay owns evidence and reconstruction only.
- Worker Platform executes only bounded authorized operations.
- Platform Digital Twin remains the canonical architectural evidence projection.
- Architectural Health remains deterministic and advisory only.
- Human Authority retains final constitutional authority.

Forbidden outcomes:

- new authority layer;
- new orchestration engine;
- Platform Core redesign;
- ACLI Next execution authority;
- Governance logic duplicated in ACLI Next;
- Replay evidence ownership moved into another component;
- broad shell execution through Worker Platform;
- deployment bypassing release discipline;
- dependency updates bypassing validation;
- Architectural Health becoming enforcement.

## 9. Generation 11 Roadmap

Generation 11 should proceed through the same certified pattern used by Generation 9 and Generation 10:

```text
Readiness review
-> Specification
-> Implementation
-> Architecture review
-> Certification
```

Recommended roadmap:

1. G11-01 Governed Git Remote Workflow Readiness Review.
2. G11-02 Governed Git Remote Workflow Specification.
3. G11-03 Governed Git Remote Workflow Implementation.
4. G11-03A Governed Git Remote Workflow Architecture Review.
5. G11-04 Dependency Management Readiness Review.
6. G11-05 Governed Dependency Management Specification.
7. G11-06 Governed Dependency Management Implementation.
8. G11-06A Governed Dependency Management Architecture Review.
9. G11-07 Governed Deployment Readiness Review.
10. G11-08 Governed Deployment Readiness Certification.
11. Later deployment and environment operation implementation only after readiness evidence supports it.

This roadmap keeps operational expansion inside the certified Governed Development Workflow.

## 10. Strategic Assessment

Generation 11 should focus primarily on:

- reducing operational friction;
- eliminating manual copy/paste;
- reducing terminal dependence;
- reducing external Codex dependence;
- expanding operational capabilities through certified composition.

Generation 11 should not pursue "ACLI Next autonomy" as a new authority model.

The correct objective is:

```text
more certified operations exposed through ACLI Next, with Platform Core and certified owners retaining authority
```

This continues the certified progression:

```text
Reuse
-> Canonicalization
-> Extension
```

## 11. Final Determination

Generation 11 operational expansion priorities are established.

The highest-value next capability is governed Git remote workflow, followed by governed dependency management, deployment readiness, deployment implementation, and evidence-backed governed environment operations.

These capabilities are operational extensions of the certified Platform Core architecture. They are not architectural redesigns.

Final verdict: OPERATIONAL_EXPANSION_PRIORITIES_ESTABLISHED

## 12. Validation Evidence

Validation performed:

```text
git diff --check
```

Validation result: clean.

Final verdict: OPERATIONAL_EXPANSION_PRIORITIES_ESTABLISHED
