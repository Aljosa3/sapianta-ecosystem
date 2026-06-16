# AIGOL Live Provider Credential Boundary V1

Status: architecture design.

Purpose: define the governed credential boundary for live provider invocation.

This artifact is design only.

It does not implement authentication.

It does not implement secret storage.

It does not retrieve credentials.

It does not invoke a live provider.

## Context

This boundary follows:

```text
AIGOL_LIVE_PROVIDER_INVOCATION_GOVERNANCE_V1
AIGOL_LIVE_PROVIDER_INVOCATION_PREREQUISITES_V1
AIGOL_LIVE_PROVIDER_TRANSPORT_BOUNDARY_V1
AIGOL_ERR_ARCHITECTURAL_ROLE_AUDIT_V1
```

Current invariant:

```text
ERR_ROLE = PASSIVE UNIVERSAL RESOURCE REGISTRY
```

ERR may identify `openai` metadata.

ERR must not store, retrieve, expose, or transport credentials.

## Credential Boundary Position

The credential boundary sits between:

```text
credential policy artifact
-> credential reference validation
```

and:

```text
transport-only credential use
-> live request dispatch
```

It is not:

- ERR;
- OCS orchestration;
- governance authority;
- provider selection;
- worker assignment;
- replay storage for secrets;
- authentication implementation in this design artifact.

## Credential Ownership Model

Credential ownership belongs outside AiGOL runtime execution.

Allowed owners:

- human operator;
- organization-controlled secret manager;
- governed deployment environment;
- explicitly approved runtime operator.

AiGOL may hold only:

- credential policy reference;
- credential retrieval boundary identifier;
- replay-visible retrieval outcome;
- redaction status;
- secret-present boolean.

AiGOL must not own:

- OpenAI API key value;
- bearer token value;
- provider account authority;
- credential rotation authority;
- credential revocation authority;
- credential issuance authority.

Ownership invariant:

```text
CREDENTIAL_OWNER = HUMAN_OR_ORGANIZATION_SECRET_AUTHORITY
AIGOL_CREDENTIAL_OWNERSHIP = NONE
```

## Credential Retrieval Model

Credential retrieval must be explicit, scoped, and non-replay.

Required input:

```text
LIVE_PROVIDER_CREDENTIAL_POLICY_ARTIFACT_V1
```

The credential policy may contain:

- policy id;
- provider id;
- credential reference;
- retrieval boundary id;
- redaction required true;
- credential secret stored false;
- credential secret replayed false.

The credential policy must not contain:

- API key value;
- bearer token value;
- authorization header value;
- secret manager response body;
- reversible encoding of secret material;
- partial secret material.

Retrieval sequence:

```text
credential policy artifact
-> approval artifact validation
-> provider id validation
-> credential reference validation
-> runtime secret lookup
-> non-empty secret presence check
-> redaction guard
-> transport-only credential handle
-> immediate disposal after request boundary
```

Allowed credential references:

- `env:AIGOL_OPENAI_API_KEY`
- governed secret-manager reference approved by future implementation milestone.

Disallowed credential references:

- inline API keys;
- inline bearer tokens;
- raw HTTP authorization headers;
- file paths containing ungoverned local secrets;
- provider responses containing credentials;
- ERR metadata fields.

## Secret Handling Requirements

Secret material may exist only in the smallest possible runtime scope.

Required:

- retrieve only after approval validation;
- retrieve only for `openai`;
- retrieve only for one approved invocation;
- never serialize the secret;
- never hash the secret for replay;
- never log the secret;
- never include the secret in exception text;
- never include the secret in audit packet;
- never include the secret in provider request attempt artifact;
- never include the secret in provider response artifact;
- never include the secret in canonical input or output;
- dispose of the credential handle after transport boundary use.

Forbidden:

- credential caching;
- credential pooling;
- credential reuse across invocations;
- credential fallback;
- multi-provider credential lookup;
- credential ranking;
- credential discovery;
- credential mutation by provider output;
- credential storage in ERR.

Permanent invariant:

```text
NO_SECRET_REPLAY = TRUE
CREDENTIAL_SECRET_STORED_IN_ARTIFACT = FALSE
CREDENTIAL_SECRET_HASHED_FOR_REPLAY = FALSE
```

## Replay-Safe Evidence Model

Replay must prove credential boundary behavior without storing secrets.

### Credential Policy Evidence

