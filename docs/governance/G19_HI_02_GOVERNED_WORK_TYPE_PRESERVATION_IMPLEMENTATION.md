# G19-HI-02 Governed Work-Type Preservation Implementation

Status: implemented.

Implementation verdict: `WORK_TYPE_PRESERVATION_REMEDIATION_IMPLEMENTED`.

## Scope

This implementation remediates the G19-HI-01 finding that clarification aggregation could preserve `AUDIT_ONLY` as text while silently converting the effective governed work type into implementation work.

The correction is Platform Core-owned. Human Interfaces remain thin adapters that transport input, render Platform Core output, and persist Platform Core metadata without interpreting work type locally.

## Implemented Controls

- Added canonical governed work-type metadata in Platform Core intent resolution.
- Supported explicit work types:
  - `AUDIT_ONLY`
  - `IMPLEMENTATION`
  - `REVIEW`
  - `CERTIFICATION`
  - `ANALYSIS`
  - `DOCUMENTATION`
- Added replay-visible fields:
  - `requested_work_type`
  - `work_type`
  - `prepared_work_type`
  - `work_type_source`
  - `work_type_source_text`
  - `mutation_allowed`
  - `runtime_implementation`
  - `work_type_change_allowed`
  - `work_type_conflict_detected`
  - `work_type_conflict_reason`
  - `knowledge_reuse_classification_is_work_type`
- Preserved active clarification work type during replay-backed clarification continuation.
- Removed implementation-specific aggregation wording for non-implementation work types.
- Blocked `summary_admissible` and `runtime_binding_admissible` whenever non-mutating work would enter implementation runtime.
- Preserved `NEW_GOVERNED_WORK` as knowledge reuse classification only.

## Boundary Preservation

Human Interface behavior remains bounded:

- `aicli` and `aigol next` pass through Platform Core work-type metadata in pending clarification state.
- Human Interfaces do not infer work type.
- Human Interfaces do not repair work-type conflicts.
- Runtime continuation remains controlled by Platform Core `runtime_binding_admissible`.

## Runtime Guard

The canonical runtime entry service already filters runtime prompts by `runtime_binding_admissible`.

G19-HI-02 makes non-mutating or conflicted work set:

- `summary_admissible: false`
- `runtime_binding_admissible: false`
- `runtime_implementation: false`

Therefore `AUDIT_ONLY`, `REVIEW`, `CERTIFICATION`, `ANALYSIS`, and `DOCUMENTATION` requests do not enter certified implementation runtime unless Platform Core receives an explicit implementation work type and the prepared action matches it.

## Validation

Regression coverage added:

`tests/test_g19_hi_02_governed_work_type_preservation.py`

Validated scenarios:

- `AUDIT_ONLY` implementation-shaped prompt fails closed before approval.
- `AUDIT_ONLY` survives clarification aggregation without runtime entry.
- `IMPLEMENTATION` remains eligible for governed implementation approval.
- `REVIEW`, `CERTIFICATION`, `ANALYSIS`, and `DOCUMENTATION` are preserved as non-mutating work.
- Runtime entry refuses non-mutating work types.
- `NEW_GOVERNED_WORK` does not imply implementation.

Executed validation:

```bash
python -m pytest tests/test_g19_hi_02_governed_work_type_preservation.py
python -m pytest tests/test_g14_22_reference_unified_human_interface_v1.py tests/test_g15_aicli_03_persistent_platform_conversation_session.py tests/test_g14_30_canonical_human_interface_runtime_entry_service_v1.py tests/test_g14_40_platform_core_conversation_ownership_completion_v1.py tests/test_g14_47_human_intent_to_capability_resolution_v1.py
```

Observed result:

- `6 passed`
- `31 passed`

## Known Boundary

This implementation preserves explicit work-type declarations and defaults legacy governed development requests to `IMPLEMENTATION` for compatibility with existing certified UHI behavior.

Changing an already-open clarification from one work type to another remains blocked by `work_type_change_allowed: false`. A future governed change may add explicit human work-type-change approval semantics if needed.
