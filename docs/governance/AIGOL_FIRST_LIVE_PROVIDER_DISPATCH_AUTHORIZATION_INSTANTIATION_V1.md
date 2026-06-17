# AIGOL First Live Provider Dispatch Authorization Instantiation V1

Status: implemented dispatch authorization instantiation.

Purpose: create the first concrete dispatch authorization artifact instance for exactly one governed OpenAI dispatch attempt.

This milestone creates replay-visible authorization evidence.

It does not invoke OpenAI.

It does not execute dispatch.

It does not disclose credentials.

It does not modify ERR or OCS.

## Context

Inputs:

```text
AIGOL_FIRST_LIVE_PROVIDER_ACTIVATION_PACKAGE_V1
AIGOL_FIRST_LIVE_PROVIDER_ACTIVATION_PACKAGE_INSTANTIATION_V1
AIGOL_FIRST_LIVE_PROVIDER_ACTIVATION_CLOSURE_AUDIT_V1
AIGOL_FIRST_LIVE_PROVIDER_DISPATCH_AUTHORIZATION_PACKAGE_V1
```

Prior state:

```text
DISPATCH_AUTHORIZATION_PACKAGE_SPECIFIED = YES
LIVE_DISPATCH_AUTHORIZATION_PRESENT = NO
```

## Architecture Summary

Implemented path:

```text
activation package replay
-> approval freshness validation
-> credential freshness validation placeholder
-> dispatch execution authorization evidence
-> dispatch authorization artifact
-> replay reconstruction
```

The dispatch authorization artifact permits exactly one dispatch attempt in evidence, but this milestone does not execute that attempt:

```text
authorization_status = DISPATCH_AUTHORIZED
dispatch_count = 1
cognition_only = true
live_dispatch_attempted = false
live_dispatch_performed = false
```

## Runtime Changes

Added:

- `aigol/runtime/first_live_provider_dispatch_authorization_instantiation.py`

The runtime provides:

- `instantiate_first_live_provider_dispatch_authorization`;
- `create_approval_freshness_validation`;
- `create_credential_freshness_validation`;
- `create_dispatch_execution_authorization_evidence`;
- `create_dispatch_authorization_artifact`;
- `reconstruct_first_live_provider_dispatch_authorization`.

## Replay Evidence

Successful dispatch authorization instantiation writes:

```text
000_first_live_provider_approval_freshness_validation.json
001_first_live_provider_credential_freshness_validation.json
002_first_live_provider_dispatch_execution_authorization_evidence.json
003_first_live_provider_dispatch_authorization.json
```

Fail-closed authorization instantiation writes:

```text
000_first_live_provider_dispatch_authorization_failed_closed.json
```

Replay reconstruction verifies:

- replay ordering;
- wrapper hashes;
- artifact hashes;
- approval freshness to dispatch evidence lineage;
- credential freshness to dispatch evidence lineage;
- dispatch evidence to authorization lineage;
- no live dispatch;
- no credential secret replay;
- no provider invocation;
- no worker invocation;
- no governance mutation;
- no replay mutation.

## Artifact Instances

Implemented artifact types:

| Artifact | Purpose |
| --- | --- |
| `FIRST_LIVE_PROVIDER_APPROVAL_FRESHNESS_VALIDATION_ARTIFACT_V1` | Verifies approval is fresh, one-time, scoped to `openai`, and not used or revoked. |
| `FIRST_LIVE_PROVIDER_CREDENTIAL_FRESHNESS_VALIDATION_ARTIFACT_V1` | Records credential freshness placeholder evidence without secret retrieval or replay. |
| `FIRST_LIVE_PROVIDER_DISPATCH_EXECUTION_AUTHORIZATION_EVIDENCE_ARTIFACT_V1` | Records that dispatch preconditions are satisfied while no dispatch is performed. |
| `FIRST_LIVE_PROVIDER_DISPATCH_AUTHORIZATION_ARTIFACT_V1` | Authorizes exactly one future governed OpenAI dispatch attempt. |

## Boundary Preservation

Preserved:

- no OpenAI invocation;
- no dispatch execution;
- no credential disclosure;
- no credential secret replay;
- no authorization header replay;
- ERR remains passive;
- OCS architecture is unchanged;
- no provider routing;
- no provider ranking;
- no provider fallback;
- no automatic retry;
- no tool use;
- no worker invocation;
- no governance mutation;
- no replay mutation.

Runtime invariant:

```text
authorization_status = DISPATCH_AUTHORIZED
dispatch_count = 1
cognition_only = true
live_dispatch_attempted = false
live_dispatch_performed = false
credential_secret_replayed = false
provider_invoked = false
worker_invoked = false
governance_modified = false
replay_modified = false
```

## Tests Added

Added:

- `tests/test_first_live_provider_dispatch_authorization_instantiation_v1.py`

Coverage:

- dispatch authorization artifact instance without dispatch;
- ordered replay evidence;
- secret-free replay artifacts;
- replay lineage reconstruction;
- approval expiration fail-closed;
- activation package tampering fail-closed;
- authorization replay tampering detection;
- static check that the module has no network or secret dispatch implementation.

## Validation Results

Focused validation:

```text
python -m pytest tests/test_first_live_provider_dispatch_authorization_instantiation_v1.py
8 passed
```

Broader regression validation:

```text
python -m pytest tests/test_first_live_provider_dispatch_authorization_instantiation_v1.py tests/test_first_live_provider_activation_package_instantiation_v1.py tests/test_live_provider_http_transport_v1.py tests/test_live_provider_runtime_boundary_v1.py tests/test_live_provider_invocation_prerequisites_v1.py tests/test_first_real_provider_runtime_v1.py tests/test_real_provider_registration_v1.py tests/test_external_resource_registry_runtime_v0.py tests/test_llm_cognition_provider_runtime_v1.py tests/test_cognition_artifact_runtime_v1.py
101 passed
```

## Remaining Gaps

Remaining gaps are intentionally outside this milestone:

- no live OpenAI dispatch has occurred;
- credential freshness is a secret-free placeholder and must be rechecked at actual dispatch time;
- live response or live error evidence does not exist yet;
- post-dispatch audit is not executed yet;
- post-dispatch recertification is not executed yet;
- rollback execution is pending live dispatch outcome.

## Final Recommendation

The concrete dispatch authorization artifact now exists as replay-visible evidence.

Proceed only to a separately approved one-attempt dispatch execution milestone.

Final position:

```text
DISPATCH_AUTHORIZATION_INSTANTIATED = YES
DISPATCH_AUTHORIZED_FOR_ONE_ATTEMPT = YES
LIVE_OPENAI_INVOCATION_PERFORMED = NO
DISPATCH_EXECUTED = NO
CREDENTIAL_DISCLOSED = NO
NEXT_STEP = FIRST_LIVE_OPENAI_ONE_ATTEMPT_DISPATCH_EXECUTION
```
