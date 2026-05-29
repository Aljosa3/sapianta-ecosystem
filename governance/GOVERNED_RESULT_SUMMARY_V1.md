# Governed Result Summary V1

Status: first operator-facing governed result presentation milestone.

This artifact defines the standardized governed result summary format. It introduces no new capability, no new authority, no replay bypass, no orchestration, and no runtime expansion.

## Primary Goal

An operator should understand:

- what happened
- why it happened
- who authorized it
- what capability was used
- where replay evidence exists
- what should happen next

without inspecting raw replay artifacts.

## Required Fields

Every governed result summary contains:

- Status
- Reason
- Capability Used
- Replay Reference
- Replay Verification Status
- Authority Boundary Reminder
- Evidence Summary
- Recommended Next Action

## Source Of Truth

The summary is replay-derived. It presents governed result and replay evidence in a compact human-readable form.

The summary is not:

- a new authority
- a new validator
- a replay replacement
- an execution engine
- a reasoning layer

## Boundary Reminder

Every summary preserves:

```text
LLM proposes; AiGOL governs; worker executes after authorization; replay records.
```

## Success

Success is not new capability.

Success is making governed results understandable without requiring the operator to inspect raw replay artifacts first.
