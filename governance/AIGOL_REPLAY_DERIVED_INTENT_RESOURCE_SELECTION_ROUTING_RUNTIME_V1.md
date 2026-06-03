# AIGOL_REPLAY_DERIVED_INTENT_RESOURCE_SELECTION_ROUTING_RUNTIME_V1

## Status

Runtime certification.

## Final Classification

```text
AIGOL_REPLAY_DERIVED_INTENT_RESOURCE_SELECTION_ROUTING_RUNTIME_STATUS = CERTIFIED
```

## Purpose

`AIGOL_REPLAY_DERIVED_INTENT_RESOURCE_SELECTION_ROUTING_RUNTIME_V1` converts cognition-routed replay-derived improvement intent into Resource Selection-compatible structured requirements.

It implements:

```text
Cognition Routed Intent
-> Resource Selection Routing Evidence
-> Resource Selection Routing Classification
-> Resource Selection Routed Intent
```

It does not invoke Resource Selection.

## Runtime

Implemented:

```text
aigol/runtime/replay_derived_intent_resource_selection_routing_runtime.py
```

Primary function:

```text
route_replay_derived_intent_to_resource_selection
```

Replay reconstruction:

```text
reconstruct_replay_derived_intent_resource_selection_routing_replay
```

## Artifacts

Defined:

```text
RESOURCE_SELECTION_ROUTING_EVIDENCE_V1
RESOURCE_SELECTION_ROUTING_CLASSIFICATION_V1
RESOURCE_SELECTION_ROUTED_INTENT_V1
```

## Replay Events

Replay steps:

```text
000_resource_selection_routing_evidence_recorded.json
001_resource_selection_routing_classification_recorded.json
002_resource_selection_routed_intent_recorded.json
003_resource_selection_routing_returned.json
```

## Resource Selection Input Contract

The routed artifact exposes:

```text
workflow_type
required_capability
requested_role_type
domain_id
provider_necessity_classification
confidence
intent_source_visible_to_resource_selection
```

The contract is source-agnostic.

Source lineage remains replay-visible outside the Resource Selection input contract.

## Intent-Source Equivalence

Human Intent and Replay-Derived Intent become equivalent Resource Selection inputs once both are normalized into structured requirements.

Resource Selection receives:

- workflow type;
- required capability;
- requested role type;
- domain id;
- provider necessity;
- confidence.

Resource Selection does not need to know whether the intent came from a human prompt or replay-derived improvement intent.

## Fail-Closed Conditions

The runtime fails closed when:

- cognition routed intent is missing;
- cognition routing evidence is missing;
- cognition routing classification is missing;
- cognition intent is not routed;
- source visibility leaks into Resource Selection;
- source lineage is broken;
- chain continuity fails;
- artifact hashes mismatch;
- Resource Selection requirement classification is ambiguous.

## Authority Boundaries

The runtime preserves:

```text
resource_selection_invoked = false
proposal_created = false
ppp_invoked = false
provider_invoked = false
worker_invoked = false
authorization_created = false
execution_requested = false
dispatch_requested = false
governance_mutated = false
replay_mutated = false
```

## Readiness Impact

Replay-derived improvement readiness now includes:

```text
Replay
-> Gap Detection
-> Improvement Intent
-> Cognition Routing
-> Resource Selection Routing
```

The next missing step is actual Resource Selection consumption and PPP integration for replay-derived improvement intent.

## Recommended Next Milestone

```text
AIGOL_REPLAY_DERIVED_INTENT_RESOURCE_SELECTION_PPP_INTEGRATION_RUNTIME_V1
```
