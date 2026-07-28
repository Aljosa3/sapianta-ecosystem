# G44-01 Constitutional Development Continuity Manager

Status: CERTIFIED  
Version: G44-01  
Date: 2026-07-28  
Owner: Platform Core Development Continuity

## 1. Purpose

The Constitutional Development Continuity Manager preserves a blocked G42
development workflow across an external repair. It creates immutable,
replay-visible checkpoint and resume-point artifacts and later determines
whether that exact workflow is eligible to continue.

The capability is additive. It does not change PCBV31, G42, G43, IVE,
Authorization, Replay, Workers, Providers, AiCLI, or Human Approval.

## 2. Responsibility boundary

The separation of responsibilities is normative:

| Capability | Retained responsibility |
|---|---|
| G43 Supervisor | Observe the workflow; identify the earliest blocker, missing evidence, affected capability, repair boundary, and re-validation scope |
| IVE-0 through IVE-4 | Impact analysis, semantic selection, entry planning, scheduling, failure analysis, and unified planning |
| G44 Continuity Manager | Checkpoint, resume point, continuity proof, additive invalidation, and workflow-continuation eligibility |
| External governed process | Human Approval, repair, validation execution, and production of validation evidence |
| Authorization | Execution and mutation authority |

No G43 or IVE responsibility migrates into G44. “Continuation authorized” in
a G44 artifact means only that the existing governed development workflow is
eligible to proceed from its certified resume point. It grants no execution,
mutation, validation, Worker, Provider, or dispatch authority.

## 3. Constitutional lifecycle

```text
G42 workflow
  -> G43 earliest-blocker diagnosis
  -> G44 immutable checkpoint
  -> G44 deterministic resume point
  -> external Human-Approved repair
  -> external validation evidence
  -> post-repair G42 workflow
  -> post-repair G43 diagnosis
  -> G44 continuity verification
  -> workflow-only continuation eligibility or fail-closed decision
```

G44 accepts a checkpoint source only when the G42 and G43 artifacts validate,
their explicit bindings agree, and both source replays reconstruct exactly.
The checkpoint is therefore bound to the diagnosed workflow rather than to a
caller assertion.

## 4. Checkpoint model

`CONSTITUTIONAL_DEVELOPMENT_CHECKPOINT_ARTIFACT_V1` contains:

- exact G42 workflow identity, hashes, status, and workflow position;
- canonical G42 and G43 replay hashes;
- planning-stage and preserved-stage lineage;
- IVE-4 bundle identity and hash;
- G43-certified repair boundary and re-validation scope;
- affected certified capability identifier;
- G43 diagnosis and evidence hashes;
- creator, timestamp, deterministic state hash, checkpoint identifier,
  checkpoint hash, and artifact hash.

Physical replay directory paths do not participate in constitutional identity.
Canonical workflow and diagnosis identifiers plus immutable replay hashes do.
This keeps identical evidence deterministic across repository locations.

The checkpoint is append-only evidence. Repair processing never rewrites it.

## 5. Resume-point model

`CONSTITUTIONAL_DEVELOPMENT_RESUME_POINT_ARTIFACT_V1` binds:

- the exact checkpoint;
- exact workflow and replay lineage;
- exact certified repair boundary;
- exact required re-validation scope;
- preserved boundary ranks that must not be repeated;
- remaining boundary ranks that must not be skipped.

Its identifier is derived from the checkpoint, workflow, replay-lineage,
repair-boundary, and validation-scope hashes. Any change invalidates the
identity proof.

## 6. External repair evidence

`EXTERNAL_REPAIR_CONTINUITY_EVIDENCE_ARTIFACT_V1` records external facts only:

- pre- and post-repair workflow bindings;
- modified boundary;
- affected capability;
- preserved lineage hash;
- validation-scope hash;
- passing, scope-bound validation evidence references;
- Human Approval reference and hash;
- optional superseding mutation reference.

The manager neither performs nor approves the repair. It neither executes nor
interprets pytest. A non-null superseding mutation prevents continuation.

## 7. Resume verification

Continuation eligibility requires all of the following:

1. checkpoint, resume point, repair evidence, G42 workflow, and G43 diagnosis
   pass deterministic validation;
2. checkpoint and resume identities bind exactly;
3. no matching additive invalidation exists;
4. source G42 and G43 replays reconstruct;
5. the repair modified exactly the G43-certified boundary;
6. affected capability and original replay lineage remain unchanged;
7. validation evidence is passing and bound to the exact G43 scope;
8. the post-repair G42 workflow is planning-ready;
9. the post-repair G43 diagnosis is healthy and complete;
10. every preserved stage has the same artifact hash;
11. every remaining stage is present.

Failure of any proof emits `RESUME_FAILED_CLOSED`. Success emits
`CONTINUATION_AUTHORIZED_FROM_RESUME_POINT`, with every execution and mutation
authority flag false.

## 8. Invalidation

`CONSTITUTIONAL_CHECKPOINT_INVALIDATION_ARTIFACT_V1` is an additive record. It
does not mutate the checkpoint or resume point. Supported reasons are:

- workflow state changed outside the repair boundary;
- replay lineage changed;
- checkpoint hash changed;
- required evidence changed;
- affected capability changed;
- checkpoint superseded by external mutation.

An invalidated checkpoint cannot resume. A replay directory is single-use, so
a duplicate resume attempt also fails closed.

## 9. Fail-closed and compatibility guarantees

Missing, malformed, ambiguous, stale, skipped, duplicated, or mismatched
evidence cannot produce workflow-continuation eligibility. G44 creates only
versioned additive artifacts and replay wrappers owned by G44. Existing replay
formats are consumed unchanged and are never rewritten.

The implementation is
`aigol.runtime.constitutional_development_continuity_manager_runtime`.

