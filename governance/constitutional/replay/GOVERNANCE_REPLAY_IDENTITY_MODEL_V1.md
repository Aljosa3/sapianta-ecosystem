# GOVERNANCE_REPLAY_IDENTITY_MODEL_V1

Status: CANONICAL GOVERNANCE REPLAY IDENTITY MODEL

## Purpose

This artifact defines canonical replay identity semantics for governance
evidence.

It does not implement replay identity generation code.

## Replay Identity Principles

- replay identity is canonical;
- replay identity is deterministic;
- replay identity is unique within its governance lineage;
- replay identity is append-only;
- replay identity supports lineage continuity;
- replay identity never grants authority.

## Identity Generation Semantics

Future governance replay identities MUST be derived from deterministic
inputs, such as:

- governance evidence domain;
- proposal identity;
- lineage predecessor;
- evidence class;
- canonical evidence hash.

Random, wall-clock-only, hidden, or runtime-private identity generation
is prohibited for canonical governance evidence.

## Uniqueness Requirements

Replay identity reuse is prohibited.

Replay identity reassignment is prohibited.

Replay identity collision MUST fail closed.

If uniqueness cannot be established:

-> quarantine evidence
-> block promotion
-> no activation

## Lineage Continuity Guarantees

Replay identities MUST preserve:

- parent/child continuity;
- replay chain continuity;
- governance ancestry visibility;
- promotion and rollback traceability;
- append-only replay lineage.

## Prohibitions

The following are prohibited:

- replay identity reuse;
- hidden replay mutation;
- replay lineage rewriting;
- replay identity reassignment;
- silent replay identity repair;
- authority escalation through replay identity.

## Replay Identity Non-Authority Rule

Replay identity proves traceability. It does not authorize mutation,
promotion, execution, or governance activation.
