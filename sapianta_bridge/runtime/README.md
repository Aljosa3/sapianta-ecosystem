# Executor Adapter Runtime v1

This package defines the first bounded adapter runtime delivery layer for AiGOL.

Runtime delivery is:

```text
Valid ExecutionEnvelope -> Bound ProviderAdapter -> NormalizedExecutionResult -> Replay-safe evidence
```

It is not orchestration.

## Envelope-First Execution

The runtime validates an execution envelope before adapter execution. Invalid envelopes are blocked.

## Bounded Adapter Semantics

Adapters execute only through a validated envelope and explicit provider binding. Providers cannot self-authorize, expand authority, mutate governance state, mutate replay state, enqueue tasks, or bypass normalized result validation.

## Provider Identity Binding

The provider adapter identity must match the envelope provider identity. Mismatches fail closed.

## Normalized Runtime Result

Runtime wraps `NormalizedExecutionResult` with envelope ID, replay identity, guard status, artifacts, and replay safety.

## Replay-Safe Evidence

Runtime evidence records envelope validity, provider binding, authority preservation, workspace preservation, normalized result validity, and explicit absence of routing, orchestration, fallback, retries, and external API calls.

## Non-Goals

This package does not implement provider routing, autonomous orchestration, dynamic scheduling, provider optimization, fallback logic, retry logic, hidden execution, real provider APIs, bridge transport, ChatGPT automation, or production execution.
