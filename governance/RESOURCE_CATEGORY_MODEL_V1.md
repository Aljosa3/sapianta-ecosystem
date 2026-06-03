# RESOURCE_CATEGORY_MODEL_V1

## Status

Resource category model.

## Purpose

Resource categories define the top-level kind of selectable ecosystem participant.

Category is identity metadata.

Category does not grant authority.

## Categories

### PROVIDER

Purpose:

```text
Produce proposal evidence.
```

Examples:

- `OPENAI`
- `ANTHROPIC`

Authority:

- no execution;
- no dispatch;
- no governance;
- no replay mutation;
- no worker authority.

### WORKER

Purpose:

```text
Perform authorized bounded work.
```

Examples:

- Replay Inspector Worker;
- Market Evidence Normalization Worker;
- Portfolio Context Worker.

Authority:

- may execute only authorized task packet;
- may not self-authorize;
- may not self-dispatch;
- may not govern;
- may not mutate replay or governance.

### HYBRID_PROVIDER_WORKER

Purpose:

```text
Represent a Resource with both proposal-source and worker-capable roles.
```

Examples:

- `CODEX`
- `CLAUDE_CODE`

Authority:

- provider role is proposal-only;
- worker role requires governed authorization;
- active role must be explicit;
- role switching must be forbidden unless separately selected and recorded.

### OPERATOR_TOOL

Purpose:

```text
Assist human operator visibility or interaction.
```

Authority:

- no provider authority;
- no worker execution authority;
- no governance mutation;
- no replay mutation.

### GOVERNANCE_RUNTIME

Purpose:

```text
AiGOL-owned validation, policy, reconstruction, or certification runtime.
```

Authority:

- governance evaluation within defined runtime scope;
- no provider proposal authority;
- no worker execution authority unless separately defined;
- no hidden mutation.

### DOMAIN_RUNTIME

Purpose:

```text
Domain-specific validation or evidence processing runtime.
```

Authority:

- domain-scoped validation only unless future worker authority is explicitly authorized.

## Category Decision

AiGOL classifies Resource category from:

- primary role;
- possible secondary roles;
- execution capability;
- proposal capability;
- governance ownership;
- operator interaction function;
- authority boundary.

Ambiguous category fails closed or requires human clarification.

## Initial Classification

```text
OPENAI = PROVIDER
ANTHROPIC = PROVIDER
CODEX = HYBRID_PROVIDER_WORKER
CLAUDE_CODE = HYBRID_PROVIDER_WORKER
```

