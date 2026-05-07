# SAPIANTA Foundation Anti-Drift Rules v1

## Document Role

This document defines architectural anti-drift rules for the finalized governed ecosystem foundation.

It is documentation-only. It does not implement drift detection tooling, runtime enforcement, governance activation, or automation.

## Prohibited Drift

Topology drift is prohibited.

Authority drift is prohibited.

Replay drift is prohibited.

Lineage drift is prohibited.

Activation drift is prohibited.

Governance reinterpretation drift is prohibited.

## Drift Definitions

Topology drift:
Changing the meaning of meta root, runtime root, domain roots, factory root, or governance memory without explicit governance review.

Authority drift:
Introducing implicit mutation, import, launcher, factory, domain, or runtime authority outside the canonical authority model.

Replay drift:
Weakening deterministic replay identity, replay propagation, replay validation, or replay-safe promotion semantics.

Lineage drift:
Weakening artifact identity, promotion continuity, audit continuity, governed inheritance, or lineage integrity hardening.

Activation drift:
Treating dormant documentation, ACTIVE focus, milestones, ADRs, domains, factory output, or architecture memory as runtime activation.

Governance reinterpretation drift:
Recasting governance memory as runtime governance execution or enforcement without explicit ADR approval.

## Governance Responsibility

Drift detection is a governance responsibility.

Semantic conflicts require explicit governance review.

Conflicts must not be resolved by silent reinterpretation, hidden assumptions, or conversational memory alone.

## Resolution Rule

When a future document conflicts with the finalized foundation:
- the conflict must be named
- affected foundation semantics must be identified
- an ADR is required if semantic architecture changes
- milestone lineage must record the decision
- activation remains blocked until explicitly approved

## Future Status

Anti-drift tooling is:
- NOT IMPLEMENTED
- NOT ACTIVE
- NOT AUTHORIZED
