# Conformance Evidence

Status: generated governance evidence for `GOVERNANCE_CONFORMANCE_SYSTEM_V1`.

## Result

Current conformance status: `PARTIALLY_CONFORMANT`

The system has no critical constitutional violations in the checked surfaces. It does have hook enforcement drift:

- root `.git/hooks/pre-commit` governance hook evidence is missing;
- `sapianta_system/.git/hooks/pre-commit` does not contain the expected `promotion_gate_v02` and `check_layer_freeze` enforcement tokens.

This matches the architectural audit finding that documented hook enforcement is stronger than installed hook enforcement.

## Deterministic Evidence

- Checks passed: `18`
- Checks failed: `2`
- Critical violations: `0`
- Warnings: `1`
- Report hash: `0790499ee53f9a82e15225e15eff1c2637b7e60523fa38be0c921281abe4cbea`

## Verification Surfaces

The conformance engine verifies:

- constitutional specifications under `docs/governance/`;
- governance audit evidence under `docs/governance_audit/`;
- Layer 0 freeze manifest and freeze checker;
- ArchitectureGuardian protected path and forbidden operation coverage;
- MutationGuard protected runtime path coverage;
- MutationValidator immutable layer classification;
- promotion gate presence;
- development governance gate presence;
- CCS certification dependencies;
- replay chain verifier and replay engine presence;
- expected versus installed governance hook coverage.

## Interpretation

`PARTIALLY_CONFORMANT` is the correct current result because the constitutional reference artifacts and runtime enforcement surfaces exist, but hook installation is not aligned with the documented governance hook expectations.

The evidence is read-only and does not modify runtime behavior.

