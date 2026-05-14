# Multimodal Provider Capability Model v1

`MULTIMODAL_PROVIDER_CAPABILITY_MODEL_V1` introduces the first provider capability governance model for SAPIANTA / AiGOL.

The model defines explicit provider capability declarations, modality classes, capability authority boundaries, admissibility rules, and replay-safe capability evidence.

It does not expand execution authority, enable multimodal execution, route providers, rank providers, invoke providers, retry execution, fallback execution, orchestrate work, or select providers autonomously.

## Invariants

- `CAPABILITY != AUTHORITY`
- `MODALITY != EXECUTION_PERMISSION`
- `PROVIDER_CAPABILITY != PROVIDER_INVOCATION`
- `CAPABILITY_MODEL != ROUTING`
- `CAPABILITY_MODEL != ORCHESTRATION`
