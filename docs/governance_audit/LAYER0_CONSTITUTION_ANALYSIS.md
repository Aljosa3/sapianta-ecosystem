# Layer 0 Constitution Analysis

Status: architectural governance audit evidence.

## What Layer 0 Is

Layer 0 is the system constitution: the set of foundational architecture rules, deterministic guarantees, kernel constraints, and freeze boundaries that must not be silently changed by autonomous or ordinary development flows.

The clearest definition appears in `SAPIANTA_MUTATION_MAP_v1.0.md`, where L0 is classified as:

- `IMMUTABLE`
- allowed mutation: `NONE`
- examples: architectural constitution, deterministic guarantees, system integrity rules

Layer 0 is therefore not a feature layer. It is the trust boundary for how the rest of the system is allowed to evolve.

## Why Layer 0 Is Immutable

Layer 0 immutability is established through overlapping evidence:

- Policy evidence: `SAPIANTA_MUTATION_MAP_v1.0.md` classifies L0 as immutable.
- Freeze evidence: `governance/phases/LAYER_0_FREEZE.yaml` locks specific kernel and governance files.
- Enforcement script: `scripts/check_layer_freeze.py` rejects staged or unstaged changes to locked files unless an explicit freeze override is provided.
- Development guard: `runtime/development/architecture_guardian.py` blocks changes to protected governance, replay, kernel, and constitution paths.
- Mutation boundary: `runtime/development/mutation_guard.py` rejects protected runtime paths such as `runtime/governance`, `runtime/system`, `runtime/ledger`, `runtime/safety`, and `runtime/layer2`.
- Mutation classification: `runtime/development/mutation_validator.py` treats L0 and L1 as immutable classes.
- Promotion controls: promotion gates classify structural changes and require approval for non-cosmetic changes.

## Technical Enforcement Points

### Layer Freeze Check

`scripts/check_layer_freeze.py` enforces the Layer 0 freeze manifest. It verifies required manifest fields, confirms locked files exist, and compares staged and unstaged changes against the locked file list.

The locked manifest includes canonical HOI specs, kernel stability declarations, kernel boundary checks, and the freeze checker itself.

### ArchitectureGuardian

`runtime/development/architecture_guardian.py` validates generated or modified code before execution or persistence in development flows. It protects:

- `sapianta_system/kernel`
- `sapianta_system/replay`
- `sapianta_system/governance`
- `sapianta_system/constitution`
- `runtime/governance`
- `runtime/system`
- `runtime/ledger`
- `runtime/safety`
- `runtime/layer2`

It also blocks forbidden operations such as `eval`, `exec`, `os.system`, `subprocess`, and dynamic imports. Validation fails closed on exceptions.

### MutationGuard and MutationValidator

`MutationGuard` enforces patch-size and path boundaries. It allows development and research roots while rejecting protected runtime paths.

`MutationValidator` maps paths to L0-L4 classes and rejects immutable layers. It is evidence of the intended layer taxonomy, though its path matching does not cover every physical repository layout.

### Development Governance Gate

`DevGovernanceGate` blocks dangerous task descriptions, routes governance-sensitive work to review, and provides a fail-closed human approval placeholder.

### Promotion Gates

`runtime/governance/promotion_gate.py` and `tools/governance/promotion_gate_v02.py` classify changes as cosmetic, parametric, or structural. Structural and parametric changes require explicit approval.

## Runtime Evidence

Layer 0 is not executed as application logic. It is enforced at mutation and certification boundaries:

- generated code is checked before write/use;
- protected paths are rejected before mutation;
- promotion level determines approval requirements;
- CCS certification requires Guardian validation and strict generated tests;
- replay-critical artifacts are hash chained and replay checked.

The practical runtime pattern is: Layer 0 constrains what lower layers are allowed to mutate or activate.

## Important Reality Check

There is a mismatch between intended and installed hook enforcement.

`scripts/hooks/pre-commit` includes Promotion Gate v0.2 and Layer 0 freeze checking. The observed installed hook at `sapianta_system/.git/hooks/pre-commit` includes kernel integrity checks but does not include the promotion gate or Layer 0 freeze checker. This means Layer 0 is strongly documented and partially enforced in tooling, but local commit enforcement may be weaker than governance documents claim.

## Conclusion

Layer 0 is real as an architectural and mutation boundary. It is enforced by a combination of freeze manifests, guard code, mutation filters, development gates, promotion gates, and replay-critical evidence. It is not enforced by one universal root-level kernel. The strongest enforcement appears inside development and domain-specific governance flows, while repository-wide enforcement depends on hook installation and correct path coverage.

