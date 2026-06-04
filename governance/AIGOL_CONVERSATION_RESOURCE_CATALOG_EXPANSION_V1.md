# AIGOL_CONVERSATION_RESOURCE_CATALOG_EXPANSION_V1

## Status

CERTIFIED

## Purpose

Expand deterministic conversation resource catalog coverage so known development requests route into the already-certified conversation-to-PPP handoff pipeline.

This milestone changes catalog recognition only. It does not add execution, dispatch, authorization, worker invocation, provider invocation, or governance mutation authority.

## Root Cause

The live conversation pipeline was operational, but normal prompts for known resources were not classified by the conversation entry catalog.

Observed failures were caused by missing catalog entries for:

- `CLAUDE_CODE` provider;
- `SERVER_MANAGEMENT` domain;
- `FILESYSTEM` worker family;
- `MONITORING` worker family.

Because the prompts were not recognized as native-development intents, they fell through to provider-unavailable clarification fallback, where they failed closed as not clarification-eligible.

## Catalog Changes

Provider catalog:

- added `CLAUDE_CODE`

Domain catalog:

- added `SERVER_MANAGEMENT`

Worker catalog:

- added `FILESYSTEM`
- added `MONITORING`

Registry mappings:

- registered `SERVER_MANAGEMENT` as a future domain;
- registered `FILESYSTEM` as a `SERVER_MANAGEMENT` worker family;
- registered `MONITORING` as a `SERVER_MANAGEMENT` worker family.

## Classification Coverage Added

| Prompt | Intent Class | Catalog Target |
| --- | --- | --- |
| `Add provider Claude Code.` | `ADD_PROVIDER` | `CLAUDE_CODE` provider |
| `Create a server management domain.` | `CREATE_DOMAIN` | `SERVER_MANAGEMENT` domain |
| `Create a filesystem worker.` | `CREATE_WORKER` | `SERVER_MANAGEMENT` / `FILESYSTEM` |
| `Create a monitoring worker.` | `CREATE_WORKER` | `SERVER_MANAGEMENT` / `MONITORING` |

## Replay Impact

Native-development intent routing now persists:

- catalog version;
- catalog version hash;
- catalog hash;
- catalog match terms;
- catalog match evidence.

Replay reconstruction verifies:

- classification lineage;
- routed intent lineage;
- catalog hash continuity;
- catalog version hash continuity;
- wrapper and artifact hash integrity.

## CLI Before And After

Before:

```text
Add provider Claude Code.
-> FAILED_CLOSED: prompt is not clarification-eligible
```

After:

```text
Add provider Claude Code.
-> ADD_PROVIDER
-> RESOURCE_SELECTION_SUCCEEDED
-> RESOURCE_PPP_INTEGRATED
-> PROVIDER_PROPOSAL_PRODUCED
-> DEVELOPMENT_PROPOSAL_CONTRACT_VALIDATED
-> IMPLEMENTATION_HANDOFF_CREATED
```

The same before/after behavior applies to:

- `Create a server management domain.`
- `Create a filesystem worker.`
- `Create a monitoring worker.`

## Authority Boundaries

The catalog expansion must not:

- execute;
- dispatch;
- authorize;
- invoke workers;
- invoke providers;
- mutate governance;
- silently resolve ambiguous resources.

Unknown resources still fail closed unless they are eligible for clarification.

## Fail-Closed Conditions

Routing remains fail-closed when:

- resource is unknown;
- resource mapping is ambiguous;
- catalog lineage is corrupted;
- replay is corrupted;
- classification conflicts are detected;
- turn allocation evidence is invalid.

## Final Classification

AIGOL_CONVERSATION_RESOURCE_CATALOG_EXPANSION_STATUS = CERTIFIED
