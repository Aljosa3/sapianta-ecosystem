# AIGOL Live Provider Transport Boundary V1

Status: architecture design.

Purpose: define the governed transport boundary for the first live OpenAI provider invocation.

This artifact is design only.

It does not implement live transport.

It does not implement authentication.

It does not retrieve credentials.

It does not invoke OpenAI.

## Context

Current architectural baseline:

```text
ERR_ROLE = UNIVERSAL_RESOURCE_REGISTRY
```

Bounded interpretation:

```text
ERR = passive capability-based registry for governed resource metadata,
currently limited to COGNITION_PROVIDER and EXECUTION_WORKER.
```

The first live invocation remains blocked by:

- live transport;
- authentication retrieval;
- live replay artifacts;
- timeout handling;
- rate-limit handling;
- malformed response handling.

This artifact defines the transport boundary required to remove those blockers in a later implementation milestone.

## Boundary Position

The live transport boundary sits after:

```text
human approval
-> credential policy
-> ERR metadata selection
-> canonical provider input
-> adapter request view
```

The transport boundary sits before:

```text
canonical provider output
-> LLM_COGNITION_ARTIFACT_V1
-> audit packet
-> replay reconstruction
```

Transport is not ERR.

Transport is not governance.

Transport is not OCS orchestration.

Transport is not worker assignment.

## Transport Boundary Responsibilities

The live transport boundary is responsible only for:

1. validating a replay-visible approval reference;
2. validating the selected provider is `openai`;
3. validating the canonical provider input hash;
4. validating the credential policy reference;
5. retrieving a credential through a governed non-replay boundary;
6. constructing the provider request payload from canonical input;
7. performing exactly one approved OpenAI request;
8. recording request-attempt metadata without secrets;
9. recording response metadata and bounded raw response evidence;
10. recording provider error evidence when the call fails;
11. classifying timeout, rate-limit, and malformed-response conditions;
12. failing closed on any boundary violation.

The transport boundary must not:

- select providers;
- rank providers;
- compare providers;
- fall back to another provider;
- invoke workers;
- call tools;
- authorize execution;
- mutate governance;
- mutate replay;
- expand ERR;
- become ELL.

## Secret Handling Model

Credential material is never replay evidence.

Allowed replay-visible credential fields:

- credential policy artifact hash;
- credential reference id;
- credential retrieval boundary id;
- credential presence boolean;
- credential redaction status;
- retrieval timestamp;
- retrieval result classification.

Prohibited replay-visible credential fields:

- API key value;
- bearer token value;
- authorization header value;
- raw environment variable value;
- secret manager response body;
- any reversible secret encoding;
- partial secret prefix or suffix unless separately approved by governance.

Required invariant:

```text
CREDENTIAL_SECRET_REPLAYED = false
```

If credential material appears in any replay artifact, the transport boundary must fail closed and mark live invocation invalid.

## Credential Retrieval Model

The credential retrieval model must use a policy reference, not inline secret material.

Required input:

```text
LIVE_PROVIDER_CREDENTIAL_POLICY_ARTIFACT_V1
```

Minimum policy fields:

- provider id: `openai`;
- credential reference: for example `env:AIGOL_OPENAI_API_KEY`;
- secret stored in artifact: false;
- secret replayed: false;
- retrieval boundary: explicit.

Retrieval sequence:

```text
credential policy artifact
-> credential reference validation
-> runtime secret lookup
-> non-empty credential presence check
-> secret redaction boundary
-> transport-only credential use
```

The credential may exist in process memory only long enough to build the live request authorization boundary.

The credential must not be copied into:

- replay artifact;
- audit packet;
- exception text;
- log text;
- provider output;
- canonical input;
- canonical output.

## Replay-Visible Transport Artifacts

The live transport implementation must add these artifacts.

### 1. Live Request Attempt

Artifact:

```text
LIVE_PROVIDER_REQUEST_ATTEMPT_ARTIFACT_V1
```

Required fields:

- invocation id;
- provider id;
- provider schema id;
- approval artifact hash;
- ERR selection artifact hash;
- credential policy artifact hash;
- canonical input artifact hash;
- adapter request artifact hash;
- request payload hash;
- timeout seconds;
- stream false;
- tool use false;
- retries disabled;
- credential secret replayed false;
- provider invoked false before dispatch;
- created at.

