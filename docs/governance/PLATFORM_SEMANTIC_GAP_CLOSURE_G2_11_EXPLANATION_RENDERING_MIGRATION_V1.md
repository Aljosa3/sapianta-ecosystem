# Platform Semantic Gap Closure G2-11 Explanation Rendering Migration V1

Status: implementation governance artifact.

Scope: CSA-primary explanation rendering where deterministic section parity with the
compatibility human-friendly explanation is proven.

This batch does not change governance, OCS, PPP, worker, provider, approval, replay, or
execution authority. Compatibility explanation remains fallback-visible.

## 1. Purpose

Batch G2-11 migrates human-facing explanation rendering toward the canonical semantic
source established by UBTR and CSA, while preserving deterministic compatibility
explanation content until parity is fully certified.

Explanation remains visibility-only. It does not approve, route, execute, invoke
providers, invoke workers, mutate governance, or mutate replay authority.

## 2. Runtime Change

The deterministic ACLI human-friendly explanation runtime now emits an
`EXPLANATION_RENDERING_COMPARISON_ARTIFACT_V1` inside replay-visible explanation
artifacts.

The comparison artifact records:

- CSA reference and hash when supplied;
- explanation rendering source;
- previous compatibility explanation hash and section set;
- CSA / Governance -> Human explanation projection;
- semantic equivalence result;
- semantic differences;
- section parity evidence;
- migration batch identifier;
- replay lineage;
- fallback status.

## 3. Explanation Rendering Migrated

CSA becomes the explanation rendering source only when:

- CSA lineage is supplied;
- Governance -> Human UBTR output is available;
- all required compatibility explanation sections remain present in the operator view;
- compatibility fallback remains visible;
- all renderer authority flags remain false.

When CSA lineage is absent, the runtime continues to expose UBTR Governance -> Human output
with compatibility fallback visible, but the G2-11 parity status records that CSA lineage
was not available.

## 4. Replay Comparison Evidence

Replay-visible G2-11 fields include:

- `explanation_rendering_source`;
- `explanation_rendering_comparison_artifact`;
- `explanation_rendering_comparison_hash`;
- `explanation_rendering_parity_status`;
- `explanation_rendering_migration_batch_id`;
- `canonical_semantic_artifact_reference`;
- `canonical_semantic_artifact_hash`;
- `explanation_rendering_fallback_status`.

Replay reconstruction exposes the same fields for downstream replay/hardening classifier
migration.

## 5. Preserved Boundaries

G2-11 preserves:

- governance authority;
- OCS authority;
- PPP authority;
- worker authority;
- provider authority;
- approval authority;
- replay authority;
- execution authorization boundaries;
- compatibility fallback.

Provider-assisted explanation remains advisory-only and subordinate to deterministic
explanation state.

## 6. Regression Coverage

Regression coverage added:

- CSA-primary explanation rendering when section parity is proven;
- compatibility fallback-visible rendering when CSA lineage is absent;
- replay reconstruction exposure of rendering source, comparison hash, parity status, and
  CSA hash;
- preservation of required operator guidance sections;
- preservation of provider, worker, approval, execution, governance, and replay
  non-authority flags.

Existing explanation tests continue to cover LLM-assisted explanation advisory-only
behavior and Governance -> Human translation replay.

## 7. Rollback Impact

Rollback is bounded:

- compatibility explanation remains recorded and visible;
- UBTR Governance -> Human output remains deterministic;
- removing G2-11 comparison fields restores the prior replay surface without changing
  rendered operator content;
- no authority-bearing workflow depends on G2-11 evidence.

## 8. Certification Impact

G2-11 certifies that explanation rendering can use CSA as canonical semantic source for
parity-proven sections while preserving deterministic compatibility output and all
Generation 1 authority boundaries.

This certification prepares replay, hardening, and replay-derived classifiers to consume
structured renderer provenance instead of deriving semantic meaning from rendered text.

## 9. Remaining Generation 2 Inventory

Remaining Generation 2 migration inventory after G2-11:

- replay, hardening, and replay-derived classifiers;
- provider-assisted and legacy classifier closure;
- compatibility retirement certification.

## 10. Final Verdict

```text
PLATFORM_SEMANTIC_GAP_CLOSURE_G2_11_READY
```
