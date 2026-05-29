# Worker Ecosystem Duplication Risks V1

Status: ecosystem duplication risk record.

## Risk Principle

AiGOL already has enough Worker semantics to constrain execution-only participation.

Creating ecosystem artifacts too early can duplicate or conflict with existing Worker, capability, authorization, and replay models.

## Duplication Risks

### Registry Before Attachment

Risk: creating a Worker registry before one real Worker attachment exists may invent abstractions without evidence.

Mitigation: implement one real Worker attachment first.

### Discovery As Orchestration

Risk: Worker discovery may become implicit orchestration or worker dispatch.

Mitigation: discovery must remain replay-visible and non-autonomous if ever introduced.

### Selection As Autonomy

Risk: Worker selection may become adaptive routing.

Mitigation: selection must be deterministic, authorization-bound, and capability-scoped.

### Taxonomy Duplication

Risk: Worker taxonomy may duplicate capability taxonomy.

Mitigation: derive Worker categories from capability classes unless a real gap proves otherwise.

### Lifecycle Duplication

Risk: Worker lifecycle may duplicate execution lifecycle or orchestration lifecycle.

Mitigation: Worker lifecycle should reference existing execution and authorization lifecycle semantics.

## Recommended Discipline

Do not introduce Worker ecosystem infrastructure until:

- one real Worker attachment exists
- pressure validation identifies ecosystem need
- multiple Workers create an actual selection problem
- replay requirements for plural Workers are clear
