# SAPIANTA Architecture Boundaries

## Purpose

This document defines the architectural boundaries of SAPIANTA.

Its purpose is to preserve:
- deterministic behavior
- governance isolation
- replay safety
- runtime stability
- market-facing separation
- dormant governance discipline

This document is documentation-only.
It does not activate runtime governance.

## Meta-Root Clarification

This document is part of meta-root architectural memory for `/sapianta`.

Although this file is physically stored under `runtime/governance/master/`, the architectural memory layer is not the governed runtime kernel.

Runtime is not governance memory. Governance memory is not runtime execution. Domain memory belongs to orchestration lineage and does not activate domain behavior.

Canonical workspace boundaries are indexed under `ARCHITECTURE/`.

---

# CORE DOMAIN SEPARATION

SAPIANTA is intentionally divided into multiple architectural domains.

These domains must remain explicitly separated unless future ADRs approve controlled integration.

---

# 1. RUNTIME DOMAIN

Purpose:
Execution, validation, deterministic processing, replay behavior, and runtime stability.

Examples:
- validation execution
- deterministic replay
- runtime engines
- pytest validation
- audit generation
- runtime determinism

Characteristics:
- execution-capable
- deterministic
- fail-closed
- runtime-active

NOT responsible for:
- governance evolution
- ADR memory
- architectural reasoning
- milestone lineage

---

# 2. GOVERNANCE DOMAIN

Purpose:
Governance lineage, architectural memory, replay-safe governance evolution, and dormant governance structures.

Examples:
- PatternMemory
- ShadowValidation
- PromotionLifecycle
- GovernanceReplayVerifier
- ADRs
- milestone lineage

Characteristics:
- dormant
- replay-safe
- append-only
- observational only
- sidecar-based
- deterministic

IMPORTANT:
ACTIVE has no runtime meaning.

NOT responsible for:
- runtime execution
- policy enforcement
- Decision Spine mutation
- runtime governance activation

---

# 3. OBSERVATIONAL DOMAIN

Purpose:
Inspection, replay analysis, audit visibility, evidence review, governance visibility.

Examples:
- replay verification
- audit viewer
- governance lineage inspection
- evidence visualization

Characteristics:
- read-oriented
- non-mutating
- inspection-first
- replay-safe

NOT responsible for:
- execution
- mutation
- enforcement

---

# 4. MARKET-FACING DOMAIN

Purpose:
Product presentation, demo flows, enterprise positioning, UI, explainability, and external communication.

Examples:
- AI Decision Validator
- cinematic landing page
- audit viewer UI
- Swagger showcase
- EU AI Act positioning
- enterprise demo flows

Characteristics:
- presentation-focused
- explainability-focused
- enterprise-oriented

IMPORTANT:
Market-facing presentation must not imply active autonomous governance unless explicitly implemented and approved.

---

# 5. EXPERIMENTAL DOMAIN

Purpose:
Exploratory concepts and future possibilities.

Examples:
- governance-native cognition
- adaptive governance pressure
- AI-generated ADR drafts
- governance graph visualization

Characteristics:
- non-binding
- exploratory
- non-runtime
- unstable by definition

Experimental ideas are NOT accepted architecture.

---

# CURRENT BOUNDARY RULES

Current enforced architectural boundaries:

- governance is dormant
- runtime governance activation is NOT IMPLEMENTED
- ACTIVE has no runtime meaning
- governance is observational only
- governance replay is read-only
- no self-modifying cognition
- no automatic governance activation
- no automatic git execution
- no runtime mutation through architectural memory

---

# FUTURE INTEGRATION RULE

Any future integration between:
- runtime
- governance
- observational
- market-facing
- experimental

requires:
1. explicit ADR
2. milestone update
3. SYSTEM_STATE update
4. CURRENT_FOCUS update
5. deterministic implementation review
6. replay-safety review
7. human approval

No implicit integration is allowed.
