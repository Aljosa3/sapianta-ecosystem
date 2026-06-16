# AIGOL First Real Provider Runtime Regression Suite V1

Status: regression protection definition.

Purpose: protect the first real provider runtime path before any live provider invocation.

This artifact defines the pre-live regression suite for:

```text
AIGOL_FIRST_REAL_PROVIDER_RUNTIME_IMPLEMENTATION_V1
```

It does not authorize live provider invocation.

## Protected Runtime Path

The protected deterministic path is:

```text
ERR metadata
-> openai selected by capability
-> canonical provider contract
-> canonical adapter views
-> AIGOL_LLM_COGNITION_PROVIDER_RUNTIME_V1
-> deterministic mock provider response
-> LLM_COGNITION_ARTIFACT_V1
-> replay evidence
```

## Critical Runtime Guarantees

The regression suite protects these guarantees:

1. ERR selects `openai` metadata for `reasoning`.
2. ERR remains passive and records no provider invocation.
3. Canonical provider contract adapter view is produced.
4. Canonical provider input adapter view is produced.
5. Canonical provider output adapter view is produced.
6. Deterministic mock provider response is used.
7. No real OpenAI call is made.
8. No provider transport implementation is added.
9. No authentication implementation is added.
10. `LLM_COGNITION_ARTIFACT_V1` is produced.
11. Replay-visible validation evidence is persisted.
12. Authority-bearing provider output fails closed.
13. No worker invocation occurs.
14. No execution or dispatch request occurs.
15. No governance mutation occurs.
16. No replay mutation occurs.

## Regression Categories

### 1. ERR-Selected OpenAI Metadata

Protected behavior:

```text
required_capability = reasoning
-> ERR
-> selected_resource_id = openai
```

Required evidence:

- selected provider id is `openai`;
- ERR selection artifact is replay-visible;
- ERR evidence records `provider_invoked = false`;
- inactive OpenAI with another active provider fails closed for this runtime path.

Primary tests:

- `tests/test_first_real_provider_runtime_v1.py`
- `tests/test_real_provider_registration_v1.py`
- `tests/test_external_resource_registry_runtime_v0.py`

### 2. Canonical Contract Adapter Views

Protected behavior:

```text
existing OpenAI contract
-> canonical OpenAI provider contract view
-> canonical input view
-> canonical output view
```

Required evidence:

- `CANONICAL_COGNITION_PROVIDER_CONTRACT_V1` is produced;
- `CANONICAL_COGNITION_PROVIDER_INPUT_V1` is produced;
- `CANONICAL_COGNITION_PROVIDER_OUTPUT_V1` is produced;
- source request and response hashes are preserved;
- provider id and schema remain `openai` / `openai.responses.v1`;
- adapter views are hash-stable.

Primary tests:

- `tests/test_first_real_provider_runtime_v1.py`
- `tests/test_llm_cognition_provider_runtime_v1.py`

### 3. Deterministic Mock Provider Response

Protected behavior:

```text
deterministic local stub
-> provider response artifact
-> real_openai_called = false
```

Required evidence:

- `deterministic_mock_provider_response = true`;
- `real_openai_called = false`;
- deterministic response is captured as untrusted provider output;
- no network transport is used.

Primary tests:

- `tests/test_first_real_provider_runtime_v1.py`

### 4. LLM_COGNITION_ARTIFACT_V1 Output

Protected behavior:

```text
provider response artifact
-> cognition artifact normalization
-> LLM_COGNITION_ARTIFACT_V1
```

Required evidence:

- cognition artifact type is `LLM_COGNITION_ARTIFACT_V1`;
- provider identity is `openai`;
- confidence is normalized;
- provider output remains non-authoritative;
- existing cognition artifact runtime tests pass.

Primary tests:

- `tests/test_first_real_provider_runtime_v1.py`
- `tests/test_cognition_artifact_runtime_v1.py`

### 5. Replay-Visible Evidence

Protected behavior:

```text
runtime validation
-> replay-visible top-level artifact
-> nested ERR, LLM provider, and cognition artifact replay
```

Required evidence:

- top-level validation replay file exists;
- ERR selection replay files exist;
- LLM provider request/response/binding replay files exist;
- cognition artifact replay files exist;
- source hashes are referenced by canonical views;
- replay reconstruction passes for underlying LLM provider replay.

Primary tests:

- `tests/test_first_real_provider_runtime_v1.py`
- `tests/test_llm_cognition_provider_runtime_v1.py`
- `tests/test_cognition_artifact_runtime_v1.py`

### 6. No Real Provider Call / No Transport / No Authentication

Protected behavior:

```text
pre-live validation
-> no OpenAI API call
-> no transport implementation
-> no authentication implementation
```

Required evidence:

- `real_openai_called = false`;
- runtime source contains no HTTP client usage;
- runtime source contains no authorization header or API key handling;
- existing lower-level LLM runtime remains the only provider runtime boundary.

Primary tests:

- `tests/test_first_real_provider_runtime_v1.py`

### 7. Authority Boundary And Fail-Closed Behavior

Protected behavior:

```text
authority-bearing provider output
-> FAILED_CLOSED
-> no worker, execution, governance, or replay mutation
```

Required evidence:

