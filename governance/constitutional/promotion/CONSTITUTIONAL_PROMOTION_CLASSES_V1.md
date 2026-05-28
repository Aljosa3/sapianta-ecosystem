# CONSTITUTIONAL_PROMOTION_CLASSES_V1

Status: CANONICAL CONSTITUTIONAL PROMOTION CLASSES

## Purpose

This artifact defines canonical promotion classes for future governance
promotion decisions.

It does not implement promotion execution.

## REJECTED

Authority scope: no promotion authority.

Replay requirements: evidence should remain replay-visible when
available.

Rollback requirements: no runtime rollback required because no
promotion occurs.

Approval requirements: rejection reason must be visible.

Evidence requirements: rejected proposal evidence and rejection reason.

Quarantine behavior: unsafe or unverifiable proposals remain
quarantined or rejected.

Lineage requirements: rejection event appends to proposal lineage.

## SANDBOX_ONLY

Authority scope: isolated sandbox evaluation only; no runtime effect.

Replay requirements: sandbox evidence and replay manifest required.

Rollback requirements: sandbox cleanup path required; no production
rollback authority implied.

Approval requirements: governance review for sandbox eligibility.

Evidence requirements: sandbox scope, replay evidence, lineage, and
blocked runtime authority statement.

Quarantine behavior: invalid sandbox evidence returns to quarantine.

Lineage requirements: sandbox lineage appends to proposal lineage.

## LIMITED_PROMOTION

Authority scope: bounded, reviewed, reversible promotion inside a
defined non-constitutional scope.

Replay requirements: deterministic replay evidence required.

Rollback requirements: rollback manifest, rollback scope, rollback
replay reference, rollback lineage reference, and rollback certification
reference required before promotion.

Approval requirements: explicit governance approval required.

Evidence requirements: approval reference, promotion scope,
certification reference, replay reference, rollback compatibility, and
promotion evidence hash.

Quarantine behavior: replay, rollback, approval, or scope uncertainty
causes quarantine.

Lineage requirements: append-only promotion lineage with approval,
replay, certification, and rollback references.

## CONSTITUTIONAL_PROMOTION

Authority scope: highest-risk constitutional promotion affecting
protected governance meaning, hierarchy, boundaries, replay
requirements, approval requirements, or fail-closed semantics.

Replay requirements: deterministic replay evidence required.

Rollback requirements: rollback guarantees required before promotion.

Approval requirements: highest approval level required.

Evidence requirements: constitutional rationale, mutation class,
authority impact, replay evidence, approval evidence, rollback evidence,
certification evidence, and promotion evidence.

Quarantine behavior: any uncertainty causes quarantine and governance
review.

Lineage requirements: append-only constitutional promotion lineage.

CONSTITUTIONAL_PROMOTION cannot self-activate.

CONSTITUTIONAL_PROMOTION cannot bypass governance.

CONSTITUTIONAL_PROMOTION cannot be authorized by cognition, replay
verification alone, or runtime success.
