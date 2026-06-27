# UBTR Consumer Migration Batch 01 ACLI Routing V1

## Status

Implemented.

Final verdict:

UBTR_CONSUMER_MIGRATION_BATCH_01_READY

## Objective

Perform the first certified UBTR consumer migration for ACLI routing.

This batch replaces direct local semantic interpretation inside ACLI routing where parity has already been demonstrated, while retaining compatibility rollback.

## Scope

Migrated decisions:

1. Explicit governance artifact creation requests that already produce decisive Canonical Semantic Artifacts.
2. High-confidence deterministic development implementation requests that produce a decisive `DEVELOPMENT` Canonical Semantic Artifact targeting `GOVERNED_DEVELOPMENT_WORKFLOW`.

Not migrated:

- ambiguous development requests;
- low-confidence development requests;
- proposal-only OCS route selection;
- Product 1 routing;
- provider onboarding routing;
- native development context routing;
- HIRR clarification markers;
- generic execution-intent fail-closed detector;
- broad `_classify_workflow()` fallback.

## Runtime Changes

Updated:

`aigol/runtime/conversational_cli_runtime.py`

Changes:

- expanded `_classify_workflow_from_canonical_semantic_artifact()` to route deterministic `DEVELOPMENT` domain CSA artifacts with high confidence and no ambiguity to `GOVERNED_DEVELOPMENT_WORKFLOW`;
- gated CSA-primary routing on compatibility route parity so CSA becomes primary only when the previous local marker route already selects `GOVERNED_DEVELOPMENT_WORKFLOW`;
- preserved compatibility fallback for ambiguous or low-confidence CSA artifacts;
- preserved compatibility fallback for decisive CSA artifacts that do not have previous-route parity;
- added CSA-derived HIRR-compatible development intake metadata so existing route consumers remain stable;
- recorded previous compatibility route evidence for CSA-selected routes;
- recorded the migration batch identifier on CSA-selected decisions.

## Replay Evidence

For migrated CSA-selected route decisions, ACLI now records:

- `migration_batch_id`;
- `previous_routing_source`;
- `previous_compatibility_workflow_id`;
- `previous_compatibility_routing_status`;
- `previous_compatibility_confidence`;
- `previous_compatibility_matched_terms`;
- `new_csa_routing_source`;
- existing CSA replay reference;
- existing CSA artifact hash;
- existing UBTR semantic cognition decision.

This preserves rollback evidence and makes the migration auditable.

## Previous Routing Source

Previous source:

`LOCAL_COMPATIBILITY_MARKERS`

The previous compatibility route is evaluated as a parity gate before CSA routing is selected.

If compatibility evidence fails closed or selects a different workflow, CSA does not become primary for this batch. ACLI retains compatibility fallback and records CSA/UBTR evidence without assigning the migration batch identifier.

## New CSA Routing Source

New source:

`CANONICAL_SEMANTIC_ARTIFACT`

The CSA route is accepted only when:

- workflow candidate is `GOVERNED_DEVELOPMENT_WORKFLOW`;
- previous compatibility route evidence also selects `GOVERNED_DEVELOPMENT_WORKFLOW`;
- previous compatibility route status is `WORKFLOW_SELECTED`;
- clarification is not required;
- requested actions include `CREATE`, `UPDATE`, or `IMPLEMENT`;
- governance artifact requests satisfy the existing safe governance-artifact predicate; or
- development requests are high-confidence `DEVELOPMENT` domain requests.

## Compatibility Rollback

Compatibility fallback remains active.

Rollback options:

- disable or narrow the CSA branch;
- continue using `_classify_workflow()`;
- preserve existing replay fields;
- preserve previous compatibility route evidence for audit.

No replay schema migration is required for rollback.

## Governance Impact

No governance authority changed.

UBTR remains semantic authority only.

ACLI routing still does not:

- approve;
- authorize execution;
- invoke providers;
- invoke workers;
- mutate governance;
- mutate replay.

## Approval Impact

No approval boundary changed.

CSA routing may select the governed development workflow, but approval remains downstream and explicit.

## Provider Impact

No provider boundary changed.

UBTR does not select or invoke providers.

OCS remains provider-selection owner when cognition is required.

## Worker Impact

No worker boundary changed.

No worker invocation occurs during ACLI route selection.

## Regression Coverage

Updated:

`tests/test_universal_translation_runtime_integration_v1.py`

Coverage verifies:

- explicit governance artifact prompts route through CSA;
- previous local marker route evidence is recorded;
- deterministic development implementation prompt routes through CSA;
- deterministic CSA development prompts without local route parity retain compatibility fallback;
- CSA-derived HIRR-compatible intake remains present;
- ambiguous development and governance prompts retain compatibility fallback;
- providers are not invoked;
- workers are not invoked.

Existing ACLI routing tests remain unchanged and pass.

## Validation Evidence

Executed:

```bash
python -m py_compile aigol/runtime/conversational_cli_runtime.py
```

Result:

Passed.

Executed:

```bash
python -m pytest tests/test_universal_translation_runtime_integration_v1.py tests/test_conversational_cli_runtime_v1.py -q
```

Result:

`158 passed`

Additional final validation shall include:

- broader ACLI/UBTR routing tests;
- full pytest;
- `git diff --check`.

## Remaining Migration Work

Remaining ACLI routing migration work:

1. proposal-only OCS route selection;
2. HIRR marker interpretation;
3. generic execution-intent fail-closed detector;
4. Product 1 routing;
5. provider onboarding routing;
6. native development context routing;
7. broad local workflow semantic parsing;
8. compatibility fallback retirement certification.

## Final Verdict

UBTR_CONSUMER_MIGRATION_BATCH_01_READY
