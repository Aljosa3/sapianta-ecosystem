# MINIMAL_RUNTIME_OPERATOR_CLI_V1

## Scope

This milestone introduces minimal read-only runtime operator observability only. It does not introduce orchestration controls, runtime mutation, execution management, or operational control planes.

The operator surface provides local deterministic visibility into:

- runtime state;
- replay lineage integrity;
- approval checkpoints;
- retry state;
- goal continuity;
- routing decisions.

## Components

- Runtime summary generation.
- Runtime query helpers.
- Text-only runtime reports.
- Local module CLI.

## CLI Commands

```bash
python -m aigol.runtime.operator.runtime_cli summary <runtime_id>
python -m aigol.runtime.operator.runtime_cli goal <goal_id>
python -m aigol.runtime.operator.runtime_cli retry <runtime_id>
```

The CLI also accepts `--root <path>` for local artifact roots.

## Boundary

The operator CLI is read-only. It reads persisted runtime artifacts and verifies replay hashes through existing runtime store loaders.

It does not execute workers, call providers, mutate runtime state, edit artifacts, repair runtime state, expose control APIs, create dashboards, or introduce orchestration controls.

## Fail-Closed Behavior

Missing or corrupted runtime artifacts fail closed through existing replay loaders.

Invalid runtime IDs, missing retry artifacts, and missing goal artifacts fail closed.

## Non-Goals

- Web dashboard.
- Distributed monitoring.
- Runtime mutation.
- Execution control APIs.
- Orchestration controls.
- Auto-repair.
- Runtime editing.
- Websocket infrastructure.
- Runtime management platform.

## Certification

`MINIMAL_RUNTIME_OPERATOR_CLI_V1` certifies minimal local read-only operational runtime visibility before Phase 3 real tool/API integration.
