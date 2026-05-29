# Filesystem Read-Only Capability Guarantees V1

Status: filesystem read-only capability guarantees.

## Guarantee 1: Explicit Allowed Paths Only

Filesystem read-only inspection may operate only on paths explicitly included in the allowed path set.

Requests outside the root or outside allowed paths fail closed.

## Guarantee 2: Read-Only Inspection

The capability may inspect metadata, directory entries, and bounded text preview only.

It must not write, delete, move, modify, execute, invoke shell, access network, or call APIs.

## Guarantee 3: Classification Compatibility

The capability uses:

- class: `READ_ONLY / INSPECTION`
- risk: `LOW`

Escalation to `QUERY`, `MUTATION`, `DESTRUCTIVE`, or `PRIVILEGED` is prohibited.

## Guarantee 4: Authorization Required

Execution requires explicit authorization evidence after validation.

Missing authorization fails closed.

## Guarantee 5: Replay Visibility

Request, validation, authorization, execution evidence, and termination are replay-visible and append-only.

## Guarantee 6: Fail-Closed Boundaries

Path ambiguity, forbidden access, mutation flags, invalid classification, replay discontinuity, or lifecycle corruption must fail closed.

