# SAPIANTA Enterprise Demo Architecture v1

## Document Role

This document defines the Product 1 enterprise demo architecture for SAPIANTA - AI Decision Validator.

This is local PC productization documentation. It does not redesign deterministic semantics, governance architecture, replay lineage, authority separation, dormant activation semantics, audit continuity semantics, certification semantics, ArchitectureGuardian behavior, or runtime core execution behavior.

## Product Positioning

SAPIANTA is not:
- chatbot tooling
- generic AI dashboard
- simple compliance checklist

SAPIANTA is:
- deterministic AI execution governance infrastructure
- AI Decision Validator
- operational governance layer
- execution validation boundary
- replay/audit governance system

Primary narrative:

```text
AI
-> SAPIANTA VALIDATION
-> EXECUTION GOVERNANCE
-> AUDIT / REPLAY / COMPLIANCE
```

## Enterprise Messaging Hierarchy

Primary message:
- AI Decision Validator

Supporting messages:
- Built for deterministic AI execution governance
- Built for EU AI Act operational compliance
- AI output cannot directly enter production safely
- SAPIANTA validates AI decisions before execution

Trust signals:
- M1 correctness/security validation
- M2 policy validation
- M3 execution/runtime validation
- deterministic replay/audit
- explainability evidence
- cryptographic audit evidence
- SHA256 and signature
- unknown-governance escalation
- human approval workflow
- dormant validation activation concept

## Screen 1: Hero / Problem Statement

Purpose:

Explain why enterprises need AI execution governance.

Required communication:
- AI systems increasingly make operational decisions
- EU AI Act introduces governance obligations
- AI output cannot directly enter production safely
- SAPIANTA validates AI decisions before execution

Visual strategy:
- dark enterprise UI
- infrastructure-grade aesthetic
- institutional governance restraint
- graphite surfaces and dark navy background
- restrained green for verified states
- disciplined whitespace and thin control boundaries
- authoritative rather than consumer AI styling

## Homepage Section Hierarchy

The homepage follows this structure:
1. Hero
2. Why Governance Matters
3. Governance Architecture
4. Runtime Validation Flow
5. Audit & Traceability
6. EU AI Act Alignment
7. Enterprise Deployment
8. Request Demo

This hierarchy keeps governance, validation, control, traceability, deterministic execution, and auditability at the center of the experience.

## Screen 2: Validation Boundary

Purpose:

Show that AI output is separated from execution by a governance boundary.

Required flow:

```text
AI OUTPUT
-> SAPIANTA GOVERNANCE BOUNDARY
-> VALIDATION PIPELINE
```

Required communication:
- AI does not directly execute
- SAPIANTA acts as governance control plane
- validation outcomes are certified, rejected, or routed to governance review

## Screen 3: M1 / M2 / M3 Pipeline

Purpose:

Make deterministic validation stages visible and understandable.

M1 - Correctness / security:
- unsafe logic blocked
- unsafe execution blocked
- deterministic validation
- ArchitectureGuardian checks presented as evidence

M2 - Policy validation:
- policy enforcement
- capital ratio checks
- explanation requirements
- risk disclosure checks

M3 - Execution safety:
- runtime validation
- execution control
- fail-closed behavior
- pytest/runtime evidence where applicable

Supported statuses:
- PASS
- FAIL
- BLOCKED
- CERTIFIED

## Screen 4: Replay + Audit

Purpose:

Present replay governance as the AI Flight Recorder.

Required evidence flow:
1. AI Output Received
2. M1 Validation
3. M2 Validation
4. M3 Validation
5. Replay Created
6. Audit Signed
7. Decision Finalized

Replay UX strategy:
- represent validation lineage as a timeline
- make deterministic replay visible as evidence, not decoration
- surface SHA256 and signature as audit integrity markers
- keep replay semantics separate from live experimentation

## Screen 5: Decision Result

Purpose:

Show authoritative deterministic outcomes.

Required result states:
- CERTIFIED
- REJECTED
- GOVERNANCE REVIEW REQUIRED

Result language should feel operational and enterprise-grade. Avoid confidence-score framing and promotional startup styling.

## Screen 6: Explainability + Evidence

Purpose:

Make decisions auditable and explainable.

Required evidence:
- failing control
- evidence
- pytest trace
- policy evidence
- deterministic reason
- governance explanation

Explainability strategy:
- show the control that passed or failed
- show the stage where the decision was made
- show concrete machine-verifiable material
- show human-readable governance rationale

## Screen 7: Unknown-Governance Escalation

Purpose:

Show that incomplete governance coverage is detected and escalated instead of silently approved.

Required flow:

```text
AI Decision
-> Validation coverage unknown
-> Governance gap detected
-> Generate governance extension proposal
-> Human approval required
-> Dormant validation rule
-> Activation review
```

Required statuses:
- UNKNOWN GOVERNANCE PATTERN
- VALIDATION COVERAGE INCOMPLETE
- GOVERNANCE REVIEW REQUIRED
- DORMANT VALIDATION PROPOSED

Semantics:
- generated proposals are not active governance
- human approval is required
- dormant validation rules remain inactive until activation review
- unknown decisions must not become certified decisions by default

## Screen 8: EU AI Act Governance

Purpose:

Frame SAPIANTA as AI execution governance infrastructure.

Required concepts:
- EU AI Act risk-based governance
- traceability
- human oversight
- auditability
- deterministic validation
- operational governance
- replayability

Positioning rule:

Do not present SAPIANTA as generic AI compliance software. Present it as AI execution governance infrastructure that operationalizes validation, evidence, audit, replay, and human oversight around AI decisions.

## Demo vs Production Separation

Demo runtime:
- controlled showcase node
- productized UX and narrative layer
- stable enterprise walkthrough environment
- not a live experimentation node
- not production enforcement

Production runtime:
- future strict deterministic runtime
- requires separate human-approved activation review
- requires production readiness, operational controls, and strict deterministic guarantees

The enterprise demo does not activate production governance, certification semantics, or runtime enforcement beyond the existing product behavior.

## Enterprise Trust-Signaling Principles

The demo should:
- use restrained infrastructure-grade visuals
- make governance boundaries visually explicit
- use deterministic state labels instead of vague scoring language
- connect every result to evidence
- make audit and replay feel operationally useful
- show that unknown decisions trigger human oversight
- preserve foundation semantics and avoid implying hidden authority changes
