# GOVERNED_OPERATIONAL_LOOP_IMPLEMENTATION_PLAN_V1

## Status

Plan only.

## Purpose

This plan defines a bounded implementation path for the governed operational
loop described by `GOVERNED_OPERATIONAL_LOOP_V1`.

This plan does not implement runtime code, add orchestration runtime, create
automatic execution, expand authority, add hidden persistence, or add semantic
autonomy.

## Implementation Scope

The first implementation should bind existing components rather than introduce
new autonomous layers:

- Browser Companion sidepanel observability;
- AGOL Bridge task and result package transport;
- append-only replay logging;
- lifecycle state transitions;
- explicit approval gates;
- Codex as the first execution provider boundary.

## Implementation Phases

### Phase 1: Loop Contract Binding

Define a small loop contract that names the current stage, task package
identity, result package identity, replay reference, lifecycle state, approval
state, and authority boundary.

No dispatch or execution behavior should be added in this phase.

### Phase 2: Task and Result Package Mapping

Map governed task synthesis and governed result package semantics to existing
AGOL Bridge schemas. Preserve deterministic JSON, replay-safe ids, lineage
references, and mutation boundaries.

### Phase 3: Approval Checkpoints

Make approval state explicit before dispatch. Missing approval must produce
`WAITING_FOR_APPROVAL` or blocked state according to existing lifecycle rules.

### Phase 4: Provider Boundary Binding

Bind Codex as the first provider only through governed transport. Provider
adapters must not approve, govern, mutate replay, or bypass lifecycle.

### Phase 5: Replay and Lifecycle Updates

Ensure task dispatch, result return, failure, quarantine, and finalization
states produce append-only replay entries and visible lifecycle state.

### Phase 6: Sidepanel Observability

Expose loop stage, replay reference, lifecycle state, approval state, provider
boundary, and next-step proposal as read-only sidepanel observability.

## Required Tests

Future implementation tests should prove:

- malformed task packages fail closed;
- missing approval blocks dispatch;
- dispatch does not occur automatically;
- provider output returns only as result package;
- replay entries append and are not rewritten;
- lifecycle state transitions are bounded;
- sidepanel observability does not create authority;
- next-step proposals are not approved continuation.

## Authority Boundaries

Implementation must preserve:

- ChatGPT / LLMs = semantic cognition only;
- AiGOL / AGOL = governance, replay, lifecycle, transport, admissibility;
- Codex / providers = execution only through governed transport;
- sidepanel = read-only observability.

## Prohibited Implementation Behavior

- hidden dispatch
- hidden execution
- automatic approval
- unrestricted orchestration
- semantic autonomy escalation
- silent mutation
- replay rewriting
- hidden persistence
- hidden networking
- lifecycle bypass
- approval bypass

## Recommended Next Step

Before runtime implementation, create a narrow loop contract artifact that maps
the operational stages to existing AGOL Bridge package fields and sidepanel
observability labels. That contract should be reviewed before code changes.
