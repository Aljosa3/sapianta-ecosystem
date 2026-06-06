# AIGOL_PROVIDER_HEALTH_AND_READINESS_RUNTIME_V1

## Status

Implemented.

## Classification

```text
CERTIFIED_PROVIDER_HEALTH_AND_READINESS_RUNTIME
```

## Objective

Create a governed provider readiness layer executed before OpenAI provider invocation.

The runtime emits `PROVIDER_READINESS_ARTIFACT_V1` and blocks provider invocation when readiness is `NOT_READY`.

## Scope

Runtime integration:

```text
aigol/provider/provider_runtime.py::run_provider_attachment
```

Test coverage:

```text
tests/test_provider_health_and_readiness_runtime_v1.py
```

The implementation does not create a new provider adapter, cognition runtime, replay model, governance authority model, comparison runtime, continuity runtime, or clarification runtime.

## Artifact

Artifact type:

```text
PROVIDER_READINESS_ARTIFACT_V1
```

Runtime version:

```text
AIGOL_PROVIDER_HEALTH_AND_READINESS_RUNTIME_V1
```

Readiness status:

```text
READY
NOT_READY
```

## Validations

The readiness artifact records deterministic checks for:

- API key presence
- provider configuration validity
- model configuration validity
- transport availability
- provider activation readiness

## Sanitized Diagnostics

Only the following diagnostic fields are emitted:

- `readiness_stage`
- `failure_category`
- `exception_type`
- `http_status`

Sensitive material is not emitted:

- API keys
- Authorization headers
- request bodies
- raw response bodies
- stack traces

## Runtime Behavior

For OpenAI provider adapters, readiness is evaluated after provider lookup and before provider invocation.

If readiness is `READY`:

- readiness replay is persisted;
- provider invocation may proceed;
- provider proposal creation continues through the existing provider attachment runtime.

If readiness is `NOT_READY`:

- readiness replay is persisted;
- provider invocation is skipped;
- the existing fail-closed provider failure path records the failure;
- existing `failure_reason` compatibility is preserved.

## Replay Evidence

Readiness evidence is persisted as:

```text
000_provider_readiness_recorded.json
```

Provider replay reconstruction exposes `provider_readiness_artifact` when readiness evidence is present.

## Boundary Guarantees

- Fail-closed behavior is preserved.
- Existing `failure_reason` field is preserved.
- Provider authority remains false.
- Execution capability remains false.
- Worker invocation remains false.
- Credentials and request bodies are not included in readiness diagnostics.

## Acceptance

Automated tests verify:

- `READY` readiness permits invocation.
- missing API key produces `NOT_READY` and skips invocation.
- invalid provider configuration produces `NOT_READY`.
- invalid model or endpoint configuration produces `NOT_READY`.
- unavailable transport produces `NOT_READY`.
- unavailable provider activation produces `NOT_READY`.
- replay readiness evidence excludes sensitive data.

## Conclusion

OpenAI provider invocation is now preceded by deterministic, replay-visible readiness evidence. Provider invocation does not execute when readiness is `NOT_READY`.
