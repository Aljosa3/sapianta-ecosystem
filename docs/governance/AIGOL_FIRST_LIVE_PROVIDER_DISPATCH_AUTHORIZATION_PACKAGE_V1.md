# AIGOL First Live Provider Dispatch Authorization Package V1

Status: dispatch authorization package specification.

Purpose: define the concrete authorization package required to permit exactly one governed OpenAI dispatch attempt.

This artifact is an authorization package only.

It does not invoke OpenAI.

It does not disclose credentials.

It does not execute dispatch.

It does not modify ERR, OCS, replay, governance, transport, or credential runtime behavior.

## Context

This package follows:

```text
AIGOL_FIRST_LIVE_PROVIDER_ACTIVATION_PACKAGE_V1
AIGOL_FIRST_LIVE_PROVIDER_ACTIVATION_PACKAGE_INSTANTIATION_V1
AIGOL_FIRST_LIVE_PROVIDER_ACTIVATION_CLOSURE_AUDIT_V1
AIGOL_FIRST_LIVE_PROVIDER_EXECUTION_AUTHORIZATION_AUDIT_V1
```

Current verdict:

```text
FIRST_LIVE_PROVIDER_EXECUTION_NOT_AUTHORIZED
```

Reason:

```text
LIVE_DISPATCH_AUTHORIZATION_PRESENT = NO
```

Current dispatch state:

```text
DISPATCH_STATUS = ARMED_NOT_DISPATCHED
LIVE_DISPATCH_ATTEMPTED = false
LIVE_DISPATCH_PERFORMED = false
```

## Package Boundary

The dispatch authorization package may authorize exactly one OpenAI dispatch attempt only after all pre-dispatch validations pass.

Allowed:

- one dispatch authorization artifact;
- one approval freshness validation;
- one credential freshness validation;
- one dispatch readiness decision;
- one allow or deny decision;
- replay-visible decision evidence.

Prohibited:

- live OpenAI invocation during package preparation;
- credential disclosure;
- credential value replay;
- authorization header replay;
- provider routing;
- provider ranking;
- provider fallback;
- provider comparison;
- automatic retry;
- worker invocation;
- tool use;
- governance mutation;
- replay mutation.

## Dispatch Authorization Artifact Schema

Artifact type:

```text
FIRST_LIVE_PROVIDER_DISPATCH_AUTHORIZATION_ARTIFACT_V1
```

Purpose:

Record the final authorization decision for exactly one governed OpenAI dispatch attempt.

Required fields:

- `artifact_type`;
- `dispatch_authorization_id`;
- `activation_package_id`;
- `approval_artifact_hash`;
- `activation_authorization_artifact_hash`;
- `credential_availability_artifact_hash`;
- `dispatch_attempt_artifact_hash`;
- `post_dispatch_audit_template_hash`;
- `post_dispatch_recertification_template_hash`;
- `rollback_evidence_artifact_hash`;
- `provider_id`;
- `provider_resource_type`;
- `required_capability`;
- `authorization_status`;
- `authorization_scope`;
- `dispatch_attempt_limit`;
- `dispatch_attempt_number_authorized`;
- `cognition_only_response_required`;
- `approval_freshness_validation_hash`;
- `credential_freshness_validation_hash`;
- `dispatch_conditions_hash`;
- `denial_conditions_hash`;
- `created_at`;
- `expires_at`;
- `replay_visible`;
- `credential_secret_replayed`;
- `authorization_header_replayed`;
- `worker_invocation_allowed`;
- `provider_routing_allowed`;
- `fallback_allowed`;
- `automatic_retry_allowed`;
- `tool_use_allowed`;
- `governance_mutation_allowed`;
- `replay_mutation_allowed`;
- `artifact_hash`.

Allowed authorization statuses:

```text
DISPATCH_AUTHORIZED
DISPATCH_DENIED
```

Required values for authorization:

```text
provider_id = openai
provider_resource_type = COGNITION_PROVIDER
authorization_scope = ONE_GOVERNED_OPENAI_DISPATCH_ATTEMPT
dispatch_attempt_limit = 1
dispatch_attempt_number_authorized = 1
cognition_only_response_required = true
credential_secret_replayed = false
authorization_header_replayed = false
worker_invocation_allowed = false
provider_routing_allowed = false
fallback_allowed = false
automatic_retry_allowed = false
tool_use_allowed = false
governance_mutation_allowed = false
replay_mutation_allowed = false
```

