# G42-01 — Constitutional Development Workflow Integration

Status: CERTIFIED

Version: V1

Date: 2026-07-28

Capability identifier:
`CONSTITUTIONAL_DEVELOPMENT_WORKFLOW_INTEGRATION`

## 1. Purpose

G42-01 adopts certified IVE-4 as the default Platform Core
development-validation planning entry:

```text
normalized Platform change
          |
          v
plan_constitutional_development_validation(...)
          |
          v
certified IVE-4, unchanged
          |
          v
immutable unified planning bundle
          |
          v
G42 workflow planning artifact
          |
          +--> existing candidate composition, when exact mapping exists
          |
          +--> existing candidate-bound Human Approval
          |
          `--> existing Authorization and validation execution
```

G42 performs only the planning integration portion of this lifecycle. It
does not compose a candidate, record approval, authorize, or execute.

## 2. Canonical Default Entry

The public workflow entry is:

```python
plan_constitutional_development_validation(
    workflow_id=...,
    session_id=...,
    normalized_change_artifact=...,
    normalized_change_reference=...,
    normalized_change_hash=...,
    created_by=...,
    created_at=...,
    replay_dir=...,
    planning_mode=INITIAL_VALIDATION_PLANNING,
    failure_context=None,
)
```

When the caller does not select a mode, initial IVE-4 planning is used.
Failure revalidation remains available through IVE-4's certified mode and
requires the exact existing failed-validation evidence defined by G40 and
G41.

The workflow artifact identifies:

```text
INTELLIGENT_VALIDATION_ORCHESTRATOR_V4
```

as `DEFAULT_PLATFORM_CORE_DEVELOPMENT_VALIDATION_PLANNER`.

The older G27, IVE-0, IVE-1, G38, IVE-2, and IVE-3 public contracts remain
unchanged as certified component boundaries. G42 is the canonical workflow
entry for new Platform Core development-validation planning.

## 3. Certified IVE-4 Consumption

G42:

1. validates the normalized-change artifact and exact binding;
2. invokes `orchestrate_intelligent_validation_planning(...)` unchanged;
3. validates the complete IVE-4 bundle;
4. reconstructs the complete IVE-4 replay;
5. verifies bundle, artifact, mode, and stage-lineage identity;
6. records the exact bundle without transformation;
7. copies only existing planning, handoff, and Human Approval fields.

No IVE-4 algorithm, schedule, dependency, failure analysis, artifact, or
replay family is modified.

## 4. Canonical Workflow Artifact

The output type is:

```text
CONSTITUTIONAL_DEVELOPMENT_VALIDATION_WORKFLOW_ARTIFACT_V1
```

It binds:

- workflow and session identity;
- normalized-change reference and hashes;
- the canonical default-planner declaration;
- exact IVE-4 orchestration reference, bundle hash, and artifact hash;
- the complete unchanged IVE-4 planning bundle;
- exact IVE stage lineage and current recommendation;
- unchanged full-regression policy;
- unchanged G38 existing-validation-pipeline handoff;
- unchanged Human Approval requirement;
- explicit non-authority and compatibility policy;
- deterministic workflow and artifact hashes.

The artifact is planning evidence. It is not an execution candidate,
approval, authorization, result, governance conclusion, or certification.

## 5. Existing Execution Continuity

G42 preserves the G38 handoff embedded in the IVE-4 bundle exactly.

Where exact allowlisted command mapping already exists:

```text
G42 planning artifact
  -> existing G27-09 candidate composition
  -> exact candidate hash
  -> existing Human Approval
  -> existing Authorization
  -> existing governed validation runtime
  -> unchanged pytest execution
```

Where no exact mapping exists, planning remains non-executable and fail
closed. G42 does not synthesize commands, infer argv, expand the allowlist, or
create a compatibility execution path.

## 6. Human Approval

Every successful workflow preserves IVE-4's exact Human Approval object:

- approval remains required before execution;
- approval is not recorded by G42;
- approval must bind the exact downstream candidate hash;
- approval alone does not authorize execution.

Every G42 artifact also records:

```text
human_approval_required = true
human_approval_recorded = false
validation_candidate_constructed = false
validation_executed = false
```

## 7. Replay

G42 writes an additive three-step workflow replay:

```text
000_normalized_change_bound.json
001_ive_4_planning_bundle_bound.json
002_constitutional_development_validation_workflow_recorded.json
```

The complete IVE-4 replay remains under:

```text
ive_4/
```

including its unchanged nested G38, IVE-0, IVE-1, IVE-2, and applicable
IVE-3 replay families.

G42 reconstruction validates both its own wrappers and the authoritative
IVE-4 reconstruction. Existing replay protocols and owners are unchanged.

## 8. Fail-Closed Policy

G42 fails closed for:

- missing or invalid normalized-change evidence;
- normalized-change reference or hash mismatch;
- missing IVE-4 planning evidence;
- failed IVE-4 planning;
- missing failure evidence in failure-revalidation mode;
- altered IVE-4 bundle, stage lineage, recommendation, handoff, or approval;
- IVE-4 replay reconstruction mismatch;
- G42 replay collision, wrapper mismatch, or deterministic mismatch.

A failed workflow:

- contains no IVE-4 bundle or planning-stage claim;
- provides no executable recommendation;
- blocks downstream candidate handoff;
- requires full regression;
- keeps Human Approval blocked;
- executes nothing.

## 9. Constitutional Boundaries

G42 does not:

- modify IVE-4 or any IVE stage;
- execute pytest or validation;
- compose validation candidates;
- record Human Approval;
- invoke Authorization;
- invoke Workers, Providers, AiCLI, or Human Interfaces;
- alter Replay protocols;
- change command mappings or allowlists;
- mutate the repository at runtime;
- modify PCBV31.

## 10. Compatibility Classification

This capability is an additive Platform Core validation-workflow integration.
It changes the canonical planning entry ownership for new development
validation calls while leaving all certified component and execution
contracts unchanged.

## 11. Known Limitations

- G42 does not add a user-interface route; Human Interface and AiCLI remain
  transport and presentation boundaries.
- G42 does not make semantic-only recommendations executable.
- Runtime parallel execution remains outside IVE and G42.
- Failure revalidation still requires explicit, hash-bound failed-group
  evidence.

