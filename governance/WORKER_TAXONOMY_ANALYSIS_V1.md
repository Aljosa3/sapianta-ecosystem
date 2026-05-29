# Worker Taxonomy Analysis V1

Status: reconstruction-only taxonomy analysis.

## Classification

`WORKER_TAXONOMY_STATUS`: `PARTIAL`

## Existing Taxonomy Foundations

AiGOL defines capability classes and risk levels:

- `READ_ONLY`
- `INSPECTION`
- `QUERY`
- `MUTATION`
- `DESTRUCTIVE`
- `PRIVILEGED`

Risk levels:

- `LOW`
- `MEDIUM`
- `HIGH`
- `CRITICAL`

Worker identity also allows `worker_type`, such as `read_only_worker`.

## Capability-Specific Workers

Capability-specific Worker semantics are partially implied by capability binding.

The first Worker attachment is constrained to:

- `READ_ONLY_RUNTIME_INSPECTION`
- `FILESYSTEM_READ_ONLY_INSPECTION`

## Domain-Specific Workers

Domain-specific Workers are not defined.

No current artifact defines domain taxonomy, domain routing, or domain-specific Worker governance.

## Risk-Classified Workers

Risk classification exists for capabilities, not Workers.

Worker risk may be derived from capability binding, but this is not yet canonical.

## Finding

Worker taxonomy is partial: capability taxonomy exists and Worker type is modeled, but Worker category taxonomy is not yet complete.
