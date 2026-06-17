# AIGOL First Live Provider Dispatch Execution Package V1

Status: dispatch execution package specification.

Purpose: define the execution evidence package for one governed OpenAI dispatch attempt.

This artifact is package preparation only.

It does not invoke OpenAI.

It does not disclose credentials.

It does not execute dispatch.

It does not modify ERR, OCS, replay, governance, transport, or credential runtime behavior.

## Context

Current certified state:

```text
PRE_DISPATCH_READY
ARCHITECTURE_BLOCKERS = NONE
GOVERNANCE_BLOCKERS = NONE
IMPLEMENTATION_BLOCKERS = NONE
AUTHORIZATION_BLOCKERS = NONE
DISPATCH_AUTHORIZED_FOR_ONE_ATTEMPT = YES
LIVE_OPENAI_INVOCATION_PERFORMED = NO
```

This package follows:

```text
AIGOL_FIRST_LIVE_PROVIDER_PRE_DISPATCH_AUDIT_V1
AIGOL_FIRST_LIVE_PROVIDER_DISPATCH_AUTHORIZATION_INSTANTIATION_V1
AIGOL_LIVE_PROVIDER_HTTP_TRANSPORT_V1
```

## Package Boundary

The dispatch execution package may execute exactly one governed OpenAI dispatch attempt only after operational dispatch approval.

Allowed:

- one live credential freshness revalidation;
- one live request replay artifact;
- one live response replay artifact or live error replay artifact;
- one post-dispatch audit packet;
- one post-dispatch recertification packet;
- one rollback execution artifact if required.

Prohibited:

- credential disclosure;
- credential value replay;
- authorization header replay;
- second dispatch attempt;
- retry;
- fallback;
- provider routing;
- provider ranking;
- provider comparison;
- worker invocation;
- tool use;
- governance mutation;
- replay mutation.

## Dispatch Execution Packet

Artifact type:

```text
FIRST_LIVE_PROVIDER_DISPATCH_EXECUTION_PACKET_V1
```

Purpose:

Bind the authorized one-attempt dispatch to concrete execution-time evidence.

Required fields:

- `artifact_type`;
- `execution_packet_id`;
- `dispatch_authorization_artifact_hash`;
- `activation_package_replay_hash`;
- `dispatch_authorization_replay_hash`;
- `provider_id`;
- `provider_resource_type`;
- `dispatch_attempt_limit`;
- `dispatch_attempt_number`;
- `execution_status`;
- `request_artifact_hash`;
- `response_artifact_hash`;
- `error_artifact_hash`;
- `post_dispatch_audit_packet_hash`;
- `post_dispatch_recertification_packet_hash`;
- `rollback_execution_artifact_hash`;
- `credential_secret_replayed`;
- `authorization_header_replayed`;
- `worker_invoked`;
- `provider_routing_performed`;
- `fallback_performed`;
- `automatic_retry_performed`;
- `governance_modified`;
- `replay_modified`;
- `created_at`;
- `artifact_hash`.

Allowed execution statuses:

```text
DISPATCH_EXECUTION_COMPLETED
DISPATCH_EXECUTION_FAILED_CLOSED
DISPATCH_EXECUTION_ABORTED_PRE_REQUEST
```

Required invariants:

```text
provider_id = openai
provider_resource_type = COGNITION_PROVIDER
dispatch_attempt_limit = 1
dispatch_attempt_number <= 1
credential_secret_replayed = false
authorization_header_replayed = false
worker_invoked = false
provider_routing_performed = false
fallback_performed = false
automatic_retry_performed = false
governance_modified = false
replay_modified = false
```

## Dispatch Timestamp Requirements

Required timestamps:

- `execution_packet_created_at`;
- `approval_revalidated_at`;
- `credential_revalidated_at`;
- `request_prepared_at`;
- `dispatch_started_at`;
- `dispatch_completed_at` or `dispatch_failed_closed_at`;
- `post_dispatch_audit_created_at`;
- `post_dispatch_recertification_created_at`;
- `rollback_executed_at` if rollback is required.

Rules:

- timestamps must be replay-visible;
- timestamps must be monotonic within the package;
- dispatch start must occur after approval freshness revalidation;
- dispatch start must occur after credential freshness revalidation;
- post-dispatch audit must occur after response or error evidence;
- recertification must occur after post-dispatch audit;
- rollback, if required, must occur after audit or recertification failure.

