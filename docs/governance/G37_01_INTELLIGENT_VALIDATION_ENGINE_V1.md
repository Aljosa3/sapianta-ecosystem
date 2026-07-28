# G37-01 — Intelligent Validation Engine V1

Status: IMPLEMENTED

Date: 2026-07-28

Capability identifier: `INTELLIGENT_VALIDATION_ENGINE_V1`

## 1. Purpose

IVE-1 extends certified IVE-0 with deterministic semantic validation selection:

```text
IVE-0 Intelligent Validation Plan
  -> Explicit Semantic Dependency Model
  -> Direct Validation Subjects
  -> Declared Transitive Dependency Closure
  -> Direct and Transitive Validation Requirements
  -> Existing Candidate Composition Boundary
  -> Existing Human Approval Boundary
  -> Existing Governed Validation Pipeline
```

IVE-1 selects and explains validation scope. It does not construct a candidate,
approve a candidate, authorize execution, invoke a Worker or Provider, execute
tests, modify pytest, parallelize validation, or mutate the repository.

## 2. Runtime and Artifacts

Runtime:

- `aigol/runtime/intelligent_validation_engine_v1.py`

Canonical artifacts:

- `SEMANTIC_VALIDATION_DEPENDENCY_MODEL_V1`;
- `SEMANTIC_VALIDATION_SELECTION_ARTIFACT_V1`.

Public operations:

- `semantic_validation_dependency_model()`;
- `validate_semantic_validation_dependency_model(...)`;
- `select_semantic_validation_scope(...)`;
- `validate_semantic_validation_selection_artifact(...)`;
- `reconstruct_semantic_validation_selection_replay(...)`.

The only semantic input to selection is a validated, non-failed
`INTELLIGENT_VALIDATION_PLAN_ARTIFACT_V1`. IVE-1 verifies the IVE-0 analysis
reference, deterministic plan hash, and artifact hash.

## 3. Semantic Dependency Model

The model contains two explicit edge families.

### 3.1 Certified capability-composition dependencies

Capability edges are derived from:

- G20-03 `KNOWN_COMPOSITION_DEPENDENCIES`; and
- the canonical Generation Certification evidence profile.

Each edge declares:

```text
required capability changes
  -> dependent certified composition requires validation
```

For example:

```text
PLATFORM_KNOWLEDGE_RUNTIME
  -> UNIFIED_PLATFORM_QUERY_ROUTER
  -> CANONICAL_PLATFORM_PRESENTATION_LAYER
  -> GENERATION_CERTIFICATION_COMPOSITION_SERVICE
```

The implementation reverses declared `dependent -> required` composition
metadata only for validation propagation. It does not invent capability
relationships.

### 3.2 Constitutional component validation dependencies

The immutable G37-01 model declares exact component-type relationships:

```text
AICLI
  -> PLATFORM_CORE
  -> GOVERNANCE
  -> AUTHORIZATION
  -> PROVIDER
  -> WORKER
  -> REPLAY
```

Additional direct edges preserve shorter constitutional relationships, such as
Platform Core to Replay, Governance to Replay, Authorization to Worker, and
Provider to Replay.

Every edge records:

- source and dependent component;
- propagation semantics;
- deterministic reason;
- dependency origin;
- constitutional authority references;
- edge hash.

The model is immutable, replay-visible, non-authoritative, hash-bound, and
acyclic. A model differing from the canonical edge set fails closed even if it
has been rehashed.

## 4. Why the Cognition Relationship Index Is Not Reused

`aigol/cognition/semantic_relationship_index.py` explicitly declares:

- no executable graph semantics;
- no hidden inference;
- no semantic reasoning;
- no planning authority.

IVE-1 does not reinterpret that index as a dependency graph. G20-03's declared
composition metadata and the new explicit constitutional validation model are
the appropriate bounded authorities.

## 5. Deterministic Selection

IVE-1 first preserves every IVE-0 affected component as a `DIRECT` validation
subject.

It then performs cycle-safe traversal over declared edges only. For each
reachable dependency, it records:

- `TRANSITIVE` scope;
- dependency kind (`CAPABILITY` or `COMPONENT_TYPE`);
- direct origin;
- dependent identifier;
- ordered dependency path;
- ordered edge hashes;
- path length;
- deterministic reason;
- dependency model hash;
- dependency hash.

