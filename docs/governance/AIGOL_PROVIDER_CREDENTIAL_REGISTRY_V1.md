# AIGOL_PROVIDER_CREDENTIAL_REGISTRY_V1

Status: canonical secret-free provider credential registry definition.

Purpose: define the canonical provider-id to credential-reference mapping used by AiGOL provider credential governance.

This artifact does not implement credential storage, credential retrieval, live provider invocation, provider routing, provider fallback, ERR redesign, worker execution, or replay mutation.

## 1. Governing Inputs

This registry is governed by:

- `AIGOL_PROVIDER_CREDENTIAL_GOVERNANCE_REVIEW_V1`
- `AIGOL_LIVE_PROVIDER_CREDENTIAL_BOUNDARY_V1`
- `AIGOL_PROVIDER_CREDENTIAL_BOUNDARY_REVIEW_V1`
- `AIGOL_DEPENDENCY_FAILURE_RUNTIME_V1`
- `AIGOL_FIRST_LIVE_COGNITION_PROVIDER_CERTIFICATION_V1`
- existing provider runtime implementation
- ERR provider metadata

## 2. Registry Principle

The provider credential registry is secret-free governance metadata.

It may define:

- provider id;
- provider aliases;
- credential reference;
- credential source type;
- required credential class;
- operator-safe remediation guidance;
- replay-safe diagnostic fields;
- certification requirements.

It must not:

- store credential values;
- hash credential values;
- replay credential values;
- retrieve credential values;
- expose credential values;
- infer credential values;
- own credential lifecycle;
- authorize provider invocation by itself;
- select providers;
- route providers;
- invoke providers;
- mutate ERR.

Permanent invariant:

```text
PROVIDER_CREDENTIAL_REGISTRY_SECRET_FREE = TRUE
CREDENTIAL_VALUE_STORED = FALSE
CREDENTIAL_VALUE_HASHED = FALSE
CREDENTIAL_VALUE_REPLAYED = FALSE
CREDENTIAL_RETRIEVAL_PERFORMED = FALSE
PROVIDER_INVOCATION_AUTHORIZED_BY_REGISTRY = FALSE
```

## 3. Relationship To ERR

ERR remains the passive resource metadata registry.

ERR may answer:

```text
Which provider resource matches this capability?
```

The provider credential registry may answer:

```text
Which secret-free credential reference is approved for this provider id?
```

ERR must not store provider credentials or credential references unless a future governance artifact explicitly changes that boundary. This registry does not change ERR.

Required separation:

```text
ERR_PROVIDER_SELECTION != CREDENTIAL_REFERENCE_RESOLUTION
CREDENTIAL_REFERENCE_RESOLUTION != CREDENTIAL_RETRIEVAL
CREDENTIAL_PRESENT != PROVIDER_INVOCATION_AUTHORIZED
```

## 4. Canonical Provider Credential Entries

Registry version:

```text
AIGOL_PROVIDER_CREDENTIAL_REGISTRY_V1
```

Initial canonical entries:

| provider_id | provider aliases | resource type | credential class | canonical credential reference | credential source type | status |
| --- | --- | --- | --- | --- | --- | --- |
| `openai` | `openai` | `COGNITION_PROVIDER` | `API_KEY` | `env:AIGOL_OPENAI_API_KEY` | `ENVIRONMENT_VARIABLE` | `ACTIVE_FOR_FIRST_LIVE_CERTIFICATION` |
| `claude` | `anthropic`, `claude` | `COGNITION_PROVIDER` | `API_KEY` | `env:AIGOL_ANTHROPIC_API_KEY` | `ENVIRONMENT_VARIABLE` | `REFERENCE_DEFINED_NOT_LIVE_CERTIFIED` |
| `gemini` | `google_gemini`, `gemini` | `COGNITION_PROVIDER` | `API_KEY` | `env:AIGOL_GEMINI_API_KEY` | `ENVIRONMENT_VARIABLE` | `REFERENCE_DEFINED_NOT_LIVE_CERTIFIED` |
| `mistral` | `mistral` | `COGNITION_PROVIDER` | `API_KEY` | `env:AIGOL_MISTRAL_API_KEY` | `ENVIRONMENT_VARIABLE` | `REFERENCE_DEFINED_NOT_LIVE_CERTIFIED` |

The canonical ERR provider id for Anthropic Claude is:

```text
provider_id = claude
```

The vendor alias is:

```text
provider_alias = anthropic
```

The canonical credential reference is:

```text
env:AIGOL_ANTHROPIC_API_KEY
```

This avoids introducing a second ERR provider id for the same provider family.

## 5. Entry Schema

Every registry entry must conform to:

