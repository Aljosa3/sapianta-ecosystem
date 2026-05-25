# FINALIZE_GOVERNED_PROVIDER_ACTIVATION_V1

## Scope

This milestone introduces the first governed real cognition-provider activation layer for AiGOL.

It adds a deterministic provider invocation envelope, an explicit provider activation gate, a minimal OpenAI provider adapter, replay-visible provider invocation persistence, and focused validation evidence.

Governed provider activation introduces cognition-provider connectivity only. It does not introduce execution authority, orchestration authority, autonomous execution, or unrestricted runtime behavior.

## Architectural Principles

- Provider is not authority.
- Cognition is not execution.
- Provider output is untrusted evidence.
- Runtime engine remains the authority layer.
- Provider activity must remain replay-visible.
- Provider activation must remain governance-gated.

## Provider Activation Boundary

Provider activation requires:

- `governance_state` is `AUTHORIZED`;
- provider is explicitly registered;
- invocation type is allowed;
- runtime id is present;
- lineage references are present;
- request payload is explicit;
- provider envelope boundary guarantees are intact;
- replay hash is valid.

Any missing, malformed, unauthorized, or unknown provider activation evidence fails closed.

## OpenAI Provider Boundary

The OpenAI provider adapter is cognition-only and supports bounded prompt-to-response invocation. It does not:

- execute tools;
- write files directly;
- spawn workers;
- call shell commands;
- mutate runtime state;
- dispatch tasks;
- call providers recursively.

The provider requires `AIGOL_OPENAI_API_KEY`. Missing key evidence fails closed. Keys are never hardcoded.

## Replay Guarantees

Provider envelopes and provider response artifacts use canonical JSON replay hashes with sorted keys, stable separators, UTF-8 persistence, and SHA-256 hashing.

Provider invocation persistence is append-only and immutable. Replay reconstruction restores the provider envelope, provider response, ledger entries, and replay chain.

## Mutation Boundaries

This milestone adds a bounded provider activation package, provider invocation persistence methods, an optional runtime engine governed provider invocation path, focused tests, and governance evidence.

It does not add orchestration, autonomous retries, shell execution, Docker execution, filesystem mutation authority, multi-provider planning, distributed runtime, or governance mutation.

## Deterministic Acceptance Evidence

Acceptance requires tests for:

- provider activation success;
- unknown provider blocking;
- unauthorized governance state blocking;
- malformed provider envelope blocking;
- missing API key blocking;
- replay-visible invocation persistence;
- deterministic replay hashing;
- provider response persistence;
- fail-closed provider validation;
- provider authority bypass prevention;
- execution prevention guarantees;
- provider invocation replay reconstruction.

## Certification

`FINALIZE_GOVERNED_PROVIDER_ACTIVATION_V1` certifies the first bounded cognition-provider connection inside AiGOL while preserving replay safety, fail-closed semantics, governance visibility, and non-orchestrating runtime boundaries.
