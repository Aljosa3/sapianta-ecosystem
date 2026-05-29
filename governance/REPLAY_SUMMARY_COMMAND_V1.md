# Replay Summary Command V1

Status: operator usability milestone.

This artifact defines a simple operator-facing replay summary command. It adds no capabilities, execution powers, orchestration, memory, or agents.

## Primary Goal

Allow an operator to quickly inspect:

- what happened
- status
- capability used
- authorization outcome
- replay verification status
- governed result

without manually opening replay artifacts.

## Summary Fields

The replay summary view includes:

- Replay ID
- Status
- Capability
- Authorization Status
- Verification Status
- Result Summary
- Timestamp / Ordering Information

## Boundary Status

The replay summary command is read-only. It reconstructs existing replay evidence and presents a deterministic view.

It does not:

- add capabilities
- execute capabilities
- authorize execution
- mutate replay
- add orchestration
- add memory
- add agents

## Success

Success is an operator understanding a replay outcome through a single replay summary view.
