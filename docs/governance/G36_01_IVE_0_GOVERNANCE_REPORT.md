# G36-01 — IVE-0 Governance Report

Status: GOVERNANCE BOUNDARIES VERIFIED

Date: 2026-07-28

## Finding

The Intelligent Validation Engine V0 is constitutionally bounded to
deterministic analysis and recommendation.

It has no authority to:

- approve a recommendation;
- construct or approve a validation candidate;
- authorize execution;
- invoke Workers or Providers;
- change an allowlist;
- execute tests;
- mutate repository, Governance, Replay, or certification state.

## Ownership Continuity

IVE-0 consumes canonical normalized-change evidence. It reuses G27-05 and
G27-07 when their certified ingress domain is satisfied. It uses an additive
exact-path repository-component inventory for required surfaces outside that
domain without changing G27.

Candidate composition remains G27-09 owned. Human Approval and authorization
remain Governance owned. Execution remains owned by the existing governed
validation runtime and Validation Command Worker. Immutable evidence transport
continues to use existing Replay serialization without modifying Replay
semantics.

## Human Authority

Every successful or failed IVE recommendation records:

- `human_approval_required = true`;
- `human_approval_recorded = false`;
- `validation_executed = false`;
- all authority flags as false.

The downstream existing approval must bind the exact candidate hash. IVE-0
cannot convert a recommendation into execution authority.

## Fail-Closed Assessment

IVE-0 fails closed for:

- invalid or failed normalized input;
- reference or hash mismatch;
- ambiguous certification-registry mapping;
- unsupported repository path classification;
- G27 impact or planning failure when the G27 strategy is selected;
- replay collision;
- artifact, component, classification, recommendation, reasoning, or replay
  tampering.

A failed plan contains no affected-component claim, blocks downstream handoff,
and cannot claim reduced validation scope.

## Governance Verdict

`IVE_0_GOVERNANCE_BOUNDARIES_PRESERVED`
