# G3-01 Release Stabilization Program V1

Status: Generation 3 release stabilization execution program.

Scope: pre-implementation program for the first Generation 3 workstream.

This artifact does not implement runtime changes, modify tests, authorize deployment,
redefine governance, or change release authority.

## 1. Purpose

Platform Core Generation 2 is certified.

Generation 3 has been initiated, the Generation 3 Master Execution Program is defined, and
Product and Operational Priorities are approved. The first implementation workstream is
Release Stabilization.

G3-01 defines how the certified Platform Core becomes a stable governed release baseline
before ACLI, Product 1, provider, worker, deployment, or production certification work
begins.

## 2. Release Objectives

Primary release objective:

```text
Create a deterministic, replay-safe, governance-visible release foundation for all
Generation 3 implementation work.
```

Release objectives:

| Objective | Required Outcome |
| --- | --- |
| Stabilize the G2 certified baseline | Generation 3 starts from a known certified semantic platform core |
| Define release packet requirements | Every future G3 release candidate has deterministic evidence |
| Preserve release topology | Local PC, GitHub, and server roles remain separated |
| Preserve governance and replay | No release can bypass validation, replay, or certification |
| Preserve Product 1 framing | Release evidence keeps AI Decision Validator as canonical product focus |
| Preserve active exceptions | G2 compatibility exceptions remain visible in release evidence |
| Prepare rollback evidence | Rollback is planned before production-facing work begins |

Non-objectives:

- runtime implementation;
- deployment automation;
- server mutation;
- provider activation;
- worker expansion;
- Product 1 runtime completion;
- autonomous release authority.

## 3. Release Evidence Requirements

Every G3 release packet should include:

| Evidence Category | Required Fields |
| --- | --- |
| Release identity | release id, generation, workstream, candidate status, created timestamp |
| Source lineage | commit hash, branch, tag if applicable, parent certification reference |
| Certification state | G2 certification, G3 workstream status, known blockers |
| Validation state | commands run, pass/fail status, skipped tests, generated artifact handling |
| Replay evidence | replay references, replay hashes, reconstruction status, generated artifact inventory |
| CSA and semantic evidence | CSA lineage expectations, G2 semantic certification reference, compatibility exceptions |
| Governance evidence | conformance checks, authority preservation statement, mutation boundary statement |
| Product evidence | Product 1 scope, scenario coverage if applicable, messaging constraints |
| Provider evidence | provider status, invocation status, advisory-only status where applicable |
| Worker evidence | worker status, authorization status, validation status where applicable |
| Rollback evidence | rollback path, restoration target, rollback drill status |
| Known limitations | active exceptions, unresolved risks, out-of-scope domains |

Release evidence must be deterministic, inspectable, and suitable for GitHub lineage as the
governed release registry.

## 4. Required Certification Artifacts

G3-01 should produce or define the following certification artifacts:

| Artifact | Purpose |
| --- | --- |
| G3-01 release evidence inventory | Inventory G2 certification evidence, G3 initiation, priorities, and active exceptions |
| Release packet schema | Define deterministic release packet structure |
| Release validation checklist | Define commands and review gates required before release candidate creation |
| Replay artifact handling policy | Define when generated replay artifacts are cleaned, retained, or packaged |
| Rollback drill specification | Define restoration evidence required before release promotion |
| Release candidate lifecycle specification | Define candidate states and promotion rules |
| G3-01 release stabilization certification | Certify the release foundation is ready for G3-02 |

These artifacts are prerequisites for later Generation 3 implementation workstreams.

## 5. Replay Requirements

Release stabilization must preserve replay as the evidence spine.

Replay requirements:

- release packets must reference replay artifacts by stable path or hash where applicable;
- generated replay artifacts from validation must be explicitly classified as packaged
  evidence or cleaned validation noise;
- historical replay must remain read-only;
- G2 compatibility retirement evidence must remain visible;
- replay reconstruction status must be recorded for covered release candidates;
- rollback drills must record before and after evidence references;
- no release process may reinterpret historical replay under new semantics.

Required replay classifications:

| Classification | Meaning |
| --- | --- |
| Packaged evidence | Replay artifact intentionally retained as release evidence |
| Validation noise | Generated artifact cleaned after validation |
| Historical reference | Existing replay artifact referenced but not modified |
| Rollback evidence | Replay or release artifact proving restoration path |
| Blocker evidence | Replay artifact that exposes failure, corruption, or incomplete lineage |

## 6. Governance Checkpoints

Required governance checkpoints:

| Checkpoint | Required Review |
| --- | --- |
| Constitutional boundary | Release does not redefine governance, invariants, or mutation layers |
| Authority preservation | UBTR, CSA, governance, approval, provider, worker, PPP, OCS, lifecycle, execution, and replay boundaries remain intact |
| Product framing | Product 1 remains AI Decision Validator |
| Release topology | Local PC, GitHub, and server responsibilities remain distinct |
| Validation integrity | Required validation commands are recorded with outcomes |
| Replay integrity | Replay artifacts are handled deterministically |
| Compatibility exceptions | G2 active exceptions remain visible |
| Known limitations | Limitations are disclosed rather than hidden |
| Human approval | Promotion to governed demo or stable release requires human approval |

Governance checkpoint failure must block release promotion.

## 7. Release Candidate Lifecycle

Release candidate states:

```text
DRAFT -> VALIDATION_READY -> VALIDATED -> EVIDENCE_PACKAGED -> REVIEW_READY ->
APPROVED_FOR_GITHUB_RELEASE -> RELEASE_CANDIDATE -> DEMO_DEPLOYMENT_READY ->
STABLE_GOVERNED_RELEASE
```

State requirements:

| State | Entry Requirement | Exit Requirement |
| --- | --- | --- |
| DRAFT | Workstream scope defined | Release evidence inventory started |
| VALIDATION_READY | Validation checklist complete | Required commands run |
| VALIDATED | Validation passes or failures documented | Generated artifacts classified |
| EVIDENCE_PACKAGED | Evidence packet assembled | Replay and rollback references checked |
| REVIEW_READY | Governance checklist complete | Human review recorded |
| APPROVED_FOR_GITHUB_RELEASE | Human approval recorded | Commit/tag lineage prepared |
| RELEASE_CANDIDATE | GitHub lineage established | Deployment readiness review begins |
| DEMO_DEPLOYMENT_READY | Server rehearsal and rollback plan complete | Human demo activation approval recorded |
| STABLE_GOVERNED_RELEASE | Demo activation and rollback evidence complete | Production certification can consume evidence |

G3-01 only defines and certifies this lifecycle. Later workstreams exercise it.

## 8. Regression Strategy

G3-01 is documentation-only, so it requires only `git diff --check`.

Later release stabilization implementation batches should use this regression strategy:

| Change Type | Required Validation |
| --- | --- |
| Documentation-only release artifact | `git diff --check` |
| Release packet schema/runtime | `git diff --check`, `py_compile`, targeted schema tests, full pytest |
| Replay artifact handling runtime | `git diff --check`, `py_compile`, targeted replay tests, full pytest |
| Governance conformance changes | governance conformance tests, conformance engine, full pytest |
| ACLI release command | targeted ACLI tests, replay tests, full pytest |
| Deployment readiness artifact | release packet validation, rollback rehearsal checks, full pytest if runtime changes |

Regression output must be captured in release evidence.

## 9. Operational Acceptance Criteria

G3-01 is operationally accepted when:

1. Release objectives are defined.
2. Release evidence requirements are defined.
3. Required certification artifacts are listed.
4. Replay handling rules are defined.
5. Governance checkpoints are defined.
6. Release candidate lifecycle is defined.
7. Regression strategy is defined.
8. Operational readiness criteria are defined.
9. Rollback strategy is defined.
10. Exit criteria for G3-01 are defined.

The acceptance result is program readiness, not release completion.

## 10. Rollback Strategy

Rollback strategy:

| Rollback Surface | Strategy |
| --- | --- |
| Documentation artifact | Revert or supersede through governed commit lineage |
| Release packet schema | Preserve previous schema and record migration note |
| Release candidate | Restore previous validated candidate and retain failed candidate evidence |
| Generated replay artifacts | Clean validation noise or preserve packaged evidence intentionally |
| GitHub release lineage | Use governed corrective commit or tag supersession |
| Server activation | Restore prior stable release only after rollback evidence is recorded |

Rollback requirements:

- rollback must not rewrite historical replay;
- rollback must preserve failed release evidence;
- rollback must identify restoration target;
- rollback must record validation status after restoration;
- rollback must preserve Product 1 and authority boundary statements.

## 11. Exit Criteria For G3-01

G3-01 exits successfully when the following are complete:

| Exit Criterion | Required Evidence |
| --- | --- |
| Release roadmap defined | This program artifact |
| Release evidence model defined | Section 3 |
| Certification artifacts identified | Section 4 |
| Replay requirements defined | Section 5 |
| Governance checkpoints defined | Section 6 |
| Candidate lifecycle defined | Section 7 |
| Regression strategy defined | Section 8 |
| Operational acceptance criteria defined | Section 9 |
| Rollback strategy defined | Section 10 |
| Validation passed | `git diff --check` |

Exit verdict:

```text
G3_01_RELEASE_STABILIZATION_PROGRAM_READY
```

## 12. Dependencies On Later Generation 3 Workstreams

G3-01 provides the release foundation consumed by:

| Later Workstream | Dependency On G3-01 |
| --- | --- |
| G3-02 ACLI conversational development | ACLI release commands and validation evidence must use release packet rules |
| G3-03 Product 1 operationalization | Product 1 scenarios must package evidence into release packets |
| G3-04 real provider activation | Provider invocation evidence must be release-packet compatible |
| G3-05 worker ecosystem expansion | Worker contract and execution evidence must be release-packet compatible |
| G3-06 deployment readiness | Deployment candidates depend on release lifecycle states |
| G3-07 production certification | Final certification consumes all release packets, rollback evidence, and validation records |

No later workstream should bypass the release evidence model established by G3-01.

## 13. Recommended Next Step

After this program is approved, the next batch should be:

```text
G3-01A_RELEASE_EVIDENCE_INVENTORY_AND_PACKET_SCHEMA_V1
```

Expected scope:

- inventory certified G2 and G3 initiation evidence;
- define the first deterministic release packet schema;
- define generated replay artifact handling rules;
- produce release packet validation criteria;
- remain documentation-only unless schema validation runtime is explicitly requested.

## 14. Final Verdict

```text
G3_01_RELEASE_STABILIZATION_PROGRAM_READY
```
