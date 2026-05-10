# Governance Runtime Flow

Status: architectural governance audit evidence.

This document maps how governance layers are used in practice. It separates active runtime checks from dormant documentation-only governance memory.

## Development Mutation Flow

The active governed development path is:

1. A task is introduced through the development loop or CAL.
2. `DevGovernanceGate` evaluates the task.
3. Dangerous tasks are blocked; sensitive tasks require review.
4. `promotion_gate.classify_change()` classifies affected paths or diffs.
5. Non-cosmetic changes require approval.
6. `DevelopmentOrchestrator` builds or receives implementation artifacts.
7. `MutationGuard` rejects forbidden paths and oversized patches.
8. `ArchitectureGuardian` validates generated code and existing targets.
9. Generated artifacts are registered in the artifact registry.
10. CCS certification validates Guardian status and strict generated tests.
11. Failures feed CAL or repair logic inside development scope.

This is the main place where bounded autonomy is actually constrained.

## CAL and Decision Spine Relationship

`CALController` is active inside the development loop. It can generate deterministic development tasks, adjust bounded scores, and write development test artifacts. It does not have authority to mutate Layer 0, governance memory, or production execution. Its authority is bounded by:

- `DevGovernanceGate`
- promotion classification
- `MutationGuard`
- `ArchitectureGuardian`
- CCS certification
- strict test execution

This is constrained development autonomy, not autonomous runtime governance activation.

## Runtime Replay Flow

The deterministic replay sidecar is implemented through:

- `DecisionEnvelope`
- `ExecutionBoundary`
- `chain_verifier`
- `replay_engine`

The flow is:

1. Runtime decision data becomes a `DecisionEnvelope`.
2. The envelope is canonically hashed.
3. Each envelope links to the previous hash.
4. `ExecutionBoundary.finalize()` verifies chain integrity.
5. `replay_and_verify()` rebuilds a fresh engine run and compares envelope hashes.
6. Replay mismatch raises a fail-closed error.

This is active replay evidence generation and verification.

## Dormant Governance Memory Flow

`runtime/governance/master` and related governance memory documents explicitly define a dormant, observational memory layer. It is:

- documentation-only;
- append-only in intent;
- replay-safe;
- not runtime activation;
- not policy enforcement;
- not Decision Spine mutation.

The governance replay verifier can inspect sidecar lineage such as pattern, candidate, shadow, and promotion events. It must not load active controls, mutate history, activate policy, or change runtime state.

## Domain Trading Constitutional Review Flow

The domain trading package contains a mature read-only constitutional review stack:

1. Governance invariants classify canonical, production, phase, expansion, and experimental constraints.
2. Domain lock policy authorizes or rejects mutation requests.
3. Architecture promotion gates classify trust-class transitions.
4. The architecture evolution constitution resolves precedence.
5. Governance compression builds constitutional digests.
6. Certification export packages replay-verifiable governance evidence.
7. Capability review and adversarial suite test governance discrimination.
8. Governed execution proposal pipeline reviews execution proposals without execution.
9. Execution envelope model formalizes immutable execution intent.
10. Runtime foundation freeze consolidates readiness without adding runtime capability.

This flow is read-only and evidence-centric. It does not place trades, connect to brokers, or authorize live execution.

## Offline Paper Trading Flow

`offline_paper_trading.py` implements an offline-only governed command path:

1. Trading signal.
2. Decision context snapshot.
3. Policy validation.
4. Risk validation.
5. Deterministic command identity.
6. Deterministic fake execution.
7. Append-only ledger record.
8. Replay verification.

This is intentionally fake and local. It is not broker execution, market execution, or production trading.

## Mutation Checkpoints

Mutation checkpoints appear at:

- task governance review;
- promotion classification;
- mutation guard path validation;
- architecture guardian validation;
- artifact registry classification;
- CCS certification;
- Layer 0 freeze checks where installed or run;
- domain lock policy in domain-trading review flows.

## Certification Checkpoints

Certification checkpoints appear at:

- CCS generated artifact certification;
- strict generated test validation;
- domain governance digest generation;
- constitutional certification export;
- proposal certification;
- execution envelope certification hashes;
- runtime foundation freeze hashes.

## What Is Not Active

The governance memory layer is not active runtime governance. Runtime governance activation, approval validation execution, governance arbitration, and production execution are repeatedly documented as not implemented.

