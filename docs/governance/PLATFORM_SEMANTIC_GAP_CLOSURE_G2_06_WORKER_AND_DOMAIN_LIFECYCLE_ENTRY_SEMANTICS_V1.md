# Platform Semantic Gap Closure G2-06: Worker And Domain Lifecycle Entry Semantics

Status: implemented for certification validation.

## Objective

Implement CSA-primary semantic handling for worker and domain lifecycle entry semantics
only where deterministic semantic parity with the compatibility implementation is proven.

This batch does not transfer governance authority, PPP ownership, approval authority,
execution authorization, worker ownership, provider ownership, replay ownership, or
lifecycle orchestration to UBTR. UBTR remains semantic authority only.

## Migrated Decisions

CSA is primary for these lifecycle-entry decisions:

- `DOMAIN_WORKER_REQUEST`
- `DOMAIN_POST_EXECUTION_REPLAY_REVIEW`

The migrated prompts preserve the compatibility-selected workflow and routing status.
The CSA path is accepted only when lifecycle stage and requested action match the
compatibility detector output.

## Compatibility Fallback

Compatibility remains available and observable for every lifecycle-entry decision.

Compatibility remains authoritative for:

- domain approval entry;
- domain execution-ready entry;
- domain execution authorization entry;
- worker assignment entry;
- worker dispatch entry;
- worker invocation entry;
- worker execution entry;
- worker result capture entry;
- worker result validation entry;
- governed termination entry;
- any CSA-unavailable, divergent, ambiguous, or unsupported lifecycle prompt.

The `detect_domain_*_entry_intent()` compatibility functions remain active.

## Replay Evidence

ACLI lifecycle routing replay now records:

- `lifecycle_entry_semantic_source`
- `lifecycle_entry_migration_batch_id`
- `lifecycle_entry_semantic_comparison_artifact`
- `lifecycle_entry_semantic_comparison_hash`
- `lifecycle_entry_semantic_comparison_parity_status`
- `lifecycle_entry_compatibility_fallback_available`
- `lifecycle_entry_compatibility_fallback_authoritative`
- previous compatibility interpretation through the existing migration evidence fields
- CSA reference/hash through the existing routing CSA fields
- parity evidence through the existing `semantic_parity_evidence` field

The lifecycle semantic comparison artifact records:

- CSA interpretation;
- compatibility lifecycle interpretation;
- CSA lifecycle-entry decision;
- lifecycle stage parity;
- requested action parity;
- authority-preservation flags;
- replay lineage;
- migration batch identifier.

## Authority Boundary

CSA authority in this batch is limited to semantic lifecycle-entry classification for the
certified subset.

CSA does not gain:

- governance authority
- PPP authority
- approval authority
- execution authorization authority
- worker ownership
- provider ownership
- lifecycle orchestration authority
- replay mutation authority

All migrated lifecycle comparison artifacts preserve:

- `approval_influence: false`
- `authorization_influence: false`
- `execution_influence: false`
- `worker_influence: false`
- `lifecycle_orchestration_influence: false`
- `authorization_created: false`
- `execution_requested: false`
- `worker_invoked: false`
- `provider_invoked: false`

## Certification Impact

This batch reduces duplicated semantic responsibility in lifecycle entry routing without
changing Generation 1 behavior. It creates replay-visible source provenance for the first
worker/domain lifecycle entries before native development semantics migrate in G2-07.

## Rollback Impact

Rollback remains direct because compatibility detector results are still computed and
recorded. Disabling CSA-primary lifecycle-entry selection would return the migrated
entries to compatibility-only detection without changing approval, authorization, worker,
provider, lifecycle, replay, PPP, or governance behavior.

## Remaining Migration Inventory

Remaining semantic gap closure work after G2-06:

- remaining worker/domain lifecycle entry detector families;
- native development semantics;
- specialized Product/domain/provider/similarity routes;
- OCS/PPP annotation semantics;
- command boundary certification;
- explanation compatibility rendering;
- replay/hardening classifiers;
- provider-assisted and legacy semantic closure;
- compatibility retirement after all certified migrations complete.