```json
{
  "registry_version": "AIGOL_PROVIDER_CREDENTIAL_REGISTRY_V1",
  "provider_id": "openai",
  "provider_aliases": ["openai"],
  "provider_resource_type": "COGNITION_PROVIDER",
  "credential_class": "API_KEY",
  "credential_reference": "env:AIGOL_OPENAI_API_KEY",
  "credential_source_type": "ENVIRONMENT_VARIABLE",
  "secret_authority": "operator_controlled_environment",
  "required_for_capabilities": [
    "reasoning",
    "planning",
    "summarization",
    "analysis",
    "generation"
  ],
  "credential_value_stored": false,
  "credential_value_hashed": false,
  "credential_value_replayed": false,
  "credential_retrieval_performed": false,
  "credential_secret_owned_by_aigol": false,
  "operator_safe_message": "OpenAI cognition requires AIGOL_OPENAI_API_KEY in the governed process environment.",
  "remediation_hint": "Provision AIGOL_OPENAI_API_KEY in the governed process environment and verify presence without printing the value.",
  "retry_guidance": "After provisioning, rerun the governed provider certification or invocation entrypoint with fresh authorization.",
  "replay_safe": true
}
```

Allowed `credential_source_type` values:

- `ENVIRONMENT_VARIABLE`
- `SECRET_MANAGER_REFERENCE_RESERVED`

Only `ENVIRONMENT_VARIABLE` is defined for V1 runtime use.

`SECRET_MANAGER_REFERENCE_RESERVED` is a future extension placeholder. It does not authorize secret-manager retrieval.

## 6. Diagnostic Fields

Provider credential diagnostics must use this secret-free structure:

| Field | Required | Source | Secret-safe rule |
| --- | --- | --- | --- |
| `provider_id` | yes | registry entry or selected provider metadata | Provider id only |
| `credential_reference` | yes | registry entry | Reference only, never value |
| `credential_present` | yes | runtime presence check | Boolean only |
| `credential_source_type` | yes | registry entry | Source class only |
| `remediation_hint` | yes | registry entry | Must not include credential value |
| `operator_safe_message` | yes | registry entry | Must not include credential value |
| `registry_version` | yes | registry entry | Secret-free |
| `provider_aliases` | optional | registry entry | Secret-free |
| `checked_at` | optional | diagnostic runtime | Timestamp only |
| `failure_classification` | optional | dependency failure runtime | Example: `MISSING_CREDENTIAL` |

Example diagnostic:

```json
{
  "artifact_type": "PROVIDER_CREDENTIAL_DIAGNOSTIC_V1",
  "registry_version": "AIGOL_PROVIDER_CREDENTIAL_REGISTRY_V1",
  "provider_id": "openai",
  "credential_reference": "env:AIGOL_OPENAI_API_KEY",
  "credential_present": false,
  "credential_source_type": "ENVIRONMENT_VARIABLE",
  "failure_classification": "MISSING_CREDENTIAL",
  "remediation_hint": "Provision AIGOL_OPENAI_API_KEY in the governed process environment and verify presence without printing the value.",
  "operator_safe_message": "OpenAI cognition cannot run because its approved credential reference is unavailable.",
  "credential_value_omitted": true,
  "credential_secret_replayed": false,
  "credential_hash_recorded": false,
  "provider_invoked": false,
  "worker_invoked": false,
  "replay_visible": true
}
```

## 7. Runtime Helper Scope

Recommended helper:

```text
aigol/runtime/provider_credential_registry.py
```

Allowed helper responsibilities:

1. return the secret-free registry version;
2. return a registry entry by provider id;
3. normalize approved provider aliases to canonical provider ids;
4. validate that a credential reference is approved for a provider id;
5. produce a secret-free diagnostic structure;
6. produce a `LIVE_PROVIDER_CREDENTIAL_POLICY_ARTIFACT_V1` input reference;
7. support dependency failure runtime with provider-specific remediation text.

Forbidden helper responsibilities:

1. read environment variables;
2. retrieve secret-manager values;
3. store credential values;
4. hash credential values;
5. print credential values;
6. authorize provider invocation;
7. select providers;
8. mutate ERR;
9. perform fallback;
10. invoke providers or workers.

Credential presence checks must remain in capability-specific governed runtime boundaries, such as operator entrypoints or provider runtime boundaries, after approval and authorization checks.

## 8. Replay-Safe Evidence Model

Registry-backed credential evidence may include:

- `registry_version`;
- `provider_id`;
- `provider_aliases`;
- `credential_reference`;
- `credential_source_type`;
- `credential_present`;
- `credential_value_omitted = true`;
- `credential_secret_replayed = false`;
- `credential_hash_recorded = false`;
- `credential_reference_registry_entry_hash`;
- `operator_safe_message`;
- `remediation_hint`;
- `failure_classification`;
- `provider_invoked`;
- `worker_invoked`;
- `replay_visible`.