## Authorization Scope

Scope:

```text
EXACTLY_ONE_PROVIDER = openai
EXACTLY_ONE_RESOURCE_TYPE = COGNITION_PROVIDER
EXACTLY_ONE_DISPATCH_ATTEMPT = 1
ALLOWED_OUTPUT_CLASS = cognition_only
```

The authorization does not permit:

- any second dispatch;
- retries;
- fallback;
- provider switching;
- worker invocation;
- tool use;
- execution authorization;
- governance mutation;
- replay mutation.

Provider output remains:

```text
PROVIDER_OUTPUT_TRUST = UNTRUSTED
PROVIDER_OUTPUT_AUTHORITY = NONE
```

## Approval Freshness Validation

Artifact type:

```text
FIRST_LIVE_PROVIDER_APPROVAL_FRESHNESS_VALIDATION_ARTIFACT_V1
```

Required checks:

- approval artifact hash matches instantiated package;
- approval provider is `openai`;
- approval resource type is `COGNITION_PROVIDER`;
- approval scope is single live invocation;
- approval is one-time use;
- approval has not expired;
- approval has not been used;
- approval has not been revoked;
- approval does not permit workers;
- approval does not permit routing, fallback, ranking, comparison, tools, governance mutation, or replay mutation;
- approval contains no secret material.

Required output:

```text
APPROVAL_FRESHNESS_VALIDATION = PASS
```

Fail closed if any check fails.

## Credential Freshness Validation

Artifact type:

```text
FIRST_LIVE_PROVIDER_CREDENTIAL_FRESHNESS_VALIDATION_ARTIFACT_V1
```

Required checks:

- credential availability artifact hash matches instantiated package;
- credential policy artifact hash matches instantiated package;
- secret authority remains approved;
- credential remains available;
- credential has not been revoked;
- credential rotation status is acceptable;
- credential value is not replayed;
- credential hash is not recorded;
- authorization header is not replayed;
- no provider output contains credential instructions.

Required output:

```text
CREDENTIAL_FRESHNESS_VALIDATION = PASS
```

Fail closed if:

- credential is unavailable;
- credential authority is not approved;
- credential is revoked;
- rotation status cannot be checked;
- credential value, bearer token, partial secret, secret hash, or authorization header appears in replay.

## Dispatch Execution Conditions

Dispatch may be authorized only if all are true:

1. instantiated activation package reconstructs successfully;
2. approval freshness validation passes;
3. credential freshness validation passes;
4. ERR selection evidence still resolves `openai`;
5. dispatch artifact status is `ARMED_NOT_DISPATCHED`;
6. live dispatch attempted is false;
7. live dispatch performed is false;
8. dispatch attempt limit equals one;
9. provider id is `openai`;
10. canonical provider contract evidence exists;
11. HTTP transport boundary is available;
12. replay path is writable and append-only;
13. post-dispatch audit template exists;
14. post-dispatch recertification template exists;
15. rollback evidence exists;
16. no worker invocation path is present;
17. no routing, fallback, ranking, comparison, retry, or tool path is present;
18. no governance mutation path is present;
19. no replay mutation path is present.

If all conditions pass, the authorization artifact may record:

```text
authorization_status = DISPATCH_AUTHORIZED
```

This status authorizes exactly one dispatch attempt and nothing else.

## Dispatch Denial Conditions

Dispatch must be denied if any are true:

1. activation package reconstruction fails;
2. approval is missing, expired, revoked, used, malformed, or out of scope;
3. credential freshness validation fails;
4. credential material appears in replay;
5. ERR does not resolve `openai`;
6. dispatch status is not `ARMED_NOT_DISPATCHED`;
7. live dispatch has already been attempted;
8. live dispatch has already been performed;
9. dispatch attempt limit is not one;
10. provider id is not `openai`;
11. provider output boundary is not cognition-only;
12. worker invocation is possible or requested;
13. routing, fallback, ranking, comparison, automatic retry, or tool use is possible or requested;
14. governance mutation is possible or requested;
15. replay mutation is possible or requested;
16. post-dispatch audit template is missing;
17. post-dispatch recertification template is missing;
18. rollback evidence is missing.

