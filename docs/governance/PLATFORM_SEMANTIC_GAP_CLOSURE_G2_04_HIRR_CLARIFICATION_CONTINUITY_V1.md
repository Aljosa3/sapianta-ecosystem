# Platform Semantic Gap Closure G2-04: HIRR Clarification Continuity

Status: implemented for certification validation.

## Objective

Implement CSA-primary semantic handling for HIRR clarification continuity only where
deterministic parity with the compatibility implementation is proven.

This batch does not alter governance, approval, PPP, execution, provider, worker, or
lifecycle authority. HIRR continues to own clarification lifecycle binding and workflow
resumption. UBTR/CSA supplies the semantic source only for certified continuity decisions.

## Migrated Decisions

CSA is primary for these HIRR clarification-continuity decisions:

- Proposal-only OCS continuity after a clarification reply asks for advisory planning,
  unresolved ambiguity help, analysis, recommendation, or no-execution guidance.
- Bounded file-write proof continuity after a clarification reply confirms the bounded
  proof-file path.

The selected workflow remains identical to the compatibility result:

- `OCS_LLM_COGNITION`
- `BOUNDED_FILE_WRITE_WORKER_USER_SESSION`

## Compatibility Fallback

Compatibility remains available and observable for every continuity decision.

Compatibility remains authoritative when:

- CSA does not produce a usable clarification-continuity semantic artifact.
- CSA workflow identity differs from the compatibility refinement.
- CSA indicates clarification is still required.
- CSA indicates execution, provider invocation, or worker invocation.
- The decision belongs to a continuity family without certified CSA parity.

Governed-domain clarification continuity remains on compatibility fallback in this batch.

## Replay Evidence

HIRR continuity replay now records:

- `semantic_routing_source`
- `previous_compatibility_interpretation`
- `migration_batch_id`
- `canonical_semantic_artifact_reference`
- `canonical_semantic_artifact_hash`
- `semantic_comparison_artifact`
- `semantic_comparison_hash`
- `semantic_equivalence_result`
- `semantic_comparison_parity_status`
- `semantic_parity_evidence`
- `compatibility_fallback_available`
- `compatibility_fallback_authoritative`

The semantic comparison artifact is hash-bound and replay-visible. It compares the CSA
interpretation with the HIRR compatibility clarification-continuity interpretation and
records semantic differences, confidence comparison, parity status, and replay lineage.

## Authority Boundary

CSA authority in this batch is limited to semantic interpretation for certified
clarification-continuity decisions.

CSA does not gain:

- governance authority
- approval authority
- PPP authority
- execution authority
- provider-selection authority
- worker authority
- lifecycle authority
- replay mutation authority

HIRR continues to own:

- active clarification lookup
- reply binding
- chain validation
- resolution artifact creation
- workflow selection after clarification
- lifecycle resumption state
- fail-closed behavior

## Certification Impact

This batch reduces duplicated semantic responsibility in HIRR clarification continuity
without changing Generation 1 behavior. Replay now exposes both the CSA interpretation and
the previous compatibility interpretation for certified and fallback paths.

## Rollback Impact

Rollback is operationally simple because compatibility interpretation remains computed and
recorded on every continuity decision. Disabling CSA-primary selection for this batch would
return all HIRR clarification-continuity decisions to the compatibility path while
preserving replay observability.

## Remaining Migration Inventory

Remaining semantic gap closure work after G2-04:

- execution intent semantics
- worker/domain lifecycle entry semantics
- native development semantics
- specialized product/domain/provider/similarity routes
- OCS/PPP annotation semantics
- command boundary certification
- explanation compatibility rendering
- replay/hardening classifiers
- provider-assisted and legacy semantic closure
- compatibility retirement after all certified migrations complete
