# AIGOL First Live Provider Activation Package V1

Status: activation package specification.

Purpose: define the evidence package required before the first governed OpenAI invocation attempt.

This artifact is activation preparation only.

It does not invoke OpenAI.

It does not disclose credentials.

It does not authorize live invocation by itself.

It does not modify ERR, OCS, replay, governance, transport, or credential runtime behavior.

## Context

This activation package follows:

```text
HIRR_CERTIFIED = YES
ERR_ROLE = UNIVERSAL_RESOURCE_REGISTRY
PROVIDER_ARCHITECTURE_COMPLETE = YES
PROVIDER_GOVERNANCE_COMPLETE = YES
PROVIDER_RUNTIME_COMPLETE = YES
HTTP_TRANSPORT_BOUNDARY_COMPLETE = YES
AIGOL_FIRST_LIVE_PROVIDER_ACTIVATION_AUDIT_V1
```

Activation audit determination:

```text
ONLY_ACTIVATION_AND_OPERATIONAL_AUTHORIZATION_REMAIN = YES
FIRST_LIVE_PROVIDER_ACTIVATION_READY = NO
```

Reason:

```text
CONCRETE_LIVE_APPROVAL_INSTANCE = MISSING
LIVE_HTTP_DISPATCH_ACTIVATION = MISSING
LIVE_CREDENTIAL_AVAILABILITY_EVENT = MISSING
```

## Package Boundary

The activation package prepares one governed OpenAI invocation attempt.

Allowed:

- one replay-visible approval artifact;
- one activation authorization artifact;
- one credential availability evidence artifact;
- one live dispatch evidence sequence;
- one post-dispatch audit packet;
- one post-dispatch recertification packet;
- one rollback evidence artifact.

Prohibited:

- live OpenAI invocation during package preparation;
- credential disclosure;
- credential value replay;
- provider routing;
- provider ranking;
- provider fallback;
- provider comparison;
- worker invocation;
- tool use;
- governance mutation;
- replay mutation;
- ERR behavior changes;
- OCS architecture changes.

## Activation Evidence Sequence

Required package sequence:

```text
001 approval artifact
002 activation authorization artifact
003 credential availability evidence
004 live dispatch evidence
005 post-dispatch audit packet
006 post-dispatch recertification packet
007 rollback evidence
```

The package is valid only if all artifacts are replay-visible, hash-linked, immutable, and secret-free.

## Approval Artifact

Artifact type:

```text
FIRST_LIVE_PROVIDER_APPROVAL_ARTIFACT_V1
```

Purpose:

Record the human approval instance for exactly one governed OpenAI invocation attempt.

Required fields:

- `artifact_type`;
- `approval_id`;
- `approved_by`;
- `approval_status`;
- `approval_granted`;
- `approved_provider_id`;
- `approved_resource_type`;
- `required_capability`;
- `approved_runtime_path`;
- `approved_transport_boundary`;
- `approved_canonical_contract`;
- `approved_scope`;
- `one_time_use`;
- `expires_at`;
- `created_at`;
- `replay_dir_reference`;
- `credential_policy_reference`;
- `rollback_required`;
- `recertification_required`;
- `worker_invocation_allowed`;
- `provider_routing_allowed`;
- `governance_mutation_allowed`;
- `replay_mutation_allowed`;
- `credential_secret_replayed`;
- `artifact_hash`.

Required values:

```text
approval_status = APPROVED
approval_granted = true
approved_provider_id = openai
approved_resource_type = COGNITION_PROVIDER
approved_scope = SINGLE_PROVIDER_SINGLE_LIVE_INVOCATION
one_time_use = true
worker_invocation_allowed = false
provider_routing_allowed = false
governance_mutation_allowed = false
replay_mutation_allowed = false
credential_secret_replayed = false
```

Fail-closed if:

- approval is missing;
- approval is expired;
- approval is not one-time;
- approved provider is not `openai`;
- approval permits workers, routing, fallback, ranking, governance mutation, or replay mutation;
- approval contains secret material.

## Activation Authorization Artifact

Artifact type:

```text
FIRST_LIVE_PROVIDER_ACTIVATION_AUTHORIZATION_ARTIFACT_V1
```

Purpose:

Record that the approved package may proceed to exactly one live dispatch attempt.

Required fields:

- `artifact_type`;
- `activation_id`;
- `approval_artifact_hash`;
- `provider_id`;
- `runtime_path`;
- `transport_boundary`;
- `activation_status`;
- `activation_scope`;
- `activation_attempt_limit`;
- `live_dispatch_allowed`;
- `live_dispatch_count_limit`;
- `activation_expires_at`;
- `created_at`;
- `replay_visible`;
- `credential_secret_replayed`;
- `worker_invocation_allowed`;
- `provider_routing_allowed`;
- `fallback_allowed`;
- `automatic_retry_allowed`;
- `governance_mutation_allowed`;
- `replay_mutation_allowed`;
- `artifact_hash`.

Required values:

```text
activation_status = AUTHORIZED
provider_id = openai
activation_scope = ONE_GOVERNED_OPENAI_INVOCATION
activation_attempt_limit = 1
live_dispatch_allowed = true
live_dispatch_count_limit = 1
credential_secret_replayed = false
worker_invocation_allowed = false
provider_routing_allowed = false
fallback_allowed = false
automatic_retry_allowed = false
governance_mutation_allowed = false
replay_mutation_allowed = false
```

Fail-closed if:

- activation authorization is missing;
- activation is not linked to approval;
- activation allows more than one dispatch;
- activation authorizes retries, fallback, routing, workers, governance mutation, or replay mutation;
- activation is expired.

## Live Credential Availability Evidence

Artifact type:

```text
FIRST_LIVE_PROVIDER_CREDENTIAL_AVAILABILITY_ARTIFACT_V1
```

Purpose:

Prove that an approved secret authority made an OpenAI credential available without replaying the credential.

Required fields:

- `artifact_type`;
- `credential_availability_id`;
- `approval_artifact_hash`;
- `activation_authorization_artifact_hash`;
- `provider_id`;
- `credential_policy_artifact_hash`;
- `credential_reference_type`;
- `secret_authority`;
- `credential_available`;
- `credential_checked_at`;
- `credential_secret_stored`;
- `credential_secret_replayed`;
- `credential_value_omitted`;
- `credential_hash_recorded`;
- `rotation_status_checked`;
- `revocation_status_checked`;
- `created_at`;
- `artifact_hash`.

Required values:

```text
provider_id = openai
credential_available = true
credential_secret_stored = false
credential_secret_replayed = false
credential_value_omitted = true
credential_hash_recorded = false
rotation_status_checked = true
revocation_status_checked = true
```

Allowed credential evidence:

- external credential reference type;
- secret authority identifier;
- boolean availability result;
- rotation status checked;
- revocation status checked;
- timestamp;
- artifact hashes.

Prohibited credential evidence:

- API key value;
- bearer token value;
- partial secret;
- reversible secret encoding;
- secret hash;
- authorization header value;
- secret manager response body.

Fail-closed if:

- credential is unavailable;
- credential authority is not approved;
- credential appears in replay;
- credential reference is inline secret material;
- rotation or revocation status cannot be checked.

## Live Dispatch Evidence

Artifact family:

```text
FIRST_LIVE_PROVIDER_DISPATCH_ATTEMPT_ARTIFACT_V1
FIRST_LIVE_PROVIDER_DISPATCH_RESPONSE_ARTIFACT_V1
FIRST_LIVE_PROVIDER_DISPATCH_ERROR_ARTIFACT_V1
```

Purpose:

Record exactly one live OpenAI dispatch attempt and its response or fail-closed error.

### Dispatch Attempt

Required fields:

