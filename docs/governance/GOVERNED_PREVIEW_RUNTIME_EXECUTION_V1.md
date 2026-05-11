# Governed Preview Runtime Execution V1

Status: bounded preview runtime lifecycle specification.

Capability:
`LOCALHOST_PREVIEW_RUNTIME_V1`

Parent governance:
- `AGENTS.md`
- `CODEX_TASK_EXECUTION_PROTOCOL_V1.md`
- `GOVERNED_CAPABILITY_MEMORY_V1.md`
- `GOVERNED_CAPABILITY_SCOPE_LOCK_V1.md`
- `LLM_ROLE_AND_BOUNDARY_MODEL_V1.md`

## Purpose

This milestone creates the first bounded preview runtime lifecycle layer for SAPIANTA.

It enables deterministic validation and command preparation for a local preview lifecycle:

start -> validate -> stop

It does not start the server silently. It does not deploy software. It does not create daemon orchestration or production runtime management.

## Allowed Lifecycle

The only approved lifecycle is:

1. start: prepare a temporary localhost preview command.
2. validate: use the preview for bounded visual and runtime verification.
3. stop: terminate the temporary preview process.

The lifecycle is temporary and bounded. It exists to prevent daemon drift, persistence creep, public exposure, and uncontrolled runtime continuation.

## Capability Boundary

Allowed:

- capability: `LOCALHOST_PREVIEW_RUNTIME_V1`
- host: `127.0.0.1`
- port: `8010`
- runtime: `uvicorn`
- app target: `sapianta_system.sapianta_product.main:app`
- lifecycle: `start -> validate -> stop`
- temporary local preview only
- visual validation support

Prepared command:

```bash
uvicorn sapianta_system.sapianta_product.main:app --host 127.0.0.1 --port 8010
```

The command is prepared as bounded evidence. It is not executed by the helper.

## Forbidden Boundaries

The preview runtime layer must not allow:

- deployment
- public binding
- `0.0.0.0`
- systemd changes
- firewall changes
- daemon persistence
- background permanent services
- production runtime mutation
- unrestricted shell execution
- arbitrary subprocess commands
- autonomous runtime orchestration

## Relation to Capability Memory

The preview runtime layer depends on `runtime/governance/capability_registry.py`.

The capability registry decides whether the requested scope matches `LOCALHOST_PREVIEW_RUNTIME_V1`.

If the scope changes, the request escalates instead of expanding trust silently.

## Why This Is Not Deployment Automation

Deployment automation would move code into a stable or public runtime environment.

This layer only prepares a localhost command for temporary preview. It does not:

- publish a service;
- alter server state;
- modify systemd;
- bind to public interfaces;
- create release artifacts;
- deploy to production or demo servers.

## Why This Is Not Autonomous Runtime Orchestration

Autonomous orchestration would start, monitor, restart, or persist runtime processes.

This layer does not do that. It only validates a request and returns a prepared command. Human/tooling approval is still required to execute the command.

## Replay-Safe Preview Semantics

Preview validation output includes:

- capability ID;
- decision;
- approved/escalation/rejected state;
- prepared command when approved;
- reason;
- lifecycle;
- forbidden boundary checks;
- deterministic hash;
- `server_started: false`.

The result is deterministic and replay-visible.

## Known Limitations

This layer does not:

- start a server;
- stop a server;
- inspect browser output;
- perform screenshot validation;
- perform deployment;
- manage processes;
- provide general shell access;
- authorize runtime mutation.

These limitations are intentional governance boundaries.

