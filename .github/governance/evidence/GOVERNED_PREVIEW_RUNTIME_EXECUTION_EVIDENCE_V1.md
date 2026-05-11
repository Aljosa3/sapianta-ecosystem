# Governed Preview Runtime Execution Evidence V1

Status: replay-safe preview runtime evidence.

Capability:
`LOCALHOST_PREVIEW_RUNTIME_V1`

## Evidence Summary

The governed preview runtime layer provides deterministic validation and command preparation for bounded local Product 1 preview.

It supports:

- request modeling;
- lifecycle description;
- capability registry validation;
- prepared command generation;
- forbidden boundary reporting;
- primitive identity;
- request, command, and scope hashes;
- replay lineage references;
- deterministic result hashes.

It does not execute the command or start a server.

## Implementation Evidence

Created runtime helper:

- `runtime/governance/preview_runtime.py`

Created tests:

- `tests/test_governed_preview_runtime.py`

Created specification:

- `docs/governance/GOVERNED_PREVIEW_RUNTIME_EXECUTION_V1.md`

## Prepared Command

```bash
uvicorn sapianta_system.sapianta_product.main:app --host 127.0.0.1 --port 8010
```

This is a prepared bounded command only.

## Boundary Evidence

Escalation is required for:

- host `0.0.0.0`;
- port changes;
- persistent runtime;
- deployment semantics;
- background execution;
- public network exposure;
- mutation scope expansion;
- unapproved app target.

## Validation Evidence

Required validation:

- `pytest tests/test_governed_preview_runtime.py`
- `python -m py_compile runtime/governance/preview_runtime.py`
- `git diff --check`

## Explicit Non-Execution Evidence

The helper does not start a server.

The result model includes:

- primitive ID;
- request hash;
- command hash;
- scope hash;
- replay lineage references;
- `server_started: false`

No deployment automation is introduced.
