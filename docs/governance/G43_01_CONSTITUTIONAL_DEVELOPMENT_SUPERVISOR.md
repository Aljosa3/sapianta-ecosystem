# G43-01 — Constitutional Development Supervisor

Status: CERTIFIED

Version: V1

Date: 2026-07-28

Capability identifier: `CONSTITUTIONAL_DEVELOPMENT_SUPERVISOR`

## 1. Purpose

The Constitutional Development Supervisor observes the certified G42
development-validation workflow and produces deterministic blocker diagnosis:

```text
immutable G42 workflow and replay
              |
              v
read-only workflow reconstruction
              |
              v
certified IVE replay reconstruction
              |
              v
earliest available/failed boundary analysis
              |
              +--> missing evidence
              +--> affected certified capability
              +--> minimal repair boundary
              `--> certified re-validation scope
```

The supervisor does not change G42 or PCBV31. It performs no repair and no
validation execution.

## 2. Canonical Entry

The public entry is:

```python
supervise_constitutional_development_workflow(
    diagnosis_id=...,
    workflow_artifact=...,
    workflow_reference=...,
    workflow_hash=...,
    workflow_artifact_hash=...,
    workflow_replay_dir=...,
    observed_by=...,
    created_at=...,
    replay_dir=...,
)
```

The workflow artifact, semantic hash, artifact hash, and immutable replay must
all agree before a diagnosis claim is allowed.

## 3. Observation Model

The supervisor observes boundaries in certified execution order:

| Rank | Boundary | Certified owner |
| --- | --- | --- |
| 0 | Platform change normalization | `PLATFORM_CHANGE_NORMALIZATION` |
| 1 | G42 workflow input binding | `CONSTITUTIONAL_DEVELOPMENT_WORKFLOW_INTEGRATION` |
| 2 | IVE-4 orchestration input binding | `INTELLIGENT_VALIDATION_ORCHESTRATOR_V4` |
| 3 | IVE-0 impact analysis | `INTELLIGENT_VALIDATION_ENGINE_V0` |
| 4 | IVE-1 semantic selection | `INTELLIGENT_VALIDATION_ENGINE_V1` |
| 5 | G38 validation entry | `INTELLIGENT_VALIDATION_ENTRY_INTEGRATION` |
| 6 | IVE-2 scheduling | `INTELLIGENT_VALIDATION_ENGINE_V2` |
| 7 | IVE-3 failure analysis | `INTELLIGENT_VALIDATION_ENGINE_V3` |
| 8 | IVE-4 unified bundle | `INTELLIGENT_VALIDATION_ORCHESTRATOR_V4` |
| 9 | G42 workflow output binding | `CONSTITUTIONAL_DEVELOPMENT_WORKFLOW_INTEGRATION` |

Each observation binds boundary, capability, evidence status, artifact hash,
and deterministic observation hash.

The first unavailable, failed-closed, or mismatched boundary is the earliest
constitutional blocker. Later boundaries are not used to displace it.

## 4. Certified IVE Diagnosis

The supervisor invokes only certified read-only reconstruction and validation:

- G42 workflow reconstruction;
- IVE-4 orchestration reconstruction;
- IVE-0, IVE-1, G38, IVE-2, and IVE-3 artifact validators.

It does not invoke planning engines to generate replacement evidence. It does
not call IVE-3 with invented failed-validation evidence.

When the observed G42 workflow already contains a successful IVE-3
failure-revalidation analysis, the supervisor preserves that exact certified
minimal re-validation recommendation.

## 5. Canonical Diagnosis Model

The output type is:

```text
CONSTITUTIONAL_DEVELOPMENT_SUPERVISOR_DIAGNOSIS_ARTIFACT_V1
```

It contains:

- exact G42 workflow binding;
- diagnosis-evidence hashes;
- diagnosis status;
- earliest constitutional blocker;
- missing evidence;
- affected certified capability and certification record hash;
- minimal repair boundary;
- minimal re-validation scope;
- Human Approval continuity;
- explicit non-authority flags;
- deterministic diagnosis and artifact hashes.

Statuses are:

```text
WORKFLOW_HEALTHY
BLOCKER_DIAGNOSED
FAILED_CLOSED
```

## 6. Earliest Blocker and Missing Evidence

For a diagnosed blocker, the artifact identifies:

- boundary rank and name;
- certified capability identifier;
- observed evidence status;
- source artifact hash;
- precise required evidence;
- certification milestone, version, and implementation owner.

The supervisor does not infer causal defects from logs or natural language.
It classifies only immutable artifact availability, certified status, binding,
and replay reconstruction.

## 7. Controlled Recovery Recommendation

A blocker diagnosis recommends only:

```text
MISSING_OR_INVALID_INPUT_EVIDENCE
EXACT_REFERENCE_AND_HASH_BINDING
```

as permitted repair targets.

It explicitly prohibits alteration of:

- valid upstream certified evidence;
- certified IVE semantics;
- Human Approval;
- Authorization;
- Worker and Provider contracts;
- AiCLI;
- PCBV31.

The recommendation does not authorize implementation. Human authority remains
required before any repair or execution.

## 8. Re-validation Scope

If the workflow is healthy, the supervisor preserves the exact current IVE-4
recommendation:

- IVE-2 initial validation schedule; or
- IVE-3 failure re-validation scope.

It does not further reduce that certified scope.

If evidence is incomplete or a blocker prevents complete planning lineage,
the supervisor makes no reduced-scope claim and requires full regression.

## 9. Human Approval

Every diagnosis records:

```text
human_approval_required = true
human_approval_recorded = false
validation_executed = false
automatic_repair_performed = false
```

Historical approval inside IVE-3 evidence remains historical evidence only.
It cannot authorize repair or re-validation.

## 10. Replay

The supervisor writes:

```text
000_constitutional_development_workflow_bound.json
001_diagnosis_evidence_recorded.json
002_constitutional_development_supervisor_diagnosis_recorded.json
```

The source G42 and IVE replay directories remain immutable and authoritative.
Supervisor replay binds them without taking ownership.

Reconstruction validates workflow evidence, every diagnostic observation,
the earliest blocker, affected capability, repair boundary, re-validation
scope, and deterministic diagnosis identity.

## 11. Fail-Closed Policy

The supervisor fails closed when:

- the workflow artifact binding is incomplete;
- G42 replay cannot reconstruct;
- IVE replay ordering or hashes are invalid;
- an artifact type is unknown at an expected boundary;
- diagnosis evidence is internally inconsistent;
- a diagnosis or replay wrapper is altered.

A failed diagnosis:

- names no affected capability;
- makes no blocker claim;
- recommends no repair target;
- requires full regression;
- performs no execution or repair.

## 12. Constitutional Boundaries

The supervisor does not:

- modify G42, IVE, or PCBV31;
- execute validation or pytest;
- automatically repair code, evidence, or configuration;
- create validation candidates;
- record Human Approval;
- invoke Authorization;
- invoke Workers, Providers, AiCLI, or Human Interfaces;
- mutate Replay or repository state;
- certify its own diagnosis.

## 13. Known Limitations

- Diagnosis is evidence-bound, not causal proof of an implementation defect.
- A failed workflow with incomplete replay cannot receive a specific blocker
  classification.
- The supervisor does not parse test output.
- The supervisor does not authorize or schedule recovery.