## Approval Freshness Revalidation Procedure

Before dispatch execution:

1. reconstruct activation package replay;
2. reconstruct dispatch authorization replay;
3. verify approval artifact hash;
4. verify approval provider is `openai`;
5. verify approval scope is single live invocation;
6. verify approval is one-time use;
7. verify approval has not expired;
8. verify approval has not been used;
9. verify approval has not been revoked;
10. verify approval permits no workers, routing, fallback, retry, tools, governance mutation, or replay mutation.

Required output:

```text
APPROVAL_FRESHNESS_REVALIDATION = PASS
```

Fail closed if any approval check fails.

## Credential Freshness Revalidation Procedure

Before dispatch execution:

1. verify credential policy artifact hash;
2. verify credential availability artifact hash;
3. verify secret authority is approved;
4. verify credential is currently available;
5. verify credential has not been revoked;
6. verify rotation status is acceptable;
7. retrieve credential only inside the transport boundary;
8. never write credential value to replay;
9. never write authorization header to replay;
10. dispose of credential handle after dispatch boundary.

Required output:

```text
CREDENTIAL_FRESHNESS_REVALIDATION = PASS
NO_SECRET_REPLAY = TRUE
```

Fail closed if credential is unavailable, revoked, malformed, leaked, or cannot be checked safely.

## Live Request Replay Requirements

Artifact type:

```text
FIRST_LIVE_PROVIDER_LIVE_REQUEST_REPLAY_ARTIFACT_V1
```

Required fields:

- `artifact_type`;
- `request_id`;
- `dispatch_authorization_artifact_hash`;
- `provider_id`;
- `provider_schema_id`;
- `endpoint`;
- `http_method`;
- `request_payload_hash`;
- `request_payload_redacted`;
- `request_prepared_at`;
- `dispatch_started_at`;
- `credential_secret_replayed`;
- `authorization_header_replayed`;
- `streaming`;
- `tool_use`;
- `automatic_retry`;
- `worker_invoked`;
- `provider_routing_performed`;
- `governance_modified`;
- `replay_modified`;
- `artifact_hash`.

Required values:

```text
provider_id = openai
http_method = POST
credential_secret_replayed = false
authorization_header_replayed = false
streaming = false
tool_use = false
automatic_retry = false
worker_invoked = false
provider_routing_performed = false
governance_modified = false
replay_modified = false
```

## Live Response Replay Requirements

Artifact type:

```text
FIRST_LIVE_PROVIDER_LIVE_RESPONSE_REPLAY_ARTIFACT_V1
```

Required fields:

- `artifact_type`;
- `response_id`;
- `request_artifact_hash`;
- `provider_id`;
- `http_status_code`;
- `response_received_at`;
- `raw_response_hash`;
- `response_text_hash`;
- `canonical_output_artifact_hash`;
- `llm_cognition_artifact_hash`;
- `provider_output_trust`;
- `provider_output_authority`;
- `authority_boundary_validation`;
- `credential_secret_replayed`;
- `authorization_header_replayed`;
- `worker_invoked`;
- `provider_routing_performed`;
- `governance_modified`;
- `replay_modified`;
- `artifact_hash`.

Required values:

```text
provider_id = openai
provider_output_trust = UNTRUSTED
provider_output_authority = NONE
credential_secret_replayed = false
authorization_header_replayed = false
worker_invoked = false
provider_routing_performed = false
governance_modified = false
replay_modified = false
```

The response must fail closed if it is authority-bearing or cannot be normalized.

## Live Error Replay Requirements

Artifact type:

```text
FIRST_LIVE_PROVIDER_LIVE_ERROR_REPLAY_ARTIFACT_V1
```

Required fields:

- `artifact_type`;
- `error_id`;
- `request_artifact_hash`;
- `provider_id`;
- `error_classification`;
- `failure_reason`;
- `dispatch_failed_closed_at`;
- `retry_attempted`;
- `fallback_attempted`;
- `credential_secret_replayed`;
- `authorization_header_replayed`;
- `worker_invoked`;
- `provider_routing_performed`;
- `governance_modified`;
- `replay_modified`;
- `artifact_hash`.

Allowed error classifications:

