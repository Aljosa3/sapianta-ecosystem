# G39-01 — Intelligent Validation Engine V2

Status: CERTIFIED

Version: V1

Date: 2026-07-28

Capability identifier: `INTELLIGENT_VALIDATION_ENGINE_V2`

## 1. Purpose

IVE-2 adds deterministic parallel-validation scheduling recommendations above
the certified G38 planning entry:

```text
G38 Intelligent Validation Planning Entry
                    |
                    v
        verify G38 replay lineage
                    |
                    v
        bind certified IVE-1 model
                    |
                    v
 group requirements by constitutional subject
                    |
                    v
 deterministic dependency waves and independence evidence
                    |
                    v
 immutable recommendation only
```

IVE-2 does not schedule runtime work. It identifies which groups are eligible
for later parallel consideration after the existing candidate, Human Approval,
Authorization, and validation-runtime boundaries have independently admitted
that work.

## 2. Canonical Entry

The public function is:

```python
recommend_parallel_validation_schedule(
    schedule_id=...,
    session_id=...,
    g38_validation_plan_artifact=...,
    g38_validation_plan_reference=...,
    g38_validation_plan_hash=...,
    g38_replay_dir=...,
    created_by=...,
    created_at=...,
    replay_dir=...,
)
```

The function:

1. validates the unchanged G38 artifact;
2. binds the G38 reference and deterministic planning-entry hash;
3. reconstructs the immutable G38 replay;
4. validates the nested unchanged IVE-1 semantic-selection artifact;
5. validates the canonical IVE-1 dependency model;
6. verifies every requirement subject and dependency-evidence hash;
7. derives deterministic groups, dependency edges, waves, and independence
   evidence;
8. records an immutable recommendation.

## 3. Scheduling Model

### 3.1 Validation groups

Requirements are grouped by their existing constitutional subject:

- component type;
- certified dependent capability.

All requirements for one subject remain sequential within that subject group.
IVE-2 does not claim that unit, integration, Replay, Authorization, Worker,
Provider, AiCLI, or capability-regression requirements for the same subject
are mutually independent.

### 3.2 Dependency edges

IVE-2 uses only:

- canonical IVE-1 component-type dependency edges;
- canonical IVE-1 certified-capability dependency edges;
- a conservative component-to-capability namespace barrier.

Cross-namespace parallelism is prohibited. Capability groups cannot be placed
in a wave until every selected component group has completed.

### 3.3 Waves

The scheduler uses deterministic topological waves. A wave containing multiple
groups is marked:

```text
PARALLEL_ELIGIBLE_AFTER_EXISTING_APPROVAL_AND_AUTHORIZATION
```

This is an eligibility recommendation, not dispatch authority. A single-group
wave is marked:

```text
SEQUENTIAL_SINGLE_GROUP
```

Ordering is canonical and independent of input dictionary order.

### 3.4 Full regression

When G38 requires full repository regression, IVE-2 adds an explicit terminal
barrier:

```text
IVE-2-FULL-REGRESSION-BARRIER
```

The barrier depends on every other recommended group, is always a
single-group sequential wave, and is never parallelized.

## 4. Independence Evidence

For each pair placed in one parallel-eligible wave, IVE-2 records:

- both immutable group identities and hashes;
- their shared dependency namespace;
- the canonical dependency-model hash;
- absence of a dependency path in both directions;
- the model-scoped independence basis;
- confirmation that unknown-dependency inference was not used.

The independence claim is deliberately bounded:

```text
CANONICAL_DECLARED_DEPENDENCY_MODEL_ONLY
```

It is not a claim that arbitrary undeclared runtime behavior is independent.

## 5. Unknown Dependency Policy

IVE-2 fails closed when it encounters:

- an unknown requirement subject kind;
- an unknown component type;
- an unknown certified-capability node;
- missing dependency evidence;
- dependency evidence bound to the wrong subject;
- an unknown dependency kind or edge;
- cross-namespace independence;
- cyclic or unresolved scheduling edges;
- altered G38 or IVE-1 lineage.

A failed schedule contains no groups, waves, or independence claims, recommends
zero concurrency, requires full regression, and blocks pipeline handoff.

## 6. Canonical Artifact

The output artifact is:

```text
PARALLEL_VALIDATION_SCHEDULE_ARTIFACT_V1
```

It binds:

- G38 reference, planning-entry hash, artifact hash, and replay hash;
- IVE-1 reference, selection hash, artifact hash, and dependency-model hash;
- immutable validation groups;
- topological waves;
- pairwise independence evidence;
- maximum recommended concurrency;
- unchanged full-regression policy;
- unchanged allowlisted command references;
- unchanged pipeline handoff;
- unchanged Human Approval object;
- all non-authority boundaries.

The artifact contains deterministic `schedule_hash` and `artifact_hash`
values.

## 7. Replay

IVE-2 writes three immutable wrappers:

```text
000_g38_validation_plan_bound.json
001_ive_1_semantic_selection_bound.json
002_parallel_validation_schedule_recorded.json
```

Reconstruction validates:

- wrapper order and hashes;
- the complete G38 source artifact;
- the complete IVE-1 source artifact and dependency model;
- G38-to-IVE-1 lineage;
- group, wave, and independence hashes;
- deterministic schedule recomputation;
- full-regression, handoff, and Human Approval continuity;
- all non-authority flags.

Replay protocol and ownership are unchanged. IVE-2 owns only its additive
artifact family.

## 8. Human Approval and Execution Boundary

IVE-2 preserves the G38 Human Approval object exactly:

- approval remains required before execution;
- approval is not recorded by IVE-2;
- approval must bind the exact downstream candidate hash;
- approval alone does not authorize execution.

IVE-2 does not:

- create a validation candidate or suite;
- synthesize commands or argv;
- invoke pytest;
- invoke Authorization;
- invoke a Worker or Provider;
- dispatch a wave;
- alter AiCLI or the Human Interface;
- mutate the repository.

## 9. Constitutional Ownership

| Concern | Owner |
| --- | --- |
| Direct impact recommendation | Certified IVE-0 |
| Semantic dependency selection | Certified IVE-1 |
| Canonical planning entry | Certified G38 |
| Scheduling recommendation | IVE-2 |
| Executable candidate composition | Existing G27-09 |
| Human Approval | Existing validation Governance |
| Authorization | Existing Authorization runtime |
| pytest and validation execution | Existing validation Worker/runtime |
| Replay protocol | Existing Replay owners |
| PCBV31 execution spine | Unchanged |

## 10. Limitations

- Parallel eligibility is bounded to the canonical declared dependency model.
- IVE-2 does not discover Python import relationships or infer dependencies
  from prose, filenames, or execution history.
- IVE-2 does not create missing exact allowlist mappings.
- A recommendation does not imply that the current execution runtime will
  execute groups concurrently.
- Actual parallel execution would require a separately governed generation;
  it is not authorized or implemented here.

