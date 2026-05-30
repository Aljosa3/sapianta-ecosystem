# Provider Proposal Runtime V1 ADR

Status: accepted architecture decision record.

## Decision

Implement `PROVIDER_PROPOSAL_RUNTIME_V1` as a deterministic advisory runtime that creates replay-visible provider proposal artifacts without invoking providers.

## Context

AiGOL already has a canonical Cognition Runtime and deterministic intent classification. The `PROVIDER_PROPOSAL` destination existed conceptually but lacked a runtime artifact.

## Accepted Approach

The runtime:

- validates or creates `PROVIDER_PROPOSAL` intent evidence
- emits `PROVIDER_PROPOSAL_V1`
- records provider proposal replay
- remains non-authoritative
- fails closed on invalid or corrupt intent

## Rejected Alternatives

Provider execution: rejected because proposal is advisory only.

Provider orchestration: rejected because V1 does not select, route, or invoke providers.

Authorization coupling: rejected because proposals cannot authorize execution.

Worker dispatch: rejected because provider proposals do not execute.

Multi-provider selection: rejected because V1 records a declared provider type only.

## Consequences

AiGOL can now represent provider usage as a replay-visible proposal without granting provider authority.

The invariant remains:

```text
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```