If any condition fails, the authorization artifact must record:

```text
authorization_status = DISPATCH_DENIED
```

Denied dispatch must produce replay-visible denial evidence and no OpenAI request.

## Required Replay Evidence

Before dispatch authorization:

- activation package reconstruction result;
- approval freshness validation artifact;
- credential freshness validation artifact;
- dispatch readiness validation artifact;
- dispatch authorization artifact.

If dispatch is authorized and later executed:

- live dispatch attempt artifact;
- live request artifact;
- live response artifact or live error artifact;
- no-secret replay validation;
- authority-boundary validation;
- canonical provider output artifact on success;
- `LLM_COGNITION_ARTIFACT_V1` on success;
- fail-closed evidence on error.

If dispatch is denied:

- dispatch denial artifact;
- denial reason;
- rollback or abort evidence;
- no OpenAI request evidence.

Replay invariants:

```text
NO_SECRET_REPLAY = true
NO_AUTHORIZATION_HEADER_REPLAY = true
NO_WORKER_INVOCATION = true
NO_PROVIDER_ROUTING = true
NO_GOVERNANCE_MUTATION = true
NO_REPLAY_MUTATION = true
```

## Post-Dispatch Audit Requirements

Post-dispatch audit must verify:

- exactly one dispatch attempt occurred;
- provider id was `openai`;
- no second dispatch occurred;
- no retry occurred;
- no fallback occurred;
- no worker invocation occurred;
- no tool use occurred;
- no credential secret was replayed;
- no authorization header was replayed;
- provider output was cognition-only or failed closed;
- authority-bearing output was rejected;
- canonical output was produced on success;
- `LLM_COGNITION_ARTIFACT_V1` was produced on success;
- error evidence was produced on fail-closed outcome;
- governance was not modified;
- replay was not mutated.

Post-dispatch audit may produce:

```text
POST_DISPATCH_AUDIT_PASS
POST_DISPATCH_AUDIT_FAIL_CLOSED
```

## Rollback Execution Requirements

Rollback must execute if:

- dispatch is denied;
- dispatch fails closed;
- post-dispatch audit fails;
- post-dispatch recertification fails;
- authority-bearing provider output is detected;
- replay integrity fails;
- credential replay violation is detected;
- more than one dispatch is attempted.

Rollback must record:

- rollback id;
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

## Recertification Requirements

Post-dispatch recertification must verify:

- HIRR certification preserved;
- ERR role preserved as universal resource registry;
- ERR remained passive;
- canonical provider contract preserved;
- OpenAI adapter boundary preserved;
- credential boundary preserved;
- transport boundary preserved;
- replay integrity preserved;
- fail-closed behavior preserved;
- authority boundary preserved;
- worker boundary preserved;
- governance boundary preserved;
- no routing, ranking, fallback, retry, worker, tool, governance mutation, or replay mutation was introduced.

Allowed recertification verdicts:

```text
FIRST_LIVE_PROVIDER_DISPATCH_CERTIFIED
FIRST_LIVE_PROVIDER_DISPATCH_NOT_CERTIFIED
```

## Final Package Position

This package defines the missing dispatch authorization layer.

It does not instantiate or execute that authorization.

Final position:

```text
DISPATCH_AUTHORIZATION_PACKAGE_SPECIFIED = YES
DISPATCH_AUTHORIZATION_ARTIFACT_SCHEMA_DEFINED = YES
LIVE_OPENAI_INVOCATION_PERFORMED = NO
CREDENTIAL_DISCLOSED = NO
DISPATCH_EXECUTED = NO
LIVE_OPENAI_CALL_ALLOWED_NOW = NO
```

## Recommendation

Proceed only to a package instantiation milestone:

```text
AIGOL_FIRST_LIVE_PROVIDER_DISPATCH_AUTHORIZATION_PACKAGE_INSTANTIATION_V1
```

That milestone should instantiate:

- approval freshness validation artifact;
- credential freshness validation artifact;
- dispatch readiness validation artifact;
- dispatch authorization or dispatch denial artifact.

It must still not perform a live OpenAI invocation unless a later explicit dispatch execution milestone is approved.
