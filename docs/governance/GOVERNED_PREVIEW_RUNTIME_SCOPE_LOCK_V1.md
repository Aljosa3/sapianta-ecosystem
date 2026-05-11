# Governed Preview Runtime Scope Lock V1

Status: finalized scope lock declaration.

Primitive:
`GOVERNED_PREVIEW_RUNTIME_EXECUTION_V1`

Capability:
`LOCALHOST_PREVIEW_RUNTIME_V1`

## Locked Scope

The preview runtime primitive is locked to:

- host: `127.0.0.1`
- port: `8010`
- runtime: `uvicorn`
- target: `sapianta_system.sapianta_product.main:app`
- lifecycle: `start -> validate -> stop`
- execution type: temporary local preview only

## Locked Command

The only approved prepared command is:

```bash
uvicorn sapianta_system.sapianta_product.main:app --host 127.0.0.1 --port 8010
```

The command is a prepared command, not an executed command.

## Controlled Changes

The following require governed review and renewed approval:

- port value;
- host value;
- app target;
- preview runtime;
- lifecycle stages;
- visual validation semantics;
- capability ID;
- command model;
- forbidden boundary checks.

## Escalation Boundary

Escalation is mandatory for:

- public binding;
- host `0.0.0.0`;
- public network exposure;
- persistence;
- background execution;
- deployment semantics;
- production runtime mutation;
- arbitrary subprocess execution;
- runtime orchestration expansion.

## Non-Inheritance Rule

Approval for this primitive does not authorize:

- deployment;
- daemon lifecycle management;
- shell command execution;
- production runtime management;
- server control beyond separately approved tooling;
- additional operational capabilities.

