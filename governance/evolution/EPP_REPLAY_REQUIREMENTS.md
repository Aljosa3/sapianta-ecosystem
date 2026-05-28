# EPP_REPLAY_REQUIREMENTS
Status: GOVERNANCE FOUNDATION
Layer: Constitutional Evolution Governance
Principle: No Promotion Without Replay Verification

---

# 1. PURPOSE

This artifact defines deterministic replay requirements for future EPP
proposals.

Replay requirements are mandatory before any proposal may become
promotable.

---

# 2. REQUIRED REPLAY GUARANTEES

Every EPP proposal MUST provide:

- replayable proposal evidence;
- deterministic evidence generation;
- deterministic proposal identity;
- append-only proposal lineage;
- replay-safe validation;
- reproducible sandbox results;
- deterministic promotion packet construction.

If any guarantee cannot be verified:

-> BLOCK evolution proposal

---

# 3. REQUIRED ARTIFACTS

Every proposal evidence bundle MUST include:

- `proposal_id`;
- `sha256`;
- `lineage_reference`;
- `evidence_bundle`;
- `replay_manifest`;
- `sandbox_result`.

The `proposal_id` MUST be deterministic from proposal content and
lineage context.

The `sha256` value MUST identify canonical proposal evidence.

The `lineage_reference` MUST bind the proposal to prior evidence
without rewriting prior evidence.

The `evidence_bundle` MUST contain all inputs required to reproduce the
proposal analysis.

The `replay_manifest` MUST define deterministic replay inputs,
validation commands, expected outputs, and failure conditions.

The `sandbox_result` MUST be reproducible from the replay manifest.

---

# 4. APPEND-ONLY LINEAGE

EPP lineage is append-only.

Replay history MUST NOT be edited, compressed, rewritten, erased, or
silently replaced.

Rollback events MUST append evidence rather than deleting promoted
history.

---

# 5. PROMOTABILITY RULE

No proposal may become promotable without replay verification.

Replay verification does not itself authorize promotion.

Replay verification only proves that evidence is reproducible enough to
enter governance review.
