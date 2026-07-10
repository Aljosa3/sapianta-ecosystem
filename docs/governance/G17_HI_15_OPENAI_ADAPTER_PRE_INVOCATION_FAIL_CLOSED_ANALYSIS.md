# G17-HI-15 OpenAI Adapter Pre-Invocation Fail-Closed Analysis

## Executive Summary

This audit identifies the exact implementation transition that records:

```text
provider_invoked_inside_adapter = true
provider_invoked = false
provider_status = FAILED_CLOSED
failure_stage = openai_provider_adapter
failure_reason = OpenAI provider unavailable
```

The transition is not produced by Platform Core, Human Interface, Runtime Entry, Worker Runtime, Governance, Replay, or Central Provider Platform ownership. It is produced inside the certified provider attachment failure path after the OpenAI adapter invocation path raises a fail-closed exception before a successful provider proposal envelope is created.

The exact branch responsible for the outer `provider_invoked = false` value is:

```text
aigol/provider/provider_runtime.py
run_provider_attachment(...)
except Exception as exc
-> _failed_envelope(...)
-> "provider_invoked": False
```

The exact adapter branch responsible for the observed `failure_stage = openai_provider_adapter` classification is:

```text
aigol/provider/providers/openai_provider.py
OpenAIProviderAdapter._call_openai(...)
except Exception as exc:
    raise FailClosedRuntimeError("OpenAI provider unavailable") from exc
```

The replay does not show a readiness, credential, provider identity, registry, or configuration defect. It shows a fail-closed adapter-level client exception normalized to `OpenAI provider unavailable`, followed by the certified provider attachment deliberately emitting a failed envelope with `provider_invoked = false`.

Final verdict: `PRE_INVOCATION_FAIL_CLOSED_EXPECTED`.

## Adapter Entry Analysis

The OpenAI external Worker adapter reaches the certified provider boundary.

Implementation evidence:

- `aigol/runtime/openai_external_worker_provider_adapter.py` lines 72-99 calls `run_certified_provider_attachment(...)`.
- The call supplies `provider_id=OPENAI_PROVIDER_ID`, an OpenAI registry, and an `OpenAIProviderAdapter(...)`.
- `aigol/provider/certified_provider_attachment.py` lines 26-61 delegates to `run_provider_attachment(...)` and then records the certified provider attachment artifact.

Replay evidence:

- `.runtime/aicli/AICLI-REFERENCE-SESSION/TURN-000019/.../openai_external_worker_provider/001_openai_provider_adapter_recorded.json` records `artifact_type=OPENAI_EXTERNAL_WORKER_PROVIDER_CAPTURE_ARTIFACT_V1`.
- The same artifact records `provider_attachment_boundary=CERTIFIED_PROVIDER_ATTACHMENT`.
- The nested certification records `certified_provider_attachment_api=run_certified_provider_attachment`.

Conclusion:

Adapter entry and certified provider attachment entry are reached deterministically.

## Invocation Decision Analysis

There are two separate invocation fields in this trace.

`provider_invoked_inside_adapter=True` is recorded by the external Worker adapter capture artifact:

```text
aigol/runtime/openai_external_worker_provider_adapter.py lines 262-291
```

Specifically, `_provider_capture_artifact(...)` sets:

```text
provider_status = "COMPLETED" if completed else FAILED_CLOSED
provider_capture = deepcopy(provider_capture)
provider_invoked_inside_adapter = True
```

The `completed` condition is stricter:

```text
aigol/runtime/openai_external_worker_provider_adapter.py lines 251-256
```

It requires:

- `created.get("provider_invoked") is True`;
- returned event type is `PROVIDER_PROPOSAL_RETURNED`;
- response text exists and is non-empty.

`provider_invoked=False` is recorded by the certified provider attachment failed envelope:

```text
aigol/provider/provider_runtime.py lines 225-260
```

Specifically, `_failed_envelope(...)` sets:

```text
event_type = FAILED_CLOSED
provider_status = FAILED_CLOSED
response = None
proposal_hash = FAILED_CLOSED
provider_invoked = False
```

Success would instead use `_created_replay(...)`, which sets `provider_invoked=True` only after `adapter.generate_proposal(...)` returns a valid envelope:

```text
aigol/provider/provider_runtime.py lines 81-91
aigol/provider/provider_runtime.py lines 171-193
```

Conclusion:

The transition is replay-consistent. `provider_invoked_inside_adapter=True` means the OpenAI external Worker adapter reached and recorded the certified provider attachment capture. `provider_invoked=False` means the provider attachment did not receive a successful provider proposal envelope.

## Exception Path Analysis

The OpenAI provider adapter invocation sequence is:

```text
OpenAIProviderAdapter.generate_proposal(...)
-> _resolve_api_key(...)
-> _extract_prompt(...)
-> _create_openai_payload(...)
-> _call_openai(...)
```

Implementation evidence:

- `aigol/provider/providers/openai_provider.py` lines 70-75 resolves the key, extracts prompt data, creates payload, and calls `_call_openai(...)`.
- `_call_openai(...)` validates that `self._client` is callable at lines 111-113.
- `_call_openai(...)` invokes the configured client at lines 114-120.
- `_call_openai(...)` preserves already fail-closed runtime errors at lines 121-122.
- `_call_openai(...)` normalizes other client exceptions at lines 123-124:

```text
except Exception as exc:
    raise FailClosedRuntimeError("OpenAI provider unavailable") from exc
```

Diagnostic evidence:

- `provider_runtime._failure_diagnostics(...)` builds diagnostics at `aigol/provider/provider_runtime.py` lines 429-439.
- `_diagnostic_exception(...)` unwraps direct HTTP, URL, timeout, or JSON decode causes at lines 442-446.
- `_failure_stage(...)` records `openai_http_request` for direct HTTP/URL/timeout/JSON causes at lines 449-451.
- `_failure_stage(...)` records `openai_provider_adapter` when the exception is a `FailClosedRuntimeError` whose message starts with `OpenAI provider` at lines 452-453.

Observed replay evidence:

```text
failure_reason = OpenAI provider unavailable
failure_stage = openai_provider_adapter
exception_type = FailClosedRuntimeError
transport_failure_category = FAIL_CLOSED
http_status = null
```

Conclusion:

The observed runtime classification points to the adapter-level generic exception normalization branch in `OpenAIProviderAdapter._call_openai(...)` lines 123-124. If the failure had been a directly unwrapped `HTTPError`, `URLError`, `TimeoutError`, or `JSONDecodeError`, the provider runtime would have recorded `failure_stage=openai_http_request` instead.

## FAIL_CLOSED Decision Analysis

The fail-closed decision is made in `run_provider_attachment(...)`.

Implementation evidence:

- `aigol/provider/provider_runtime.py` lines 64-91 is the success path.
- The success path reaches `_created_replay(...)` only after a validated provider proposal envelope exists.
- `aigol/provider/provider_runtime.py` lines 92-112 catches exceptions from registry lookup, readiness, adapter validation, request validation, adapter invocation, response extraction, or envelope validation.
- The exception path calls `_failed_envelope(...)` at lines 95-103.
- `_failed_envelope(...)` records `provider_invoked=False` at line 249.
- `_failed_returned(...)` records `provider_invoked=False` at line 280.
- `certified_provider_attachment._certification_artifact(...)` records `provider_invoked` as `created.get("provider_invoked") is True` at `aigol/provider/certified_provider_attachment.py` line 84.

The branch is therefore:

```text
OpenAIProviderAdapter._call_openai(...)
-> raises FailClosedRuntimeError("OpenAI provider unavailable")
-> run_provider_attachment(...) except Exception as exc
-> _failed_envelope(...)
-> provider_invoked = False
-> _failed_returned(...)
-> provider_invoked = False
-> certified_provider_attachment.provider_invoked = False
```

Conclusion:

The branch intentionally suppresses successful-provider evidence when no successful provider proposal envelope exists. It does not suppress a successful external provider response; no response artifact exists in this trace.

## Replay Consistency Analysis

The replay fields are internally consistent.

Runtime evidence from TURN-000019:

- `certified_provider_attachment/000_provider_readiness_recorded.json`
  - `readiness_status=READY`
  - `api_key_present=true`
  - `provider_configuration_valid=true`
  - `model_configuration_valid=true`
  - `transport_available=true`
  - `provider_activation_ready=true`
  - `provider_invocation_allowed=true`
  - `provider_invoked=false`

- `certified_provider_attachment/000_provider_proposal_created.json`
  - `event_type=FAILED_CLOSED`
  - `provider_status=FAILED_CLOSED`
  - `provider_version=UNKNOWN`
  - `response=null`
  - `proposal_hash=FAILED_CLOSED`
  - `provider_invoked=false`
  - `failure_reason=OpenAI provider unavailable`
  - `failure_stage=openai_provider_adapter`
  - `transport_failure_category=FAIL_CLOSED`

- `certified_provider_attachment/001_provider_proposal_returned.json`
  - `event_type=FAILED_CLOSED`
  - `provider_invoked=false`
  - `failure_reason=OpenAI provider unavailable`
  - `failure_stage=openai_provider_adapter`

- `certified_provider_attachment/002_certified_provider_attachment_recorded.json`
  - `provider_invoked=false`
  - `provider_status=FAILED_CLOSED`
  - `failure_reason=OpenAI provider unavailable`
  - `failure_stage=openai_provider_adapter`

