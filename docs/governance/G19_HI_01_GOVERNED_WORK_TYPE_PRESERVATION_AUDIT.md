# G19-HI-01 Governed Work-Type Preservation Audit

Status: audit-only.

Final verdict: `WORK_TYPE_PRESERVATION_REMEDIATION_REQUIRED`.

This audit examines the observed G19-07 `./aicli` behavior where an explicitly non-mutating audit request was preserved as text but converted into governed implementation work during clarification resolution and approval preparation.

No runtime behavior is modified by this artifact.

## Scope

Lifecycle under audit:

Human Interface input -> Human Intent Resolution -> clarification lifecycle -> clarification aggregation -> governed work preparation -> approval summary -> runtime continuation.

Work-type constraints under audit:

- `work_type: AUDIT_ONLY`
- `mutation_allowed: false`
- `runtime_implementation: false`
- explicit instruction not to implement or modify runtime behavior
- explicit instruction not to convert the request into implementation work

## Required Runtime Evidence

The observed evidence confirms that the original request was not textually lost.

Evidence artifact:

`.runtime/aicli/AICLI-REFERENCE-SESSION/uhi_project_services/170_uhi_project_context_recorded.json`

- artifact hash: `sha256:73075dc30ea07ed429f31f88ccaf5ae29baa36389ade02624018d2821e895835`
- message hash: `sha256:fb3f79bf5a87c1fd54339cf89a61ce94c1f3bb7eccd70d161057e71e64ada9eb`
- response mode: `CLARIFICATION`
- summary admissible: `False`
- runtime binding admissible: `False`
- knowledge classification: `NEW_GOVERNED_WORK`
- preserved request text includes:
  - `This is an AUDIT-ONLY governance task.`
  - `Do not implement or modify runtime behavior.`
  - `Preserve the original work type as AUDIT_ONLY throughout clarification, approval preparation, and governed continuation.`
  - `Do not convert this request into implementation work.`

The clarification was accepted and produced an approval preparation artifact.

Evidence artifact:

`.runtime/aicli/AICLI-REFERENCE-SESSION/uhi_project_services/171_uhi_project_context_recorded.json`

- artifact hash: `sha256:767627a025ff9fc9f173b5068d9ac8457408f158f913fbc99cdf39cc11630ef8`
- message hash: `sha256:6465ca0d5c2890217e8b6970e074c5f7486d234331448b97ed8590f4c531893a`
- clarification status: `CLARIFICATION_RESOLVED`
- clarification resolved: `True`
- reply resolution source: `ORIGINAL_REQUEST_WITH_BOUND_CLARIFICATION_REPLY`
- response mode: `APPROVAL_PREPARATION`
- summary admissible: `True`
- runtime binding admissible: `True`
- runtime after approval: `CERTIFIED_PLATFORM_CORE_RUNTIME`
- approval state: `PENDING_HUMAN_APPROVAL`

The approval summary preserved the original text but nevertheless converted the action into implementation:

- `raw_prompt` contains `AUDIT_ONLY` and the non-mutation instructions.
- `approval_summary.original_request` contains `AUDIT_ONLY` and the non-mutation instructions.
- `approval_summary.canonical_runtime_prompt` contains the original text, but wraps it with:
  - `Implement the clarification-resolved governed development request.`
  - `Implement as a governed development workflow.`

This is the core failure: `AUDIT_ONLY` was preserved as string evidence but not preserved as authoritative work-type metadata.

## Deterministic Root Cause

`AUDIT_ONLY` is not lost as text. It is ignored as a semantic boundary.

The first destructive conversion occurs in `clarification_resolved_development_request` in `aigol/runtime/platform_core_project_services.py`.

That function reconstructs the post-clarification request with fixed implementation phrases:

- `Implement the clarification-resolved governed development request.`
- `Implement as a governed development workflow.`

These phrases are hard-coded. They are not produced by Human Interface rendering and are not inferred from the clarification answer.

After that reconstruction, `resolve_development_intent` evaluates the combined prompt as development intent. The artifact it returns contains `raw_prompt`, `governed_request`, `canonical_runtime_prompt`, `summary_admissible`, and `runtime_binding_admissible`, but it does not contain canonical fields for:

- `work_type`
- `mutation_allowed`
- `runtime_implementation`
- original work-type source evidence
- work-type conflict status

Approval preparation then treats `summary_admissible=True` as sufficient to create a `GOVERNED_IMPLEMENTATION_SUMMARY`, set `runtime_after_approval` to `CERTIFIED_PLATFORM_CORE_RUNTIME`, and mark approval as pending.

The resulting failure is deterministic:

1. clarification preserves the original text;
2. clarification resolution wraps that text in implementation wording;
3. intent resolution has no immutable work-type guard;
4. approval preparation has no work-type conflict check;
5. runtime continuation consumes the admissible canonical prompt.

