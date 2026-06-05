# AIGOL_LLM_COGNITION_PROVIDER_RUNTIME_V1

## Status

Certified single-provider cognition runtime.

This milestone implements the first governed bridge between OCS context assembly and one approved `COGNITION_PROVIDER`.

## Scope

Runtime:

- `aigol/runtime/llm_cognition_provider_runtime.py`

Artifacts:

- `LLM_COGNITION_PROVIDER_REQUEST_ARTIFACT_V1`
- `LLM_COGNITION_PROVIDER_RESPONSE_ARTIFACT_V1`
- `LLM_COGNITION_PROVIDER_REPLAY_BINDING_ARTIFACT_V1`

Classification:

```text
CERTIFIED_SINGLE_PROVIDER_COGNITION_RUNTIME
```

## Implemented Flow

```text
Human Request
-> OCS_CONTEXT_ASSEMBLY_ARTIFACT_V1
-> LLM_COGNITION_PROVIDER_REQUEST_ARTIFACT_V1
-> Approved COGNITION_PROVIDER
-> LLM_COGNITION_PROVIDER_RESPONSE_ARTIFACT_V1
-> Replay Binding
-> Replay Reconstruction
```

## Runtime Preconditions

The runtime fails closed unless:

- OCS context artifact is present;
- OCS context artifact type is `OCS_CONTEXT_ASSEMBLY_ARTIFACT_V1`;
- OCS context status is assembled;
- OCS context artifact is replay-visible;
- OCS context artifact hash validates;
- provider contract is present;
- provider role is `COGNITION_PROVIDER`;
- provider is approved;
- provider contract hash validates;
- provider authority flags are all false;
- explicit human approval is present;
- governed credential policy can load a registered credential;
- replay path is append-only.

## Request Artifact

`LLM_COGNITION_PROVIDER_REQUEST_ARTIFACT_V1` captures:

- human request;
- human request hash;
- provider identity;
- provider role;
- provider schema;
- provider contract hash;
- credential policy hash;
- approval evidence;
- OCS context reference;
- OCS context hash;
- OCS context artifact hash;
- lineage references;
- authority flags.

## Response Artifact

`LLM_COGNITION_PROVIDER_RESPONSE_ARTIFACT_V1` captures:

- provider identity;
- provider metadata;
- request hash;
- response hash;
- raw response hash;
- response text hash;
- OCS context hash;
- lineage references;
- non-authoritative provider-output flag;
- authority flags.

Provider output remains untrusted and non-authoritative.

## Replay Binding

The replay binding captures:

- provider request artifact hash;
- provider response artifact hash;
- provider identity;
- provider metadata;
- context hash;
- request hash;
- response hash;
- provider contract hash;
- approval evidence hash.

Replay reconstruction verifies:

- replay wrapper hashes;
- artifact hashes;
- request-to-response lineage;
- binding-to-request lineage;
- binding-to-response lineage.

## Authority Preservation

The runtime preserves:

```text
provider_authority = false
approval_authority = false
execution_authority = false
worker_authority = false
governance_authority = false
replay_authority = false
```

The runtime also preserves:

- no execution;
- no worker invocation;
- no approval creation;
- no domain creation;
- no governance mutation;
- no replay mutation;
- no cognition artifact runtime;
- no multi-provider cognition;
- no cognition comparison;
- no cognition memory integration;
- no cognition continuity integration;
- no cognition clarification integration.

## Fail-Closed Conditions

The runtime fails closed when:

- provider is not approved;
- provider is not registered;
- provider contract is missing;
- provider role is not `COGNITION_PROVIDER`;
- provider authority flags are missing;
- provider authority flags are not false;
- OCS context artifact is missing or invalid;
- OCS context hash cannot be verified;
- explicit human approval is missing;
- credential policy cannot load a registered credential;
- provider response exceeds authority boundary;
- provider response cannot be bounded or normalized as response text;
- replay path collides with existing append-only artifacts;
- replay reconstruction detects tampering.

## Explicit Non-Goals Preserved

This milestone does not implement:

- multi-provider cognition;
- cognition comparison;
- cognition continuity;
- cognition memory integration;
- cognition clarification integration;
- cognition artifact runtime;
- provider selection intelligence;
- worker invocation;
- execution authorization;
- approval creation;
- governance mutation;
- replay mutation.

## Constitutional Invariant

The runtime preserves:

- LLM proposes.
- AiGOL governs.
- Worker executes.
- Replay records.