- `001_openai_provider_adapter_recorded.json`
  - `provider_status=FAILED_CLOSED`
  - `provider_invoked_inside_adapter=true`
  - nested provider capture records `provider_invoked=false`
  - `raw_provider_response_hash=null`
  - `raw_provider_response_text=""`
  - `failure_reason=OpenAI provider unavailable`

- `002_openai_external_worker_result_recorded.json`
  - `execution_status=FAILED_CLOSED`
  - `execution_outcome=FAILED_CLOSED`
  - `failure_reason=OpenAI provider unavailable`

TURN-000021 records the same deterministic pattern: readiness succeeds, adapter capture records `provider_invoked_inside_adapter=true`, certified provider attachment records `provider_invoked=false`, and the Worker result fails closed with `OpenAI provider unavailable`.

Conclusion:

Replay is consistent with a failed adapter-level invocation path before successful provider proposal creation.

## Root Cause

Root cause:

```text
OpenAIProviderAdapter._call_openai(...)
adapter-level generic client exception normalization
```

Exact source branch:

```text
aigol/provider/providers/openai_provider.py lines 123-124
```

Exact outer replay transition branch:

```text
aigol/provider/provider_runtime.py lines 92-112
aigol/provider/provider_runtime.py lines 225-260
```

The observed `failure_stage=openai_provider_adapter`, `exception_type=FailClosedRuntimeError`, and `transport_failure_category=FAIL_CLOSED` rule out the directly unwrapped HTTP request diagnostic branch for this replay. The external provider may not have received a successful HTTP request, but the adapter execution path was reached and failed while invoking its configured client.

This is expected fail-closed behavior for a provider client exception before successful proposal envelope creation.

## Existing Capability Reuse

No redesign is required.

Existing capabilities already provide:

- certified provider boundary routing through `run_certified_provider_attachment(...)`;
- provider readiness evidence before invocation;
- fail-closed exception normalization;
- replay-visible failed envelope creation;
- certified provider attachment evidence;
- external Worker result package failure propagation;
- governance authority preservation;
- replay authority preservation.

The existing runtime path correctly distinguishes:

- adapter boundary reached: `provider_invoked_inside_adapter=true`;
- successful provider proposal not created: `provider_invoked=false`;
- fail-closed provider status: `provider_status=FAILED_CLOSED`;
- normalized failure reason: `OpenAI provider unavailable`.

## Architectural Conclusions

1. Platform Core remains certified.
2. Human Interface remains certified.
3. Runtime Entry remains certified.
4. Governed Development Bridge remains certified.
5. Worker Runtime remains certified.
6. Central Provider Platform remains certified.
7. Provider Registry and readiness are reached and pass.
8. Replay ownership is preserved.
9. The observed failure is localized to the OpenAI provider adapter invocation branch.
10. The `provider_invoked_inside_adapter=true` to `provider_invoked=false` transition is expected because the two fields describe different boundaries.

This audit does not identify a Provider Platform architecture defect.

This audit does not identify a Worker architecture defect.

This audit does not identify a Governance or Replay defect.

## Final Recommendation

Preserve the current fail-closed semantics.

Recommended operational follow-up:

- Preserve `provider_invoked=false` for failed provider proposal envelopes.
- Preserve `provider_invoked_inside_adapter=true` as the external Worker adapter boundary indicator.
- Add, in a future implementation task if desired, a more precise diagnostic field for adapter client exception causes when `_call_openai(...)` catches a non-HTTP generic exception. This would improve operations but is not required to preserve governance correctness.

Do not redesign Platform Core, Runtime, Governance, Replay, Worker Platform, or the Central Provider Platform.

## Final Verdict

`PRE_INVOCATION_FAIL_CLOSED_EXPECTED`

Deterministic support:

- Adapter boundary is reached through `run_openai_external_worker_provider_adapter(...)`.
- Certified Provider Attachment is reached through `run_certified_provider_attachment(...)`.
- Provider readiness records `READY`.
- OpenAI adapter `_call_openai(...)` normalizes generic client exceptions to `FailClosedRuntimeError("OpenAI provider unavailable")`.
- Provider runtime diagnostics classify the observed failure as `openai_provider_adapter`.
- `run_provider_attachment(...)` catches the exception and creates a failed envelope.
- `_failed_envelope(...)` records `provider_invoked=false`.
- `_provider_capture_artifact(...)` records `provider_invoked_inside_adapter=true` because the external Worker adapter recorded a provider capture after certified provider attachment returned.
- No successful provider proposal envelope, provider response text, raw provider response hash, or completed provider result exists in replay.
- The behavior is expected fail-closed runtime behavior, not an implementation or configuration defect.
