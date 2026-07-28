# G36-01 — Intelligent Validation Engine V0

Status: IMPLEMENTED

Date: 2026-07-28

Final capability identifier: `INTELLIGENT_VALIDATION_ENGINE_V0`

## 1. Constitutional Purpose

G36-01 introduces one additive Platform Core planning service:

```text
Normalized Proposed Change
  -> Deterministic Impact Analysis
  -> Affected Component Discovery
  -> Impact Classification
  -> Validation Recommendation
  -> Existing Candidate Composition Boundary
  -> Existing Human Approval Boundary
  -> Existing Governed Validation Pipeline
```

IVE-0 owns only the first four transitions and the replay-visible planning
artifact. It does not construct a validation candidate, record Human Approval,
authorize execution, invoke a Worker or Provider, run tests, modify an
allowlist, or mutate the repository.

## 2. Architecture

The runtime is:

- `aigol/runtime/intelligent_validation_engine_v0.py`

The canonical artifact is:

- `INTELLIGENT_VALIDATION_PLAN_ARTIFACT_V1`

The public operations are:

- `analyze_intelligent_validation_scope(...)`;
- `validate_intelligent_validation_plan_artifact(...)`;
- `reconstruct_intelligent_validation_engine_v0_replay(...)`.

The runtime consumes only a hash-valid, non-failed
`NORMALIZED_CHANGE_ARTIFACT_V1`. Raw dialogue, unbound paths, diffs, pytest
arguments, and free-form test commands are not accepted.

## 3. Reused Constitutional Owners

| Responsibility | Existing owner reused |
| --- | --- |
| Change ingress and canonical path normalization | G27-04 `PLATFORM_CHANGE_NORMALIZATION` |
| Certified capability impact projection | G27-05 `PLATFORM_CHANGE_IMPACT_ANALYSIS` |
| Typed validation requirement planning | G27-07 `PLATFORM_VALIDATION_PLANNING` |
| Candidate construction boundary | G27-09 `PLATFORM_VALIDATION_PLAN_TO_CANDIDATE_COMPOSITION` |
| Candidate Human Approval | Existing Platform Core validation Governance runtimes |
| Governance authorization | Existing Platform Core validation Governance runtimes |
| Validation execution | Existing governed validation runtime and Validation Command Worker |
| Canonical hashing and immutable evidence transport | Existing replay serialization utilities |
| Capability identity and certification metadata | Platform Capability Certification Registry |

IVE-0 does not replace any listed owner.

## 4. Two Deterministic Analysis Strategies

### 4.1 Certified G27 composition

`G27_CERTIFIED_IMPACT_AND_PLANNING` is selected only when every normalized path:

- has exactly one Platform Capability Certification Registry match; and
- is inside the constitutional path domain already accepted by G27-05.

IVE-0 then invokes G27-05 and G27-07 unchanged. Their immutable replay
artifacts are stored below the IVE replay root and bound by reference,
deterministic hash, and artifact hash.

### 4.2 Direct exact-path discovery

`IVE_0_DIRECT_EXACT_PATH_DISCOVERY` is selected when at least one path is
outside G27-05's deliberately narrower domain.

This strategy is necessary for the required Worker, Provider, Authorization,
AiCLI, test-infrastructure, and general documentation surfaces. It:

- validates the same normalized source artifact;
- uses exact repository path families only;
- uses a certification-registry identity only when exactly one match exists;
- otherwise identifies the component by its exact repository path;
- fails closed on multiple registry matches;
- fails closed on an unsupported path family;
- performs no fuzzy, semantic, probabilistic, or natural-language inference.

This is an additive repository-component inventory. It does not widen or alter
G27-05.

## 5. Affected Component Model

Every affected component records:

- `component_identifier`;
- `component_type`;
- `capability_identifier`;
- `target_path`;
- `dependency_origin`;
- `reason_for_inclusion`;
- `classification_rule`;
- `constitutional_layer`;
- source impact or normalized-change entry hash;
- exact certification evidence, when available;
- deterministic `component_hash`.

Supported component types are:

- `PLATFORM_CORE`;
- `REPLAY`;
- `AUTHORIZATION`;
- `WORKER`;
- `PROVIDER`;
- `AICLI`;
- `GOVERNANCE`;
- `TEST_INFRASTRUCTURE`;
- `DOCUMENTATION`.

The overall classification equals the one affected type or
`MULTI_COMPONENT` when more than one type is present.

## 6. Validation Recommendation Model

The recommendation contains explicit requirement families for:

- unit tests;
- integration tests;
- replay validation;
- authorization validation;
- Worker validation;
- Provider validation;
- AiCLI validation;
- full repository regression.

Each requirement binds:

