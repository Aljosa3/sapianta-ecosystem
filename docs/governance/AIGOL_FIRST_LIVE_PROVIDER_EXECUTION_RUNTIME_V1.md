# AIGOL First Live Provider Execution Runtime V1

Status: implemented runtime milestone.

Purpose: close the executable-path gap identified by `AIGOL_FIRST_LIVE_PROVIDER_EXECUTION_PATH_AUDIT_V1`.

This milestone implements the smallest governed runtime needed to execute one authorized OpenAI dispatch attempt through the existing live provider boundary.

It does not expand ERR.

It does not authorize retries.

It does not authorize fallback.

It does not authorize workers.

It does not authorize provider routing.

## Runtime Boundary

Runtime:

```text
AIGOL_FIRST_LIVE_PROVIDER_EXECUTION_RUNTIME_V1
```

Implementation:

```text
aigol/runtime/first_live_provider_execution_runtime.py
```

Test coverage:

```text
tests/test_first_live_provider_execution_runtime_v1.py
```

## Execution Path

The implemented path is:

```text
FIRST_LIVE_PROVIDER_DISPATCH_AUTHORIZATION_ARTIFACT_V1
-> activation package replay reconstruction
-> approval freshness revalidation
-> credential freshness revalidation
-> live provider approval view
-> live provider credential policy view
-> governed live provider runtime boundary
-> credential retrieval boundary
-> request envelope evidence
-> response envelope or error envelope evidence
-> canonical provider output
-> LLM_COGNITION_ARTIFACT_V1
-> post-dispatch audit packet
-> post-dispatch recertification packet
-> rollback execution artifact
-> FIRST_LIVE_PROVIDER_DISPATCH_EXECUTION_PACKET_V1
```

## Replay Evidence

The runtime records ordered immutable replay evidence:

```text
000_first_live_provider_execution_approval_revalidation.json
001_first_live_provider_execution_credential_revalidation.json
002_first_live_provider_live_transport_execution_evidence.json
003_first_live_provider_llm_cognition_artifact.json
004_first_live_provider_post_dispatch_audit_packet.json
005_first_live_provider_post_dispatch_recertification_packet.json
006_first_live_provider_rollback_execution.json
007_first_live_provider_dispatch_execution_packet.json
```

The live provider boundary records nested replay evidence under:

```text
live_provider_boundary/
```

## Implemented Artifacts

New artifact types:

- `FIRST_LIVE_PROVIDER_EXECUTION_APPROVAL_REVALIDATION_ARTIFACT_V1`;
- `FIRST_LIVE_PROVIDER_EXECUTION_CREDENTIAL_REVALIDATION_ARTIFACT_V1`;
- `FIRST_LIVE_PROVIDER_LIVE_TRANSPORT_EXECUTION_EVIDENCE_ARTIFACT_V1`;
- `FIRST_LIVE_PROVIDER_POST_DISPATCH_AUDIT_PACKET_ARTIFACT_V1`;
- `FIRST_LIVE_PROVIDER_POST_DISPATCH_RECERTIFICATION_PACKET_ARTIFACT_V1`;
- `FIRST_LIVE_PROVIDER_ROLLBACK_EXECUTION_ARTIFACT_V1`;
- `FIRST_LIVE_PROVIDER_DISPATCH_EXECUTION_PACKET_V1`.

## Governance Constraints

Preserved invariants:

```text
ERR_PASSIVE = true
PROVIDER = openai
PROVIDER_RESOURCE_TYPE = COGNITION_PROVIDER
DISPATCH_ATTEMPT_LIMIT = 1
COGNITION_ONLY = true
SECRET_REPLAY = false
AUTHORIZATION_HEADER_REPLAY = false
WORKER_INVOCATION = false
PROVIDER_ROUTING = false
FALLBACK = false
AUTOMATIC_RETRY = false
GOVERNANCE_MUTATION = false
REPLAY_MUTATION = false
```

The runtime fails closed if:

- dispatch authorization is missing;
- dispatch authorization is malformed;
- dispatch authorization is expired;
- dispatch authorization has already been marked attempted or performed;
- activation package lineage does not match dispatch authorization;
- credential is unavailable;
- credential policy is unsupported;
- transport boundary fails;
- provider output is authority-bearing;
- replay artifacts already exist.

## Credential Boundary

The activation package preserves its own credential policy evidence.

The execution runtime creates a secret-free live provider credential policy view for the live boundary using:

```text
env:AIGOL_OPENAI_API_KEY
```

The credential value is never written to replay.

The credential hash is not recorded.

The authorization header is not replayed.

## Rollback Behavior

Success:

```text
ROLLBACK_STATUS = ROLLBACK_NOT_REQUIRED
```

Failure:

```text
ROLLBACK_STATUS = ROLLBACK_EXECUTED
```

Rollback evidence disallows:

- activation reuse;
- dispatch reuse;
- credential reuse;
- additional live dispatch without new authorization.

## Validation Results

Focused validation:

```text
python -m pytest tests/test_first_live_provider_execution_runtime_v1.py
6 passed
```

Validated behaviors:

- dispatch authorization is consumed;
- approval freshness is revalidated;
- credential freshness is revalidated;
- credential retrieval boundary is exercised;
- transport execution evidence is replay-visible;
- `LLM_COGNITION_ARTIFACT_V1` is produced on success;
- post-dispatch audit is produced;
- post-dispatch recertification is produced;
- rollback is not required on success;
- rollback is executed on failure;
- credential material is not replayed;
- replay reuse fails closed.

## Remaining Operational Constraint

This runtime executes through the governed live provider boundary with injected transport validation.

Actual external network activation remains an operational decision controlled by the live transport boundary and credential environment.

No retry, fallback, routing, worker invocation, or governance mutation is introduced by this milestone.
