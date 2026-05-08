# SAPIANTA Unknown-Governance Escalation v1

## Document Role

This document defines the Product 1 unknown-governance escalation concept for the enterprise demo.

This is documentation and UX semantics only. It does not activate governance, alter certification semantics, change ArchitectureGuardian behavior, or modify runtime core execution behavior.

## Problem

AI systems may produce decisions that do not match existing validation coverage.

SAPIANTA must not silently approve decisions when governance coverage is incomplete. Unknown governance patterns should become explicit review events with evidence and human oversight.

## Governance Gap Detection

A governance gap is detected when an AI decision cannot be fully evaluated by the currently available validation controls, policies, runtime checks, or evidence requirements.

Demo status language:
- UNKNOWN GOVERNANCE PATTERN
- VALIDATION COVERAGE INCOMPLETE
- GOVERNANCE REVIEW REQUIRED
- DORMANT VALIDATION PROPOSED

## Unknown Decision Semantics

An unknown decision is not a certified decision.

Unknown decisions should be routed to governance review when:
- validation coverage is missing
- policy scope is unclear
- risk classification is incomplete
- required explanation evidence is missing
- runtime safety cannot be determined
- replay/audit requirements are not yet defined

Default posture:
- fail closed
- preserve evidence
- do not execute automatically
- require human review

## Approval Workflow

The approval workflow is:

```text
AI Decision
-> Validation coverage unknown
-> Governance gap detected
-> Governance extension proposal generated
-> Human approval required
-> Dormant validation rule created
-> Activation review
```

Proposal generation may assist the human reviewer, but it does not create active governance by itself.

## Dormant Validation Proposal

A dormant validation proposal is a candidate governance extension that has not been activated.

It may include:
- proposed validation control
- proposed policy rule
- required evidence fields
- replay/audit requirements
- risk classification
- explanation requirement
- activation criteria

Dormant means:
- not active
- not enforcing production behavior
- not certifying decisions
- waiting for human approval and activation review

## Activation Review Semantics

Activation review is the human-governed process that determines whether a dormant validation proposal may become an active validation rule in a future approved architecture.

Activation review should consider:
- deterministic behavior
- policy scope
- evidence quality
- audit lineage
- replay safety
- authority boundaries
- production/demo separation
- rollback and deactivation requirements

Activation review is not automated by the enterprise demo.

## Human Oversight Role

Human oversight exists to prevent unsafe governance drift.

The human reviewer:
- confirms whether the gap is real
- evaluates proposed governance coverage
- approves, rejects, or revises the proposal
- decides whether dormant validation should proceed to activation review
- preserves audit lineage of the decision

The demo should make this role visible without implying autonomous governance evolution.

## Demo Boundary

The unknown-governance escalation UI is a concept and productization layer.

It demonstrates how SAPIANTA should communicate incomplete coverage, review requirements, dormant proposals, and activation review. It does not change runtime core behavior or activate new validation semantics.
