# G11-09 Governed Dependency Management Workflow Specification V1

Status: governed dependency management workflow specified.

Final verdict: GOVERNED_DEPENDENCY_MANAGEMENT_WORKFLOW_SPECIFIED

## 1. Executive Summary

Generation 11 has certified governed Git remote workflow architecture. The next operational gap is dependency management: package inspection, installation, update, removal, lock synchronization, and environment verification still require external terminal execution.

This specification defines governed dependency management as a minimal operational extension of the certified Worker Platform.

Canonical architectural position:

```text
Dependency management is bounded Worker Platform execution.
```

Dependency management is not a new Platform Core subsystem, not an ACLI Next capability, not a Governance subsystem, not a Replay subsystem, and not a Provider Platform authority.

Platform Core continues to orchestrate. Governance continues to authorize. Replay continues to record evidence. Worker Platform executes. Architectural Health observes. ACLI Next presents and guides.

Final finding:

```text
Governed dependency management requires a bounded Dependency Management Worker capability, but no new architecture.
```

## 2. Governed Development Workflow Compliance

This specification applies the certified Governed Development Workflow:

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
| Platform Core | Certified orchestration authority for governed development, mutation, validation, rollback, Git commit, Git remote workflow, and operational snapshots. | Reuse for routing dependency intent, coordinating authorization, dispatch, validation, rollback preparation, and result presentation. |
| ACLI Next | Certified primary human interface, conversational UX, dashboard, and hybrid guidance layer. | Reuse for dependency request capture, status presentation, approval prompts, Replay references, and external exception guidance only. |
| Worker Platform | Certified bounded execution, worker registration, dispatch, invocation, completion, and failure reporting. | Reuse for Dependency Management Worker registration and execution. |
| Provider Platform | Certified non-authoritative cognition/provider boundary. | Not required for package-manager execution; providers may offer advisory explanation only when separately governed. |
| Governance | Certified approval and authorization authority. | Reuse for package operation authorization, registry policy, credential references, protected dependency handling, and execution approval. |
| Replay | Certified evidence and reconstruction authority. | Reuse for dependency intent, authorization, execution, package-manager output, manifest and lockfile changes, validation, rollback references, and failure evidence. |
| Platform Digital Twin | Canonical architectural evidence projection. | Reuse to project Dependency Management Worker identity, boundaries, policy evidence, and certified integration state. |
| Architectural Health | Deterministic advisory checkpoint. | Reuse to observe dependency consistency, unsupported package-manager states, policy violations, version conflicts, and responsibility preservation. |
| Governed Development Workflow | Certified development lifecycle. | Reuse as the only path for dependency capability implementation and certification. |
| Worker registration | Certified worker identity registration model. | Reuse for Dependency Management Worker identity. |
| Worker dispatch | Certified replay-visible dispatch model. | Reuse before package-manager execution. |
| Execution authorization | Certified Governance-owned authorization records. | Reuse for exact dependency operation authorization. |
| Validation runtime | Certified governed validation command execution. | Reuse for dependency verification and post-change validation where commands are allowlisted. |
| Validation suites | Certified deterministic validation suite composition. | Reuse for ordered validation after dependency changes. |
| Rollback runtime | Certified governed rollback execution for supported repository mutations. | Reuse for manifest and lockfile rollback when supported; do not imply automatic environment rollback. |
| Git Worker | Certified local and remote Git operational execution. | Reuse after dependency validation for commit or remote publication; do not use Git Worker for dependency execution. |
| Environment management | Not yet certified as a general operational capability. | Dependency management may verify environment consistency, but broad environment administration remains out of scope. |

Audit conclusion:

```text
The architecture already provides the required ownership model, but dependency execution itself is not yet certified.
```

The missing behavior is a bounded dependency execution worker, package-manager policy envelope, registry and credential boundary evidence, lockfile-aware result evidence, and dependency-specific failure handling.

## 4. Existing Capability Reuse Assessment

Governed dependency management must reuse existing certified capabilities instead of creating a new workflow.

Required reuse:

- Platform Core orchestration;
- ACLI Next presentation and guided request capture;
- Governance authorization records;
- Worker Platform registration, dispatch, execution lifecycle, completion, and failure reporting;
- Replay evidence and reconstruction;
- validation runtime and validation suites;
- rollback metadata and governed rollback where repository-file rollback is certified;
- Architectural Health advisory observations;
- Platform Digital Twin architectural projection.

Forbidden duplication:

- no dependency orchestration inside ACLI Next;
- no package-manager execution inside Platform Core;
- no package approval logic inside Worker Platform;
- no package policy decisions inside Replay;
- no separate dependency evidence ledger;
- no provider-driven dependency execution;
- no package-manager shell execution outside certified Worker allowlists;
- no automatic deployment, environment mutation, or Git publication as a side effect.

## 5. Dependency Worker Architectural Position

Canonical Worker identity:

```text
GOVERNED_DEPENDENCY_MANAGEMENT_WORKER
```

Canonical scope:

```text
BOUNDED_DEPENDENCY_OPERATION
```

The Dependency Management Worker owns execution only.

It may execute only the exact authorized package-manager operation against the exact authorized manifest, lockfile, package identity, version constraint, registry boundary, and environment context.

It must not:

- choose dependencies;
- choose package versions;
- authorize registry access;
- approve private credentials;
- decide validation sufficiency;
- decide rollback sufficiency;
- mutate Governance state;
- mutate Replay state outside evidence emission;
- invoke providers;
- deploy artifacts;
- perform Git commit or Git remote operations;
- execute arbitrary shell commands;
- broaden its package-manager scope after authorization.

Platform Core determines whether Dependency Management Worker execution is required.

## 6. Required Dependency Capability Scope

The first governed dependency management workflow should support these operation classes:

| Operation Class | First Certified Scope |
| --- | --- |
| Dependency inspection | Inspect manifests, lockfiles, package manager identity, package manager version, and dependency graph metadata without mutation. |
| Dependency install | Install an explicitly authorized package identity and version or version constraint through an authorized package manager. |
| Dependency update | Update explicitly authorized package identities or lockfile scopes only. |
| Dependency removal | Remove explicitly authorized package identities from authorized manifests and lockfiles. |
| Dependency verification | Verify installed dependency state, lockfile consistency, and package-manager consistency. |
| Lock synchronization | Regenerate or synchronize lockfiles only when the exact manifest and lockfile set is authorized. |
| Environment consistency verification | Verify environment consistency for the authorized project context without broad environment administration. |
| Package manager selection | Select from an authorized package manager candidate derived from repository evidence and Governance authorization. |
| Private registry access | Use credential references and registry fingerprints without replaying secrets. |
| Failure handling | Fail closed with replay-visible reason, bounded output, and no automatic retry escalation. |
| Rollback preparation | Record manifest, lockfile, and environment evidence sufficient for governed rollback where rollback is certified. |

Excluded from first scope:

- unrestricted package-manager commands;
- arbitrary scripts from package managers;
- deployment;
- container mutation;
- operating-system package installation;
- global package installation;
- automatic environment provisioning;
- credential creation;
- provider invocation;
- broad transitive dependency updates without explicit policy;
- automatic rollback of installed runtime environments;
- Git commit or push side effects.

## 7. Package Manager Model

Dependency management should support a package-manager adapter model under one Worker Platform boundary.

Initial ecosystem classes:

| Ecosystem | Candidate Package Managers | Required Boundary |
| --- | --- | --- |
| Python | `pip`, `uv`, `poetry` | Authorized project environment, manifest, lockfile, package identity, and index/registry boundary. |
| Node | `npm`, `pnpm`, `yarn` | Authorized project workspace, manifest, lockfile, package identity, and registry boundary. |
| Future ecosystems | Future package managers | Must implement the same authorization, execution, evidence, and validation contract before certification. |

Package-manager-specific behavior remains a Worker implementation detail.

The common governed contract remains stable:

```text
authorized dependency intent
->
authorized package manager
->
bounded Worker execution
->
Replay evidence
->
validation suite
->
Architectural Health advisory observation
```

## 8. Platform Core Interaction Model

Platform Core remains the orchestration authority.

Platform Core responsibilities:

