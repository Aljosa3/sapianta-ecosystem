# Worker Position Duplication Risks V1

Status: duplication and overengineering risk record.

## Risk Principle

Because Worker is already substantially defined, creating new Worker architecture without consolidation risks semantic duplication.

## Duplication Risks

### Parallel Worker Authority Model

Risk: introducing a second Worker authority model could conflict with the existing execution-only definition.

Mitigation: preserve Worker as execution-only and non-authoritative.

### Parallel Worker Identity Model

Risk: defining new identity fields without reconciling `WORKER_IDENTITY_MODEL_V1` could fragment Worker identity.

Mitigation: extend or implement existing identity fields before creating new ones.

### Parallel Worker Replay Model

Risk: separate worker logs or traces could be treated as replay substitutes.

Mitigation: keep `WORKER_REPLAY_MAPPING_V1` canonical.

### Premature Worker Registry

Risk: creating registration/discovery too early may imply orchestration or worker pools.

Mitigation: define registration only when a real Worker attachment requires it.

### Capability-Specific Worker Inflation

Risk: domain-specific workers may multiply before the first real Worker attachment proves the boundary.

Mitigation: implement one read-only Worker attachment before introducing specialization.

## Recommended Discipline

Future Worker work should:

- implement existing semantics first
- avoid creating new authority language
- avoid worker orchestration
- avoid worker pools
- avoid hidden memory
- preserve replay centrality
- preserve fail-closed behavior
