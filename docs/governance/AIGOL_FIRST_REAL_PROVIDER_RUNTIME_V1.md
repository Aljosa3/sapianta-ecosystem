# AIGOL First Real Provider Runtime V1

Status: runtime validation design.

Purpose: define the smallest possible real cognition-provider runtime validation path after ERR, real provider registration, canonical provider contract, migration audit, and adapter strategy.

This artifact is design only.

It does not implement provider execution, transport redesign, authentication, routing, ranking, comparison, marketplace behavior, ELL, lifecycle management, worker invocation, governance mutation, or replay mutation.

## Selected Provider

The first provider for runtime validation is:

```text
openai
```

Rationale:

- `openai` is already registered in ERR as `COGNITION_PROVIDER`.
- Existing code already references `openai.responses.v1`.
- Existing single-provider cognition runtime already models OpenAI-specific request and response evidence.
- OpenAI can validate the canonical provider contract path without introducing multi-provider routing or provider comparison.

No other provider is selected for this milestone.

Explicitly excluded:

```text
claude
gemini
mistral
```

These remain registered metadata only until separate governed milestones.

## Runtime Architecture

The smallest validation path is:

```text
Human-approved cognition request
-> OCS context assembly
-> ERR capability lookup: reasoning
-> ERR selects openai metadata
-> canonical OpenAI provider contract
-> SingleProviderContractToCanonicalAdapter
-> ProviderRequestToCanonicalInputAdapter
-> existing single-provider cognition runtime boundary
-> ProviderResponseToCanonicalOutputAdapter
-> LLM_COGNITION_ARTIFACT_V1 normalization
-> replay evidence
```

The path is single-provider only.

There is no provider comparison.

There is no multi-provider routing.

There is no provider ranking.

There is no transport redesign.

## Canonical Contract Use

The selected provider must use:

```text
CANONICAL_COGNITION_PROVIDER_CONTRACT_V1
```

Minimum OpenAI canonical contract fields:

```text
artifact_type = CANONICAL_COGNITION_PROVIDER_CONTRACT_V1
contract_reference = AIGOL_CANONICAL_PROVIDER_CONTRACT_V1
provider_id = openai
provider_role = COGNITION_PROVIDER
provider_schema_id = openai.responses.v1
capabilities = [reasoning, planning, summarization, analysis, generation]
provider_approved = true
replay_visible = true
authority_flags all false
```

The canonical contract does not authorize provider invocation by itself.

Human approval and runtime governance gates remain separate.

## Adapter Strategy

The first real-provider runtime validation should use these adapters:

| Adapter | Purpose |
| --- | --- |
| `SingleProviderContractToCanonicalAdapter` | Converts existing OpenAI single-provider contract registration into canonical contract view. |
| `ProviderRequestToCanonicalInputAdapter` | Converts provider request artifact into canonical input view. |
| `ProviderResponseToCanonicalOutputAdapter` | Converts provider response artifact into canonical output view. |
| `NoOpCanonicalCognitionArtifactAdapter` | Validates `LLM_COGNITION_ARTIFACT_V1` without changing its shape. |
| `ErrResourceToCanonicalProviderReferenceAdapter` | Confirms ERR selected `openai` as passive metadata only. |

Adapters must be pure schema adapters.

Adapters must not invoke providers.

Adapters must not call transport.

Adapters must not authenticate.

Adapters must not mutate existing replay artifacts.

## ERR Boundary Preservation

ERR remains passive.

ERR may do only:

```text
capability lookup
ACTIVE filtering
provider metadata selection
replay-visible selection evidence
```

ERR must not:

- invoke OpenAI;
- authorize OpenAI invocation;
- route among providers;
- compare providers;
- rank providers;
- optimize provider choice;
- manage credentials;
- manage lifecycle;
- become ELL;
- mutate replay history.

ERR selection evidence must continue to record:

```text
provider_invoked = false
worker_invoked = false
orchestration_performed = false
governance_modified = false
replay_visible = true
```

## Validation Strategy

Validation should proceed in three tiers.

### Tier 1: Non-Executing Schema Validation

Goal:

```text
prove canonical OpenAI provider contract and adapters work without provider invocation
```

Evidence:

- ERR resolves `openai` for `reasoning`;
- canonical OpenAI provider contract validates;
- existing OpenAI single-provider contract converts to canonical contract;
- canonical provider input view can be produced from request artifact;
- adapter outputs are replay-visible and hash-stable;
- no transport is called.

### Tier 2: Deterministic Transport Stub Validation

Goal:

```text
prove runtime replay chain with a deterministic non-network transport stub
```

Evidence:

- governed runtime path accepts canonical contract-derived input;
- deterministic stub response is captured as provider response artifact;
- canonical output view is produced;
- response is normalized into `LLM_COGNITION_ARTIFACT_V1`;
- authority-bearing output fails closed;
- replay reconstruction validates.

This tier still does not call OpenAI.

### Tier 3: Governed Live Provider Validation

Goal:

```text
prove one bounded live OpenAI cognition call can be replay-captured
```

Prerequisites:

- explicit human approval;
- governed credential policy;
- canonical OpenAI contract;
- no multi-provider mode;
- no comparison;
- no routing engine;
- no automatic retries;
- no streaming;
- no tool use;
- no worker invocation.

This tier is optional and must be separately approved before execution.

## Replay Requirements

The replay chain must be:

```text
ERR_RESOURCE_SELECTION_EVIDENCE_V0
-> CANONICAL_COGNITION_PROVIDER_CONTRACT_V1
-> CANONICAL_COGNITION_PROVIDER_INPUT_V1
-> existing LLM cognition provider request artifact
-> existing LLM cognition provider response artifact
-> CANONICAL_COGNITION_PROVIDER_OUTPUT_V1
-> LLM_COGNITION_ARTIFACT_V1
-> OCS result evidence
```

