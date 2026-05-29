# Capability Authorization Mapping V1

Status: capability authorization mapping only.

## Mapping Table

| Capability Class | Risk | Default Boundary | Authorization Requirement | Current Attachment Status |
| --- | --- | --- | --- | --- |
| `READ_ONLY` | `LOW` | `RESTRICTED` | explicit authorization | first read-only runtime inspection attached |
| `INSPECTION` | `LOW` | `RESTRICTED` | explicit authorization | attached only as bounded runtime inspection |
| `QUERY` | `MEDIUM` | `RESTRICTED` | explicit authorization plus source/response capture | not attached |
| `MUTATION` | `HIGH` | `DENIED` | future constitutional gate required | not attached |
| `DESTRUCTIVE` | `CRITICAL` | `DENIED` | not authorized under current baseline | not attached |
| `PRIVILEGED` | `CRITICAL` | `DENIED` | not authorized under current baseline | not attached |

## Authorization Rule

Every capability attachment must prove:

- capability class
- risk level
- boundary state
- authorization evidence
- replay lineage
- fail-closed conditions
- constitutional freeze compatibility

## Attachment Rule

The existence of a capability class does not permit attachment.

Every future capability attachment requires a specific governance artifact and focused test evidence.

## Escalation Rule

A capability may not escalate from a lower-risk class to a higher-risk class during execution.

Examples:

- `READ_ONLY` may not become `QUERY`
- `INSPECTION` may not become `MUTATION`
- `QUERY` may not become `CREATE`, `UPDATE`, or `DELETE`
- no class may become `PRIVILEGED`

Escalation fails closed.

