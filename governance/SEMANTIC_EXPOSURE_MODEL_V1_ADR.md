# SEMANTIC_EXPOSURE_MODEL_V1_ADR

## Context

AiGOL/SAPIANTA must govern semantic visibility, payload exposure, cognition routing, and replay payload retention without requiring centralized ownership of sensitive payloads.

The governed identity and authority model defines identity, authority scopes, replay visibility, approval hierarchy, and capability entitlement. Semantic exposure governance depends on that substrate so payload visibility and cognition routing can be evaluated without confusing visibility with execution authority.

## Decision

Define `SEMANTIC_EXPOSURE_MODEL_V1` as a documentation-only constitutional governance milestone.

The model establishes:

- canonical payload classifications;
- exposure levels from no payload to full content;
- semantic routing categories;
- semantic abstraction contract;
- redaction governance;
- replay payload governance;
- exposure approval authority;
- organization policy overlays;
- fail-closed semantic exposure control.

This milestone does not implement redaction, payload processing, local inference, LLM integration, API endpoints, authentication, replay implementation changes, provider behavior changes, or capability execution changes.

## Consequences

Future capability governance, local node architecture, and sovereign replay milestones must evaluate payload classification, exposure eligibility, routing category, identity authority, replay visibility, and organization overlays before exposing payloads.

Cloud cognition must be explicitly allowed by classification, exposure level, organization policy, authority profile, replay scope, and approval evidence.

Replay can preserve governance evidence through metadata, hashes, classifications, routing decisions, and approval evidence without storing unrestricted raw payloads.

Unresolved classification, authority, organization scope, exposure eligibility, or replay visibility must fail closed.

## Non-Goals

- Implement redaction logic.
- Implement payload processing.
- Implement local inference.
- Implement LLM integration.
- Implement authentication.
- Add API endpoints.
- Modify runtime execution code.
- Change replay implementation.
- Change provider behavior.
- Change capability execution behavior.

## Rejected Alternatives

- Full cloud payload by default: rejected because payload sovereignty and regulated confidentiality require explicit exposure eligibility.
- Unrestricted LLM visibility: rejected because LLMs are non-authoritative and cannot receive payloads without governed exposure control.
- Replay containing unrestricted raw payload: rejected because replay must support governance evidence without centralized sensitive payload ownership.
- Frontend-only privacy controls: rejected because semantic exposure must be governed at runtime authority, routing, replay, and approval layers.
- Trust-based implicit exposure: rejected because organization membership or user trust does not resolve payload classification, replay visibility, or exposure eligibility.
- No payload classification layer: rejected because routing, approval, replay, retention, and export decisions require explicit classification.
- Exposure without authority resolution: rejected because identity and authority resolution are upstream constitutional dependencies.
- Cloud-only cognition architecture: rejected because sovereign local cognition and local-only classifications are required for confidential and regulated domains.
