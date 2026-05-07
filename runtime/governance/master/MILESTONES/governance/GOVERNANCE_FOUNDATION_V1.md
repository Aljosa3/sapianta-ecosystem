# GOVERNANCE_FOUNDATION_V1

## 1. CONTEXT

SAPIANTA needed persistent architectural memory that can survive long-horizon development across Codex, Claude, GPT, and human sessions. The foundation records governance decisions, system state, constraints, development focus, milestone lineage, and future evolution context in deterministic markdown files.

The market-facing product is AI Decision Validator.

## 2. DECISIONS

- Create `runtime/governance/master/` as the AI-readable architectural memory root.
- Separate system state, current focus, roadmap, ideas, milestones, ADRs, and commit guidance.
- Categorize milestones deterministically by architectural domain.
- Keep governance dormant, replay-safe, and observational only.
- Delay runtime activation intentionally.
- Preserve server/demo branch separation from governance foundation work.

ACTIVE has no runtime meaning.

## 3. IMPLEMENTED MODULES

- `SYSTEM_STATE.md`
- `CURRENT_FOCUS.md`
- `ROADMAP.md`
- `IDEAS.md`
- `COMMIT_GUIDELINES.md`
- `MILESTONES/governance/GOVERNANCE_FOUNDATION_V1.md`
- `ADR/ADR-0001-governance-sidecar.md`
- `ADR/ADR-0002-shadow-validation.md`
- `ADR/ADR-0003-transition-legality.md`
- `ADR/ADR-0004-governance-replay.md`
- `ADR/ADR-0005-server-demo-separation.md`

These are documentation modules only. They are not runtime modules.

## 4. GOVERNANCE CONSTRAINTS

- Governance remains dormant.
- Governance is replay-safe.
- Governance is observational only.
- Runtime activation is intentionally delayed.
- No Decision Spine changes.
- No policy engine changes.
- No enforcement activation.
- No runtime integration.
- No active reads.
- No governance activation.
- No automated milestone generation.
- No automatic git execution.

## 5. EXPLICIT NON-GOALS

- Runtime governance activation
- Self-modifying cognition
- Runtime automation
- Policy enforcement
- Approval validation execution
- Governance arbitration
- Decision Spine modification
- Policy engine modification
- ADR generator implementation
- Runtime mutation

## 6. CONSEQUENCES

Future AI and human sessions have a deterministic architectural memory entry point. SAPIANTA can preserve development lineage without creating new runtime behavior or governance enforcement.

The governance foundation can remain stable while server/demo productization proceeds independently.

## 7. WHAT IS STILL MISSING

- Runtime-safe activation plan
- Governance UI
- Approval validation execution model
- Artifact lineage integration
- Governance arbitration model
- Replay UI
- Formal promotion process from ideas to accepted ADRs

## 8. WHY IT IS NOT IMPLEMENTED YET

These items are intentionally delayed because runtime activation and governance execution require later human review, stronger validation, explicit ADRs, and deterministic implementation plans. The current milestone preserves memory and lineage only.

## 9. NEXT PHASE

Continue server/demo branch work for AI Decision Validator productization, including UI, demo, audit viewer, cinematic landing page, EU AI Act positioning, and enterprise demo flow.

## 10. RELATED ADRS

- `ADR-0001-governance-sidecar.md`
- `ADR-0002-shadow-validation.md`
- `ADR-0003-transition-legality.md`
- `ADR-0004-governance-replay.md`
- `ADR-0005-server-demo-separation.md`

## 11. RELATED TAG

`governance-foundation-v1`

## 12. RELATED BRANCH

server/demo branch
