# UNIFIED_RESOURCE_SELECTION_PPP_INTEGRATION_V1

## Status

Runtime integration certification.

## Final Classification

```text
UNIFIED_RESOURCE_SELECTION_PPP_INTEGRATION_STATUS = CERTIFIED
```

## Purpose

This milestone integrates Unified Resource Selection with PPP as a deterministic pre-production gate.

PPP can now consume:

- selected Resource id;
- Resource category;
- active role;
- capability match;
- trust match;
- authority match;
- selection hash;
- context reference.

## Runtime Component

Implemented:

```text
aigol/runtime/unified_resource_selection_ppp_integration.py
```

## Integration Position

Updated PPP lifecycle:

```text
Conversation
Task Intake
Context Assembly
Resource Selection
Resource PPP Integration
PPP
Proposal Production
Proposal Validation
Repair / Retry
Clarification / Approval
Implementation Handoff
```

This runtime implements the `Resource Selection -> PPP` integration boundary only.

It does not invoke proposal production.

## Defined Artifact

Defined:

```text
RESOURCE_PPP_INTEGRATION_ARTIFACT_V1
```

## Supported Resource Categories

Supported:

- `PROVIDER`;
- `WORKER`;
- `HYBRID_PROVIDER_WORKER`.

Provider role selections become:

```text
PPP_PROVIDER_PROPOSAL_READY
```

Worker role selections become:

```text
PPP_WORKER_HANDOFF_REFERENCE_READY
```

## Hybrid Resource Handling

Hybrid Resources require explicit role selection.

Valid examples:

```text
CODEX as PROVIDER_ROLE
CODEX as WORKER_ROLE
```

Invalid:

```text
CODEX with no active role
CODEX with implicit role switch
```

The integration does not allow provider authority to flow into worker authority or worker authority to flow into provider authority.

## Replay

Replay steps:

```text
000_resource_ppp_integration_recorded.json
001_resource_ppp_integration_returned.json
```

Replay preserves:

- integration id;
- selected Resource id;
- Resource category;
- active role;
- selected Resource version;
- selected authority profile;
- selection hash;
- selection rationale;
- capability match;
- trust match;
- authority match;
- context hash;
- PPP stage;
- PPP Resource status.

## Fail-Closed Conditions

The integration fails closed when:

- resource selection is missing;
- resource selection did not succeed;
- selected role is missing or ambiguous;
- provider or worker category conflicts with selected role;
- capability match is false;
- trust match is false;
- authority match is false;
- replay inconsistency is detected;
- PPP stage is incompatible with selected role;
- replay artifact already exists;
- replay corruption is detected.

## Authority Boundaries

The runtime does not:

- invoke providers;
- invoke Workers;
- dispatch;
- execute;
- authorize;
- create provider authority;
- create worker authority;
- mutate governance;
- mutate replay outside append-only integration evidence.

## Ecosystem Readiness Impact

PPP can now consume Resource Selection output deterministically.

Updated readiness:

```text
RESOURCE_SELECTION_READY = 100%
PPP_RESOURCE_INTEGRATION_READY = 100%
PROVIDER_OR_WORKER_INVOCATION_READY = NOT_STARTED
```

## Recommended Next Milestone

```text
CONVERSATION_PPP_RESOURCE_SELECTION_ROUTING_V1
```

This should update conversation PPP routing to call Resource Selection and this integration gate before provider proposal production.

