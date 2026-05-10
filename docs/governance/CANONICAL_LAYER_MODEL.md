# Canonical Layer Model

Status: canonical constitutional specification.

This document defines the canonical interpretation of SAPIANTA layers. It reconciles the historical layer vocabularies without removing their original meanings.

## Canonical Rule

The L0-L4 mutation model is the canonical governance layer model.

The four-layer safety architecture is preserved as a separate authority model. It must not be used to reinterpret L0-L4 mutation semantics.

## Mutation Layer Hierarchy

### L0 - System Constitution

Purpose:
- Define the fundamental architecture laws.
- Preserve deterministic guarantees.
- Protect kernel and constitutional freeze boundaries.
- Prevent silent mutation of system integrity rules.

Mutability:
- Immutable.

Enforcement:
- Layer freeze manifest.
- Layer freeze checker.
- ArchitectureGuardian protected paths.
- MutationValidator immutable classification.
- MutationGuard protected runtime paths.
- Promotion and certification gates where the change enters development flow.

Runtime role:
- L0 constrains mutation and activation. It is not ordinary runtime feature logic.

### L1 - Canonical Artifact Definitions

Purpose:
- Define canonical envelopes, contracts, schemas, ledgers, hashes, audit records, and replay identities.

Mutability:
- Immutable.

Enforcement:
- Mutation map.
- MutationValidator L1 classification.
- Replay hash verification.
- Domain invariant registries.

Runtime role:
- Provides stable identity and audit structure for replay and certification.

### L2 - Decision Spine

Purpose:
- Define deterministic decision flow from proposal to policy validation, advisory, decision envelope, ledger, and replay chain.

Mutability:
- Restricted.

Enforcement:
- MutationGuard protected paths.
- Replay chain verification.
- Decision envelope hashing.
- Policy and certification gates.

Runtime role:
- Active in deterministic envelope and replay sidecar flows.

### L3 - Governance System

Purpose:
- Evaluate, certify, promote, block, or route proposed changes.
- Maintain artifact registry and governance review surfaces.

Mutability:
- Governed.

Enforcement:
- DevGovernanceGate.
- PromotionGate.
- CCS certification.
- Artifact registry checks.
- Domain lock and constitutional review where domain-scoped.

Runtime role:
- Active in development mutation review and domain constitutional proposal review.

### L4 - Research System

Purpose:
- Support research, CAL, experiment generation, follow-up development tasks, and bounded exploration.

Mutability:
- Evolvable.

Enforcement:
- Allowed-root checks.
- MutationGuard.
- ArchitectureGuardian.
- DevGovernanceGate.
- PromotionGate.
- CCS certification.

Runtime role:
- Active only in bounded development and research scope. It cannot directly mutate governance or execute production actions.

## Safety Authority Model

The historical safety model remains authoritative for control relationships:

| Authority Layer | Canonical Interpretation |
| --- | --- |
| Human Authority | Final authority over constitutional change, system direction, and stop decisions. |
| Governance Layer | Evaluates research and execution admissibility through policy, risk, promotion, validation, and certification. |
| Autonomous Research Layer | May propose, experiment, and generate within bounded regions. |
| Execution Layer | May act only through deterministic, signed, ledgered, governed boundaries. |

Relationship to mutation layers:

- Human Authority governs changes to L0 and high-risk L1-L3 surfaces.
- Governance Layer corresponds mostly to L3 controls over L2 and L4.
- Autonomous Research corresponds mostly to L4.
- Execution Layer corresponds to runtime use of L2 and domain execution boundaries.

## Domain Constitutional Hierarchy

Domain-trading adds an explicit hierarchy:

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

Canonical interpretation:
- This is a domain-level constitutional ordering consistent with the system constitution.
- It does not replace the L0-L4 mutation model.
- It provides concrete read-only enforcement for domain proposal, digest, certification, and envelope workflows.

## Mutability Classes

Immutable:
- L0 and L1.
- Finalized replay evidence.
- Finalized governance evidence.
- Ledger history and finalized envelopes.

Restricted:
- L2 Decision Spine.
- Policy validation and runtime decision contracts.

Governed:
- L3 governance engines.
- Promotion and certification logic.
- Trusted-scope topology where classified as governed mutable.

Evolvable:
- L4 research and development generation.
- Domain features outside protected scopes.
- Presentation and productization surfaces.

Experimental:
- Isolated research or proposal zones with no authority over canonical layers.

Forbidden:
- Production bypasses, broker/API execution paths, hidden runtime mutation, replay-breaking edits, autonomous constitutional mutation.

