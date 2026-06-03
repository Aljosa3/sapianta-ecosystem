# AIGOL_PROVIDER_WORKER_BOUNDARY_ANALYSIS_V1

## Status

Provider versus Worker boundary analysis.

## Purpose

This artifact classifies initial ecosystem resources and identifies whether AiGOL should evolve toward provider-only selection or unified resource selection.

## Boundary Definitions

Provider role:

```text
Prompt or context packet -> proposal evidence
```

Worker role:

```text
Authorized task packet -> bounded domain work evidence
```

Hybrid Provider-Worker role:

```text
Resource has both possible roles, but each role is selected, governed, authorized, and replayed separately.
```

Hybrid classification does not merge authority paths.

## OpenAI

Classification:

```text
PROVIDER
```

Rationale:

- OpenAI produces proposal or explanatory response evidence.
- OpenAI does not execute AiGOL task packets.
- OpenAI does not receive governed worker authorization.
- OpenAI must remain proposal-only.

PPP implication:

- eligible for provider proposal production when approved and available.

Registry implication:

- provider registry entry only.

Replay implication:

- provider request, response, proposal, validation, and chain references.

## Anthropic

Classification:

```text
PROVIDER
```

Rationale:

- Anthropic/Claude model output is proposal evidence.
- Existing Claude compatibility analysis supports provider substitutability.
- No Worker execution boundary is certified by this foundation.

PPP implication:

- eligible future provider for proposal production when adapter and approval exist.

Registry implication:

- provider registry entry only.

Replay implication:

- same provider evidence model as OpenAI, with Anthropic identity and adapter version.

## Codex

Classification:

```text
HYBRID_PROVIDER_WORKER
```

Rationale:

- Codex can assist with proposal or implementation plan shaping.
- Codex can also perform bounded implementation work in the shared repository when explicitly invoked by a human outside AiGOL or by future governed Worker paths.
- Treating Codex as provider-only would hide its Worker-like implementation role.
- Treating Codex as Worker-only would hide its proposal-generation role.

Required separation:

- provider role: proposal-only, no mutation authority;
- Worker role: bounded implementation work only after governed authorization, with replay-visible task packet and result evidence;
- no role may self-authorize or cross into the other path implicitly.

PPP implication:

- Codex may propose via provider path.
- Codex Worker creation, upgrade, or invocation must pass through Worker governance.

Registry implication:

- provider registry entry and Worker registry entry may both reference a shared resource identity.
- role-specific registry hashes and authority profiles are required.

Replay implication:

- replay must record which role was active for each interaction.

## Claude Code

Classification:

```text
HYBRID_PROVIDER_WORKER
```

Rationale:

- Claude Code can potentially propose implementation plans.
- Claude Code can also potentially perform bounded code-oriented work.
- Its interactive coding-tool nature makes provider-only classification too narrow.

Required separation:

- provider role is proposal-only;
- Worker role is authorized task-packet work only;
- no automatic continuation, dispatch, governance mutation, or replay mutation may be inferred.

PPP implication:

- may participate in provider proposal production if approved;
- may participate as a Worker-capable implementation resource only after separate Worker foundation, certification, and authorization.

Registry implication:

- hybrid resource identity with separate provider and Worker role entries.

Replay implication:

- every use must record role, provider or Worker boundary, request hash, response or result hash, and chain id.

## Comparative Classification

| Resource | Classification | Provider Role | Worker Role | Notes |
| --- | --- | --- | --- | --- |
| `OPENAI` | `PROVIDER` | Yes | No | Proposal-only LLM source |
| `ANTHROPIC` | `PROVIDER` | Yes | No | Proposal-only LLM source |
| `CODEX` | `HYBRID_PROVIDER_WORKER` | Yes | Future governed Worker-capable | Must separate proposal and implementation roles |
| `CLAUDE_CODE` | `HYBRID_PROVIDER_WORKER` | Yes | Future governed Worker-capable | Must separate proposal and implementation roles |

## Implications For PPP

PPP must know whether it is asking for:

- proposal evidence;
- Worker lifecycle proposal;
- implementation handoff;
- authorized Worker execution.

PPP may create proposal and handoff artifacts.

PPP may not invoke Worker-capable resources as Workers.

## Implications For Selection Models

Provider Selection Runtime alone is too narrow.

Worker Selection Runtime alone is also too narrow.

AiGOL should evolve toward:

```text
UNIFIED_RESOURCE_SELECTION_FOUNDATION_V1
```

The unified resource model should reason about:

- Providers;
- Workers;
- Hybrid Provider-Workers;
- role-specific capabilities;
- role-specific authority profiles;
- role-specific replay requirements.

## Governance Implication

Hybrid resources require stronger boundaries, not weaker ones.

The presence of both roles must increase validation burden and replay clarity.

It must never create shortcut authority.

