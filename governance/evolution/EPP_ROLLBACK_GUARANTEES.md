# EPP_ROLLBACK_GUARANTEES
Status: GOVERNANCE FOUNDATION
Layer: Constitutional Evolution Governance
Principle: Rollback Before Promotion

---

# 1. PURPOSE

This artifact defines rollback obligations for future EPP-governed
changes.

Rollback readiness is required before promotion.

---

# 2. REQUIRED GUARANTEES

All promoted changes MUST be reversible.

A rollback path MUST exist before promotion.

Replay history MUST be preserved during rollback.

Rollback MUST NOT erase lineage.

Rollback events MUST be append-only.

Rollback evidence MUST be deterministic and replay-visible.

---

# 3. MANDATORY ROLLBACK CONDITIONS

Failed evolution:

-> rollback mandatory

Unstable behavior:

-> rollback mandatory

Loss of replayability:

-> rollback mandatory

Approval boundary violation:

-> rollback mandatory

Protected-layer mutation:

-> rollback mandatory

---

# 4. ROLLBACK EVIDENCE

Rollback evidence MUST include:

- rollback trigger;
- affected proposal identity;
- affected promotion decision;
- rollback steps;
- replay preservation confirmation;
- lineage append confirmation;
- post-rollback validation result.

---

# 5. LINEAGE PRESERVATION

Rollback restores bounded runtime state where authorized. It does not
rewrite governance evidence, replay history, proposal lineage, or
promotion decisions.

Rollback is an additional governed event, not erasure.
