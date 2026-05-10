# Governance Enforcement Hierarchy

Status: canonical constitutional specification.

This document defines the canonical enforcement ordering observed in the audit. It describes how enforcement actually works across distributed components.

## Enforcement Precedence

When multiple mechanisms apply, the highest applicable authority should be interpreted first:

1. Replay safety and replay immutability.
2. Layer 0 freeze and constitutional constraints.
3. Layer 1 canonical artifact stability.
4. Protected path and trust-boundary guards.
5. Mutation classification and mutation authorization.
6. Promotion classification.
7. Development governance review.
8. Certification and strict validation.
9. Research and CAL feedback.
10. Product or presentation evolution.

This is an interpretive hierarchy over existing mechanisms. It does not create a new runtime engine.

## Enforcement Components

### Freeze Manifests

Primary role:
- Protect Layer 0 locked files.
- Provide explicit freeze evidence.

Observed implementation:
- `governance/phases/LAYER_0_FREEZE.yaml`
- `scripts/check_layer_freeze.py`

Authority:
- Highest file-level constitutional freeze authority when executed.

Known limitation:
- Installed git hook evidence does not currently show the full freeze check included.

### ArchitectureGuardian

Primary role:
- Reject protected paths and dangerous code patterns in development flows.

Authority:
- Development-time protection for governance, replay, kernel, constitution, ledger, safety, and Layer 2 surfaces.

Failure mode:
- Invalid result or block reason; fails closed on exceptions.

### MutationGuard

Primary role:
- Enforce patch-size and allowed-root restrictions.

Authority:
- Development mutation boundary.

Failure mode:
- Raises or rejects mutation before write.

### MutationValidator

Primary role:
- Classify target paths into mutation layers.
- Reject immutable L0/L1 changes.

Authority:
- Layer taxonomy evidence and mutation permission check.

Known limitation:
- Path coverage does not fully match every observed repository layout.
- L2/L3 approval semantics are not centralized here.

### Promotion Gates

Primary role:
- Classify changes as cosmetic, parametric, or structural.
- Require approval for non-cosmetic changes.

Authority:
- Structural evolution control.

Observed implementations:
- `runtime/governance/promotion_gate.py`
- `tools/governance/promotion_gate_v02.py`
- `tools/governance/promotion_gate_validator.py`

Known limitation:
- Stronger hook script and actual installed hook differ.

### Development Governance Gate

Primary role:
- Evaluate development tasks before implementation.
- Block dangerous tasks.
- Route sensitive tasks to review.

Authority:
- Task-level governance control.

Failure mode:
- BLOCK or REVIEW for unsafe or sensitive work.

### CCS Certification

Primary role:
- Certify generated artifacts after Guardian validation and strict tests.

Authority:
- Generated artifact admissibility.

Failure mode:
- REJECTED certification; repair or CAL feedback may be triggered inside development scope.

### Replay Verification

Primary role:
- Validate deterministic envelope chains and replay equivalence.

Authority:
- Runtime evidence integrity and replay safety.

Failure mode:
- Replay mismatch or chain verification failure.

### Domain Constitutional Engines

Primary role:
- Evaluate domain-scoped invariants, domain locks, promotion gates, constitutional conflicts, governance compression, certification exports, capability review, proposal certification, and execution envelopes.

Authority:
- Domain-scoped read-only constitutional evidence.

Failure mode:
- REJECTED, ESCALATED, INVALID, or fail-closed classification.

## Certification Dependencies

A generated or proposed artifact is constitutionally stronger when it has:

- valid mutation scope;
- Guardian validation;
- promotion classification;
- artifact registry identity;
- strict test evidence;
- replay hash evidence;
- certification result;
- governance lineage record;
- human approval where required.

Missing evidence reduces authority or causes fail-closed rejection depending on the layer.

## Documentation-Only Boundaries

Some governance artifacts are first-class evidence but not runtime enforcement:

- `runtime/governance/master` governance memory;
- workspace integrity requirements;
- runtime acceptance gate requirements;
- maturity maps and roadmaps;
- some finalize and freeze reports.

These documents constrain interpretation and future evolution, but they do not themselves activate runtime behavior.

