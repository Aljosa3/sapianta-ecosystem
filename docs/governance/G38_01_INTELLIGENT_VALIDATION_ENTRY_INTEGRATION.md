# G38-01 — Intelligent Validation Entry Integration

Status: CERTIFIED

Version: V1

Date: 2026-07-28

Capability identifier: `INTELLIGENT_VALIDATION_ENTRY_INTEGRATION`

## 1. Purpose

G38-01 establishes one constitutional development-validation planning entry:

```text
Normalized Change
        |
        v
plan_development_validation(...)
        |
        +--> certified IVE-0 impact analysis and recommendation
        |
        +--> certified IVE-1 semantic validation selection
        |
        v
Immutable Intelligent Validation Planning Entry
        |
        +--> exact mapping exists: unchanged G27-09 candidate composition
        |
        `--> no exact mapping: planning-only, fail closed for execution
```

The entry is an orchestration and evidence-binding boundary. It is not a new
impact analyzer, semantic selector, candidate composer, approval owner,
authorization owner, scheduler, or validation executor.

## 2. Canonical Entry

The public entry is:

```python
plan_development_validation(
    entry_id=...,
    session_id=...,
    normalized_change_artifact=...,
    normalized_change_reference=...,
    normalized_change_hash=...,
    created_by=...,
    created_at=...,
    replay_dir=...,
)
```

It performs this deterministic sequence:

1. validate the canonical normalized-change artifact and its reference/hash;
2. invoke `analyze_intelligent_validation_scope(...)` unchanged;
3. validate the complete IVE-0 artifact and reject a failed analysis;
4. invoke `select_semantic_validation_scope(...)` unchanged;
5. validate the complete IVE-1 artifact and reject a failed selection;
6. copy the IVE-1 planning and downstream-boundary fields without alteration;
7. record one immutable planning-entry artifact.

No execution-side component is imported or invoked.

## 3. Canonical Artifact

The output artifact type is:

```text
INTELLIGENT_VALIDATION_PLANNING_ENTRY_ARTIFACT_V1
```

It binds:

- normalized-change reference, normalized-change hash, and artifact hash;
- IVE-0 reference, deterministic plan hash, artifact hash, and replay path;
- IVE-1 reference, deterministic selection hash, artifact hash, and replay
  path;
- direct validation subjects;
- transitive dependencies;
- selected validation requirements;
- full-regression requirement;
- certification evidence targets;
- existing exact allowlisted command references;
- existing validation-pipeline handoff;
- the unchanged Human Approval requirement;
- explicit non-authority and compatibility policy.

The artifact has a deterministic `planning_entry_hash` and an immutable
`artifact_hash`.

## 4. Existing Pipeline Handoff

G38-01 preserves the handoff emitted by IVE-0 and carried by IVE-1.

If the source G27 plan contains exact allowlisted command mappings, the
handoff remains:

```text
READY_FOR_EXISTING_G27_09_CANDIDATE_COMPOSITION
```

G27-09 remains the only owner that may compose an executable validation
candidate. The resulting exact candidate hash must then receive Human
Approval through existing Platform Core validation Governance. Existing
Authorization and governed validation runtime remain responsible for any
later execution.

If there is no exact mapping, the handoff remains:

```text
PLANNING_ONLY_NO_EXACT_ALLOWLIST_MAPPING
```

G38-01 does not synthesize a command, infer argv, expand the allowlist, or
convert semantic requirements into executable work.

## 5. Human Approval

The entry preserves the IVE Human Approval object exactly:

- approval is required before execution;
- approval is not recorded by IVE or G38-01;
- approval must bind the exact downstream candidate hash;
- approval alone does not authorize execution.

Every successful or failed entry records:

- `human_approval_required = true`;
- `human_approval_recorded = false`;
- `validation_candidate_constructed = false`;
- `validation_executed = false`;
- all authority flags false.

## 6. Replay

One G38 wrapper is written:

```text
000_intelligent_validation_planning_entry_recorded.json
```

The certified nested replay families remain independent:

```text
ive_0/000_intelligent_validation_plan_recorded.json
ive_1/000_ive_0_plan_bound.json
ive_1/001_semantic_validation_selection_recorded.json
```

Existing IVE-0 nested G27 replay is retained when its certified strategy uses
G27 impact and planning.

Reconstruction validates:

- the G38 wrapper order and hash;
- the deterministic entry and artifact hashes;
- the complete IVE-0 replay;
- the complete IVE-1 replay;
- IVE-0 to IVE-1 lineage;
- exact preservation of selected requirements, full-regression policy,
  downstream handoff, and Human Approval;
- all non-authority boundaries.

No Replay protocol or ownership rule is changed.

## 7. Fail-Closed Behavior

Invalid source bindings, failed IVE analysis, failed semantic selection,
tampered replay, lineage mismatch, altered planning fields, missing Human
Approval constraints, or authority escalation produce or validate as
`FAILED_CLOSED`.

A failed entry:

- claims no selected scope;
- requires full regression before any reduced-scope claim;
- blocks candidate handoff;
- records no approval;
- invokes no Authorization, Worker, Provider, AiCLI, pytest, or execution.

## 8. Constitutional Separation

| Concern | Owner after G38-01 |
| --- | --- |
| Change impact and recommendation | Certified IVE-0 |
| Semantic direct/transitive selection | Certified IVE-1 |
| Planning entry orchestration and lineage | G38-01 |
| Executable candidate composition | Existing G27-09 |
| Candidate-bound Human Approval | Existing validation Governance |
| Authorization | Existing Authorization runtime |
| Validation execution and pytest invocation | Existing governed validation runtime and Worker |
| Replay ownership | Existing replay owners |
| Worker, Provider, AiCLI, PCBV31 execution | Unchanged |

## 9. Explicit Non-Goals

G38-01 does not:

- execute validation;
- optimize validation;
- schedule or parallelize tests;
- modify pytest;
- reduce IVE-0 or IVE-1 scope;
- synthesize commands;
- construct validation candidates;
- record Human Approval;
- grant Authorization;
- invoke Workers, Providers, or AiCLI;
- mutate the repository;
- modify the PCBV31 execution spine.

## 10. Known Limitation

The integrated entry improves planning precision but does not create missing
exact allowlist mappings. A semantic recommendation without an existing exact
mapping remains planning-only. This is intentional fail-closed behavior, not
an execution defect.

