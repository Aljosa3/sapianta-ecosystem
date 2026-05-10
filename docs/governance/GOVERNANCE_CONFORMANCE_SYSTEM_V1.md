# Governance Conformance System V1

Status: canonical milestone specification.

This milestone introduces constitutional conformance verification for SAPIANTA. It does not refactor runtime behavior, redesign governance, mutate architecture, or repair detected drift.

## Purpose

The Governance Conformance System verifies whether runtime enforcement, governance documents, mutation controls, replay guarantees, and constitutional specifications remain aligned.

It answers:

- Does runtime conform to the constitution?
- Are immutable layers protected?
- Are governance hooks installed consistently?
- Are mutation boundaries enforced?
- Are replay guarantees present?
- Is certification evidence still connected to enforcement?
- Has governance drift occurred?

## Architecture

The system consists of:

- `runtime/governance/conformance_models.py`
- `runtime/governance/conformance_rules.py`
- `runtime/governance/governance_conformance_engine.py`
- `tests/test_governance_conformance.py`
- `.github/governance/evidence/GOVERNANCE_CONFORMANCE_REPORT.json`
- `.github/governance/evidence/CONFORMANCE_EVIDENCE.md`

The engine is read-only. It performs deterministic file-existence, content-token, hook, lineage, replay, certification, and mutation-boundary checks.

## Verification Model

The engine verifies:

- constitutional reference artifacts under `docs/governance/`;
- Layer 0 freeze manifest and checker;
- ArchitectureGuardian protected path coverage;
- MutationGuard protected runtime path coverage;
- MutationValidator immutable L0/L1 classification;
- PromotionGate approval semantics;
- DevGovernanceGate fail-closed review surface;
- CCS certification dependency on Guardian and strict tests;
- replay hash-chain and replay engine presence;
- governance audit lineage evidence;
- expected versus installed pre-commit governance hook coverage.

## Conformance Semantics

The deterministic classifications are:

- `CONFORMANT`: all checks pass.
- `PARTIALLY_CONFORMANT`: non-critical drift or partial enforcement exists.
- `NON_CONFORMANT`: reserved for future broad non-critical systemic failure modes.
- `CRITICAL_VIOLATION`: a critical constitutional or foundational check fails.

Current scoring is intentionally conservative:

- any critical violation produces `CRITICAL_VIOLATION`;
- any high-severity violation produces `PARTIALLY_CONFORMANT`;
- zero violations produces `CONFORMANT`.

## Fail-Closed Principles

The engine fails closed when:

- constitutional docs are missing;
- Layer 0 freeze evidence is missing;
- protected path enforcement is missing;
- replay verification surfaces are missing;
- certification gates are missing;
- required hook governance checks are absent.

Fail-closed means the report records a violation and lowers conformance status. The engine does not repair the violation.

## Limitations

This system verifies evidence and enforcement surfaces. It does not prove semantic equivalence of every runtime path.

Known limitations:

- hook checks compare expected token coverage, not shell execution behavior;
- content checks are deterministic evidence checks, not full formal verification;
- repository-wide enforcement remains distributed;
- documentation-only governance remains evidence, not runtime activation;
- domain-specific constitutional enforcement remains scoped to its domain.

## Constitutional Position

This system is meta-governance verification. It verifies whether governance still obeys the constitutional architecture. It is not runtime governance itself and not autonomous mutation governance.