- authority-bearing deterministic response fails closed;
- worker invocation remains false;
- execution request remains false;
- dispatch request remains false;
- governance mutation remains false;
- replay mutation remains false.

Primary tests:

- `tests/test_first_real_provider_runtime_v1.py`
- `tests/test_llm_cognition_provider_runtime_v1.py`

## CI Test Set

The named pre-live regression suite is:

```bash
python -m pytest \
  tests/test_first_real_provider_runtime_v1.py \
  tests/test_real_provider_registration_v1.py \
  tests/test_external_resource_registry_runtime_v0.py \
  tests/test_llm_cognition_provider_runtime_v1.py \
  tests/test_cognition_artifact_runtime_v1.py
```

Current baseline:

```text
45 passed
```

The CI job name should be:

```text
first-real-provider-runtime-regression-suite
```

The job should run on changes touching:

- `aigol/runtime/first_real_provider_runtime.py`;
- `aigol/runtime/external_resource_registry_runtime.py`;
- `aigol/runtime/llm_cognition_provider_runtime.py`;
- `aigol/runtime/cognition_artifact_runtime.py`;
- `tests/test_first_real_provider_runtime_v1.py`;
- `tests/test_real_provider_registration_v1.py`;
- `tests/test_external_resource_registry_runtime_v0.py`;
- `tests/test_llm_cognition_provider_runtime_v1.py`;
- `tests/test_cognition_artifact_runtime_v1.py`;
- governance docs for ERR, canonical provider contract, adapters, or first provider runtime.

`git diff --check` must accompany the suite.

## Governance Evidence Model

Every suite run intended to preserve pre-live readiness must record:

- suite id: `AIGOL_FIRST_REAL_PROVIDER_RUNTIME_REGRESSION_SUITE_V1`;
- source revision or change reference;
- command executed;
- test files included;
- total tests collected;
- pass/fail result;
- failure list if any;
- `git diff --check` result;
- whether `real_openai_called = false` remains protected;
- whether `deterministic_mock_provider_response = true` remains protected;
- whether `LLM_COGNITION_ARTIFACT_V1` remains produced;
- whether ERR remains passive;
- whether no transport/auth implementation was introduced;
- whether no worker/governance/replay mutation occurred.

Passing evidence:

```text
FIRST_REAL_PROVIDER_RUNTIME_REGRESSION_SUITE = PASS
LIVE_PROVIDER_INVOCATION_APPROVED = NO
PRE_LIVE_RUNTIME_PROTECTION_PRESERVED = YES
```

Failing evidence:

```text
FIRST_REAL_PROVIDER_RUNTIME_REGRESSION_SUITE = FAIL
LIVE_PROVIDER_INVOCATION_APPROVED = NO
RECERTIFICATION_REQUIRED = YES
```

## Recertification Triggers

Recertification is required if any of the following change:

- ERR resource schema or provider registration behavior;
- ERR selection evidence fields;
- OpenAI provider metadata;
- canonical provider contract schema;
- canonical adapter behavior;
- deterministic response transport stub;
- LLM cognition provider request artifact shape;
- LLM cognition provider response artifact shape;
- LLM cognition replay binding shape;
- cognition artifact normalization;
- confidence or uncertainty normalization;
- replay hashing or serialization;
- fail-closed behavior;
- authority-boundary phrase rejection;
- no-transport/no-auth static checks;
- any test in the CI set is removed, skipped, weakened, or reclassified;
- any code path can perform a real provider call during pre-live validation;
- any worker invocation, execution request, dispatch request, governance mutation, or replay mutation appears.

Recertification must produce a new governance artifact before live-call approval can be considered.

## Acceptance Criteria For Future Live-Call Approval

Future live OpenAI validation may be considered only if all criteria are met:

1. This regression suite passes.
2. `git diff --check` is clean.
3. A separate live-call approval artifact exists.
4. Human approval is explicit and replay-visible.
5. Credential policy is explicit and captures no secret.
6. Exactly one provider is allowed: `openai`.
7. No multi-provider routing is enabled.
8. No provider comparison is enabled.
9. No provider fallback is enabled.
10. No streaming is enabled.
11. No tool use is enabled.
12. No automatic retries are enabled.
13. No worker invocation is allowed.
14. No execution or dispatch request is allowed.
15. Provider output remains untrusted and non-authoritative.
16. `LLM_COGNITION_ARTIFACT_V1` normalization remains required.
17. Replay reconstruction must pass after the live call.

Live-call approval output must not be inferred from this suite.

Required live-call precondition:

```text
FIRST_REAL_PROVIDER_RUNTIME_REGRESSION_SUITE = PASS
LIVE_PROVIDER_INVOCATION_APPROVED = SEPARATE_GOVERNED_ARTIFACT_REQUIRED
```

## Final Recommendation

Adopt this suite as the mandatory pre-live protection gate for the first real provider runtime path.

Final protected status:

```text
FIRST_REAL_PROVIDER_RUNTIME_PRE_LIVE_PROTECTED = YES
OPENAI_LIVE_CALL_AUTHORIZED_BY_THIS_SUITE = NO
REGRESSION_SUITE_REQUIRED_BEFORE_LIVE_APPROVAL = YES
```