- `TIMEOUT`;
- `RATE_LIMIT`;
- `MALFORMED_RESPONSE`;
- `AUTHENTICATION_UNAVAILABLE`;
- `CREDENTIAL_POLICY_INVALID`;
- `AUTHORITY_BOUNDARY_VIOLATION`;
- `TRANSPORT_UNAVAILABLE`;
- `REPLAY_WRITE_FAILURE`;
- `DISPATCH_SCOPE_VIOLATION`;

Required values:

```text
retry_attempted = false
fallback_attempted = false
credential_secret_replayed = false
authorization_header_replayed = false
worker_invoked = false
provider_routing_performed = false
governance_modified = false
replay_modified = false
```

## Post-Dispatch Audit Procedure

Post-dispatch audit must:

1. verify exactly one dispatch attempt occurred;
2. verify provider id was `openai`;
3. verify dispatch authorization hash;
4. verify live request artifact hash;
5. verify live response artifact hash or live error artifact hash;
6. verify no retry occurred;
7. verify no fallback occurred;
8. verify no worker invocation occurred;
9. verify no provider routing occurred;
10. verify no credential secret was replayed;
11. verify no authorization header was replayed;
12. verify provider output was cognition-only or failed closed;
13. verify governance was not modified;
14. verify replay was not mutated.

Allowed audit verdicts:

```text
POST_DISPATCH_AUDIT_PASS
POST_DISPATCH_AUDIT_FAIL_CLOSED
```

## Post-Dispatch Recertification Procedure

Recertification must verify:

- HIRR certification preserved;
- ERR role preserved;
- ERR remained passive;
- provider contract preserved;
- OpenAI adapter boundary preserved;
- credential boundary preserved;
- transport boundary preserved;
- replay integrity preserved;
- fail-closed behavior preserved;
- authority boundary preserved;
- worker boundary preserved;
- governance boundary preserved.

Allowed recertification verdicts:

```text
FIRST_LIVE_PROVIDER_DISPATCH_CERTIFIED
FIRST_LIVE_PROVIDER_DISPATCH_NOT_CERTIFIED
```

If recertification fails, rollback must execute and no further dispatch may occur.

## Rollback Execution Procedure

Rollback must execute if:

- dispatch aborts before request;
- live error artifact is produced;
- authority-bearing output is detected;
- post-dispatch audit fails;
- post-dispatch recertification fails;
- replay integrity fails;
- credential replay violation is detected;
- more than one dispatch attempt is detected.

Rollback evidence must record:

- rollback execution id;
- triggering artifact hash;
- rollback reason;
- activation reuse disallowed;
- credential reuse disallowed;
- dispatch reuse disallowed;
- further live calls disallowed;
- secret material not retained;
- governance not modified;
- replay not modified.

Rollback must not:

- delete replay artifacts;
- mutate prior evidence;
- retry dispatch;
- invoke another provider;
- invoke a worker.

## Execution Evidence Model

Required success path:

```text
approval freshness revalidation
-> credential freshness revalidation
-> live request replay artifact
-> live response replay artifact
-> canonical output artifact
-> LLM_COGNITION_ARTIFACT_V1
-> post-dispatch audit packet
-> post-dispatch recertification packet
-> rollback not required evidence
-> dispatch execution packet
```

Required fail-closed path:

```text
approval freshness revalidation
-> credential freshness revalidation
-> live request replay artifact if request boundary was reached
-> live error replay artifact
-> post-dispatch audit packet
-> post-dispatch recertification packet
-> rollback execution artifact
-> dispatch execution packet
```

## Final Package Position

This package defines the execution evidence model and operational procedures for the one authorized dispatch attempt.

It does not execute the dispatch.

Final position:

```text
DISPATCH_EXECUTION_PACKAGE_SPECIFIED = YES
LIVE_OPENAI_INVOCATION_PERFORMED = NO
CREDENTIAL_DISCLOSED = NO
DISPATCH_EXECUTED = NO
```

## Recommendation

Proceed only to an explicitly controlled execution milestone:

```text
AIGOL_FIRST_LIVE_OPENAI_ONE_ATTEMPT_DISPATCH_EXECUTION_V1
```

That milestone must instantiate the execution packet, perform the final credential freshness check, execute at most one dispatch, and produce live request plus live response or live error replay evidence.