Where multiple declared paths reach the same target from the same origin,
IVE-1 selects the shortest path. Equal-length paths are resolved by canonical
lexical ordering of nodes and edge hashes. The result is independent of input
dictionary order, selection identifier, timestamp, or replay directory.

Direct subjects take precedence. A component or capability already directly
affected is not duplicated as a transitive target.

## 6. Validation Requirements

IVE-1 preserves all direct IVE-0 requirements and labels them `DIRECT`.

For transitive component types, it applies the same certified IVE-0 validation
dimension policy. For transitive certified capabilities, it adds an explicit
`CAPABILITY_REGRESSION` requirement bound to:

- IVE-0 plan hash;
- current capability certification-record hash;
- transitive dependency hashes.

Every selected requirement records:

- direct or transitive scope;
- validation dimension;
- subject kind and identifier;
- source evidence hashes;
- dependency evidence hashes;
- deterministic reason;
- required status;
- stable index and identifier;
- requirement hash.

IVE-1 does not infer test paths from filenames or prose. Concrete evidence
targets and exact allowlisted command references are carried forward unchanged
from IVE-0. No argv or validation command is synthesized.

IVE-1 never reduces IVE-0's full-regression requirement.

## 7. Human Approval and Execution Boundary

IVE-1 preserves the IVE-0 Human Approval object exactly.

The downstream existing candidate must still be created through G27-09 where
an exact allowlisted mapping exists. Existing validation Governance must bind
Human Approval to the exact candidate hash. Existing authorization and
governed validation runtimes remain unchanged.

IVE-1 records:

- `human_approval_required = true`;
- `human_approval_recorded = false`;
- `validation_candidate_constructed = false`;
- `validation_executed = false`;
- `authorization_invoked = false`;
- `worker_invoked = false`;
- `provider_invoked = false`;
- all authority flags false.

## 8. Replay Evidence

Each IVE-1 selection writes two immutable wrappers:

```text
000_ive_0_plan_bound.json
001_semantic_validation_selection_recorded.json
```

Replay reconstruction validates:

- wrapper ordering and hashes;
- the complete IVE-0 source artifact;
- source reference, plan hash, and artifact hash;
- the canonical dependency model;
- direct subject hashes;
- transitive path and edge hashes;
- requirement ordering and hashes;
- recomputed direct subjects, dependency closure, and requirements;
- Human Approval and all non-authority boundaries.

Failed source binding remains replay-visible, blocks handoff, contains no scope
claim, and requires full regression before any reduced scope may be claimed.

## 9. Runtime Inventory

### Added

| Module | Responsibility |
| --- | --- |
| `aigol/runtime/intelligent_validation_engine_v1.py` | Dependency model, deterministic traversal, semantic selection, artifact validation, immutable replay, and reconstruction |
| `tests/test_g37_01_intelligent_validation_engine_v1.py` | Model, direct/transitive selection, capability composition, determinism, failure, replay, tamper, and registry coverage |

### Additive metadata

| Module | Change |
| --- | --- |
| `aigol/runtime/platform_capability_certification_registry.py` | Adds metadata-only `INTELLIGENT_VALIDATION_ENGINE_V1`; grants no execution or Human Interface authority |

### Unchanged

- IVE-0 runtime and artifact semantics;
- G20-03 composition coverage behavior;
- cognition semantic relationship index;
- G27 impact, planning, and candidate composition;
- validation allowlist;
- Human Approval and Governance authorization;
- Replay ownership and semantics;
- Worker and Provider execution;
- AiCLI and Human Interface;
- pytest and repository test orchestration.

## 10. Limitations

- Transitive scope is complete only for relationships explicitly declared by
  the canonical model. Unknown relationships remain unknown.
- The capability graph currently covers the certified G20 composition family.
  IVE-1 does not parse Python imports or infer hidden dependencies.
- Component-type dependencies are constitutional validation relationships, not
  runtime call-graph claims.
- IVE-1 improves semantic requirement precision but does not add executable
  allowlist mappings.
- No caching, scheduling, parallelization, failure replay orchestration, or
  automatic execution is introduced.

## 11. Verdict Reference

Final certification is recorded in:

- `docs/governance/G37_01_IVE_1_CONSTITUTIONAL_CERTIFICATION_REPORT.md`.
