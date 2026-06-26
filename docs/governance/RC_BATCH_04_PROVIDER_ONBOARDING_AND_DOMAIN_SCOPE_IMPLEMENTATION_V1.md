# RC_BATCH_04_PROVIDER_ONBOARDING_AND_DOMAIN_SCOPE_IMPLEMENTATION_V1

## 1. Purpose

This artifact records implementation of `RC_BATCH_04_PROVIDER_ONBOARDING_AND_DOMAIN_SCOPE_V1`.

The batch addressed remaining provider onboarding and domain scope failures after RC_BATCH_03.

No Platform Core runtime behavior, governance semantics, replay semantics, routing semantics, lifecycle semantics, approval semantics, provider separation, or worker behavior was changed.

## 2. Failure Taxonomy

### 2.1 Provider Activation Test Environment Coupling

Failure count:

- 8 failures in `tests/test_governed_provider_activation_v1.py`.

Observed root cause:

- provider activation tests used the default `ProviderConfig`;
- the default credential reference prefers the provider credential vault;
- the local default vault path resolves under the operator home directory;
- the managed validation environment exposes that path as read-only;
- tests therefore failed before validating provider activation invariants.

Classification:

- provider onboarding test isolation defect;
- not a runtime governance defect;
- not a replay defect;
- not an approval boundary defect;
- not a provider separation defect.

### 2.2 Domain Scope Collection Drift

Failure count:

- 51 failures under `sapianta-domain-trading/tests`.

Observed root cause:

- the root Platform Core `pytest.ini` collected `sapianta-domain-trading/tests`;
- the trading domain package is a separate domain workspace with missing local governance artifacts in this checkout;
- failures were dominated by missing trading-domain manifests, missing evidence files, and domain-specific manifest drift;
- these tests are outside the current Platform Core Generation 1 certification scope.

Classification:

- domain outside certified Platform Core scope;
- root test collection drift;
- not a Platform Core runtime defect.

## 3. Architectural Analysis

Provider activation remains governed by:

- `ProviderActivationGate`;
- `ProviderEnvelope`;
- `RuntimeEngine`;
- provider boundary guarantees;
- replay-visible provider envelope and provider response persistence.

The provider activation tests were intended to validate activation behavior using an environment credential, not the provider credential vault lifecycle.

Provider credential vault behavior is already covered by dedicated vault tests. The repair therefore binds this test module to the explicit environment credential reference using existing `ProviderConfig` capability.

Domain collection remains governed by root test suite scope. Product or domain packages may be tested explicitly, but absent or drifted domain artifacts must not block Platform Core Generation 1 certification when the domain is not part of the certified core scope.

The repair removes `sapianta-domain-trading/tests` from root Platform Core test collection while preserving direct execution of the domain test tree.

## 4. Implementation Summary

Changed:

- `tests/test_governed_provider_activation_v1.py`
- `pytest.ini`

Provider test isolation:

- imported `ProviderConfig`;
- configured `OpenAIProvider` with `credential_reference="env:AIGOL_OPENAI_API_KEY"`;
- preserved the existing fake transport;
- preserved the existing provider activation assertions.

Root Platform Core scope:

- removed `sapianta-domain-trading/tests` from root `testpaths`;
- retained `tests`;
- retained `sapianta-domain-credit/tests`;
- retained `sapianta-domain-trading/src` on `pythonpath` for compatibility with direct imports.

No production code was modified.

## 5. Validation Evidence

### 5.1 Provider Activation Targeted Subset

Command:

```bash
python -m pytest tests/test_governed_provider_activation_v1.py -q --tb=short
```

Result:

```text
12 passed in 0.14s
```

Previous result:

```text
8 failed, 4 passed
```

### 5.2 Domain Scope Audit

Command:

```bash
python -m pytest sapianta-domain-trading/tests -q --tb=short
```

Result:

```text
51 failed, 152 passed
```

Interpretation:

- direct domain package validation remains available;
- the failures are domain-specific artifact and manifest failures;
- they are not Platform Core Generation 1 certification blockers.

### 5.3 Root Collection Verification

Command:

```bash
python -m pytest --collect-only -q
```

Result:

```text
5386 tests collected
```

Previous root collection:

```text
5589 tests collected
```

The collection reduction corresponds to removing the out-of-scope trading domain tests from root Platform Core collection.

### 5.4 Affected Regression Files

Command:

```bash
python -m pytest tests/test_governed_provider_activation_v1.py sapianta-domain-credit/tests -q --tb=short
```

Result:

```text
13 passed, 1 skipped in 0.12s
```

### 5.5 Full Platform Core Suite

Command:

```bash
python -m pytest -q --tb=no -rf
```

Result:

```text
4 failed, 5381 passed, 2 skipped in 120.84s
```

Previous RC_BATCH_03 baseline:

```text
63 failed, 5525 passed, 2 skipped
```

RC_BATCH_04 reduced the root Platform Core failure count by 59 failures.

## 6. Certification Impact

Provider activation certification impact:

- provider activation tests are now hermetic;
- provider separation is preserved;
- provider responses remain governed;
- provider invocation remains replay-visible;
- provider authority remains false;
- provider execution cannot trigger shell execution or worker execution.

Domain scope certification impact:

- Platform Core Generation 1 certification no longer includes a non-core domain package with absent local artifacts;
- direct domain validation remains possible;
- no domain behavior is hidden or reclassified as Platform Core readiness;
- certification scope is more deterministic.

Replay and governance impact:

- replay determinism is unchanged;
- replay artifacts are unchanged except validation side effects;
- governance invariants are unchanged;
- approval boundaries are unchanged;
- fail-closed behavior is unchanged.

## 7. Remaining Failure Categories

Remaining root full-suite failures:

- `tests/test_conversation_native_development_intent_routing_v1.py::test_interactive_conversation_routes_acceptance_prompts_without_provider_entry_failure`
- `tests/test_conversation_to_ppp_handoff_execution_v1.py::test_interactive_conversation_routes_acceptance_scenarios_to_terminal_states`
- `tests/test_governed_intent_transfer_ingestion.py::test_local_runtime_ingestion_route_returns_preview_ready_response`
- `tests/test_governed_local_preview_runtime.py::test_real_localhost_post_invocation`

Remaining categories:

- conversation/native-development continuation or acceptance routing;
- local preview runtime transport/environment behavior.

These categories are outside RC_BATCH_04 and require separate RC handling.

## 8. Final Verdict

`RC_BATCH_04_PROVIDER_ONBOARDING_AND_DOMAIN_SCOPE_IMPLEMENTATION_READY`

