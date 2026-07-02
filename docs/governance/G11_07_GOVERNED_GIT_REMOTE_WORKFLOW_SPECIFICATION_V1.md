# G11-07 Governed Git Remote Workflow Specification V1

Status: governed Git remote workflow specified.

Final verdict: GOVERNED_GIT_REMOTE_WORKFLOW_SPECIFIED

## 1. Executive Summary

Generation 11 has certified persistent ACLI Next operation and governed Codex Worker/Provider integration. The remaining daily development friction now centers on manual Git remote operations.

This specification defines governed Git remote workflow support as a minimal operational extension of the certified Worker Platform architecture.

The canonical architectural position is:

```text
Git remote operations are bounded Worker Platform execution.
```

Git remote operations are not a Platform Core capability, not an ACLI Next capability, not a Governance subsystem, and not a Replay subsystem.

Platform Core continues to orchestrate. Governance continues to authorize. Replay continues to record evidence. Worker Platform executes. Architectural Health observes. ACLI Next presents and guides.

Final finding:

```text
Governed Git remote workflow requires a new bounded Git Remote Worker capability, but no new architecture.
```

## 2. Governed Development Workflow Compliance

This specification applies:

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
Specification
```

No implementation is performed by this artifact.

## 3. Capability Audit

| Capability | Existing Certified State | Reuse Finding |
| --- | --- | --- |
| Platform Core | Certified orchestration authority for governed development and local Git commit coordination. | Reuse for routing Git remote intent into governed Worker execution. |
| ACLI Next | Certified primary human interface and conversational UX. | Reuse for presenting Git remote status, approvals, Replay references, and hybrid guidance only. |
| Worker Platform | Certified bounded execution, worker registration, dispatch, invocation, completion, and failure reporting. | Reuse for Git Remote Worker execution. |
| Provider Platform | Certified non-authoritative cognition/provider boundary. | Not required for Git execution; may provide advisory explanation only if separately authorized. |
| Governance | Certified approval and authorization authority. | Reuse for remote, branch, protected operation, and failure handling authorization. |
| Replay | Certified evidence and reconstruction authority. | Reuse for remote inspection, authorization, execution, validation, failure, and recovery evidence. |
| Platform Digital Twin | Canonical architectural evidence projection. | Reuse to project Git Remote Worker identity and boundary evidence. |
| Architectural Health | Deterministic advisory checkpoint. | Reuse to observe branch policy, remote consistency, failures, and responsibility preservation. |
| Governed Development Workflow | Certified development lifecycle. | Reuse as the required path for Git remote capability implementation and certification. |
| Existing Worker registration | Certified worker identity registration model. | Reuse for Git Remote Worker identity. |
| Existing Worker dispatch | Certified replay-visible dispatch model. | Reuse before Git remote execution. |
| Existing execution authorization | Certified authorization record and Governance-owned authorization patterns. | Reuse for exact Git remote operation authorization. |
| Existing validation runtime | Certified governed validation command execution. | Reuse for pre/post Git remote validation. |
| Existing validation suite runtime | Certified deterministic validation suite composition. | Reuse for ordered validation before push and after fetch/pull. |
| Existing rollback runtime | Certified governed rollback execution for supported repository mutation. | Reuse where applicable; remote recovery is not automatic rollback. |
| Governed local Git commit | Certified one local commit from an authorized file set. | Reuse commit evidence as prerequisite for push, but do not extend local commit Worker. |

Audit conclusion:

```text
Local Git commit is certified; Git remote workflow is not yet certified.
```

The missing behavior is bounded remote Git execution, branch/remote verification, authentication boundary evidence, remote result evidence, and remote-specific failure handling.

## 4. Existing Capability Reuse Assessment

The certified local Git commit Worker already establishes important Git execution principles:

- explicit Governance authorization;
- exact operation scope;
- expected branch and `HEAD` checks;
- prohibited remote operation flags;
- argument-vector Git execution with `shell=False`;
- Replay-visible pre-state and result evidence;
- fail-closed behavior.

G11-07 must reuse these principles without expanding the local commit Worker.

Required reuse:

- Worker registration for a new Git Remote Worker identity;
- Worker dispatch and invocation lifecycle;
- Governance authorization records;
- Replay ordered evidence;
- validation runtime and validation suites;
- rollback metadata where applicable;
- Architectural Health advisory observations;
- ACLI Next presentation.

Forbidden duplication:

- no Git remote orchestration inside Worker;
- no Git remote execution inside ACLI Next;
- no Git remote authorization inside Worker;
- no separate Git evidence ledger;
- no provider-driven Git execution;
- no remote operation by local Git commit Worker.

## 5. Git Worker Architectural Position

Canonical Worker identity:

```text
GOVERNED_GIT_REMOTE_WORKER
```

Canonical scope:

```text
BOUNDED_GIT_REMOTE_OPERATION
```

The Git Remote Worker owns execution only.

It may execute only the exact authorized Git operation against the exact authorized repository, remote, branch, and expected state.

It must not:

- select operations;
- authorize operations;
- approve protected branch changes;
- decide release readiness;
- create deployment effects;
- invoke providers;
- mutate Governance state;
- mutate Replay state outside evidence emission;
- orchestrate validation;
- orchestrate rollback;
- execute arbitrary shell commands.

Platform Core determines whether Git Remote Worker execution is required.

## 6. Required Git Remote Capability Scope

The first governed Git remote workflow should support:

| Capability | First Scope |
| --- | --- |
| Remote inspection | Read configured remotes and remote URLs without mutation. |
| Branch verification | Verify current branch, target branch, expected local `HEAD`, and local cleanliness requirements. |
| Remote verification | Verify authorized remote name and URL fingerprint. |
| Upstream verification | Verify configured upstream branch or authorized absence of upstream. |
| Fetch | Fetch an authorized remote and branch/refspec. |
| Pull | Pull only when fast-forward-only or explicitly authorized merge behavior is certified. First phase should prefer fast-forward-only. |
| Push | Push only an authorized local commit/ref to an authorized remote branch. |
| Protected branch handling | Require explicit Governance policy and approval for protected branches. |
| Authentication boundary | Record credential reference and credential availability without replaying secrets. |
| Failure handling | Fail closed with replay-visible reason and no automatic retry escalation. |
| Recovery handling | Provide operator-visible recovery guidance; execute recovery only through separate Governance authorization. |

Excluded from first scope:

- merge commits created by pull;
- rebase;
- force push;
- tag creation or push;
- pull request creation;
- remote deletion;
- branch deletion;
- deployment;
- dependency management;
- arbitrary Git command execution.

## 7. Platform Core Interaction Model

Platform Core remains the orchestration authority.

Platform Core responsibilities:

1. detect Git remote intent;
2. determine whether existing certified local commit, validation, or rollback capabilities are prerequisites;
3. request Git remote candidate formation;
4. obtain Governance authorization;
5. coordinate validation prerequisites;
6. dispatch the Git Remote Worker through Worker Platform;
7. collect Replay references;
8. coordinate post-operation validation;
9. present result through ACLI Next.

Platform Core must not:

- execute Git;
- authenticate directly to remotes;
- bypass Worker Platform;
- replace Governance authorization;
- record alternate Replay evidence;
- allow the Git Worker to decide workflow progression.

## 8. Governance Model

Governance remains the sole authorization authority.

Governance must authorize:

- operation type: inspection, fetch, pull, push;
- repository identity;
- remote name;
- remote URL or URL fingerprint;
- local branch;
- remote branch;
- expected local `HEAD`;
- expected remote ref where applicable;
- upstream relationship;
- protected branch policy;
- credential reference;
- validation prerequisites;
- post-operation validation requirements;
- failure handling scope;
- recovery operation scope if any.

Protected operation approval is required for:

- push to protected branch;
- pull that may update protected release branch;
- any operation that changes remote-visible state;
- any operation crossing release discipline boundaries.

Governance must fail closed when:

- remote target is ambiguous;
- branch target is ambiguous;
- protected branch policy is missing;
- credential reference is unavailable;
- local state differs from authorized expected state;
- validation prerequisite is missing or failed;
- operation requested is outside certified scope.

## 9. Replay Model

Replay remains the canonical evidence authority.

Required Replay evidence:

| Evidence | Required Content |
| --- | --- |
| Git remote candidate | Operation type, repository, local branch, remote, remote branch, expected local and remote state. |
| Governance approval | Human or policy approval bound to candidate hash. |
| Authorization | Exact operation, Worker id, scope, remote, branch, credential reference, validation requirements. |
| Pre-state | Current branch, local `HEAD`, cleanliness, remotes, upstream, remote ref snapshot where available. |
| Worker request | Authorized Worker-facing request and request hash. |
| Execution | Git argv class, operation, bounded stdout/stderr, exit code, timeout result. |
| Result | New local state, new remote state where observable, pushed/fetched/pulled refs, no unauthorized side effects. |
| Validation | Pre/post validation result or validation suite result. |
| Failure | Fail-closed reason, failed checkpoint, whether remote state changed. |
| Recovery reference | Rollback/recovery guidance or separately authorized recovery operation reference. |

Replay reconstruction must verify:

- candidate-to-approval binding;
- approval-to-authorization binding;
- authorization-to-Worker request binding;
- operation-to-remote binding;
- operation-to-branch binding;
- credential reference continuity;
- pre-state continuity;
- result continuity;
- validation continuity;
- failure and recovery evidence.

## 10. Validation Integration

Git remote workflow must reuse existing validation capabilities.

Pre-push validation should normally require:

- governed validation suite success;
- local Git commit evidence when pushing a governed commit;
- clean working tree or explicitly authorized file state;
- branch and remote verification.

Post-fetch or post-pull validation should normally require:

- repository state verification;
- conflict absence verification;
- validation suite if code changed locally;
- Architectural Health advisory check when architecture artifacts changed.

Post-push validation should normally require:

- remote ref verification;
- local/remote commit continuity;
- Replay evidence completeness;
- optional release discipline checks if branch is release-bound.

Validation logic must not be duplicated in the Git Remote Worker.

## 11. Rollback And Recovery Integration

Existing rollback runtime covers certified repository mutation recovery, not uncontrolled remote recovery.

Git remote workflow must distinguish:

- local rollback;
- remote recovery;
- operational retry;
- manual external remediation.

First phase policy:

- no automatic rollback of remote operations;
- no automatic force push;
- no automatic reset;
- no automatic branch deletion;
- recovery guidance is allowed;
- recovery execution requires separate Governance authorization and certified Worker support.

Rollback references should be recorded when a remote operation depends on a prior governed local commit or mutation.

## 12. Authentication Boundary

Git authentication must be governed as an operational credential boundary.

Required evidence:

- credential reference;
- credential source class;
- credential availability diagnostic;
- secret not replayed;
- token value not hashed into Replay;
- authorization binding to the exact remote operation;
- failure reason for missing or invalid credential.

The Git Remote Worker must never print or replay credentials.

## 13. Architectural Health Integration

Architectural Health remains advisory only.

Architectural Health should observe:

- Git Worker behavior;
- operation class and scope;
- remote consistency;
- branch policy;
- protected branch handling;
- validation completeness;
- Replay evidence completeness;
- failure and recovery patterns;
- responsibility preservation.

Architectural Health must not:

- authorize Git operations;
- execute repairs;
- retry failed Git operations;
- override Governance;
- mutate branches or remotes.

## 14. Responsibility Verification

| Component | Responsibility | Verification |
| --- | --- | --- |
| ACLI Next | Present and guide. | Must not execute, authorize, or manage Git remotes. |
| Platform Core | Orchestrate workflow. | Determines when Git Remote Worker is needed. |
| Worker Platform | Execute bounded Git operation. | Git Worker executes exact authorized operation only. |
| Provider Platform | Advisory cognition only. | Not required for Git execution. |
| Governance | Authorize. | Owns remote, branch, protected operation, credential, and failure authorization. |
| Replay | Evidence and reconstruction. | Owns Git remote evidence chain. |
| Platform Digital Twin | Architectural projection. | Projects worker identity and evidence, does not execute. |
| Architectural Health | Advisory findings. | Observes drift and policy risks only. |
| Git Worker | Execution only. | No orchestration, authorization, validation ownership, or Replay ownership. |

Responsibility verification result:

```text
No responsibility movement is required.
```

## 15. Future Extensibility

The Git Remote Worker must become one governed Worker implementation, not a special architectural case.

The same pattern should support future workers for:

- dependency management;
- deployment;
- environment management;
- infrastructure operations;
- release publication.

Future operational workers must reuse:

- Platform Core orchestration;
- Governance authorization;
- Worker Platform execution;
- Replay evidence;
- validation suites;
- Architectural Health advisory review.

## 16. Implementation Readiness Assessment

Implementation is ready to proceed after this specification if the first implementation remains narrow:

1. Read-only remote and branch inspection.
2. Fetch with exact remote/ref authorization.
3. Push of an already-governed local commit to an authorized remote branch.
4. Fast-forward-only pull only after fetch/inspection evidence is certified.
5. Protected branch support only after explicit Governance policy.

Recommended first implementation:

```text
Governed Git remote inspection and push of an already governed local commit.
```

Required implementation artifacts:

- Git Remote Worker identity;
- Git remote candidate artifact;
- Governance approval and authorization artifact;
- Worker request artifact;
- Worker execution evidence;
- Replay reconstruction;
- validation integration;
- Architectural Health observation;
- targeted tests.

## 17. Final Determination

Governed Git remote workflow does not already fully emerge from the current certified Worker Platform because remote execution, authentication boundary, branch policy, protected operation handling, and remote-specific Replay evidence are not yet implemented.

However, the certified architecture already provides the correct owners and lifecycle.

Therefore the correct next step is a minimal Git Remote Worker implementation over existing Platform Core, Governance, Worker Platform, Replay, validation, and Architectural Health boundaries.

Final verdict: GOVERNED_GIT_REMOTE_WORKFLOW_SPECIFIED

## 18. Validation Evidence

Validation performed:

```text
git diff --check
```

Validation result: clean.

Final verdict: GOVERNED_GIT_REMOTE_WORKFLOW_SPECIFIED
