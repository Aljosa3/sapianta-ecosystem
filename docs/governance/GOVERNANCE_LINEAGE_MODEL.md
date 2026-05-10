# Governance Lineage Model

Status: canonical constitutional specification.

Governance lineage is the evidence chain proving where a governance rule, mutation, proposal, artifact, certification, or replay result came from and how it was allowed to exist.

## Lineage Principles

Governance lineage must preserve:

- source evidence;
- mutation provenance;
- replay identity;
- certification status;
- promotion history;
- approval or review context where required;
- fail-closed decisions;
- residual risk visibility.

Lineage is not a single database. It is distributed across manifests, markdown evidence, hash chains, ledgers, certification results, replay outputs, and development records.

## Lineage Sources

Primary lineage evidence includes:

- governance audit docs;
- Layer 0 freeze manifest;
- mutation map;
- system state documents;
- architecture boundary documents;
- promotion gate records;
- artifact registry entries;
- CCS certification records;
- replay envelope histories;
- domain governance manifests;
- domain evidence docs;
- constitutional digest hashes;
- certification export hashes;
- proposal certification objects;
- execution envelope hashes.

## Governance Evolution Evidence

Governance evolution is traceable through:

- milestone specifications;
- finalize manifests;
- freeze manifests;
- architecture maps;
- promotion gate artifacts;
- domain lock policy artifacts;
- constitutional hierarchy artifacts;
- governance compression and certification artifacts;
- audit reports and gap analysis.

Evolution evidence may be documentation-only, runtime-enforced, or domain-scoped. The lineage model must identify which class applies.

## Mutation Provenance

Mutation provenance answers:

- what changed;
- which layer was touched;
- whether the layer was immutable, restricted, governed, or evolvable;
- which guard or gate reviewed it;
- whether certification passed;
- whether replay evidence exists;
- whether approval was required;
- whether the change remained inside its authorized scope.

For generated development work, provenance normally passes through:

1. task or CAL proposal;
2. DevGovernanceGate;
3. PromotionGate;
4. MutationGuard;
5. ArchitectureGuardian;
6. artifact registry;
7. CCS certification;
8. strict test evidence.

## Replay Lineage

Replay lineage proves that deterministic evidence remains equivalent across verification.

Replay lineage includes:

- envelope hash;
- previous hash;
- chain verification result;
- replay verification result;
- deterministic digest hash;
- certification export hash;
- proposal hash;
- execution envelope hash where applicable.

Replay lineage must be read-only. Replay must observe and verify; it must not generate authoritative history.

## Certification Inheritance

Certification inheritance means a later artifact may depend on earlier certified evidence, but may not silently upgrade it.

Examples:

- A proposal certification may depend on constitutional review and replay review hashes.
- An execution envelope may depend on immutable intent, proposal certification, provenance, and replay identity hashes.
- A runtime foundation freeze may depend on digest, certification export, adversarial review, and envelope consistency.

Inherited certification remains valid only if the underlying evidence remains stable and replay-verifiable.

## Rollback Expectations

Rollback expectations are documented more strongly than they are uniformly implemented.

Canonical expectation:

- high-risk governed mutation should preserve enough evidence to understand, reject, or reverse unsafe evolution;
- structural evolution should have approval and lineage evidence;
- replay-critical evidence should not be rewritten to simulate rollback;
- rollback must not mutate history or erase the original decision.

Observed limitation:

- rollback evidence is partial and distributed. It is a future hardening area, not a fully uniform current capability.

## Lineage Classes

Canonical:
- freeze manifests;
- invariant registries;
- replay-critical hashes;
- finalized envelopes;
- immutable governance evidence.

Runtime-enforced:
- Guardian validation;
- MutationGuard rejection;
- CCS certification;
- replay chain verification.

Domain-scoped:
- domain lock policy;
- architecture promotion gates;
- constitutional certification export;
- execution proposal certification;
- execution envelope evidence.

Documentation-only:
- governance memory;
- maturity maps;
- workspace integrity requirements;
- architecture acceptance gate docs where no active enforcement exists.

Partially enforced:
- promotion gate enforcement where scripts exist but installed hooks differ;
- mutation validation where path coverage is incomplete;
- approval flows where fail-closed placeholders exist but centralized approval evidence is not uniform.

