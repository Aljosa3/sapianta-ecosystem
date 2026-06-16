# AIGOL_ERR_OCS_INTEGRATION_V1

Status: implemented integration milestone.

Purpose: prove that a real OCS workflow can request a capability, resolve a resource through ERR_V0, and preserve replay evidence without hardcoded provider routing.

## Current OCS Selection Point

The OCS end-to-end cognition workflow previously accepted direct `provider_contracts` in:

- `aigol/runtime/ocs_llm_cognition_end_to_end_runtime.py`

That made provider identity an external input to the OCS workflow. For legacy compatibility the direct-contract path remains available, but the new integration path allows OCS to operate from capability intent instead:

```text
OCS requests required_capability = reasoning
ERR_V0 resolves mock_provider
OCS derives a bounded cognition provider contract from that selection
OCS continues through existing provider cognition, availability, mode selection, comparison, and continuity stages
```

## Runtime Change

`run_ocs_llm_cognition_end_to_end(...)` now supports:

- `use_err_resource_lookup=True`
- `err_required_capability="reasoning"`
- optional `err_registry`

When enabled, OCS does not use caller-provided provider contracts. It asks ERR_V0 for an active `COGNITION_PROVIDER` with the requested capability. ERR records append-only selection evidence, and OCS derives its provider contract from the selected resource id.

## Replay Evidence

The OCS stage replay map now includes:

- `err_resource_selection`

ERR-enabled reconstruction exposes:

- `err_resource_selection_enabled`
- `err_selected_resource_id`
- `err_required_capability`
- `stage_replay["err_resource_selection"]`

The ERR replay evidence records that ERR did not invoke a provider, invoke a worker, orchestrate, mutate governance, or mutate replay.

## Boundary Preservation

This integration preserves:

- Human authority;
- OCS orchestration authority;
- provider cognition-only boundaries;
- worker non-invocation;
- fail-closed behavior;
- replay visibility;
- no real provider calls.

The test path uses `mock_provider` with a deterministic mock transport. `mock_filesystem_worker` remains registered in ERR_V0 as the execution-worker test resource, but OCS cognition does not invoke it.

## Evidence

Validation proves:

- OCS can request capability `reasoning`;
- ERR resolves `mock_provider`;
- OCS derives the provider contract from ERR selection;
- replay records ERR selection;
- OCS completes through the existing end-to-end cognition workflow;
- OCS fails closed when no active cognition provider matches the required capability.

## Remaining Gaps

This milestone does not migrate every OCS or worker-facing selection surface. It integrates ERR_V0 into the primary OCS LLM cognition workflow only.

Future bounded work may migrate worker-selection call sites to `mock_filesystem_worker` capability lookup where an OCS execution workflow explicitly requests an execution worker. That should remain separate from provider cognition lookup to preserve the provider/worker boundary.
