# Multimodal Provider Capability Model v1

`MULTIMODAL_PROVIDER_CAPABILITY_MODEL_V1` defines replay-safe provider capability declarations before future execution expansion.

Capabilities are explicit governance metadata. They do not grant execution authority, bypass execution envelopes, bypass provider abstraction, enable routing, enable orchestration, or enable autonomous provider selection.

## Invariants

- `CAPABILITY != AUTHORITY`
- `MODALITY != EXECUTION_PERMISSION`
- `PROVIDER_CAPABILITY != PROVIDER_INVOCATION`
- `CAPABILITY_MODEL != ROUTING`
- `CAPABILITY_MODEL != ORCHESTRATION`
