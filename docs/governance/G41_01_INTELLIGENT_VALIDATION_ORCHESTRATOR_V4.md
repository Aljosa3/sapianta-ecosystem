# G41-01 — Intelligent Validation Orchestrator V4

Status: CERTIFIED

Version: V1

Date: 2026-07-28

Capability identifier: `INTELLIGENT_VALIDATION_ORCHESTRATOR_V4`

## 1. Purpose

IVE-4 composes the certified Intelligent Validation planning capabilities
behind one deterministic, planning-only entry:

```text
normalized change
       |
       v
G38 entry integration
  |         |
  v         v
IVE-0      IVE-1
       |
       v
IVE-2 scheduling recommendation
       |
       +---- no failed evidence ----> IVE-3 NOT_APPLICABLE
       |
       +---- failed governed result -> IVE-3 failure analysis
       |
       v
immutable unified validation planning bundle
       |
       v
future Human Approval and unchanged validation execution
```

IVE-4 performs no validation execution and no automatic repair.

## 2. Canonical Entry

The single public planning entry is:

```python
orchestrate_intelligent_validation_planning(
    orchestration_id=...,
    session_id=...,
    planning_mode=...,
    normalized_change_artifact=...,
    normalized_change_reference=...,
    normalized_change_hash=...,
    failure_context=...,
    created_by=...,
    created_at=...,
    replay_dir=...,
)
```

It supports exactly two modes:

| Mode | Certified stages | Current recommendation |
| --- | --- | --- |
| `INITIAL_VALIDATION_PLANNING` | G38 invokes unchanged IVE-0 and IVE-1; IVE-4 then invokes unchanged IVE-2 | IVE-2 initial validation schedule |
| `FAILURE_REVALIDATION_PLANNING` | The initial chain plus unchanged IVE-3 using an existing failed governed validation | IVE-3 re-validation scope |

The initial mode does not fabricate a failed result merely to invoke IVE-3.
It records an immutable
`IVE_3_NOT_APPLICABLE_NO_FAILED_VALIDATION_EVIDENCE` state. The failure mode
requires complete, exact failed-validation evidence before any stage runs.

## 3. Unchanged Stage Composition

IVE-4 delegates certified responsibility:

- G38 remains the entry owner for IVE-0 and IVE-1;
- IVE-0 remains the owner of direct impact analysis;
- IVE-1 remains the owner of semantic dependency selection;
- IVE-2 remains the owner of parallel scheduling recommendations;
- IVE-3 remains the owner of failed-validation lineage analysis and
  re-validation recommendations.

IVE-4 neither reimplements nor alters those algorithms. It validates and
preserves their returned artifacts exactly.

## 4. Unified Planning Bundle

The canonical output is:

```text
UNIFIED_VALIDATION_PLANNING_BUNDLE_ARTIFACT_V1
```

It binds:

- orchestration identity, session, mode, creator, and timestamp;
- the normalized-change identity and hash;
- exact IVE-0, IVE-1, G38, IVE-2, and IVE-3 state artifacts;
- each stage artifact hash;
- explicit stage invocation status and lineage;
- the current executable-planning recommendation;
- full-regression continuity;
- the unchanged future Human Approval requirement;
- explicit non-authority, non-execution, and non-repair flags;
- deterministic bundle and artifact hashes.

The bundle is a planning artifact. It is not approval, authorization, a
validation candidate, an execution schedule, or certification.

## 5. Current Recommendation

For initial planning, the current recommendation contains the exact IVE-2
groups and full-regression policy.

For failure revalidation, it contains the exact IVE-3 earliest known boundary
and recommended re-validation groups. It does not claim causal diagnosis and
does not suppress an existing full-regression requirement.

## 6. Human Approval

Every successful or failed bundle declares:

```text
required_before_execution = true
approval_recorded = false
validation_executed = false
```

IVE-4 does not create a validation candidate, record approval, invoke
Authorization, or dispatch validation. Historical approval consumed by IVE-3
remains evidence only and cannot authorize re-validation.

## 7. Replay

IVE-4 writes an additive seven-step artifact family:

```text
000_normalized_change_bound.json
001_ive_0_plan_bound.json
002_ive_1_semantic_selection_bound.json
003_g38_validation_plan_bound.json
004_ive_2_schedule_bound.json
005_ive_3_analysis_state_bound.json
006_unified_validation_planning_bundle_recorded.json
```

The nested, unchanged G38, IVE-2, and IVE-3 replays remain authoritative for
their own stages. IVE-4 wrapper records are immutable orchestration bindings;
they do not replace or mutate the source replay protocols.

Replay reconstruction validates every wrapper and artifact, reconstructs the
cross-stage lineage, and deterministically recomputes the unified bundle.

## 8. Fail-Closed Policy

IVE-4 fails closed for:

- unsupported or missing planning mode;
- normalized-change identity or hash mismatch;
- missing failure context in failure mode;
- unexpected failure context in initial mode;
- failed or tampered G38, IVE-0, IVE-1, IVE-2, or IVE-3 evidence;
- cross-stage reference or hash mismatch;
- incomplete or invalid failed-validation evidence;
- replay collision, wrapper mismatch, or bundle mismatch.

A failed bundle contains no recommendation, stage claim, approval, execution,
or repair authority. Full regression remains required.

## 9. Constitutional Boundaries

IVE-4 does not:

- invoke pytest or execute validation;
- create validation candidates;
- record Human Approval;
- authorize or dispatch execution;
- invoke Workers, Providers, AiCLI, or Human Interfaces;
- parallelize runtime work;
- modify Replay protocols;
- modify IVE-0, IVE-1, G38, IVE-2, or IVE-3;
- mutate source, tests, configuration, governance, or certification;
- perform automatic repair;
- alter the PCBV31 execution spine.

## 10. Known Limitations

- IVE-4 produces planning bundles only; an existing downstream governed
  validation workflow must separately obtain Human Approval and execute.
- Failure mode requires explicit, hash-bound association between the failed
  result and an IVE-2 group.
- The orchestration bundle records no runtime progress or ETA.
- It recommends independence but does not execute groups in parallel.