The request attempt must not contain the credential value.

### 2. Live Response Capture

Artifact:

```text
LIVE_PROVIDER_RESPONSE_CAPTURE_ARTIFACT_V1
```

Required fields:

- invocation id;
- provider id;
- request attempt artifact hash;
- response status;
- response timestamp;
- bounded raw response;
- raw response hash;
- extracted response text hash;
- canonical output adapter required true;
- untrusted provider output true;
- non-authoritative true;
- authority flags all false;
- credential secret replayed false;
- worker invoked false;
- governance modified false;
- replay modified false.

The raw response must be bounded and JSON-serializable.

### 3. Live Provider Error

Artifact:

```text
LIVE_PROVIDER_ERROR_ARTIFACT_V1
```

Required fields:

- invocation id;
- provider id;
- request attempt artifact hash if created;
- error class;
- error classification;
- error timestamp;
- retry attempted false;
- fallback attempted false;
- credential secret replayed false;
- final status `FAILED_CLOSED`;
- replay visible true.

Allowed error classifications:

- `TIMEOUT`;
- `RATE_LIMIT`;
- `MALFORMED_RESPONSE`;
- `TRANSPORT_UNAVAILABLE`;
- `AUTHENTICATION_UNAVAILABLE`;
- `CREDENTIAL_POLICY_INVALID`;
- `AUTHORITY_BOUNDARY_VIOLATION`;
- `REPLAY_WRITE_FAILURE`.

### 4. Live Transport Binding

Artifact:

```text
LIVE_PROVIDER_TRANSPORT_BINDING_ARTIFACT_V1
```

Required fields:

- invocation id;
- request attempt artifact hash;
- response capture artifact hash or error artifact hash;
- final status;
- provider id;
- live provider call performed boolean;
- replay reconstruction required true;
- credential secret replayed false;
- no worker invocation true;
- no governance mutation true;
- no replay mutation true.

## Timeout Handling

Timeout must be explicit, bounded, and replay-visible.

Requirements:

- timeout seconds must be declared before request dispatch;
- timeout value must be recorded in request attempt evidence;
- timeout must fail closed;
- no retry is allowed in V1;
- no fallback provider is allowed;
- timeout error evidence must be replay-visible.

Timeout output:

```text
error_classification = TIMEOUT
final_status = FAILED_CLOSED
retry_attempted = false
fallback_attempted = false
```

## Rate-Limit Handling

Rate limits must fail closed in V1.

Requirements:

- rate-limit response must be recorded as provider error evidence;
- no retry is allowed;
- no backoff scheduler is allowed;
- no provider fallback is allowed;
- no ranking or optimization is introduced.

Rate-limit output:

```text
error_classification = RATE_LIMIT
final_status = FAILED_CLOSED
retry_attempted = false
fallback_attempted = false
```

## Malformed Response Handling

Malformed response must fail closed.

Malformed includes:

- non-JSON response where JSON is required;
- JSON response without bounded response text;
- response exceeding size bounds;
- response containing authority-bearing output;
- response that cannot map to canonical provider output;
- response with non-serializable fields;
- response containing secret-like material.

Malformed output:

```text
error_classification = MALFORMED_RESPONSE
final_status = FAILED_CLOSED
canonical_output_created = false
```

Authority-bearing malformed output must use:

```text
error_classification = AUTHORITY_BOUNDARY_VIOLATION
```

## Fail-Closed Behavior

The transport boundary must fail closed if:

1. approval is missing, malformed, expired, or out of scope;
2. provider id is not `openai`;
3. ERR selection does not identify active `openai` metadata;
4. credential policy is missing or malformed;
5. credential retrieval fails;
6. credential material appears in replay;
7. canonical input hash is missing or invalid;
8. adapter request cannot be produced;
9. timeout occurs;
10. rate-limit occurs;
11. provider response is malformed;
12. provider response is authority-bearing;
13. response cannot be normalized to canonical output;
14. replay write fails;
15. worker invocation is attempted;
16. provider routing, fallback, ranking, comparison, or retry is attempted;
17. governance mutation is attempted;
18. replay mutation is attempted.

Fail-closed output must preserve:

