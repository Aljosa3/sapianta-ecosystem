# Constitutional Architecture Spec V1

Status: canonical constitutional specification.

Source basis: governance audit evidence in `docs/governance_audit/`, runtime enforcement code, governance manifests, freeze manifests, replay code, development guards, certification flow, and domain constitutional artifacts.

This specification describes how SAPIANTA actually works. It does not redesign governance, change runtime behavior, introduce new enforcement, or replace historical semantics.

## Constitutional Definition

SAPIANTA is a constitutionally constrained autonomous system with enforced mutation boundaries and replay-safe governance.

The constitution is the collection of immutable and governed rules that constrain:

- what may mutate;
- what must remain replay-safe;
- what autonomous systems may propose;
- what autonomous systems may not execute;
- which domains are protected;
- how governance evidence is preserved;
- how architectural evolution is reviewed.

The constitution is not one file and not one runtime service. It is distributed across Layer 0 freeze manifests, mutation policy, runtime guards, promotion gates, certification gates, replay verification, governance docs, and domain constitutional review engines.

## Canonical Layer Taxonomy

The canonical layer model for mutation governance is the L0-L4 model:

| Layer | Canonical Name | Mutability | Constitutional Meaning |
| --- | --- | --- | --- |
| L0 | System Constitution | Immutable | Fundamental architecture laws, deterministic guarantees, kernel freeze boundaries, system integrity constraints. |
| L1 | Canonical Artifact Definitions | Immutable | Stable schemas, contracts, envelopes, ledger structures, replay identities, and audit artifact definitions. |
| L2 | Decision Spine | Restricted | Deterministic proposal, policy, advisory, decision envelope, ledger, and replay chain behavior. |
| L3 | Governance System | Governed | Promotion gates, validation pipelines, certification, governance review, approval surfaces, artifact registry. |
| L4 | Research System | Evolvable | CAL, experiments, research memory, generated development tasks, bounded exploratory mutation. |

The four-layer safety architecture remains valid, but it is an authority model rather than the canonical mutation layer taxonomy. It defines who may authorize or control whom:

- Human Authority governs final direction and constitutional change.
- Governance Layer evaluates and constrains research and execution admissibility.
- Autonomous Research Layer may propose or experiment inside bounded regions.
- Execution Layer may act only through governed, deterministic, ledgered boundaries.

## Constitutional Hierarchy

Where multiple governance mechanisms conflict, authority is interpreted in this order:

1. Replay safety.
2. Layer 0 constitutional constraints.
3. Governance invariants and immutable artifact definitions.
4. Trust boundaries and protected domains.
5. Domain lock policy and trusted scopes.
6. Semantic freeze and freeze manifests.
7. Promotion gates and governed mutation rules.
8. Certification gates and strict validation.
9. Research, CAL, and experimental evolution.
10. Temporary or product-facing development layers.

This ordering reflects the audited architecture. Domain-trading implements an explicit constitutional hierarchy with replay safety first; the wider system implements the same pattern through distributed guards and freeze logic.

## Constitutional Invariants

The following principles are constitutional:

- Replay verification must not mutate evidence, ledgers, finalized envelopes, or governance history.
- Layer 0 and Layer 1 must not be silently mutated.
- Protected runtime and governance paths must be rejected by autonomous mutation flows.
- Generated or proposed code must pass guard validation before certification or use.
- Structural and parametric changes require governance review or approval.
- Certification must fail closed when evidence, tests, artifact type, or validation is missing.
- Governance memory under `runtime/governance/master` is dormant and observational unless a separate governed activation milestone changes that state.
- Domain execution proposals must remain proposals until separately authorized by future governance; proposal review is not execution.
- Experimental and research layers cannot override replay safety, invariants, trust boundaries, or semantic freeze.

## Mutation Constitution

Mutation authority is classified as follows:

- Immutable: Layer 0, Layer 1, replay-critical evidence, finalized envelopes, immutable ledger history, canonical invariant evidence.
- Restricted: Layer 2 Decision Spine and deterministic runtime decision paths.
- Governed: Layer 3 governance systems, promotion gates, certification flows, trusted-scope topology where classified as governed mutable.
- Evolvable: Layer 4 research, generated development modules, experiments, domain feature work, and product presentation layers.
- Forbidden: broker bypasses, hidden execution paths, unauthorized mutation of protected domains, replay-breaking mutation, undocumented activation of dormant governance.

Mutation is only constitutional when it remains inside the correct class, passes applicable gates, preserves replay evidence, and does not violate higher-authority constraints.

## Enforcement Reality

SAPIANTA does not have a single universal enforcement kernel. Enforcement is distributed:

- `scripts/check_layer_freeze.py` validates Layer 0 locked files when run.
- `ArchitectureGuardian` blocks protected paths and dangerous code patterns in development flows.
- `MutationGuard` rejects forbidden runtime paths and oversized patches.
- `MutationValidator` classifies paths into mutation layers and rejects immutable layers.
- `DevGovernanceGate` blocks or routes sensitive development tasks.
- Promotion gates classify cosmetic, parametric, and structural changes.
- CCS certification requires Guardian validation and strict generated tests.
- Replay engines verify hash chains and deterministic replay equivalence.
- Domain constitutional modules evaluate invariants, domain locks, promotion gates, constitutional conflicts, digests, certification exports, proposal review, and execution envelopes.

The strongest active enforcement is in development mutation flows and domain constitutional review flows. Some governance remains documentation-only by design.

## Ambiguity and Partial Enforcement

The following are constitutional facts, not defects to hide:

- The installed `sapianta_system/.git/hooks/pre-commit` is weaker than `scripts/hooks/pre-commit`; it omits some documented promotion and Layer 0 freeze checks.
- `MutationValidator` path matching does not cover every physical repository layout.
- Approval semantics are distributed across multiple gates and are not centralized in one validator.
- Governance memory is explicitly dormant even though development governance enforcement is active.
- Domain-trading constitutional enforcement is strong but domain-scoped.

These facts must be preserved in future analysis until runtime evidence changes.

## Constitutional Limits

Autonomous systems may:

- propose development tasks;
- generate code in allowed development regions;
- generate tests in bounded development scope;
- request certification;
- produce replay-verifiable evidence;
- participate in proposal review where explicitly allowed.

Autonomous systems may not:

- mutate Layer 0 or Layer 1;
- bypass guards, promotion gates, certification, or replay verification;
- activate dormant governance memory;
- execute broker, market, or production actions;
- infer missing constitutional state;
- silently repair governance history;
- promote experimental concepts into canonical layers without governed evidence.

## Canonical Outcome

SAPIANTA governance is both documented and partially executable. Its constitutional architecture is real, but distributed. The canonical model is therefore:

SAPIANTA constrains autonomy through immutable constitutional layers, protected mutation boundaries, deterministic replay evidence, governed promotion, certification gates, and explicit human authority over constitutional change.

