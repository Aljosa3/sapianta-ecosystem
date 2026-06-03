# CONVERSATION_PPP_RESOURCE_SELECTION_ROUTING_V1

## Status

Certified routing integration.

## Purpose

`CONVERSATION_PPP_RESOURCE_SELECTION_ROUTING_V1` connects conversation-mode native development prompts to the certified Resource Selection and PPP pipeline.

It routes:

```text
Human Prompt
-> Cognition
-> Context Assembly
-> Resource Selection
-> Resource Selection PPP Integration
-> PPP Proposal Production
-> Proposal Validation
-> Repair / Retry
-> Clarification / Approval
-> Implementation Handoff
```

## Layer Boundary

Conversation remains an entrypoint and routing surface only.

It does not become:

- Resource Selection;
- PPP;
- Governance;
- Execution;
- Worker invocation.

## Runtime

Runtime module:

```text
aigol/runtime/conversation_ppp_resource_selection_routing.py
```

Primary artifact:

```text
CONVERSATION_PPP_RESOURCE_SELECTION_ROUTING_ARTIFACT_V1
```

Replay-visible events:

```text
000_conversation_resource_ppp_route_recorded.json
001_conversation_resource_ppp_route_returned.json
```

## Supported Resources

Supported resource categories:

- `PROVIDER`;
- `WORKER`;
- `HYBRID_PROVIDER_WORKER`.

Supported explicit hybrid roles:

- `CODEX_PROVIDER_ROLE`;
- `CODEX_WORKER_ROLE`;
- `CLAUDE_CODE_PROVIDER_ROLE`;
- `CLAUDE_CODE_WORKER_ROLE`.

Hybrid resources require explicit role selection. AiGOL must fail closed on implicit hybrid role switching.

## Provider Path

Provider resources may be routed into proposal production only after:

- task intake succeeds;
- context assembly succeeds;
- domain and worker resolution succeeds;
- provider necessity is `PROVIDER_REQUIRED`;
- unified resource selection succeeds;
- resource selection PPP integration returns `PPP_PROVIDER_PROPOSAL_READY`;
- selected provider resource matches the provider id used for proposal production.

Provider output remains proposal-only.

## Worker Path

Worker-role resources may only produce a PPP handoff reference.

Conversation routing must not:

- invoke workers;
- dispatch workers;
- execute work;
- authorize work;
- create domains;
- create workers.

## Fail-Closed Conditions

The runtime fails closed when:

- cognition or context assembly fails;
- domain or worker resolution fails;
- provider necessity is not `PROVIDER_REQUIRED`;
- resource selection fails;
- resource role is ambiguous;
- hybrid role is implicit;
- resource PPP integration fails;
- selected provider resource mismatches the provider id;
- provider proposal production fails without repair or escalation;
- replay reconstruction detects corruption.

## Authority Boundaries

The runtime records:

- `provider_authority = false`;
- `aigol_governance_only = true`;
- `human_final_authority = true`;
- `worker_invoked = false`;
- `execution_requested = false`;
- `dispatch_requested = false`;
- `authorization_created = false`;
- `governance_modified = false`.

## Final Classification

```text
CONVERSATION_PPP_RESOURCE_SELECTION_ROUTING_STATUS = CERTIFIED
```
