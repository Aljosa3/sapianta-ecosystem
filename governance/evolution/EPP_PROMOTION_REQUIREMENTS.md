# EPP_PROMOTION_REQUIREMENTS
Status: GOVERNANCE FOUNDATION
Layer: Constitutional Evolution Governance
Principle: EPP Cannot Self-Promote

---

# 1. PURPOSE

This artifact defines promotion requirements for future EPP proposals.

Promotion is a governed decision. It is not an EPP runtime action.

---

# 2. PROMOTION REQUIRES

Promotion requires:

- replay verification;
- deterministic evidence;
- bounded scope;
- rollback capability;
- governance review;
- approval visibility;
- stability validation;
- no protected-layer mutation;
- explicit promotion decision evidence.

If any requirement is missing:

-> BLOCK promotion

---

# 3. PROMOTION CLASSES

EPP promotion decisions MUST use one of the following classes:

- `REJECTED`
- `SANDBOX_ONLY`
- `LIMITED_PROMOTION`
- `GOVERNED_PROMOTION`

## REJECTED

The proposal is not accepted for sandbox or runtime consideration.

## SANDBOX_ONLY

The proposal may be evaluated only in an isolated sandbox and may not
affect runtime behavior.

## LIMITED_PROMOTION

The proposal may be promoted only within a bounded, reviewed, reversible
scope with explicit monitoring and rollback conditions.

## GOVERNED_PROMOTION

The proposal may be promoted under full governance review, explicit
approval visibility, replay verification, stability validation, and
rollback readiness.

---

# 4. NON-AUTHORIZATION RULES

EPP cannot self-promote.

Runtime cannot authorize evolution.

Replay verification cannot authorize promotion.

Sandbox success cannot authorize promotion.

Only governed promotion decision evidence can authorize a promotion
class.

---

# 5. PROTECTED-LAYER RULE

No promotion may mutate protected layers unless a separate
constitutional process explicitly authorizes that change.

Uncertainty:

-> BLOCK promotion
