# Governed Preview Runtime Finalization Evidence V1

Status: replay-safe preview runtime finalization evidence.

Primitive:
`GOVERNED_PREVIEW_RUNTIME_EXECUTION_V1`

Capability:
`LOCALHOST_PREVIEW_RUNTIME_V1`

Certification state:
`CERTIFIED_BOUNDED_PREVIEW_RUNTIME`

## Evidence Summary

The governed preview runtime primitive is finalized as a deterministic, non-executing lifecycle helper for local Product 1 preview preparation.

It provides:

- deterministic request modeling;
- capability-scoped validation;
- prepared command generation;
- forbidden boundary checks;
- escalation-first behavior;
- explicit primitive identity;
- request, command, and scope hashes;
- replay lineage references;
- replay-visible deterministic hashes;
- lifecycle description.

## Implementation Evidence

Runtime helper:

- `runtime/governance/preview_runtime.py`

Dependency surfaces:

- `runtime/governance/capability_registry.py`
- `runtime/governance/capability_models.py`

Tests:

- `tests/test_governed_preview_runtime.py`

Governance docs:

- `docs/governance/GOVERNED_PREVIEW_RUNTIME_EXECUTION_V1.md`
- `docs/governance/GOVERNED_PREVIEW_RUNTIME_FINALIZATION_V1.md`
- `docs/governance/GOVERNED_PREVIEW_RUNTIME_ACCEPTANCE_CRITERIA_V1.md`
- `docs/governance/GOVERNED_PREVIEW_RUNTIME_SCOPE_LOCK_V1.md`

## Scope Evidence

Locked scope:

- host: `127.0.0.1`
- port: `8010`
- runtime: `uvicorn`
- target: `sapianta_system.sapianta_product.main:app`
- lifecycle: `start -> validate -> stop`

## Non-Execution Evidence

The helper explicitly reports:

- `server_started: false`

The helper does not:

- start a server;
- execute subprocesses;
- deploy software;
- create daemons;
- manage production lifecycle.

## Validation Evidence

Required validation:

- `pytest tests/test_governed_preview_runtime.py`
- `python -m py_compile runtime/governance/preview_runtime.py`
- `python -m json.tool .github/governance/finalize/GOVERNED_PREVIEW_RUNTIME_FINALIZE_MANIFEST_V1.json`
- `python -m json.tool .github/governance/finalize/GOVERNED_PREVIEW_RUNTIME_CERTIFICATION_V1.json`
- `git diff --check`

## Known Limitations

The primitive does not perform browser checks, screenshot validation, runtime health polling, process management, deployment, or daemon orchestration. These limitations are intentional governance boundaries.
