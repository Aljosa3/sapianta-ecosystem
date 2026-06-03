# UNIFIED_RESOURCE_SELECTION_RUNTIME_V1

## Status

Runtime implementation certification.

## Final Classification

```text
UNIFIED_RESOURCE_SELECTION_RUNTIME_STATUS = CERTIFIED
```

## Purpose

This runtime implements deterministic, replay-visible Resource selection across:

- Providers;
- Workers;
- Hybrid Provider-Workers;
- Governance runtimes.

The runtime selects Resources only.

It does not invoke, dispatch, execute, authorize, or mutate governance.

## Runtime Component

Implemented:

```text
aigol/runtime/unified_resource_selection_runtime.py
```

## Defined Artifacts

Defined:

```text
RESOURCE_SELECTION_ARTIFACT_V1
RESOURCE_SELECTION_STATUS_V1
RESOURCE_SELECTION_DIAGNOSTICS_V1
```

## Default Resource Registry

The runtime includes a deterministic default registry with:

| Resource | Category | Supported Role |
| --- | --- | --- |
| `OPENAI` | `PROVIDER` | `PROVIDER_ROLE` |
| `ANTHROPIC` | `PROVIDER` | `PROVIDER_ROLE` |
| `CODEX` | `HYBRID_PROVIDER_WORKER` | `PROVIDER_ROLE`, `WORKER_ROLE` |
| `CLAUDE_CODE` | `HYBRID_PROVIDER_WORKER` | `PROVIDER_ROLE`, `WORKER_ROLE` |
| `REPLAY_INSPECTOR_WORKER` | `WORKER` | `WORKER_ROLE` |
| `UNIFIED_REPLAY_RECONSTRUCTION_RUNTIME` | `GOVERNANCE_RUNTIME` | `GOVERNANCE_RUNTIME_ROLE` |

## Selection Lifecycle

Lifecycle:

1. Validate replay path availability.
2. Load or construct deterministic Resource registry.
3. Validate registry consistency and authority profiles.
4. Validate requested role against provider necessity or worker authorization requirements.
5. Evaluate category compatibility.
6. Evaluate role compatibility.
7. Evaluate capability compatibility.
8. Evaluate trust compatibility.
9. Evaluate authority compatibility.
10. Select deterministic eligible Resource.
11. Persist `RESOURCE_SELECTION_ARTIFACT_V1`.
12. Persist returned selection status.

## Replay

Replay steps:

```text
000_resource_selection_recorded.json
001_resource_selection_returned.json
```

Replay preserves:

- selected Resource id;
- Resource category;
- active role;
- selected version;
- registry hash;
- selection rationale;
- capability matches;
- trust matches;
- authority matches;
- rejected Resource diagnostics;
- replay hash.

## Hybrid Resource Handling

Hybrid Resources require explicit active role selection.

Example:

```text
CODEX as PROVIDER_ROLE
CODEX as WORKER_ROLE
```

These are distinct selections with distinct authority profiles.

No implicit role switching is permitted.

## Fail-Closed Conditions

The runtime fails closed when:

- no eligible Resource exists;
- provider is prohibited;
- provider necessity conflicts with selected role;
- Worker authorization requirement is missing;
- Worker authorization conflicts with selected role;
- capability mismatch occurs;
- trust mismatch occurs;
- authority mismatch occurs;
- registry is inconsistent;
- duplicate Resource registration exists;
- Resource resolution is ambiguous;
- replay artifact already exists;
- replay hash mismatch is detected.

## Authority Boundaries

The runtime does not:

- invoke providers;
- invoke Workers;
- dispatch;
- execute;
- authorize;
- create Resources;
- create Workers;
- mutate governance;
- mutate replay outside append-only selection evidence.

## Ecosystem Readiness Impact

Unified ecosystem readiness increases to:

```text
RESOURCE_SELECTION_READY = 100%
RUNTIME_INVOCATION_READY = NOT_STARTED
```

AiGOL can now deterministically choose the correct Resource role before provider or worker runtime interaction.

## Recommended Next Milestone

```text
UNIFIED_RESOURCE_SELECTION_PPP_INTEGRATION_V1
```

This should allow PPP routing to select a proposal-producing Resource before provider proposal production, while preserving provider-only and hybrid-role boundaries.