## Is `NEW_GOVERNED_WORK` Incorrectly Mapped To Implementation?

`NEW_GOVERNED_WORK` is currently a knowledge reuse classification, not a work type.

The fallback classification is assigned when no deterministic workspace match is found. It sets:

- `classification = "NEW_GOVERNED_WORK"`
- `new_work_required = True`
- `reuse_recommended = False`

That classification does not distinguish audit, implementation, review, or certification work. In the observed flow it contributes to the broader governed development path, but the direct implementation conversion is caused by the clarification-resolved prompt builder and the summary/runtime admissibility path.

Conclusion:

`NEW_GOVERNED_WORK` should not imply implementation. It should remain a knowledge reuse result unless paired with an explicit immutable work type such as `IMPLEMENTATION`.

## Current Work-Type Support

The audited path does not currently expose first-class support for these work types:

- `AUDIT_ONLY`
- `IMPLEMENTATION`
- `REVIEW`
- `CERTIFICATION`

Instead, it supports implicit development categories:

- goal-oriented request
- guided development request
- continuation development request
- collaborative development request
- native development prompt

It also supports knowledge reuse classifications:

- `ALREADY_SATISFIED`
- `RELATES_TO_CERTIFIED_CAPABILITY`
- `MODIFIES_EXISTING_CAPABILITY`
- `EXTENDS_EXISTING_MILESTONE`
- `NEW_GOVERNED_WORK`

These are useful but insufficient. They classify reuse and development shape, not mutability or work type.

## Canonical Ownership

`work_type` should be owned by Platform Core, not by Human Interfaces.

Canonical owner:

`PLATFORM_CORE_DEVELOPMENT_INTENT_RESOLUTION_ARTIFACT_V1`

Required immutable fields:

- `work_type`
- `work_type_source`
- `work_type_source_text`
- `mutation_allowed`
- `runtime_implementation`
- `work_type_change_allowed`
- `work_type_conflict_detected`
- `work_type_conflict_reason`

The active clarification state should carry the same fields forward so clarification can refine missing details without changing the work type.

Approval summary should mirror the resolved work type and fail closed when the prepared runtime action conflicts with it.

Runtime entry should consume only work-type-consistent admissible prompts.

## Ownership Map

| Layer | Current role | Required role |
| --- | --- | --- |
| Human Interface | Captures input, renders Platform Core output, requests approval | Remain thin; must not infer or repair work type |
| Human Intent Resolution | Detects development intent and canonical runtime prompt | Own immutable work-type extraction and conflict detection |
| Clarification lifecycle | Preserves original text and binds clarification reply | Preserve original work type as immutable clarification state |
| Clarification aggregation | Builds clarification-resolved request | Compose without changing work type or injecting implementation verbs for non-implementation work |
| Knowledge Reuse | Classifies reuse/new governed work | Remain reuse classification only; must not imply implementation |
| Governed work preparation | Builds approval summary | Fail closed on work-type/runtime-action conflict |
| Runtime continuation | Uses admissible canonical prompt | Refuse runtime entry when work type is non-mutating or conflicted |
| Governance evidence | Records replay-safe artifacts | Certify work-type preservation and conflict evidence |

## Lifecycle Map

### Current Lifecycle

1. Human submits `AUDIT_ONLY` request through `aicli`.
2. `aicli` delegates to `prepare_unified_human_interface_project_context`.
3. Platform Core records the original request and asks clarification.
4. Human clarification is accepted.
5. `clarification_resolved_development_request` constructs a new prompt with hard-coded implementation instructions.
6. `resolve_development_intent` treats the resolved prompt as native governed development.
7. Human Conversation Experience prepares a governed implementation summary.
8. Approval summary sets `runtime_after_approval` to `CERTIFIED_PLATFORM_CORE_RUNTIME`.
9. Runtime entry later consumes `canonical_runtime_prompt` when `runtime_binding_admissible=True`.

### Required Lifecycle

1. Human submits a request.
2. Platform Core extracts immutable `work_type` and mutability fields.
3. Clarification may fill missing target/outcome information.
4. Clarification resolution carries original `work_type` forward unchanged.
5. Governed preparation compares requested work type with generated action.
6. If action and work type conflict, approval preparation fails closed.
7. Runtime continuation occurs only when work type authorizes it.

## Affected Artifacts And Functions

Primary affected functions:

- `aigol/runtime/platform_core_project_services.py::clarification_resolved_development_request`
- `aigol/runtime/platform_core_project_services.py::resolve_development_intent`
- `aigol/runtime/platform_core_project_services.py::canonical_development_runtime_prompt`
- `aigol/runtime/platform_core_project_services.py::_conversation_approval_summary`
- `aigol/runtime/human_interface_runtime_entry_service.py::run_human_interface_runtime_entry`

