# META_ROOT_ARCHITECTURE_FORMALIZATION_V1

## CONTEXT

SAPIANTA evolved into a multi-root workspace with a meta root, governed runtime root, factory root, and domain roots.

The existing path `runtime/governance/master/` originally looked like runtime governance infrastructure, but its actual role became architectural memory, orchestration memory, meta-governance memory, cross-domain lineage memory, ADR lineage, roadmap memory, and domain memory.

This created ambiguity for future Codex, Claude, GPT, and human review sessions because path naming alone could imply runtime authority where none exists.

## DECISIONS

- Formalize `/sapianta` as the meta root.
- Formalize `/sapianta/sapianta_system` as the governed runtime root.
- Formalize `/sapianta/sapianta_factory` as the factory root.
- Formalize `/sapianta/sapianta-domain-*` as domain capability roots.
- Keep existing governance memory documents in place for minimal deterministic change.
- Add `/sapianta/ARCHITECTURE/` as the authoritative meta-root architecture index.
- Document that `runtime/governance/master/` is physically located under `runtime/` but architecturally belongs to meta-root memory.

## IMPLEMENTED DOCUMENTS

- `ARCHITECTURE/WORKSPACE_BOUNDARIES.md`
- `ARCHITECTURE/REPOSITORY_AUTHORITIES.md`
- `ARCHITECTURE/CANONICAL_ROOTS.md`
- `ARCHITECTURE/WORKSPACE_INTEGRITY_LAYER.md`
- `ARCHITECTURE/MILESTONES/infrastructure/META_ROOT_ARCHITECTURE_FORMALIZATION_V1.md`

## GOVERNANCE CONSTRAINTS

- Documentation-only
- Deterministic only
- No runtime mutation
- No Decision Spine changes
- No policy engine changes
- No enforcement activation
- No runtime integration
- No autonomous activation
- No automatic git execution

## EXPLICIT NON-GOALS

- Moving runtime files
- Refactoring execution code
- Activating governance
- Changing runtime semantics
- Creating workspace automation
- Creating autonomous authority
- Generating ADRs automatically
- Integrating factory output into runtime

## CONSEQUENCES

Future AI and human sessions have an explicit root-level authority map.

The governance memory layer remains stable, dormant, observational, replay-safe, and documentation-only.

Runtime execution and governance memory remain separated even when memory documents are physically stored under a `runtime/` path.

Factory isolation is preserved because generated proposals have no promotion, activation, or runtime authority without human review.

## WHAT IS STILL MISSING

- Automated workspace root verification
- Persisted filesystem verification tooling
- Repository authority validation tooling
- Lineage-aware mutation validation tooling
- Any future runtime-safe activation model

## WHY IT IS NOT IMPLEMENTED YET

The current milestone is a documentation-only architecture clarification. Tooling or automation would require separate design review, authority boundaries, deterministic verification rules, and human-approved ADRs before implementation.

Runtime activation remains delayed because architectural memory is not an execution surface.

## NEXT PHASE

Return primary development focus to server/demo productization:
- AI Decision Validator
- cinematic enterprise demo
- audit viewer polish
- EU AI Act positioning
- explainability UX
- enterprise trust narrative

## RELATED ADRS

No ADR semantic updates were required by this milestone.

Existing ADR lineage remains unchanged.

## RELATED TAG

Proposed tag:
`meta-root-architecture-formalization-v1`

## RELATED BRANCH

`feature/governance-evolution-loop`