```text
provider_invoked = false before dispatch failure
or live_provider_call_performed = true only if request crossed transport boundary
worker_invoked = false
governance_modified = false
replay_modified = false
credential_secret_replayed = false
```

If the request crossed the transport boundary before failure, replay evidence must record that fact without hiding the failed live attempt.

## Governance Boundaries

The transport boundary must preserve:

- Human authority;
- OCS orchestration;
- ERR passive registry role;
- provider cognition-only role;
- worker separation;
- replay immutability;
- fail-closed behavior.

Provider output remains:

```text
PROVIDER_OUTPUT_TRUST = UNTRUSTED
PROVIDER_OUTPUT_AUTHORITY = NONE
```

The provider may propose cognition.

The provider may not:

- approve;
- authorize;
- validate;
- dispatch;
- execute;
- invoke workers;
- select providers;
- mutate governance;
- mutate replay.

## ERR Passive Role Preservation

ERR may provide only:

- selected resource id;
- selected resource type;
- required capability;
- active selection evidence;
- registry hash.

ERR must not provide:

- endpoint credentials;
- transport handles;
- authentication material;
- dispatch instruction;
- invocation approval;
- retry policy;
- fallback policy;
- provider ranking;
- lifecycle state.

Required invariant:

```text
ERR_ROLE = PASSIVE UNIVERSAL RESOURCE REGISTRY
ERR_PROVIDER_INVOKED = false
ERR_WORKER_INVOKED = false
```

## Acceptance Criteria

The future implementation of this boundary is acceptable only if:

1. no live call occurs without replay-visible approval;
2. exactly one provider is allowed: `openai`;
3. credentials are retrieved only through policy reference;
4. credentials are never replayed;
5. request attempt artifact is written before dispatch;
6. response capture or error artifact is written after dispatch;
7. timeout fails closed;
8. rate-limit fails closed;
9. malformed response fails closed;
10. authority-bearing output fails closed;
11. no retry is performed;
12. no fallback is performed;
13. no worker is invoked;
14. no tool use is enabled;
15. no routing, ranking, or comparison is introduced;
16. canonical output is required before cognition normalization;
17. `LLM_COGNITION_ARTIFACT_V1` remains the normalized cognition artifact;
18. audit packet links approval, ERR selection, credential policy, request attempt, response or error, canonical output if present, and cognition artifact if present;
19. replay reconstruction passes;
20. ERR remains passive.

Acceptance output:

```text
LIVE_PROVIDER_TRANSPORT_BOUNDARY_DEFINED = YES
LIVE_PROVIDER_TRANSPORT_IMPLEMENTED = NO
LIVE_PROVIDER_INVOKED = NO
AUTHENTICATION_IMPLEMENTED = NO
```

## Implementation Plan

Recommended next implementation milestone:

```text
AIGOL_FIRST_LIVE_OPENAI_TRANSPORT_BOUNDARY_IMPLEMENTATION_V1
```

Minimal implementation sequence:

1. add request-attempt artifact model;
2. add credential retrieval boundary using existing credential policy reference;
3. add secret redaction checks;
4. add single OpenAI transport function behind explicit approval;
5. add response capture artifact;
6. add provider error artifact;
7. add transport binding artifact;
8. add timeout fail-closed test;
9. add rate-limit fail-closed test;
10. add malformed-response fail-closed test;
11. add credential-not-replayed test;
12. add no-routing/no-fallback/no-worker tests;
13. integrate canonical output adapter;
14. integrate cognition artifact normalization;
15. extend live audit packet evidence.

The implementation must run first against deterministic transport fixtures before any real live call is attempted.

## Final Recommendation

Adopt this transport boundary design as the governed architecture for the first live OpenAI invocation.

Do not implement or perform a live OpenAI call until the transport boundary implementation has tests proving replay, credential, timeout, rate-limit, malformed-response, authority, and ERR-passivity guarantees.

Final status:

```text
AIGOL_LIVE_PROVIDER_TRANSPORT_BOUNDARY_V1 = PREPARED
LIVE_OPENAI_CALL_ALLOWED_NOW = NO
ERR_REMAINS_PASSIVE = YES
NEXT_STEP = FIRST_LIVE_OPENAI_TRANSPORT_BOUNDARY_IMPLEMENTATION
```
