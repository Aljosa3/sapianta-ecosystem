# G14_44_CERTIFIED_PROVIDER_ATTACHMENT_V1

## Executive Summary

G14.44 establishes the Certified Provider Attachment as the canonical Platform Core boundary for external cognition provider access.

The implementation adds:

```text
aigol.provider.certified_provider_attachment.run_certified_provider_attachment(...)
```

All production provider invocation call sites now delegate through this certified attachment API. The existing Provider Platform runtime remains the internal engine responsible for registry lookup, provider readiness, adapter validation, transport invocation, diagnostics, fail-closed capture, and replay evidence.

Final verdict:

```text
CERTIFIED_PROVIDER_ATTACHMENT_CERTIFIED
```

## Architectural Invariant

The certified provider access chain is now:

```text
Human Interface
  -> Platform Core
  -> Certified Provider Attachment
  -> Provider Platform
  -> Provider Transport
  -> External Provider
```

No Human Interface owns provider access.

No Platform Core runtime component invokes provider transport directly.

No external cognition provider is reached without the Certified Provider Attachment boundary.

## Implementation

### New Canonical Attachment API

Implemented:

```text
aigol/provider/certified_provider_attachment.py
```

The canonical API is:

```text
run_certified_provider_attachment(...)
```

It delegates to the existing Provider Platform runtime:

```text
run_provider_attachment(...)
```

The underlying runtime continues to own:

- provider registration lookup
- provider readiness
- adapter validation
- request validation
- adapter invocation
- transport diagnostics
- fail-closed replay capture
- provider proposal replay reconstruction

The certified wrapper adds a stable certification artifact to each capture:

```text
certified_provider_attachment
```

It is also persisted beside provider attachment evidence:

```text
002_certified_provider_attachment_recorded.json
```

The artifact records canonical ownership for:

- request construction
- request metadata
- transport invocation
- response normalization
- provider diagnostics
- failure normalization
- retry entry
- provider evidence generation

### Production Call Site Migration

Production call sites were migrated from the internal Provider Platform engine to the certified attachment API:

```text
run_provider_attachment(...)
```

to:

```text
run_certified_provider_attachment(...)
```

Updated runtime surfaces include:

- provider proposal production
- provider proposal repair and retry
- provider-assisted intent classification
- provider-assisted conversation
- domain execution binding
- first real implementation generation epoch
- multi-provider competitive proposal runtime
- governed CLI operation provider path
- conversational OCS cognition provider path

The internal `run_provider_attachment(...)` function remains only inside the Provider Platform and the certified attachment wrapper.

## Provider Responsibility Audit

| Responsibility | Canonical Owner |
| --- | --- |
| Provider attachment entry | Certified Provider Attachment |
| Request construction boundary | Certified Provider Attachment |
| Request metadata boundary | Certified Provider Attachment |
| Provider registry lookup | Provider Platform |
| Provider readiness | Provider Platform |
| Adapter validation | Provider Platform |
| Transport invocation | Certified Provider Attachment through Provider Platform |
| Response normalization | Certified Provider Attachment boundary through Provider Platform/adapters |
| Provider diagnostics | Certified Provider Attachment boundary through Provider Platform |
| Failure normalization | Certified Provider Attachment boundary through Provider Platform |
| Retry entry | Certified Provider Attachment boundary |
| Replay evidence | Provider Platform under certified attachment boundary |

## Regression Evidence

Added:

```text
tests/test_g14_44_certified_provider_attachment_v1.py
```

Regression coverage proves:

- certified attachment wraps the Provider Platform runtime;
- provider captures include the certified attachment artifact;
- provider replay includes `002_certified_provider_attachment_recorded.json`;
- request construction ownership is recorded at the certified boundary;
- response normalization ownership is recorded at the certified boundary;
- provider diagnostics ownership is recorded at the certified boundary;
- failure normalization ownership is recorded at the certified boundary;
- retry entry ownership is recorded at the certified boundary;
- provider evidence ownership is recorded at the certified boundary;
- no production runtime or CLI module calls `run_provider_attachment(...)` directly outside the internal Provider Platform and certified wrapper.

Updated an existing domain execution binding source-inspection test to require the certified attachment API rather than the raw Provider Platform engine.

## Runtime Validation

Real runtime validation was performed through both current Human Interfaces:

```text
./aicli
python -m aigol.cli.aigol_cli next
```

Both were validated with an ordinary development request:

```text
Implement governance validation utility.
```

Expected lifecycle:

```text
Platform Core
  -> Certified Provider Attachment
  -> Provider Platform
  -> External Provider
  -> Worker Platform
  -> Result Validation
  -> Replay Certification
```

Validation evidence confirmed:

- canonical runtime entered;
- provider invocation reached;
- worker execution reached;
- result validation completed;
- replay certification completed;
- Human Interfaces remained thin adapters;
- Platform Core orchestration remained unchanged.

## Ownership Verification

| Component | Status |
| --- | --- |
| Human Interfaces | unchanged; presentation only |
| Runtime Entry | unchanged |
| Project Services | unchanged |
| Development Intent Resolution | unchanged |
| Platform Core orchestration | unchanged |
| Certified Provider Attachment | new canonical provider boundary |
| Provider Platform | internal provider attachment runtime preserved |
| Governance | unchanged |
| Worker Platform | unchanged |
| Replay | unchanged |

No provider authority moved into Human Interfaces.

No governance authority moved into Provider Platform.

No worker execution authority moved into the provider adapter.

## Provider Independence

The certified attachment API accepts a `ProviderRegistry` and `ProviderAdapter`.

That preserves provider independence for:

- OpenAI
- Claude
- Gemini
- Mistral
- Llama
- future providers

Adding a provider requires implementing a compatible provider adapter and registering provider metadata. Platform Core orchestration does not need provider-specific changes.

## Validation

Validation performed:

```text
python -m py_compile ...
python -m pytest -q tests/test_g14_44_certified_provider_attachment_v1.py
python -m pytest -q tests/test_provider_proposal_production_runtime_v1.py tests/test_minimal_provider_attachment_runtime_v1.py tests/test_openai_provider_failure_diagnostics_v1.py tests/test_g14_22_reference_unified_human_interface_v1.py tests/test_domain_execution_binding_runtime_v1.py tests/test_first_real_implementation_generation_epoch_v1.py tests/test_multi_provider_competitive_proposal_runtime_v1.py tests/test_g14_44_certified_provider_attachment_v1.py
python -m pytest -q
git diff --check
```

Real provider validation was performed with network access available because the default sandbox blocks outbound OpenAI transport.

## Certification Summary

The Certified Provider Attachment is now the single production-facing provider invocation boundary.

Provider transport behavior remains isolated behind a stable Platform Core attachment layer.

Final verdict:

```text
CERTIFIED_PROVIDER_ATTACHMENT_CERTIFIED
```
