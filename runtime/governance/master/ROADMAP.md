# SAPIANTA Roadmap

## Document Role

This is a canonical state document. It records the current authoritative roadmap only.

Historical milestone summaries remain append-only lineage documents.

This roadmap is documentation-only and does not activate runtime governance.

ACTIVE has no runtime meaning. ACTIVE WORK means current human development focus, not runtime execution.

## ACTIVE WORK

- Server/demo productization
- AI Decision Validator productization
- Cinematic enterprise demo
- Audit viewer polish
- EU AI Act positioning
- Explainability UX
- Enterprise trust narrative

## Productization Phase — Product 1

- Foundation architecture phase completed
- Transition to execution/productization phase
- Product 1 = AI Decision Validator
- Focus on EU AI Act execution governance
- Local PC is the innovation layer
- GitHub is the governed release registry
- Server is the stable demo runtime

## GOVERNANCE MEMORY STATE

The governance memory layer is frozen, stable, deterministic, replay-safe, dormant, observational, and documentation-only.

Future governance memory changes should be append-only lineage updates unless a later human-approved ADR explicitly changes the governance memory model.

Runtime activation remains intentionally delayed.

## META-ROOT ARCHITECTURE STATE

The `/sapianta` workspace is the meta root for orchestration, architectural memory, governance memory, roadmap memory, ADR lineage, milestone lineage, and domain memory.

Canonical meta-root architecture index:
- `ARCHITECTURE/WORKSPACE_BOUNDARIES.md`
- `ARCHITECTURE/REPOSITORY_AUTHORITIES.md`
- `ARCHITECTURE/CANONICAL_ROOTS.md`
- `ARCHITECTURE/WORKSPACE_INTEGRITY_LAYER.md`
- `ARCHITECTURE/ECOSYSTEM_TOPOLOGY_SPEC_v1.md`
- `ARCHITECTURE/LAUNCHER_AUTHORITY_MODEL_v1.md`
- `ARCHITECTURE/REPOSITORY_INTERACTION_CONTRACT_v1.md`
- `ARCHITECTURE/GOVERNED_ORCHESTRATION_MODEL_v1.md`
- `ARCHITECTURE/REPLAY_LINEAGE_MODEL_v1.md`
- `ARCHITECTURE/SANDBOX_AND_FACTORY_ISOLATION_v1.md`
- `ARCHITECTURE/REPOSITORY_INTERACTION_FLOW_v1.md`
- `ARCHITECTURE/DOMAIN_LIFECYCLE_MODEL_v1.md`
- `ARCHITECTURE/FACTORY_PROPOSAL_FLOW_v1.md`
- `ARCHITECTURE/RUNTIME_ACCEPTANCE_GATE_v1.md`
- `ARCHITECTURE/ARTIFACT_IDENTITY_MODEL_v1.md`
- `ARCHITECTURE/REPLAY_LINEAGE_PROPAGATION_v1.md`
- `ARCHITECTURE/PROMOTION_LINEAGE_CONTINUITY_v1.md`
- `ARCHITECTURE/AUDIT_CONTINUITY_MODEL_v1.md`
- `ARCHITECTURE/GOVERNED_ARTIFACT_INHERITANCE_v1.md`
- `ARCHITECTURE/FOUNDATION_FINALIZATION_v1.md`
- `ARCHITECTURE/FOUNDATION_CANONICAL_SEMANTICS_v1.md`
- `ARCHITECTURE/FOUNDATION_EXTENSION_RULES_v1.md`
- `ARCHITECTURE/FOUNDATION_ANTI_DRIFT_RULES_v1.md`

Existing governance memory location:
- `runtime/governance/master/`

Important clarification:
`runtime/governance/master/` is physically located under `runtime/`, but it is not runtime execution. It is meta-root governance memory and cross-domain lineage memory.

## ECOSYSTEM TOPOLOGY STATE

The SAPIANTA workspace is documented as a federated governed ecosystem architecture.

