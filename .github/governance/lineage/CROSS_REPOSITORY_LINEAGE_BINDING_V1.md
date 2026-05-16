# CROSS_REPOSITORY_LINEAGE_BINDING_V1

## Status

Bound and replay-safe.

This milestone creates deterministic cross-repository lineage between the outer governance/evidence repository and the inner implementation/runtime repository. It binds governance evidence to exact repository identities; it does not authorize execution or alter runtime behavior.

## Deterministic Pairing

- outer repository commit: `8d3a28f358eef48d6cfa69eceaeecf717269d5e1`
- inner repository commit: `decf9d90410ccd1387baac6f35de006a29db9b99`
- binding id: `CROSS-REPOSITORY-LINEAGE-BINDING-4f1b4617c32957dfd3d3575a`
- binding hash: `4d3edb6d3ee8dcb500e73ac872a6527a719f3dea28815b9197a3fac92b5340ad`
- canonical JSON hash: `4f1b4617c32957dfd3d3575a2df1f12f33e09d06e3c44ea05520bf1538ce4581`

## Linked Milestones

- finalization: `FINALIZE_FIRST_OPERATIONAL_GOVERNED_RUNTIME_V1`
- validation epoch: `FIRST_OPERATIONAL_RUNTIME_VALIDATION_EPOCH_V1`
- inner implementation milestone: `FIRST_OPERATIONAL_RUNTIME_VALIDATION_EPOCH_V1`

## Replay Linkage

The binding captures content hashes for:

- finalization evidence
- validation epoch evidence
- replay certification evidence
- inner runtime validation implementation

This prevents certification from floating free of the implementation that was actually validated.

## Mutation Boundaries

- read-only after creation
- does not authorize execution
- does not create runtime authority
- does not change execution behavior

## Limitation

No commit-specific structural approval artifact was located for the bound inner implementation commit. The binding records the existing structural approval policy template and preserves that limitation explicitly rather than treating a template as a specific approval record.
