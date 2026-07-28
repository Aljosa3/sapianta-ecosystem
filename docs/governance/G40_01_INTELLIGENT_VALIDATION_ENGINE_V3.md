# G40-01 — Intelligent Validation Engine V3

Status: CERTIFIED

Version: V1

Date: 2026-07-28

Capability identifier: `INTELLIGENT_VALIDATION_ENGINE_V3`

## 1. Purpose

IVE-3 performs deterministic, replay-backed analysis of an existing failed
validation without changing validation execution:

```text
IVE-0 impact recommendation
          |
          v
IVE-1 semantic selection
          |
          v
G38 planning entry
          |
          v
IVE-2 schedule recommendation
          |
          +---- failed governed validation replay
          |
          v
IVE-3 earliest-boundary analysis
          |
          v
minimal dependency-preserving re-validation recommendation
```

IVE-3 neither executes the recommendation nor repairs the failed result.

## 2. Canonical Entry

The public function is:

```python
analyze_failed_validation(
    analysis_id=...,
    session_id=...,
    ive_2_schedule_artifact=...,
    ive_2_schedule_reference=...,
    ive_2_schedule_hash=...,
    ive_2_replay_dir=...,
    g38_replay_dir=...,
    validation_result_artifact=...,
    validation_result_reference=...,
    validation_result_hash=...,
    validation_replay_dir=...,
    failed_group_id=...,
    failed_group_hash=...,
    failed_requirement_hashes=...,
    observed_by=...,
    created_at=...,
    replay_dir=...,
)
```

The failed-group association is explicit and hash-bound. IVE-3 does not infer
which semantic requirement failed from stdout, stderr, a filename, command
text, or probabilistic analysis.

## 3. Required Evidence

IVE-3 accepts only evidence that reconstructs successfully:

- the complete IVE-2 replay;
- the G38 artifact bound by IVE-2;
- the IVE-1 selection and dependency model bound by IVE-2;
- the complete external G38 replay;
- the IVE-0 artifact and replay bound by IVE-1 and G38;
- the complete governed validation replay;
- the exact candidate and candidate-bound Human Approval;
- a `VALIDATION_FAILED` or `VALIDATION_TIMED_OUT` result;
- the exact IVE-2 group hash;
- exact failed requirement hashes for a non-barrier group.

The failed execution evidence is recorded as:

```text
FAILED_VALIDATION_EXECUTION_EVIDENCE_ARTIFACT_V1
```

## 4. Earliest Known Planning Boundary

IVE-3 reports the earliest boundary supported by the exact failed requirement
evidence:

| Failed evidence | Earliest boundary |
| --- | --- |
| Direct selected requirement | `IVE_0_DIRECT_IMPACT_RECOMMENDATION` |
| Transitive selected requirement | `IVE_1_SEMANTIC_DEPENDENCY_SELECTION` |
| Full-regression barrier | `IVE_2_FULL_REGRESSION_BARRIER` |

The result is an evidence-bound diagnostic classification. It does not claim
that the planning boundary caused the test failure. It identifies the earliest
known planning artifact associated with that failure.

G38 is reconstructed as a lineage boundary but does not originate validation
scope, so it is not reported as an earlier semantic cause than IVE-0 or IVE-1.

## 5. Minimal Re-validation Scope

The re-validation recommendation contains:

1. only the exact failed requirement hashes within the failed group;
2. every downstream IVE-2 group reachable through certified scheduling
   dependencies;
3. all unchanged requirements of each downstream group;
4. the terminal full-regression barrier when the source schedule requires it.

Independent groups with no dependency path from the failed group are excluded.

The scope is minimal only relative to the certified IVE-2 dependency graph. It
does not suppress an existing full-regression requirement.

## 6. Unknown Dependency and Binding Policy

IVE-3 fails closed for:

- unknown or mismatched schedule groups;
- unbound or duplicate failed requirement hashes;
- missing schedule descendants;
- unknown dependency groups;
- failed or tampered IVE-0 through IVE-2 lineage;
- mismatched G38 or validation replay;
- result/candidate mismatch;
- missing or invalid Human Approval;
- passed or otherwise unsupported validation status;
- replay or artifact hash mismatch.

A failed analysis:

- reports no reconstructed planning lineage;
- makes no earliest-boundary claim;
- recommends no reduced re-validation groups;
- requires full regression;
- executes nothing;
- performs no repair.

## 7. Human Approval

Two distinct Human Approval properties are preserved:

1. The failed governed validation replay must contain its original immutable
   candidate-bound Human Approval.
2. Any future re-validation remains subject to the unchanged G39/G38 Human
   Approval requirement and downstream Authorization.

IVE-3 does not reuse the historical approval as authority for re-validation.
It records historical approval only as evidence that the observed result came
from the governed validation runtime.

## 8. Canonical Analysis Artifact

The output type is:

```text
VALIDATION_FAILURE_ANALYSIS_ARTIFACT_V1
```

It binds:

- four-stage planning lineage from IVE-0 through IVE-2;
- failed execution evidence hash and status;
- exact failed group and requirement hashes;
- earliest known planning boundary and evidence;
- dependency-path-preserving re-validation groups;
- unchanged full-regression and Human Approval policies;
- explicit non-authority boundaries;
- deterministic analysis and artifact hashes.

## 9. Replay

IVE-3 writes:

```text
000_ive_0_plan_bound.json
001_ive_1_semantic_selection_bound.json
002_g38_validation_plan_bound.json
003_ive_2_schedule_bound.json
004_failed_validation_execution_evidence_bound.json
005_validation_failure_analysis_recorded.json
```

Reconstruction validates every wrapper and source artifact, re-validates the
candidate and Human Approval, verifies all lineage hashes, and independently
recomputes the earliest boundary and re-validation scope.

Replay protocol and ownership remain unchanged. IVE-3 owns only this additive
artifact family.

## 10. Constitutional Boundaries

IVE-3 does not:

- invoke pytest;
- execute validation;
- schedule runtime work;
- create validation candidates;
- record new Human Approval;
- invoke Authorization;
- invoke Workers or Providers;
- modify AiCLI or Human Interface behavior;
- mutate source, tests, configuration, or Replay;
- generate patches;
- perform automatic repair;
- modify the PCBV31 execution spine.

## 11. Known Limitations

- Association between an observed failed validation and an IVE-2 group must be
  supplied explicitly and hash-bound; no runtime dispatch integration is
  introduced.
- Failure output is not semantically interpreted.
- The earliest boundary is an evidence lineage result, not causal proof.
- Minimal scope is bounded by declared certified dependencies. Unknown
  dependencies force fail-closed full-regression treatment.