Current documented topology:
- meta-root workspace: ecosystem coordination, topology, orchestration memory, governance lineage
- `sapianta_system`: governed runtime authority
- `sapianta-domain-*`: isolated bounded domain repositories
- `sapianta_factory`: sandbox-only proposal generation
- `runtime/governance/master`: governance lineage memory

The launcher authority model, repository interaction contract, replay lineage model, sandbox isolation model, and governed orchestration model are documented only. They do not activate runtime orchestration.

Repository interaction flow, domain lifecycle states, factory proposal flow, and runtime acceptance gate semantics are documented only. They do not implement lifecycle enforcement, runtime acceptance tooling, promotion automation, or activation.

Governed artifact identity, replay lineage propagation, promotion continuity, audit continuity, and artifact inheritance semantics are documented only. They do not implement hashing, replay tooling, audit tooling, runtime acceptance, promotion automation, or activation.

The governed ecosystem foundation is finalized for Foundation Phase v1. Future work must extend foundation semantics and must not redefine foundation semantics.

## DOMAIN MEMORY STATE

- Trading: LEVEL 2 dormant validation/simulation domain. Not production-active and not autonomous.
- Explosion: LEVEL 1 conceptual latent acceleration domain. No formal Explosion domain currently exists.

Both domains remain dormant while server/demo productization continues.

Latest domain research milestone: `TRADING_EXPLOSION_DOMAIN_STATE_INVESTIGATION_V1`.

Persistence status: confirmed in workspace as documentation-only domain roadmap context.

## FUTURE WORK

- Governance foundation maintenance
- Meta-root architecture memory maintenance
- Governed ecosystem topology maintenance
- Future launcher authority design
- Future repository interaction validation
- Future repository interaction flow validation
- Future domain lifecycle enforcement design
- Future runtime acceptance gate design
- Future governed artifact identity design
- Future audit continuity design
- Future promotion lineage continuity design
- Future governed artifact inheritance design
- Future replay lineage propagation design
- Future foundation-compatible extension design
- Future anti-drift review process design
- Future governed orchestration design
- Workspace integrity verification design
- Trading domain memory maintenance
- Explosion domain memory maintenance
- Future governed activation
- Future governance UI
- Future approval validation
- Future artifact lineage integration
- Future governance arbitration
- Future runtime-safe activation

Future work requires explicit human review, ADR updates when semantic decisions change, milestone summaries, deterministic implementation planning, and replay-safety review before any runtime integration is considered.

Governance foundation maintenance means preserving deterministic architectural memory, maturity mapping, architecture boundaries, ADR lineage, and milestone summaries. It does not mean runtime governance activation.

## EXPERIMENTAL IDEAS

- Governance graph visualization
- Governance-native cognition
- AI-generated ADR drafts
- Governance replay UI
- Adaptive governance pressure

Experimental ideas are not accepted architecture. They may be promoted only through future human-reviewed ADRs.

## Standard Milestone Workflow

After every major milestone:

1. Commit
2. Git tag
3. Milestone summary
4. ADR update if semantic decisions changed
5. `SYSTEM_STATE.md` update
6. `CURRENT_FOCUS.md` update
7. `ROADMAP.md` update
8. `GOVERNANCE_MATURITY_MAP.md` update if maturity status changed

Purpose: create persistent architectural lineage and reduce AI context loss across long-horizon development.

This workflow is human-governed. Do not automate milestone generation logic. Codex may prepare deterministic commit summaries, proposed tags, proposed milestone categories, and proposed affected ADR lists, but humans must review and execute commits and tags manually.

## Current Governance Baseline

- Latest governance milestone: `GOVERNANCE_MEMORY_FOUNDATION_FINALIZATION_V1`
- Milestone category: governance
- Branch: `feature/governance-evolution-loop`
- Milestone tag: `governance-memory-foundation-v1`
- State: governance memory frozen; runtime activation intentionally delayed
