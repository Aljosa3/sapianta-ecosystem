# Governance Layer Map

Status: architectural governance audit evidence.

This map reconstructs the governance layers as they appear in source, manifests, and documentation. SAPIANTA currently has more than one layer vocabulary. The primary mutation-governance model is the L0-L4 model from `SAPIANTA_MUTATION_MAP_v1.0.md`. A separate four-layer safety architecture defines authority flow between execution, research, governance, and human authority. These two maps should not be collapsed into one numbering scheme.

## Primary Mutation Governance Layers

| Layer | Name | Purpose | Mutability | Enforcement Evidence | Runtime Usage |
| --- | --- | --- | --- | --- | --- |
| L0 | System Constitution | Fundamental architecture principles, deterministic guarantees, system integrity rules, kernel freeze boundaries. | Immutable | `governance/phases/LAYER_0_FREEZE.yaml`, `scripts/check_layer_freeze.py`, `runtime/development/architecture_guardian.py`, mutation policy docs. | Used as a protected boundary for mutation review and freeze validation. It is not ordinary runtime business logic. |
| L1 | Canonical Artifact Definitions | Stable schemas and contracts such as decision envelope, ledger, artifact, and contract definitions. | Immutable | `SAPIANTA_MUTATION_MAP_v1.0.md`, mutation validator L1 rules, domain invariant registries. | Provides stable identity and replay surfaces for runtime and certification artifacts. |
| L2 | Decision Spine | Deterministic decision path: proposal, policy validation, advisory, decision envelope, ledger, replay chain. | Restricted | `runtime/governance/decision_envelope.py`, `execution_boundary.py`, `chain_verifier.py`, `replay_engine.py`, MutationGuard protected paths. | Active in deterministic envelope creation, hash chaining, replay verification, and ledger-style audit surfaces. |
| L3 | Governance System | Promotion gates, validation pipelines, certification, artifact registry, governance review, approval boundaries. | Governed | `dev_governance_gate.py`, `promotion_gate.py`, `ccs/certification_engine.py`, artifact registry integration, domain promotion gates. | Used by the development loop, generated artifact certification, promotion classification, and constitutional review engines. |
| L4 | Research System | Experimentation, CAL, IdeaEngine-style development tasks, research memory, strategy or capability exploration. | Evolvable | `cal_controller.py`, `dev_autonomous_loop.py`, MutationGuard allowed roots. | Active only inside bounded development/research scope. It can propose and generate, but cannot directly mutate protected governance surfaces. |

Runtime modules and domain packages are treated as evolvable unless they cross a protected path, trusted scope, invariant, or domain lock boundary.

## Separate Safety Authority Stack

`SAPIANTA_4_LAYER_SAFETY_ARCHITECTURE_v1.0.md` defines a different four-layer model:

| Safety Layer | Meaning | Authority Rule |
| --- | --- | --- |
| L4 Human Authority | Final authority over constitution, governance direction, and stop decisions. | AI cannot override. |
| L3 Governance Layer | GAD-style validation, policy, risk, and promotion decisions. | Governs research and execution admissibility. |
| L2 Autonomous Research Layer | Research, experiments, strategy generation, analysis. | Cannot change governance rules or execute directly. |
| L1 Execution Layer | Real-world action boundary. | Must receive deterministic, signed, ledgered decision envelopes. |

This safety stack describes authority flow, while the mutation map describes mutability and protected architecture surfaces.

## Domain Trading Constitutional Stack

The domain trading package adds a constitutional hierarchy:

1. Replay Safety
2. Governance Invariants
3. Trust Boundaries
4. Domain Lock Policy
5. Trusted Scopes
6. Semantic Freeze
7. Architecture Promotion Gates
8. Governed Mutation Rules
9. Experimental Evolution
10. Temporary Expansion Layers

This stack is implemented in `sapianta-domain-trading/src/sapianta_domain_trading/architecture_evolution_constitution.py` and related modules. It is read-only, deterministic, and fail-closed. It is evidence of mature domain constitutional governance, but it is not the only enforcement mechanism in the broader workspace.

## Interaction Rules

- L0 and L1 are treated as immutable governance foundations.
- L2 is restricted and may only evolve through explicit governance review.
- L3 is governed: proposals may be evaluated, certified, or rejected, but not silently applied.
- L4 is evolvable only inside allowed development and research scopes.
- Experimental zones cannot override replay safety, invariants, trust boundaries, or semantic freeze.
- Documentation under `runtime/governance/master` is explicitly dormant and observational; it must not be interpreted as runtime governance activation.

## Mutability Classification

Immutable:
- Layer 0 constitutional files and freeze-manifest locked files.
- Layer 1 canonical artifact definitions.
- Replay-critical evidence, finalized envelopes, immutable ledger history, and canonical invariant evidence.
- Domain-trading canonical trusted scopes unless a domain-specific governed update path allows evidence-backed mutation.

Governed or restricted:
- Decision Spine, policy validation, promotion gates, certification flow, governance review layers.
- Trusted scope topology and survivability parameters where explicitly classified as governed mutable.

Evolvable:
- Research, experiments, generated development modules, domain feature modules, and product-facing presentation layers, provided they do not cross protected paths or canonical scopes.