1. detect dependency-management intent;
2. determine whether dependency execution is required;
3. identify existing certified capabilities that should be composed;
4. request or receive a dependency operation candidate;
5. coordinate Governance authorization;
6. coordinate pre-execution validation or inspection when required;
7. dispatch the Dependency Management Worker through Worker Platform;
8. collect Replay references;
9. coordinate post-operation validation suites;
10. coordinate rollback preparation where applicable;
11. expose result state to ACLI Next;
12. preserve Governed Development Workflow continuity.

Platform Core must not:

- execute package managers;
- select unauthorized package versions;
- bypass Governance;
- bypass Worker Platform;
- record alternate Replay evidence;
- perform dependency policy decisions that belong to Governance;
- treat dependency execution as deployment.

## 9. Governance Model

Governance remains the sole authorization authority.

Governance must authorize:

- operation class;
- package manager;
- package identity;
- requested version, version constraint, or lockfile scope;
- project root;
- manifest paths;
- lockfile paths;
- registry or index boundary;
- credential reference for private registries;
- network access allowance;
- protected dependency handling;
- allowed transitive change policy;
- expected file mutation set;
- validation requirements;
- rollback preparation requirements;
- timeout and output bounds;
- failure handling policy.

Governance must fail closed when:

- package identity is ambiguous;
- package-manager scope is broader than authorized;
- manifest or lockfile paths are not authorized;
- registry source is unknown or unauthorized;
- private credentials are required but not authorized;
- transitive changes exceed policy;
- package-manager scripts would execute outside certified policy;
- validation requirements are missing;
- rollback preparation is insufficient for the requested mutation.

Governance does not execute package managers.

## 10. Replay Model

Replay remains the evidence and reconstruction authority.

Replay evidence must include:

- dependency request intent;
- dependency operation candidate;
- Governance approval and authorization reference;
- Worker identity;
- package-manager identity and version;
- package identity and requested version or constraint;
- manifest path and pre-hash;
- lockfile path and pre-hash where present;
- registry or index fingerprint;
- credential reference metadata without secrets;
- authorized operation class;
- execution argv class and bounded command representation;
- timeout and output bounds;
- stdout and stderr summaries within bounds;
- exit code;
- changed manifest and lockfile paths;
- post-hashes;
- validation suite reference;
- validation outcome;
- rollback metadata reference;
- failure reason when fail-closed behavior occurs;
- Architectural Health advisory reference where applicable.

Replay must not:

- store secrets;
- authorize dependency changes;
- execute package managers;
- infer package policy;
- substitute for validation;
- substitute for rollback execution.

## 11. Validation Integration

Dependency management must compose existing validation capabilities.

Validation requirements:

- pre-operation inspection when package-manager state is uncertain;
- post-operation manifest and lockfile integrity checks;
- package-manager verification where the command is certified or executed through the Dependency Management Worker;
- existing validation suites appropriate to the affected project surface;
- targeted tests when dependency changes affect runtime code;
- `git diff --check` when repository files are modified;
- replay-visible validation summary.

Validation remains owned by the certified validation runtime and validation suite model.

The Dependency Management Worker may perform package-manager verification as an authorized dependency operation, but it must not replace governed validation suite orchestration.

## 12. Rollback Integration

Dependency management must prepare rollback evidence.

Rollback preparation includes:

- manifest pre-state;
- lockfile pre-state;
- package-manager metadata;
- changed file set;
- post-operation hashes;
- rollback candidate references;
- validation results needed to evaluate rollback safety.

Governed rollback execution remains a separate authorized workflow.

The Dependency Management Worker must not automatically rollback dependency changes unless a separately certified and authorized rollback operation exists.

Environment-level rollback is not certified by this specification.

## 13. Architectural Health Integration

Architectural Health remains deterministic and advisory only.

Architectural Health should observe:

- dependency consistency;
- lockfile drift;
- manifest and lockfile mismatch;
- unsupported package-manager state;
- private registry boundary visibility;
- dependency policy violations;
- version conflict indicators;
- transitive change risk;
- missing validation;
- missing rollback metadata;
- responsibility preservation.

Architectural Health must not:

- approve dependencies;
- block or authorize execution;
- execute repairs;
- select versions;
- mutate manifests or lockfiles;
- become a package policy authority.

Architectural Health findings are mandatory advisory input for later architecture review and certification.

## 14. Responsibility Verification

| Component | Certified Responsibility | Dependency Management Boundary |
| --- | --- | --- |
| ACLI Next | Human interaction, dashboard, conversational guidance, presentation. | Captures requests and displays state only. No execution, authorization, orchestration, or evidence ownership. |
| Platform Core | Orchestration and capability composition. | Coordinates dependency workflow and dispatches Worker execution only after Governance authorization. |
| Governance | Authorization, approval, admissibility, policy decisions. | Authorizes exact dependency operation and registry/package policy. |
| Replay | Evidence, execution history, reconstruction. | Records dependency operation evidence and reconstruction references. |
| Worker Platform | Bounded execution. | Executes exact authorized package-manager operation through Dependency Management Worker. |
| Dependency Management Worker | Bounded package-manager execution. | Executes only authorized operation class and reports evidence. |
| Provider Platform | Non-authoritative cognition/provider boundary. | No execution authority; advisory provider use remains separate and governed. |
| Platform Digital Twin | Canonical architectural evidence projection. | Projects worker identity, boundary evidence, and certification state. |
| Architectural Health | Deterministic advisory findings. | Observes dependency consistency and responsibility preservation only. |
| Human Authority | Final approval and constitutional authority. | Approves governed changes and operational risk acceptance where required. |

Responsibility movement required:

```text
None.
```

The specification preserves all certified ownership boundaries.

## 15. Hybrid Transition Model

Until dependency management is implemented and certified, ACLI Next must treat package-manager work as a bounded hybrid exception.

When a request exceeds certified dependency capabilities, ACLI Next should present:

- why external execution is required;
- the package-manager operation that remains outside certification;
- the governance evidence that should be preserved;
- the Replay continuity expectation;
- the return point into the Governed Development Workflow.

After governed dependency management is certified, the same requests should remain inside ACLI Next and Platform Core unless they exceed the certified package-manager, registry, or environment scope.

## 16. Future Extensibility

Future operational capabilities should extend the same model:

- container dependency management;
- operating-system package management;
- infrastructure dependency management;
- cloud dependency or provider module management;
- deployment prerequisite package verification;
- environment provisioning;
- private registry policy expansion.

Each future extension must:

- use Platform Core orchestration;
- use Governance authorization;
- use Worker Platform execution;
- use Replay evidence;
- use Architectural Health advisory review;
- preserve ACLI Next as a thin interface;
- avoid introducing a new authority layer or orchestration engine.

## 17. Implementation Readiness

Governed dependency management is ready for implementation specification and subsequent implementation as a bounded Worker Platform extension.

Recommended implementation sequence:

1. Define Dependency Management Worker request and result schemas.
2. Register `GOVERNED_DEPENDENCY_MANAGEMENT_WORKER`.
3. Implement dependency inspection and verification first.
4. Implement lockfile-aware install, update, and removal for explicitly authorized operations.
5. Integrate Governance authorization records.
6. Integrate Replay evidence and reconstruction references.
7. Integrate validation suite sequencing through Platform Core.
8. Integrate rollback metadata preparation.
9. Add Architectural Health advisory observations.
10. Certify architecture before expanding package-manager scope.

Initial implementation should favor inspection, verification, and exact package operations over broad update commands.

## 18. Final Determination

Governed dependency management does not require a new Platform Core subsystem.

The certified architecture already provides the necessary orchestration, authorization, execution, evidence, validation, rollback preparation, dashboard, and advisory checkpoints.

The missing capability is a bounded Dependency Management Worker and dependency-specific policy/evidence envelope.

Final verdict:

```text
GOVERNED_DEPENDENCY_MANAGEMENT_WORKFLOW_SPECIFIED
```

## 19. Validation Evidence

Validation performed:

```text
git diff --check
```

Validation result: clean.

Final verdict: GOVERNED_DEPENDENCY_MANAGEMENT_WORKFLOW_SPECIFIED
