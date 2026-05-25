# MOC_V1_SPEC

Status: foundation specification.

MOC V1 means Minimal Operational Cognition.

## Core Principle

Cognition does not equal authority.

MOC V1 defines a bounded operational cognition protocol for AiGOL / SAPIANTA. It may organize, normalize, classify, and propose within governance-visible boundaries, but it cannot issue authority, execute tasks, dispatch workers, mutate governance, or create hidden continuation.

## Purpose

MOC V1 provides the first protocol definition for bounded operational cognition after the cognition observability epoch. It converts explicit human intent and governance evidence into advisory semantic contracts and bounded proposals that remain subject to human approval and governed execution boundaries.

## Allowed Cognition Operations

MOC V1 may:

- normalize intent
- retrieve governance anchors
- build semantic contracts
- propose next steps
- classify scope and risk
- prepare bounded worker task proposals
- interpret governed returns
- propose governance artifacts

These operations are advisory, deterministic where specified, replay-visible, and non-authoritative.

## Forbidden Cognition Operations

MOC V1 must not:

- execute tasks
- self-dispatch
- mutate governance
- bypass approval
- create hidden continuations
- spawn recursive orchestration
- issue authority
- activate providers
- schedule workers
- infer hidden context
- repair semantic artifacts

## Protocol Boundary

MOC V1 operates between human intent and governed execution authorization. It can prepare a semantic contract and advisory proposal, but the proposal remains inert until explicit human approval and downstream governed authorization occur through existing governance paths.

## Required Sequence

No hidden branches are allowed.

`Human Intent -> Intent Normalization -> Governance Retrieval -> Semantic Contract -> Advisory Proposal -> Human Approval -> Worker Task -> Governed Return -> Return Interpretation`

## Semantic Contract Role

The semantic contract is an advisory governance artifact. It records intent, scope, risk, mutation classification, governance anchors, allowed actions, forbidden actions, required approvals, expected outputs, and deterministic constraints.

The contract must explicitly preserve:

- `advisory_only: true`
- `replay_safe: true`

## Authority Model

MOC V1 does not grant:

- execution authority
- dispatch authority
- orchestration authority
- mutation authority
- provider authority
- governance authority

Human approval and governed execution authorization remain separate. Approval does not imply execution. Dispatch does not imply successful execution. Return interpretation does not imply semantic truth certification.

## Relationship To Existing Substrate

MOC V1 builds on the frozen cognition observability substrate:

- cognition state envelope
- semantic replay continuity check
- cognition registry
- topology report
- lifecycle model
- integrity summary
- authority propagation verifier
- semantic context state
- semantic relationship index
- semantic boundary propagation
- semantic context diff
- semantic context audit bundle

This specification introduces no runtime behavior.