- `artifact_type`;
- `dispatch_id`;
- `approval_artifact_hash`;
- `activation_authorization_artifact_hash`;
- `credential_availability_artifact_hash`;
- `err_selection_artifact_hash`;
- `canonical_input_artifact_hash`;
- `provider_id`;
- `provider_schema_id`;
- `endpoint`;
- `http_method`;
- `request_payload_hash`;
- `request_created_at`;
- `live_dispatch_attempted`;
- `dispatch_attempt_number`;
- `dispatch_attempt_limit`;
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
live_dispatch_attempted = true
dispatch_attempt_number = 1
dispatch_attempt_limit = 1
credential_secret_replayed = false
authorization_header_replayed = false
worker_invoked = false
provider_routing_performed = false
governance_modified = false
replay_modified = false
```

### Dispatch Response

Required fields:

- `artifact_type`;
- `dispatch_response_id`;
- `dispatch_attempt_artifact_hash`;
- `provider_id`;
- `http_status_code`;
- `response_received`;
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
- `governance_modified`;
- `replay_modified`;
- `artifact_hash`.

Required values:

```text
provider_id = openai
response_received = true
provider_output_trust = UNTRUSTED
provider_output_authority = NONE
authority_boundary_validation = PASS
credential_secret_replayed = false
authorization_header_replayed = false
worker_invoked = false
governance_modified = false
replay_modified = false
```

### Dispatch Error

Required fields:

- `artifact_type`;
- `dispatch_error_id`;
- `dispatch_attempt_artifact_hash`;
- `provider_id`;
- `error_classification`;
- `failure_reason`;
- `response_received`;
- `retry_attempted`;
- `fallback_attempted`;
- `credential_secret_replayed`;
- `authorization_header_replayed`;
- `worker_invoked`;
- `governance_modified`;
- `replay_modified`;
- `created_at`;
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
- `ACTIVATION_SCOPE_VIOLATION`.

Required values:

```text
retry_attempted = false
fallback_attempted = false
credential_secret_replayed = false
authorization_header_replayed = false
worker_invoked = false
governance_modified = false
replay_modified = false
```

## Post-Dispatch Audit Packet

Artifact type:

```text
FIRST_LIVE_PROVIDER_POST_DISPATCH_AUDIT_PACKET_V1
```

Purpose:

Summarize the live attempt outcome and verify boundary preservation.

Required fields:

- `artifact_type`;
- `audit_packet_id`;
- `approval_artifact_hash`;
- `activation_authorization_artifact_hash`;
- `credential_availability_artifact_hash`;
- `dispatch_attempt_artifact_hash`;
- `dispatch_response_artifact_hash`;
- `dispatch_error_artifact_hash`;
- `final_status`;
- `provider_id`;
- `attempt_count`;
- `worker_invocation_observed`;
- `provider_routing_observed`;
- `fallback_observed`;
- `credential_secret_replayed`;
- `authorization_header_replayed`;
- `authority_boundary_result`;
- `canonical_output_created`;
- `llm_cognition_artifact_created`;
- `governance_modified`;
- `replay_modified`;
- `audit_created_at`;
- `artifact_hash`.

Allowed final statuses:

```text
LIVE_PROVIDER_INVOCATION_COMPLETED
LIVE_PROVIDER_INVOCATION_FAILED_CLOSED
LIVE_PROVIDER_INVOCATION_ABORTED
```

Required invariants:

```text
provider_id = openai
attempt_count <= 1
worker_invocation_observed = false
provider_routing_observed = false
fallback_observed = false
credential_secret_replayed = false
authorization_header_replayed = false
governance_modified = false
replay_modified = false
```

## Post-Dispatch Recertification Packet

Artifact type:

```text
FIRST_LIVE_PROVIDER_POST_DISPATCH_RECERTIFICATION_PACKET_V1
```

Purpose:

Determine whether the first live invocation evidence preserves HIRR, ERR, provider, credential, transport, and replay certification boundaries.

Required fields:

- `artifact_type`;
- `recertification_id`;
- `post_dispatch_audit_packet_hash`;
- `hirr_certification_preserved`;
- `err_role_preserved`;
- `provider_contract_preserved`;
- `credential_boundary_preserved`;
- `transport_boundary_preserved`;
- `replay_integrity_preserved`;
- `fail_closed_integrity_preserved`;
- `authority_boundary_preserved`;
- `worker_boundary_preserved`;
- `governance_boundary_preserved`;
- `recertification_verdict`;
- `recertification_created_at`;
- `artifact_hash`.

Allowed verdicts:

```text
FIRST_LIVE_PROVIDER_INVOCATION_CERTIFIED
FIRST_LIVE_PROVIDER_INVOCATION_NOT_CERTIFIED
```

Required pass values:

```text
hirr_certification_preserved = true
err_role_preserved = true
provider_contract_preserved = true
credential_boundary_preserved = true
transport_boundary_preserved = true
replay_integrity_preserved = true
fail_closed_integrity_preserved = true
authority_boundary_preserved = true
worker_boundary_preserved = true
governance_boundary_preserved = true
```

## Rollback Evidence

Artifact type:

```text
FIRST_LIVE_PROVIDER_ROLLBACK_EVIDENCE_ARTIFACT_V1
```

Purpose:

Record that the activation package can terminate safely after success, fail-closed result, abort, or post-dispatch certification failure.

Required fields:

- `artifact_type`;
- `rollback_id`;
- `approval_artifact_hash`;
- `activation_authorization_artifact_hash`;
- `post_dispatch_audit_packet_hash`;
- `post_dispatch_recertification_packet_hash`;
- `rollback_required`;
- `rollback_status`;
- `activation_reuse_allowed`;
- `credential_reuse_allowed`;
- `dispatch_reuse_allowed`;
- `further_live_calls_allowed`;
- `cleanup_completed`;
- `secret_material_retained`;
- `governance_modified`;
- `replay_modified`;
- `created_at`;
- `artifact_hash`.

Allowed rollback statuses:

```text
ROLLBACK_NOT_REQUIRED_AFTER_CERTIFIED_SINGLE_ATTEMPT
ROLLBACK_COMPLETED_AFTER_FAILED_CLOSED_ATTEMPT
ROLLBACK_COMPLETED_AFTER_ABORT
ROLLBACK_COMPLETED_AFTER_RECERTIFICATION_FAILURE
```

Required values:

```text
activation_reuse_allowed = false
credential_reuse_allowed = false
dispatch_reuse_allowed = false
further_live_calls_allowed = false
secret_material_retained = false
governance_modified = false
replay_modified = false
```

## Success Criteria

Activation package success requires:

1. replay-visible approval exists;
2. approval is one-time, scoped to `openai`, unexpired, and human-authorized;
3. activation authorization exists and allows exactly one live dispatch;
4. credential availability evidence exists without secret replay;
5. ERR selection resolves `openai`;
6. canonical provider input is created;
7. exactly one live dispatch attempt is recorded;
8. response is captured or error is fail-closed;
9. provider output is non-authoritative;
10. authority-boundary validation passes or fails closed;
11. canonical output and `LLM_COGNITION_ARTIFACT_V1` are produced on success;
12. post-dispatch audit packet is produced;
13. post-dispatch recertification packet is produced;
14. rollback evidence is produced;
15. no worker invocation occurs;
16. no provider routing, ranking, fallback, or comparison occurs;
17. no credential secret or authorization header is replayed;
18. governance is not modified;
19. replay is not mutated;
20. replay reconstruction passes.

Success verdict:

```text
FIRST_LIVE_PROVIDER_ACTIVATION_PACKAGE_VALID = YES
LIVE_OPENAI_CALL_ALLOWED = ONE_APPROVED_ATTEMPT_ONLY
```

## Failure Criteria

The package must fail closed if:

1. approval is missing, expired, malformed, reused, or out of scope;
2. activation authorization is missing, expired, reused, or allows more than one attempt;
3. credential availability is missing or secret material appears in replay;
4. ERR does not select `openai`;
5. canonical input cannot be created;
6. live dispatch evidence cannot be written immutably;
7. live dispatch attempts exceed one;
8. timeout, rate-limit, authentication, transport, malformed-response, or replay failure occurs;
9. provider output is authority-bearing;
10. provider output cannot be normalized;
11. `LLM_COGNITION_ARTIFACT_V1` cannot be produced on success;
12. worker invocation is attempted;
13. tool use is attempted;
14. routing, fallback, ranking, or comparison is attempted;
15. governance mutation is attempted;
16. replay mutation is attempted;
17. post-dispatch audit is missing;
18. recertification fails or is missing;
19. rollback evidence is missing.

Failure verdict:

```text
FIRST_LIVE_PROVIDER_ACTIVATION_PACKAGE_VALID = NO
LIVE_OPENAI_CALL_ALLOWED = NO
FINAL_STATUS = FAILED_CLOSED
```

## Acceptance Checklist

Before any live invocation attempt, the activation package must answer `YES` to all of:

```text
APPROVAL_ARTIFACT_PRESENT
ACTIVATION_AUTHORIZATION_PRESENT
CREDENTIAL_AVAILABILITY_EVIDENCE_PRESENT
ERR_OPENAI_SELECTION_EVIDENCE_PRESENT
CANONICAL_INPUT_EVIDENCE_PRESENT
LIVE_DISPATCH_EVIDENCE_READY
POST_DISPATCH_AUDIT_REQUIRED
POST_DISPATCH_RECERTIFICATION_REQUIRED
ROLLBACK_EVIDENCE_REQUIRED
NO_SECRET_REPLAY_CONFIRMED
NO_WORKER_INVOCATION_CONFIRMED
NO_GOVERNANCE_MUTATION_CONFIRMED
NO_REPLAY_MUTATION_CONFIRMED
ONE_ATTEMPT_LIMIT_CONFIRMED
```

## Final Recommendation

Use this package as the required activation gate for:

```text
AIGOL_FIRST_LIVE_OPENAI_ACTIVATION_V1
```

Do not perform a live OpenAI invocation until this package is instantiated as replay-visible evidence and approved for exactly one attempt.

Final package position:

```text
ACTIVATION_PACKAGE_SPECIFIED = YES
LIVE_OPENAI_INVOCATION_PERFORMED = NO
CREDENTIAL_DISCLOSED = NO
LIVE_OPENAI_CALL_ALLOWED_NOW = NO
LIVE_OPENAI_CALL_ALLOWED_AFTER_PACKAGE_APPROVAL = ONE_ATTEMPT_ONLY
```