Replay requirements:

- every artifact must be replay-visible;
- every artifact must be hash-verifiable;
- canonical views must preserve source artifact hashes;
- no existing replay artifact may be rewritten;
- request lineage must bind to canonical contract hash;
- output lineage must bind to canonical input hash and source response hash;
- cognition artifact lineage must bind to context, input, output, provider identity, and provider contract;
- replay reconstruction must fail closed on corruption, missing hashes, mismatched lineage, authority escalation, or missing required fields;
- secrets, API keys, credential values, session state, and transport handles must never appear in replay.

## Governance Constraints

The runtime validation path must preserve:

- Human authority;
- OCS orchestration authority;
- ERR passive lookup boundary;
- provider non-authority;
- worker/provider separation;
- replay append-only semantics;
- fail-closed validation;
- no hidden execution;
- no credential capture;
- no governance mutation;
- no replay mutation.

The provider output must remain:

```text
untrusted_provider_output = true
non_authoritative = true
human_review_required = true
```

The validation path must not:

- compare providers;
- invoke more than one provider;
- route dynamically;
- rank providers;
- optimize provider selection;
- invoke workers;
- dispatch work;
- authorize execution;
- mutate governance;
- mutate replay;
- redesign transport;
- introduce ELL;
- introduce lifecycle management.

## No Multi-Provider Behavior

The first real provider runtime must explicitly disable:

```text
multi_provider_cognition
provider_comparison
confidence_aggregation_across_providers
provider_ranking
provider_fallback
dynamic_provider_routing
```

Only this path is allowed:

```text
openai selected by ERR for reasoning
-> one bounded cognition request
-> one bounded provider response
-> one canonical cognition artifact
```

## No Transport Redesign

The design must use the existing single-provider transport boundary if live validation is later approved.

Allowed:

```text
existing transport injection point
deterministic transport stub for tests
existing OpenAI response schema extraction
```

Not allowed:

```text
new transport layer
new authentication system
new session manager
streaming transport
tool transport
automatic retry engine
provider lifecycle manager
```

## Acceptance Criteria

`AIGOL_FIRST_REAL_PROVIDER_RUNTIME_V1` is accepted when:

1. OpenAI is the only selected provider.
2. ERR resolves OpenAI by capability and remains passive.
3. A canonical OpenAI provider contract is used.
4. Adapter views are used for contract, input, and output.
5. Existing runtime behavior is preserved.
6. Existing replay compatibility is preserved.
7. `LLM_COGNITION_ARTIFACT_V1` remains the normalized cognition artifact.
8. No provider comparison is introduced.
9. No multi-provider routing is introduced.
10. No transport redesign is introduced.
11. No worker invocation occurs.
12. Provider output remains non-authoritative.
13. Replay evidence is hash-verifiable and fail-closed.
14. Live provider validation, if performed, is explicitly human-approved and separately gated.

## Implementation Plan

Phase 1: Contract Fixture

- Add canonical OpenAI provider contract fixture.
- Validate required fields, authority flags, capabilities, prohibited outputs, and hashes.
- No provider invocation.

Phase 2: Adapter Validation

- Implement pure adapters for OpenAI contract, input, output, and cognition artifact no-op validation.
- Validate adapters using deterministic artifacts.
- Preserve source artifact hashes.
- No provider invocation.

Phase 3: ERR-to-Contract Binding Evidence

- Demonstrate:

```text
required_capability = reasoning
-> ERR selects openai
-> canonical OpenAI contract selected by provider_id
```

- Record replay-visible evidence that ERR did not invoke or authorize the provider.

Phase 4: Deterministic Stub Runtime Validation

- Use existing single-provider runtime boundary with deterministic stub transport.
- Produce provider response artifact.
- Adapt response to canonical output.
- Normalize to `LLM_COGNITION_ARTIFACT_V1`.
- Validate replay reconstruction.
- No network call.

Phase 5: Optional Governed Live Validation

- Run one OpenAI live call only after explicit human approval and credential policy validation.
- Use existing transport boundary.
- No streaming.
- No tools.
- No retries.
- No comparison.
- No worker invocation.

Phase 6: Certification

- Run provider contract adapter tests.
- Run ERR provider registration tests.
- Run OCS cognition tests.
- Run HIRR post-certification regression suite.
- Produce a separate certification artifact before declaring runtime readiness.

## Remaining Non-Goals

This milestone does not deliver:

- Claude runtime;
- Gemini runtime;
- Mistral runtime;
- multi-provider execution;
- provider comparison;
- provider ranking;
- provider fallback;
- provider marketplace;
- transport redesign;
- authentication redesign;
- lifecycle management;
- ELL;
- worker invocation;
- execution authorization.

## Final Recommendation

Proceed with the first real provider runtime validation path using OpenAI only.

The smallest safe path is:

```text
ERR-selected openai metadata
-> canonical OpenAI provider contract
-> pure adapters
-> existing single-provider runtime boundary
-> canonical output view
-> LLM_COGNITION_ARTIFACT_V1
-> replay evidence
```

Recommendation:

```text
FIRST_REAL_PROVIDER = openai
USE_CANONICAL_PROVIDER_CONTRACT = YES
USE_ADAPTER_STRATEGY = YES
ERR_REMAINS_PASSIVE = YES
MULTI_PROVIDER_ROUTING_ALLOWED = NO
PROVIDER_COMPARISON_ALLOWED = NO
TRANSPORT_REDESIGN_ALLOWED = NO
LIVE_CALL_ALLOWED_BY_THIS_ARTIFACT = NO
LIVE_CALL_REQUIRES_SEPARATE_GOVERNED_APPROVAL = YES
```