Human Interface evidence:

- `aigol/cli/aicli.py::_submit_composed_request` delegates to Platform Core and renders the returned summary.
- `aigol/cli/aicli.py::_summary_from_conversation` copies the Platform Core approval summary.

This confirms that `aicli` is not the root cause. It does not convert `AUDIT_ONLY` into implementation. The conversion happens inside Platform Core.

## Fixed Phrase Determination

The phrases are hard-coded in `clarification_resolved_development_request`:

- `Implement the clarification-resolved governed development request.`
- `Implement as a governed development workflow.`

Related broad defaulting also exists in `canonical_development_runtime_prompt`, where guided or continuation development prompts may receive:

- `Implement as a native development governance workflow.`
- `Implement as a governed development workflow.`

For the G19-07 observed artifact, the direct source of the two exact phrases is the clarification-resolved request builder.

## Reuse Opportunities

The correction can reuse existing Platform Core capabilities:

- Human Intent Resolution as the canonical semantic owner.
- Clarification state and clarification replay binding for immutable propagation.
- Human Conversation Experience for fail-closed user-facing responses.
- Knowledge Reuse for reuse classification, kept separate from work type.
- Runtime entry admissibility flags for blocking conflicted runtime continuation.
- Replay evidence and artifact hashes for certification.
- Platform Presentation Layer for rendering a unified conflict response without interface-specific logic.

No second semantic interpretation layer is needed.

## Minimal Correction Plan

1. Add deterministic work-type extraction to Platform Core intent resolution.
2. Persist `work_type`, `mutation_allowed`, and `runtime_implementation` in the development intent artifact.
3. Carry those fields into active clarification state.
4. Update clarification resolution so it does not inject implementation wording for non-implementation work.
5. Add approval summary validation that compares original work type with generated canonical action.
6. Fail closed when:
   - `work_type=AUDIT_ONLY` and generated action is implementation;
   - `mutation_allowed=false` and runtime continuation would mutate;
   - `runtime_implementation=false` and `runtime_after_approval` is a runtime implementation path.
7. Ensure `NEW_GOVERNED_WORK` remains reuse classification only.
8. Add focused regression tests for all supported work types.

## Regression Scenarios

Required regression coverage:

1. `AUDIT_ONLY` request without clarification remains non-mutating and cannot produce implementation approval.
2. `AUDIT_ONLY` request with clarification keeps `work_type=AUDIT_ONLY` after reply aggregation.
3. `AUDIT_ONLY` request whose generated prompt contains `Implement` fails closed before approval.
4. `mutation_allowed=false` blocks runtime binding even when development intent is otherwise detected.
5. `runtime_implementation=false` blocks `runtime_after_approval=CERTIFIED_PLATFORM_CORE_RUNTIME`.
6. `IMPLEMENTATION` request may produce governed implementation summary when explicit and admissible.
7. `REVIEW` request produces review-appropriate preparation and does not mutate.
8. `CERTIFICATION` request routes to certification semantics and does not default to implementation.
9. Human explicitly changes `work_type` during clarification; Platform Core records the explicit change and recomputes admissibility.
10. `NEW_GOVERNED_WORK` classification alone never authorizes implementation.

## Certification Readiness

Current status:

`NOT_CERTIFICATION_READY`

Reason:

Platform Core preserves the original non-mutating instruction as replay evidence, but it does not preserve `work_type` as an immutable canonical semantic field. Approval preparation can therefore conflict with the original work type while still becoming runtime-admissible.

Certification blockers:

- no canonical `work_type` field in the development intent artifact;
- no immutable propagation through clarification state;
- hard-coded implementation language in clarification aggregation;
- no approval summary work-type conflict check;
- no runtime entry guard for non-mutating work types;
- no regression tests for `AUDIT_ONLY`, `REVIEW`, or `CERTIFICATION` preservation.

Certification can proceed only after regression evidence demonstrates:

- clarification refines intent but does not change work type;
- `AUDIT_ONLY` requests remain non-mutating through approval and execution boundaries;
- approval is blocked when prepared work conflicts with original work type;
- Human Interfaces remain thin adapters and do not locally repair Platform Core semantics.

## Final Determination

Platform Core can guarantee governed work-type preservation with a small, deterministic correction.

The required fix is not a Human Interface change. It is a Platform Core semantic continuity change:

- make `work_type` a first-class immutable field;
- preserve it through clarification;
- validate approval preparation against it;
- fail closed on conflict;
- keep `NEW_GOVERNED_WORK` separate from implementation authorization.

Final verdict:

`WORK_TYPE_PRESERVATION_REMEDIATION_REQUIRED`
