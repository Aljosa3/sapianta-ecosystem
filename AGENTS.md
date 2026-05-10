# SAPIANTA Codex Orchestration Guide

Status: canonical Codex entrypoint.

Purpose: governance-native repository interpretation for Codex-assisted development.

This file defines how Codex should understand and work inside the SAPIANTA repository. It does not redesign governance, change runtime behavior, introduce autonomous mutation, or replace existing constitutional artifacts.

## 1. What SAPIANTA Is

SAPIANTA is constitutional AI execution governance infrastructure.

The canonical product direction is Product 1: AI Decision Validator.

SAPIANTA governs AI execution before runtime activation by preserving:

- constitutional execution boundaries;
- deterministic validation semantics;
- replay-safe governance evidence;
- fail-closed execution review;
- mutation-constrained development;
- enterprise-readable audit continuity.

SAPIANTA is not:

- unrestricted autonomous AI;
- an AGI system;
- self-evolving intelligence;
- an autonomous governance replacement;
- unconstrained agent infrastructure;
- broker/API execution infrastructure;
- a system that silently rewrites its own constitution.

## 2. Source of Truth

Codex must treat these artifacts as constitutional repository guidance:

- `docs/governance/CONSTITUTIONAL_ARCHITECTURE_SPEC_V1.md`
- `docs/governance/CANONICAL_LAYER_MODEL.md`
- `docs/governance/CONSTITUTIONAL_INVARIANTS.md`
- `docs/governance/GOVERNANCE_ENFORCEMENT_HIERARCHY.md`
- `docs/governance/GOVERNANCE_LINEAGE_MODEL.md`
- `docs/governance/STABLE_SUBSTRATE_DECLARATION_V1.md`
- `docs/governance/GOVERNANCE_CONFORMANCE_SYSTEM_V1.md`
- `.github/governance/evidence/`
- `.github/governance/finalize/`
- `.github/governance/manifests/`

Product and enterprise execution guidance is defined by:

- `docs/product_lifecycle/PRODUCT_1_EXECUTION_PHASE_V1.md`
- `docs/product_lifecycle/PRODUCT_1_RELEASE_DISCIPLINE_V1.md`
- `docs/product_lifecycle/ENTERPRISE_DEMO_ACCEPTANCE_CRITERIA_V1.md`
- `docs/product_lifecycle/PRODUCT_1_DEMO_SCRIPT_V1.md`
- `docs/product_lifecycle/PRODUCT_1_ENTERPRISE_MESSAGE_ARCHITECTURE_V1.md`

Conformance verification is implemented by:

- `runtime/governance/governance_conformance_engine.py`
- `runtime/governance/conformance_rules.py`
- `runtime/governance/conformance_models.py`

Governance artifacts are not "documentation only" in the ordinary sense. They are constitutional orchestration artifacts, bounded development constraints, semantic control layers, and replay-safe repository guidance.

## 3. Governance Topology

The canonical mutation layer model is:

- L0: System Constitution, immutable.
- L1: Canonical Artifact Definitions, immutable.
- L2: Decision Spine, restricted.
- L3: Governance System, governed.
- L4: Research System, bounded and evolvable.

The historical safety authority model is separate:

- Human Authority retains final constitutional authority.
- Governance Layer constrains research and execution admissibility.
- Autonomous Research Layer may propose or experiment inside bounded regions.
- Execution Layer may act only through governed, deterministic, ledgered boundaries.

Codex must not conflate these two models.

## 4. Constitutional Boundaries

Codex must preserve:

- constitutional semantics;
- canonical layer meanings;
- invariant semantics;
- enforcement hierarchy semantics;
- governance lineage semantics;
- replay read-only semantics;
- fail-closed semantics;
- mutation boundary declarations;
- known limitation visibility.

Codex must not silently reinterpret:

- Layer 0 immutability;
- Layer 1 canonical artifact stability;
- Decision Spine restrictions;
- dormant governance memory;
- Product 1 enterprise positioning;
- partial conformance evidence.

## 5. Codex Execution Expectations

Codex should:

- preserve governance semantics;
- preserve replay guarantees;
- preserve mutation boundaries;
- preserve deterministic semantics;
- preserve audit continuity;
- preserve enterprise positioning;
- document limitations and known gaps;
- prefer targeted validation over broad speculative changes;
- keep generated artifacts replay-safe where the surrounding layer requires it.

Codex should not:

- drift toward unrestricted autonomy;
- silently redefine governance;
- bypass constitutional constraints;
- bypass release discipline;
- create hidden runtime mutation paths;
- introduce self-modifying governance;
- frame SAPIANTA as AGI or unrestricted agent autonomy;
- hide unresolved partial conformance.

## 6. Allowed Evolution

Allowed evolution includes:

- enterprise UX refinement;
- audit visualization refinement;
- runtime explainability refinement;
- governance evidence refinement;
- release discipline refinement;
- bounded remediation proposals;
- replay-safe tooling;
- enterprise demo refinement;
- product narrative refinement consistent with the enterprise message architecture.

Allowed evolution must remain governance-preserving, bounded, and scoped.

## 7. Forbidden Evolution

Forbidden evolution includes:

- autonomous constitutional mutation;
- unrestricted self-modifying governance;
- hidden runtime autonomy;
- governance bypass mechanisms;
- replay-breaking changes;
- uncontrolled deployment semantics;
- unrestricted agent framing;
- AGI/singularity messaging;
- broker/API execution introduction through governance or productization work;
- AI replacing governance or human oversight.

## 8. Enterprise Message Constraints

Codex must preserve governance-first framing:

- AI execution governance;
- bounded execution semantics;
- constitutional positioning;
- replay-safe terminology;
- deterministic validation;
- enterprise trust orientation;
- auditability and evidence continuity;
- EU AI Act aligned governance evidence where phrased carefully.

Codex must avoid:

- AGI hype;
- singularity framing;
- unrestricted autonomy language;
- self-aware AI narratives;
- "AI replacing governance" framing;
- perfect safety or guaranteed compliance claims;
- generic chatbot positioning.

Canonical Product 1 identity:

- AI Decision Validator.

Acceptable secondary descriptions:

- AI Execution Governance Layer;
- Runtime AI Governance Infrastructure;
- Constitutional AI Execution Layer;
- AI Runtime Validation Infrastructure.

## 9. Release Discipline

Codex must understand the release topology:

Local PC -> innovation layer.

GitHub -> governed release registry.

Server -> stable governed runtime.

Release work should preserve:

- replay lineage;
- governance evidence;
- deterministic semantics;
- constitutional continuity;
- certification evidence;
- known limitations;
- conformance status.

Codex must not introduce uncontrolled deployment automation or direct server mutation semantics.

## 10. Validation Expectations

Codex should run validation appropriate to the touched surface.

For governance conformance changes, prefer:

```bash
pytest tests/test_governance_conformance.py
python -m runtime.governance.governance_conformance_engine
git diff --check
```

For documentation-only governance or product lifecycle changes, at minimum run:

```bash
git diff --check
```

Codex should preserve:

- fail-closed semantics;
- governance evidence;
- replay-safe artifacts;
- conformance semantics;
- explicit non-goals;
- limitation visibility.

## 11. Self-Building Philosophy

Codex-assisted development in SAPIANTA is:

- bounded;
- governance-native;
- replay-aware;
- constitutionally constrained;
- enterprise-positioned;
- lineage-preserving.

The goal is not unrestricted autonomous self-improvement.

The goal is governance-preserving bounded evolution.

## 12. Completion Discipline

Codex should:

- create replay-safe artifacts when the task calls for evidence;
- preserve lineage continuity;
- use governance-oriented commit semantics when commits are requested;
- maintain explicit scope boundaries;
- preserve deterministic documentation;
- mention validation performed;
- mention known gaps when relevant.

Codex should not:

- silently mutate unrelated files;
- create uncontrolled architecture drift;
- bypass governance documentation;
- hide unresolved limitations;
- change runtime behavior from a documentation or orchestration task;
- reinterpret constitutional semantics for convenience.

## 13. Current Constitutional Baseline

Baseline: `constitutional-governance-finalize-v1`.

Stable substrate status:

- governance-native;
- replay-safe;
- mutation-constrained;
- fail-closed;
- lineage-preserving;
- constitutionally bounded.

Current active product focus:

- Product 1, AI Decision Validator.

Current conformance reality:

- conformance verification exists;
- known hook drift remains visible;
- partial conformance must not be hidden or reframed as full conformance.

## 14. Core Rule

When in doubt, preserve the constitution first:

1. replay safety;
2. constitutional invariants;
3. mutation boundaries;
4. governance lineage;
5. enterprise release discipline;
6. product refinement.

SAPIANTA is not merely a governed AI system.

It is a constitutionally constrained autonomous system with replay-safe governance, enforced mutation boundaries, and deterministic constitutional verification.

