# AIGOL_RUNTIME_PROGRESS_VISIBILITY_V1

## Status

CERTIFIED

## Purpose

Create a deterministic, replay-visible progress visibility layer for AiGOL CLI workflows.

The layer lets an operator inspect whether a workflow is pending, running, waiting, completed, or failed closed without granting new execution, dispatch, provider, worker, PPP, or governance authority.

## Runtime Surface

Runtime module:

- `aigol/runtime/runtime_progress_visibility.py`

CLI commands:

- `python -m aigol.cli.aigol_cli runtime-status <runtime_id>`
- `python -m aigol.cli.aigol_cli runtime-progress <runtime_id>`
- `python -m aigol.cli.aigol_cli runtime-watch <runtime_id>`

Default progress replay root:

- `.aigol_runtime_progress/<runtime_id>/`

## Status Model

Supported statuses:

- `PENDING`
- `RUNNING`
- `WAITING_FOR_PROVIDER`
- `WAITING_FOR_HUMAN_CLARIFICATION`
- `WAITING_FOR_HUMAN_APPROVAL`
- `COMPLETED`
- `FAILED_CLOSED`

Terminal statuses:

- `COMPLETED`
- `FAILED_CLOSED`

## Stage Model

Canonical stages:

- `CONVERSATION`
- `CLARIFICATION`
- `COGNITION`
- `RESOURCE_SELECTION`
- `PPP`
- `PROVIDER_PROPOSAL_PRODUCTION`
- `PROPOSAL_VALIDATION`
- `APPROVAL`
- `HANDOFF`
- `REPLAY_IMPROVEMENT`

The stage model may be supplied explicitly for a runtime, but it must be ordered, non-empty, and duplicate-free.

## Progress Model

Progress is deterministic:

- `stage_count` is the number of configured stages.
- `completed_stages` is an ordered subset of the stage model.
- `completed_stage_count` is the length of `completed_stages`.
- `current_stage` must exist in the stage model.
- `progress_percent` is `completed_stage_count / stage_count`, except `COMPLETED`, which is `100`.

The runtime does not infer hidden work or observe private provider progress.

## ETA Model

`RUNTIME_DURATION_HISTORY_V1` records replay-visible duration inputs:

- stage average duration;
- stage last duration;
- stage sample count;
- runtime duration;
- history hash.

ETA is replay-only and deterministic:

- `estimated` when all remaining stages have average duration data;
- `unknown` when duration data is incomplete or the runtime failed closed;
- `00:00:00` when the runtime is completed.

ETA is advisory visibility, not scheduling authority.

## Replay Model

Each visibility snapshot is persisted as:

- `NNN_runtime_progress_visibility_snapshot.json`

Each snapshot records:

- runtime status;
- stage transitions;
- timestamps;
- elapsed duration;
- ETA calculation inputs;
- visibility snapshot hash;
- previous snapshot hash;
- authority boundary flags.

Replay reconstruction verifies:

- wrapper hash integrity;
- artifact hash integrity;
- runtime id continuity;
- stage ordering;
- timestamp ordering;
- status continuity;
- completed-stage continuity.

## CLI Visibility

`runtime-status` renders compact operator status.

`runtime-progress` renders the full progress view:

```text
[RUNNING]

Runtime ID:
RUNTIME-12345

Current Stage:
PROVIDER_PROPOSAL_PRODUCTION

Progress:
███████░░░ 70%

Elapsed:
00:00:14

Estimated Remaining:
00:00:06

Current Activity:
Validating provider request packet
```

`runtime-watch` refreshes progress from replay. It does not control the runtime.

## Fail-Closed Conditions

The runtime fails closed when:

- runtime id is missing;
- status is invalid;
- current stage is missing;
- current stage is not in the stage model;
- completed stages are out of order;
- timestamps are invalid;
- timestamp ordering regresses;
- replay hash verification fails;
- artifact hash verification fails;
- status continuity regresses;
- stage ordering regresses;
- duration history is malformed.

## Authority Boundaries

This runtime must not:

- alter execution;
- alter governance;
- alter PPP;
- alter providers;
- alter workers;
- authorize;
- dispatch;
- execute.

It only creates and reads governed visibility artifacts.

## Final Classification

AIGOL_RUNTIME_PROGRESS_VISIBILITY_STATUS = CERTIFIED
