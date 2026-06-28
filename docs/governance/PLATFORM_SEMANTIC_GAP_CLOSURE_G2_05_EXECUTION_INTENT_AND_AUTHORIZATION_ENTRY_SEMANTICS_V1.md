# Platform Semantic Gap Closure G2-05: Execution Intent And Authorization Entry Semantics

Status: implemented for certification validation.

## Objective

Implement CSA-primary semantic handling for execution-intent detection and
authorization-entry semantics only where deterministic parity with the compatibility
implementation is proven.

This batch does not transfer approval authority, execution authorization, PPP ownership,
provider ownership, worker ownership, lifecycle ownership, or governance authority to
UBTR. CSA may identify execution intent for certified detector classes only.

## Migrated Decisions

CSA is primary for these execution-intent detector decisions:

- `GENERIC_GOVERNED_ARTIFACT_CREATION`
- `NO_EXECUTION_INTENT`

The compatibility detector output remains identical for:

- intent detected or not detected;
- intent class;
- target kind;
- clarification requirement;
- routing action;
- execution authority not granted.

## Compatibility Fallback

Compatibility remains available and observable for every execution-intent detector
decision.

Compatibility remains authoritative when:

- CSA is unavailable.
- CSA cannot map to a certified execution-intent detector class.
- CSA diverges from the compatibility detector.
- CSA lacks target parity.
- CSA indicates semantics outside the certified G2-05 subset.

The following detector paths remain compatibility fallback in this batch:

- `GENERIC_GOVERNED_DOMAIN_CREATION`
- `GENERIC_GOVERNED_EXECUTION_REQUEST`

Generic governed execution requests continue to fail closed unless a certified structured
workflow mapping exists.

## Replay Evidence

Execution-intent detection now records:

- `semantic_execution_intent_source`
- `migration_batch_id`
- `canonical_semantic_artifact_reference`
- `canonical_semantic_artifact_hash`
- `previous_compatibility_interpretation`
- `semantic_comparison_artifact`
- `semantic_comparison_hash`
- `semantic_equivalence_result`
- `semantic_comparison_parity_status`
- `semantic_parity_evidence`
- `compatibility_fallback_available`
- `compatibility_fallback_authoritative`

ACLI routing replay surfaces the same evidence under execution-intent-specific fields so
execution-intent migration evidence remains separate from workflow-routing migration
evidence.

## Authority Boundary

CSA authority in this batch is limited to semantic execution-intent classification for
certified detector classes.

CSA does not gain:

- approval authority
- execution authorization authority
- PPP authority
- provider-selection authority
- worker authority
- lifecycle authority
- governance mutation authority
- replay mutation authority

The detector and ACLI routing artifacts continue to record:

- `execution_authority_granted: false`
- `authorization_created: false`
- `execution_requested_by_detector: false`
- `provider_invoked: false`
- `worker_invoked: false`

## Certification Impact

This batch reduces duplicated semantic responsibility in the human execution-intent
detector while preserving Generation 1 behavior. It also establishes replay-visible
execution-intent source provenance before worker/domain lifecycle entry semantics migrate
in G2-06.

## Rollback Impact

Rollback remains direct because the compatibility detector result is still computed and
recorded for every execution-intent decision. Disabling CSA-primary execution-intent
selection would return the detector to compatibility-only interpretation without changing
authorization, approval, PPP, provider, worker, lifecycle, or governance behavior.

## Remaining Migration Inventory

Remaining semantic gap closure work after G2-05:

- worker/domain lifecycle entry semantics
- native development semantics
- specialized Product/domain/provider/similarity routes
- OCS/PPP annotation semantics
- command boundary certification
- explanation compatibility rendering
- replay/hardening classifiers
- provider-assisted and legacy semantic closure
- compatibility retirement after all certified migrations complete
