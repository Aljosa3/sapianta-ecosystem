# AIGOL_HUMAN_DECISION_RUNTIME_V1

## Status

Certified runtime milestone.

`AIGOL_HUMAN_DECISION_RUNTIME_STATUS = CERTIFIED`

## Purpose

`AIGOL_HUMAN_DECISION_RUNTIME_V1` implements explicit human decision handling
for operations that reach `HUMAN_APPROVAL_REQUIRED`.

The runtime presents and records three governed choices:

- `APPROVE`;
- `REJECT`;
- `REQUEST_MODIFICATION`.

## Runtime Model

The runtime records a replay-visible human decision artifact before any
downstream branch is taken.

Decision behavior:

| Decision | Runtime outcome |
| --- | --- |
| `APPROVE` | Records human decision and continues through the existing approval resume path. |
| `REJECT` | Records governed rejection and terminates the pending approval operation without implementation handoff. |
| `REQUEST_MODIFICATION` | Records a modification request and enters replay-visible clarification state. |

## Replay Model

Human decisions emit:

1. `000_human_decision_recorded.json`;
2. `001_human_decision_returned.json`.

Replay reconstruction verifies:

- replay order;
- wrapper hashes;
- decision artifact hash;
- returned artifact hash;
- decision reference continuity;
- chain continuity;
- approval scope continuity.

## Approval Lineage

The decision runtime validates:

- approval-required artifact hash;
- `HUMAN_APPROVAL_REQUIRED` terminal status;
- approval resume packet hash;
- approval request artifact hash;
- approval request pending status;
- approval lineage between request and approval-required artifact.

The existing approval resume runtime remains authoritative for the approved
implementation handoff continuation.

## Authority Boundaries

The human decision artifact does not create execution, dispatch, invocation,
provider authority, worker authority, automatic approval, governance mutation,
or replay mutation.

Reject and modification paths do not create:

- implementation handoff;
- execution authorization;
- worker invocation request;
- worker assignment;
- worker dispatch;
- worker invocation;
- executable bundle.

## Human-Facing CLI Interaction

When `HUMAN_APPROVAL_REQUIRED` is reached, the interactive CLI shows:

- `APPROVE`;
- `REJECT`;
- `REQUEST_MODIFICATION`.

The following turn records the selected human decision before branching.

## Replay Impact

The approval-required lifecycle is now replay-visible across all three human
decision outcomes. `APPROVE` preserves the existing approval resume lineage.
`REJECT` creates a governed terminal rejection record. `REQUEST_MODIFICATION`
creates a replay-visible clarification state suitable for bounded future
proposal revision work.

## Validation Results

Validation passed for:

- direct human decision runtime replay reconstruction;
- interactive approve path;
- interactive reject path;
- interactive request-modification path;
- existing approval resume compatibility.

Direct CLI validation also passed for:

- `Improve trading strategy.` -> `Approve`;
- `Improve trading strategy.` -> `Reject`;
- `Improve trading strategy.` -> `Request modification`.

## Commit Message

`Certify human decision runtime`

## Final Classification

AIGOL_HUMAN_DECISION_RUNTIME_STATUS = CERTIFIED