Registry-backed credential evidence must not include:

- credential value;
- credential hash;
- authorization header;
- bearer token;
- raw secret-manager response;
- partial secret;
- credential prefix;
- credential suffix;
- reversible encoding of secret material.

`credential_reference_registry_entry_hash` may hash the secret-free registry entry metadata only. It must never hash the credential value.

## 9. Integration With Credential Boundary

The live credential boundary should continue to receive invocation-scoped credential policy artifacts.

The registry should provide the canonical source for the credential reference used to construct those policy artifacts.

Required path:

```text
provider_id
-> provider credential registry lookup
-> secret-free credential reference
-> invocation-scoped credential policy artifact
-> approval validation
-> runtime credential presence check
-> credential retrieval into memory only
-> transport-only use
-> no-secret replay evidence
```

The registry does not replace:

- human approval;
- dispatch authorization;
- credential retrieval boundary;
- dependency failure runtime;
- live provider runtime boundary;
- replay reconstruction.

## 10. Integration With Dependency Failure Runtime

For missing provider credentials, dependency failure runtime should use registry metadata to populate:

```text
classification = MISSING_CREDENTIAL
dependency_id = credential_reference
provider_id = provider_id
credential_source_type = credential_source_type
operator_safe_message = operator_safe_message
remediation_hint = remediation_hint
retry_guidance = retry_guidance
```

Required user/operator meaning:

```text
The provider was not invoked because its approved credential reference was unavailable.
No credential value was printed, stored, hashed, or replayed.
The operator must provision the credential in the approved location and retry through a governed entrypoint.
```

## 11. Certification Tests

Required certification tests for `AIGOL_PROVIDER_CREDENTIAL_REGISTRY_V1`:

1. OpenAI maps to `env:AIGOL_OPENAI_API_KEY`.
2. Claude maps to `env:AIGOL_ANTHROPIC_API_KEY`.
3. `anthropic` alias normalizes to canonical provider id `claude`.
4. Gemini maps to `env:AIGOL_GEMINI_API_KEY`.
5. Mistral maps to `env:AIGOL_MISTRAL_API_KEY`.
6. Unknown provider id fails closed.
7. Unsupported credential reference fails closed.
8. Registry entries contain no credential values.
9. Registry entries contain no authorization headers.
10. Registry entries contain no credential hashes.
11. Registry helper does not read environment variables.
12. Registry helper does not invoke providers.
13. Registry helper does not mutate ERR.
14. Diagnostic output includes `provider_id`, `credential_reference`, `credential_present`, `credential_source_type`, `remediation_hint`, and `operator_safe_message`.
15. Diagnostic output never includes secret values.
16. Replay evidence includes registry version and secret-free credential reference.
17. Missing credential diagnostic maps to `MISSING_CREDENTIAL`.
18. Credential-present boolean is computed outside the registry helper and passed into diagnostics.
19. Existing OpenAI first-live certification path remains behaviorally unchanged except that the credential reference may be derived from this registry.
20. ERR remains credential-free.

Certification pass output:

```text
PROVIDER_CREDENTIAL_REGISTRY_SECRET_FREE = TRUE
OPENAI_CREDENTIAL_REFERENCE_DEFINED = TRUE
CLAUDE_CREDENTIAL_REFERENCE_DEFINED = TRUE
FUTURE_PROVIDER_EXTENSION_MODEL_DEFINED = TRUE
ERR_REMAINS_CREDENTIAL_FREE = TRUE
NO_SECRET_REPLAY_INVARIANT_PRESERVED = TRUE
```

## 12. Provider Onboarding Rule

Future provider onboarding must include a credential registry entry before live certification may proceed.

Required onboarding sequence:

```text
ERR provider metadata registered
-> provider credential registry entry defined
-> provider credential diagnostics certified
-> provider runtime boundary certified with fake credentials
-> live credential presence verified without printing value
-> one-attempt live certification authorized
```

No provider may proceed to live invocation solely because it is present in ERR.

## 13. Non-Goals

This registry does not:

- implement Anthropic, Gemini, or Mistral transport;
- certify multi-provider cognition;
- approve live invocation for non-OpenAI providers;
- introduce provider fallback;
- introduce credential fallback;
- authorize automatic retries;
- store credential values;
- move credential handling into ERR;
- change the first live OpenAI execution path by itself.

## 14. Final Verdict

`PROVIDER_CREDENTIAL_REGISTRY_DEFINED`

The canonical provider credential registry is defined as a secret-free governance metadata layer. It maps provider ids to approved credential references, defines operator-safe diagnostics, preserves ERR passivity, and establishes a deterministic credential-onboarding substrate without storing, hashing, replaying, retrieving, or exposing secret values.
