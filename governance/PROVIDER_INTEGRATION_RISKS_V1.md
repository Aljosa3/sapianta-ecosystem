# Provider Integration Risks V1

Status: provider integration risk record.

## Shared Risks

### Network Behavior Drift

Provider integrations introduce network failure modes, timeouts, rate limits, partial responses, and transport ambiguity.

Mitigation: provider adapters must produce deterministic fail-closed evidence and must not retry automatically.

### Credential Boundary Leakage

Provider SDKs require credentials.

Mitigation: credentials must remain outside replay, outside governance artifacts, and outside model output. Credential failures should be represented without secret leakage.

### Raw Response Ambiguity

Providers expose different response structures.

Mitigation: raw provider output must be captured before normalization, and extraction failure must fail closed.

### Authority Confusion

Provider output may sound imperative.

Mitigation: provider text remains proposal source evidence only and must pass through proposal normalization and AiGOL governance.

### Replay Fragmentation

Provider-specific logs could become parallel evidence.

Mitigation: provider adapter logs are not replay substitutes. Replay remains source of truth.

## OpenAI Risks

- SDK response shape drift
- model output format variability
- credential or quota errors
- accidental live retry behavior

Classification: manageable under `READY_WITH_CONSTRAINTS`.

## Claude Risks

- SDK response shape drift
- model output format variability
- credential or quota errors
- accidental live retry behavior

Classification: manageable under `READY_WITH_CONSTRAINTS`.

## Codex Risks

- role confusion between proposal source and execution worker
- filesystem/tool mutation implications
- accidental framing as worker execution
- hidden authority escalation through development tooling

Classification: blocking. `CODEX_PROVIDER_ADAPTER_V1` is `NOT_READY`.

## Missing Replay Requirements

Provider-specific adapters still need replay fields for:

- provider invocation id
- model identity
- response id
- raw response hash
- provider error class
- provider timeout/failure state
- adapter boundary version

## Missing Fail-Closed Paths

Provider-specific adapters still need fail-closed paths for:

- credential missing
- credential rejected
- timeout
- rate limit
- malformed provider response
- missing response text
- oversized response
- SDK exception
- provider-specific response extraction failure
