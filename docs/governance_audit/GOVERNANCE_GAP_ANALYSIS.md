# Governance Gap Analysis

Status: architectural governance audit evidence.

This document identifies gaps and risks. It does not prescribe or implement fixes.

## High Severity

| Gap | Evidence | Risk |
| --- | --- | --- |
| Installed hook does not match governance hook script | `scripts/hooks/pre-commit` includes Promotion Gate v0.2 and Layer 0 freeze; observed `sapianta_system/.git/hooks/pre-commit` omits those checks. | Layer 0 and structural-change enforcement may be weaker locally than governance docs state. |
| Layer terminology collision | Mutation map uses L0-L4; safety architecture uses L1-L4 with different meanings. | Future agents may conflate mutation layers with authority layers. |
| Path classification mismatch | `MutationValidator` checks paths like `governance/constitution`, while repository evidence includes `governance/constitutional` and nested roots. | Some protected domains may not be classified as intended depending on working directory and path form. |
| No single root-level constitutional enforcement engine | Main system, governance memory, factory, and domain-trading each contain governance mechanisms. | Constitutional guarantees may be strong locally but not uniformly enforced across the whole workspace. |

## Medium Severity

| Gap | Evidence | Risk |
| --- | --- | --- |
| L2/L3 approval is not centralized in `MutationValidator` | Validator only rejects immutable L0/L1; restricted/governed layers are allowed there and rely on other gates. | Approval semantics can be bypassed if the wrong validation entry point is used. |
| Approval gate contains nondeterministic mutation | `approval_gate.py` uses current timestamps and mutates request dictionaries. | If treated as replay evidence, approval artifacts may not be replay-stable. |
| Execution guard is operational, not replay deterministic | `execution_guard.py` uses process listing and wall-clock time. | Appropriate for dev safety, but unsuitable as constitutional replay evidence. |
| Governance memory versus active dev enforcement is easy to misread | Governance memory says runtime governance activation is not implemented; system state says development governance is enforced. | Readers may confuse dormant governance memory with active mutation enforcement. |
| Workspace integrity layer is documented future work | `WORKSPACE_INTEGRITY_LAYER.md` defines risks and requirements but not full enforcement. | AI tooling may still mutate the wrong root or rely on unpersisted patches. |
| Rollback and lineage are documented more strongly than implemented | Runtime acceptance docs require lineage and rollback evidence; implementation is partial and distributed. | Recovery evidence may be incomplete for production-grade governance. |

## Low Severity

| Gap | Evidence | Risk |
| --- | --- | --- |
| Domain-trading constitutional stack is dense and partly parallel to main-system governance | Multiple manifests, evidence docs, digest/export/review layers. | Architecture comprehension cost increases; governance compression helps but does not unify enforcement. |
| Development syntax repair path has narrower validation | `dev_orchestrator.apply_fix` contains a forced syntax repair path that writes after compile checks. | Limited to generated/development files, but it is a different validation path from normal Guardian validation. |
| CAL has bounded adaptive scoring | `CALController` adjusts scores and generates follow-up tasks. | Safe as development-scope behavior, but should not be described as inactive if discussing development autonomy. |

## Conceptual Runtime Mismatches

- Documentation sometimes says governance is "enforced" while governance memory says runtime activation is not implemented. The audit interpretation is that development mutation governance is active, while runtime governance activation remains dormant.
- Domain-trading review engines are highly constitutional, but they govern proposal and evidence flows rather than live execution.
- Offline paper trading contains fake deterministic fills, while newer proposal/envelope layers explicitly avoid execution and simulation. These belong to different milestones and should remain distinguished.

## Mutation Boundary Ambiguities

- Relative path matching differs between tools.
- Domain roots and nested repositories have separate governance policies.
- Human approval artifacts are described but not uniformly required by all mutation validators.
- `SAPIANTA_FREEZE_OVERRIDE=1` can bypass Layer 0 freeze checks if the script is run, so override governance depends on surrounding process discipline.

## Drift Risks

- Future agents may treat documentation-only governance memory as active runtime control.
- Future productization may accidentally imply production execution capability.
- Constitutional vocabulary may continue expanding without consolidation.
- Domain-specific constitutional guarantees may be mistaken for workspace-wide enforcement.