Artifact:

```text
LIVE_PROVIDER_CREDENTIAL_POLICY_ARTIFACT_V1
```

Allowed fields:

- policy id;
- provider id;
- credential reference;
- retrieval boundary;
- redaction required;
- credential secret stored false;
- credential secret replayed false;
- secret material present false;
- artifact hash.

### Credential Retrieval Attempt Evidence

Future artifact:

```text
LIVE_PROVIDER_CREDENTIAL_RETRIEVAL_ATTEMPT_ARTIFACT_V1
```

Required fields:

- retrieval attempt id;
- invocation id;
- provider id;
- credential policy artifact hash;
- approval artifact hash;
- credential reference id;
- retrieval boundary id;
- retrieval attempted true;
- credential present boolean;
- credential secret replayed false;
- credential value omitted true;
- retrieval status;
- created at.

The artifact must not include:

- credential value;
- credential hash;
- authorization header;
- raw environment value.

### Credential Use Evidence

Future artifact:

```text
LIVE_PROVIDER_CREDENTIAL_USE_BOUNDARY_ARTIFACT_V1
```

Required fields:

- invocation id;
- retrieval attempt artifact hash;
- provider id;
- transport boundary id;
- credential used for exactly one request;
- credential secret replayed false;
- credential disposed after use true;
- request attempt artifact hash;
- created at.

## Credential Rotation Handling

Credential rotation is owned outside AiGOL.

AiGOL may observe rotation only through a changed credential reference or retrieval outcome.

Rotation handling rules:

1. rotation must not mutate historical replay evidence;
2. previous invocation replay remains valid without revealing the old secret;
3. new invocation must validate the current credential policy;
4. retrieval must occur at invocation time;
5. stale credential failure must fail closed;
6. rotation event may be referenced by policy version, not by secret value.

Allowed replay evidence:

- credential policy version;
- rotation observed boolean;
- prior policy artifact hash;
- current policy artifact hash;
- retrieval status.

Forbidden replay evidence:

- old secret;
- new secret;
- diff between secrets;
- partial token comparison.

Rotation output:

```text
CREDENTIAL_ROTATION_HANDLED_BY_REFERENCE = TRUE
SECRET_VALUE_REPLAYED = FALSE
```

## Credential Revocation Handling

Credential revocation must fail closed.

Revocation may be detected through:

- explicit revocation marker;
- credential retrieval failure;
- provider authentication failure;
- policy status no longer active;
- approval revocation before invocation.

Revocation handling rules:

1. do not retry with another credential;
2. do not fall back to another provider;
3. do not request a worker;
4. record replay-visible revocation evidence without secret values;
5. mark live invocation failed closed;
6. require renewed approval and credential policy before retry.

Revocation output:

```text
CREDENTIAL_STATUS = REVOKED_OR_UNAVAILABLE
LIVE_PROVIDER_INVOCATION_STATUS = FAILED_CLOSED
RETRY_ALLOWED_WITHOUT_REAPPROVAL = FALSE
SECRET_VALUE_REPLAYED = FALSE
```

## Fail-Closed Behavior

The credential boundary must fail closed if:

1. approval artifact is missing, malformed, expired, or out of scope;
2. credential policy artifact is missing or malformed;
3. provider id is not `openai`;
4. credential reference is missing;
5. credential reference uses a prohibited scheme;
6. credential value is included in policy;
7. credential retrieval fails;
8. credential is empty;
9. credential appears in replay evidence;
10. credential appears in exception text;
11. credential appears in audit text;
12. credential appears in canonical input or output;
13. credential rotation invalidates current policy;
14. credential revocation is detected;
15. provider output requests credential disclosure;
16. provider output attempts credential mutation;
17. worker invocation is attempted;
18. provider fallback is attempted;
19. governance mutation is attempted;
20. replay mutation is attempted.

Fail-closed evidence must record:

```text
CREDENTIAL_BOUNDARY_STATUS = FAILED_CLOSED
CREDENTIAL_SECRET_REPLAYED = FALSE
LIVE_PROVIDER_CALL_ALLOWED = FALSE
WORKER_INVOKED = FALSE
GOVERNANCE_MODIFIED = FALSE
REPLAY_MODIFIED = FALSE
```

If secret leakage is detected, the replay artifact must not reproduce the leaked secret. It must record only:

```text
SECRET_LEAKAGE_DETECTED = TRUE
SECRET_VALUE_REDACTED = TRUE
```

## Audit Requirements

Every live invocation that reaches credential retrieval must produce an audit entry.

Audit packet must include:

- approval artifact hash;
- credential policy artifact hash;
- credential retrieval attempt artifact hash;
- credential use boundary artifact hash if use occurs;
- provider id;
- retrieval status;
- credential present boolean;
- credential secret replayed false;
- rotation status;
- revocation status;
- redaction status;
- failure classification if any;
- no worker invocation;
- no governance mutation;
- no replay mutation.

Audit packet must not include:

- credential value;
- credential hash;
- authorization header;
- secret-manager response body.

Audit verdicts:

```text
CREDENTIAL_BOUNDARY_AUDIT = PASS
CREDENTIAL_BOUNDARY_AUDIT = FAILED_CLOSED
```

Audit pass does not authorize provider invocation by itself.

## Governance Constraints

Credential boundary governance constraints:

- Human approval remains required.
- ERR remains passive.
- OCS remains orchestration.
- Provider output remains non-authoritative.
- Workers remain unreachable from providers.
- Replay remains immutable.
- Credential ownership remains outside AiGOL.
- Credential retrieval is not credential ownership.
- Credential policy is not live invocation approval.
- Credential availability is not live invocation approval.

Required interpretation:

```text
CREDENTIAL_AVAILABLE != PROVIDER_INVOCATION_AUTHORIZED
CREDENTIAL_POLICY != SECRET
CREDENTIAL_REFERENCE != SECRET_VALUE
```

## Acceptance Criteria

The future implementation of this boundary is acceptable only if:

1. credential ownership is outside AiGOL;
2. credential policy contains no secret;
3. credential retrieval requires approval validation;
4. provider id must be `openai`;
5. retrieval supports only approved reference schemes;
6. retrieved secret is never replayed;
7. retrieved secret is never hashed for replay;
8. retrieved secret is never logged;
9. retrieved secret is never included in exception text;
10. retrieval attempt evidence is replay-visible;
11. credential use boundary evidence is replay-visible;
12. credential rotation is represented by policy/reference changes only;
13. credential revocation fails closed;
14. secret leakage detection records redacted evidence only;
15. no credential fallback occurs;
16. no provider fallback occurs;
17. no worker invocation occurs;
18. no governance mutation occurs;
19. no replay mutation occurs;
20. audit evidence proves no-secret replay.

Acceptance output:

```text
LIVE_PROVIDER_CREDENTIAL_BOUNDARY_DEFINED = YES
AUTHENTICATION_IMPLEMENTED = NO
SECRET_STORAGE_IMPLEMENTED = NO
LIVE_PROVIDER_INVOKED = NO
NO_SECRET_REPLAY_INVARIANT = PRESERVED
```

## Implementation Plan

Recommended implementation milestone:

```text
AIGOL_LIVE_PROVIDER_CREDENTIAL_BOUNDARY_IMPLEMENTATION_V1
```

Minimal implementation sequence:

1. define credential retrieval attempt artifact;
2. define credential use boundary artifact;
3. validate approval artifact before retrieval;
4. validate credential policy artifact;
5. validate provider id `openai`;
6. support only `env:AIGOL_OPENAI_API_KEY` initially;
7. retrieve credential into memory only;
8. validate non-empty credential;
9. enforce no-secret replay checks;
10. produce retrieval evidence without secret material;
11. produce credential use evidence without secret material;
12. fail closed on missing credential;
13. fail closed on unsupported reference scheme;
14. fail closed on detected secret leakage;
15. fail closed on revocation marker;
16. add audit packet integration;
17. add tests for no-secret replay, missing credential, unsupported reference, revocation, rotation reference, and provider-output credential disclosure.

The implementation must be tested with fake credentials only before any live OpenAI call is attempted.

## Final Recommendation

Adopt this credential boundary design before implementing live transport.

The live transport boundary must depend on this credential boundary and must not retrieve credentials directly.

Final status:

```text
AIGOL_LIVE_PROVIDER_CREDENTIAL_BOUNDARY_V1 = PREPARED
AUTHENTICATION_IMPLEMENTED = NO
SECRET_STORAGE_IMPLEMENTED = NO
LIVE_PROVIDER_INVOKED = NO
NO_SECRET_REPLAY_INVARIANT = PRESERVED
```
