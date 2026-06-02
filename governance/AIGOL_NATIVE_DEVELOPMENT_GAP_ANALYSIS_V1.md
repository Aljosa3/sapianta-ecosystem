# AIGOL_NATIVE_DEVELOPMENT_GAP_ANALYSIS_V1

## Status

Review-only gap analysis.

## Gap Summary

The failed worker-foundation attempt exposed gaps between operator conversation readiness and native development readiness.

## Gap 1: Durable Conversation Session Continuity

Current gap:

- default session ids are reused;
- turn counters restart at `TURN-000001`;
- append-only router artifacts collide with existing replay.

Required capability:

- discover existing session turns;
- allocate the next unused turn id;
- preserve append-only replay;
- expose resumed session state to the operator.

## Gap 2: Native Development Task Intake

Current gap:

- development prompts are treated as conversation or provider-assisted intent classification;
- no canonical development task artifact exists;
- no deterministic target artifact list is produced.

Required capability:

- create a read-only task-intake artifact for development requests;
- identify milestone id, domain, worker, output files, and validation scope;
- fail closed when the target cannot be resolved.

## Gap 3: Development Context Assembly

Current gap:

- provider context capsule is intentionally minimal;
- Trading Domain artifacts, cognition coverage, policy constraints, fixture model, and current worker recommendations are not assembled into a canonical context bundle.

Required capability:

- deterministic development context assembly;
- explicit artifact references;
- replay-visible context hash;
- known-gap preservation.

## Gap 4: Domain And Worker Resolution

Current gap:

- no canonical registry maps prompts to Trading Domain milestones or worker foundation classes;
- worker family resolution is implicit.

Required capability:

- domain registry;
- worker foundation registry;
- milestone naming validation;
- explicit resolution failure when ambiguous.

## Gap 5: Provider Necessity Policy

Current gap:

- complex prompts often fall back to provider assistance without a stable policy artifact that says whether a provider is required, optional, or prohibited.

Required capability:

- classify provider necessity before invocation;
- allow deterministic self-resolution where sufficient;
- request provider proposals only as non-authoritative assistance.

## Gap 6: Development Proposal Contract

Current gap:

- provider output is free-form and may include multiple destinations or authority-bearing language;
- AiGOL rejects ambiguous suggestions, correctly but often.

Required capability:

- bounded development proposal schema;
- one target milestone per proposal;
- no authorization, dispatch, execution, replay mutation, or governance mutation claims;
- deterministic validation before any downstream use.

## Gap 7: Conversation-To-Implementation Handoff

Current gap:

- conversation can recommend next work but cannot reliably hand off into a governed development artifact creation path.

Required capability:

- explicit operator-facing handoff;
- no automatic implementation;
- preserved human authority;
- replay-visible task packet suitable for Codex-assisted or future native development flow.

## Development Workflow Impact

Workflow impact by class:

- governance review: mostly supported, with session collision risk;
- domain foundation review: mostly supported if read-only;
- trading worker foundation: partial, high ambiguity risk;
- marketing worker foundation: partial, high ambiguity risk;
- implementation/runtime creation: not ready as a native conversation capability;
- execution or dispatch: correctly unsupported.

