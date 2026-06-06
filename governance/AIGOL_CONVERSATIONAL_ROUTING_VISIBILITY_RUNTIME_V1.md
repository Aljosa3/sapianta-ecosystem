# AIGOL_CONVERSATIONAL_ROUTING_VISIBILITY_RUNTIME_V1

## Status

Certified runtime milestone.

Classification:

```text
CERTIFIED_CONVERSATIONAL_ROUTING_VISIBILITY_RUNTIME
```

## Objective

Implement operator-visible conversational routing transparency for:

```text
aigol conversation
```

This milestone addresses routing visibility findings from
`AIGOL_CONVERSATIONAL_CLI_OPERATIONAL_VALIDATION_V1`:

- routing is deterministic but opaque;
- operators cannot see why a prompt routed to a specific workflow;
- operators cannot distinguish OCS cognition routing from fallback routing;
- diagnosis currently requires replay inspection or source-code review.

## Runtime Behavior

Before workflow execution begins, each conversational turn emits a routing
visibility block:

```text
================================
ROUTING DECISION
workflow: OCS_LLM_COGNITION
confidence: MEDIUM
matched:
- sell domains
- license the platform
- managed services
competing:
- OPERATOR_DECISION_SUPPORT
reason:
Prompt requests comparative strategic analysis.
================================

[1/8] Routing
```

If no certified workflow matches, the operator sees:

```text
================================
ROUTING FAILED CLOSED
confidence: LOW
matched:
[]
competing:
[]
reason:
No certified workflow matched.
================================
```

The legacy fallback path remains behaviorally unchanged; the failed routing
visibility appears before fallback execution.

## Artifact

The runtime persists:

```text
CONVERSATIONAL_ROUTING_VISIBILITY_ARTIFACT_V1
```

Required fields:

- `turn_id`;
- `workflow_id`;
- `routing_confidence`;
- `matched_signals`;
- `competing_signals`;
- `routing_reason`;
- `routing_timestamp`.

The artifact is replay-visible and visibility-only. It grants no authority.

## Confidence Model

Confidence is deterministic and bounded:

- `HIGH`;
- `MEDIUM`;
- `LOW`.

No probabilistic scoring is introduced.

When a selected route has competing partial signals, confidence may be reduced
from `HIGH` to `MEDIUM` for operator visibility.

## Replay Evidence

Each turn records routing visibility under:

```text
<runtime_root>/<session_id>/<turn_id>/routing_visibility/
```

Replay file:

```text
000_conversational_routing_visibility_recorded.json
```

Replay reconstruction proves:

```text
Human Prompt -> Routing Signals -> Routing Decision -> Workflow Selection
```

without source-code inspection.

## Boundary Preservation

This milestone does not change:

- workflow routing behavior;
- OCS cognition runtime;
- provider runtime;
- worker runtime;
- existing routing replay schemas;
- execution authority;
- approval authority;
- governance authority.

It adds only deterministic routing explanation evidence and operator rendering.

## Acceptance

Accepted when routing visibility is rendered and reconstructable for:

1. OCS cognition prompt;
2. operator decision-support prompt;
3. domain creation prompt;
4. replay review prompt;
5. failed/default routing prompt.

The operator can determine:

- where the prompt routed;
- why it routed there;
- what alternatives were considered;

without reading replay files.