- the validation dimension;
- the component type;
- exact component identifiers;
- component hashes;
- deterministic inclusion reason;
- policy authority.

IVE-0 does not infer a test's unit/integration semantics from its filename.
Concrete test paths are included only if structured certification metadata
already declares them. The current registry declares governance reports as
evidence, so the requirements are normally semantic obligations rather than
invented pytest targets.

Full regression is required for every non-documentation component. A change
containing only non-governance documentation does not automatically require a
full regression. Failure to complete impact analysis requires full regression
and blocks reduced-scope claims.

## 7. Existing Validation Pipeline Handoff

IVE-0 preserves the existing allowlist exactly.

When G27-07 provides exact allowlisted command references, the handoff status is
`READY_FOR_EXISTING_G27_09_CANDIDATE_COMPOSITION`.

When no exact mapping exists, the status is
`PLANNING_ONLY_NO_EXACT_ALLOWLIST_MAPPING`. IVE-0 does not synthesize argv,
infer commands from requirement prose, or expand the allowlist. The plan
remains useful as review evidence, but executable candidate composition remains
fail-closed until the existing pipeline has a separately governed exact
mapping.

Human Approval is not an IVE artifact. The generated downstream candidate must
be approved through the existing validation Governance owner, with approval
bound to the exact candidate hash. Approval alone does not authorize
execution.

## 8. Replay Evidence

IVE-0 writes one immutable wrapper:

```text
000_intelligent_validation_plan_recorded.json
```

When the G27 strategy is used, the replay root also contains:

```text
impact/000_platform_change_impact_recorded.json
validation_plan/000_platform_validation_plan_recorded.json
```

Reconstruction verifies:

- IVE wrapper ordering and hash;
- IVE artifact and deterministic plan hashes;
- component, classification, recommendation, and reasoning hashes;
- all non-authority flags;
- Human Approval requirement;
- G27 replay reconstruction and lineage hashes when G27 is used;
- absence of validation execution and repository mutation.

Failed analysis remains replay-visible. It contains no affected-component
claim, blocks pipeline handoff, requires full regression before any reduced
scope may be claimed, and preserves all non-authority flags.

## 9. Runtime Module Inventory

### Added

| Module | Responsibility |
| --- | --- |
| `aigol/runtime/intelligent_validation_engine_v0.py` | IVE-0 composition, direct exact-path inventory, classification, recommendation, artifact validation, and replay reconstruction |
| `tests/test_g36_01_intelligent_validation_engine_v0.py` | Determinism, classification, recommendation, fail-closed, replay, tamper, and registry certification coverage |

### Additive metadata

| Module | Change |
| --- | --- |
| `aigol/runtime/platform_capability_certification_registry.py` | Adds metadata-only `INTELLIGENT_VALIDATION_ENGINE_V0`; grants no runtime or Human Interface authority |

### Unchanged

- G27-04 normalization;
- G27-05 impact analysis;
- G27-07 validation planning;
- G27-09 candidate composition;
- validation candidate and suite models;
- validation allowlist;
- validation Governance approval and authorization;
- validation execution runtimes;
- Authorization;
- Replay semantics and ownership;
- Workers and Providers;
- AiCLI and Human Interface;
- pytest and repository test orchestration.

## 10. Constitutional Integration Assessment

IVE-0 is an additive planning layer, not an execution-spine revision.

The service can recommend and justify scope without gaining authority. The
existing pipeline remains authoritative for executable candidates, approval,
authorization, Worker invocation, result evidence, and completion.

The Platform Capability Certification Registry addition is metadata-only. It
does not make IVE-0 discoverable through AiCLI, add an execution route, or
grant automatic invocation authority.

## 11. Known Limitations

- IVE-0 discovers direct changed components. It does not claim a transitive
  dependency graph that no certified structured registry currently supplies.
- Direct-path discovery identifies unregistered files by exact repository path,
  not by invented capability identity.
- The current validation allowlist rarely has an exact command target set for
  an IVE recommendation. Those plans remain non-executable until a separately
  governed mapping exists.
- Test-kind metadata is not currently part of capability certification records.
  IVE-0 therefore does not guess unit versus integration test paths.
- IVE-0 does not optimize execution, cache results, schedule parallel work, or
  predict runtime.

These limitations remain visible and fail closed. They define bounded inputs
for IVE-1 through IVE-4 without requiring IVE-0 to own future execution
responsibilities.

## 12. Constitutional Verdict

IVE-0 preserves deterministic semantics, immutable replay-visible evidence,
Human Authority, the existing validation pipeline, Authorization, Worker,
Provider, Replay, and AiCLI boundaries.

Final verdict is recorded in:

- `docs/governance/G36_01_IVE_0_CONSTITUTIONAL_CERTIFICATION_REPORT.md`.
