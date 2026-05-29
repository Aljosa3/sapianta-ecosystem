# LLM Attachment Fail-Closed Rules V1

Status: model-only fail-closed rule definition.

## Fail-Closed Principle

Any real LLM attachment ambiguity must fail closed.

Failure must preserve replay evidence and must not continue into authorization or worker execution.

## Failure Modes

### Malformed Proposal

Malformed provider output fails closed when required proposal fields are missing, invalid, non-deterministic, or structurally incompatible with the proposal bridge.

Expected behavior:

- raw response evidence preserved
- normalization rejected
- no proposal authority granted
- no execution request created

### Ambiguous Proposal

Ambiguous provider output fails closed when intent, capability, arguments, identity, or lineage cannot be determined deterministically.

Expected behavior:

- ambiguity recorded
- no autonomous interpretation
- no assumption recovery
- no worker execution

### Provider Failure

Provider failure fails closed when the provider returns no response, times out, returns incomplete output, or cannot produce deterministic response evidence.

Expected behavior:

- provider failure represented as replay-visible attachment failure
- no hidden retry
- no hidden continuation
- no proposal artifact emitted unless deterministic normalized structure exists

### Replay Corruption

Replay corruption fails closed when identity evidence, raw response evidence, hash links, or ordering references cannot be verified.

Expected behavior:

- replay violation recorded
- no normalization acceptance
- no authorization
- no worker execution

### Normalization Failure

Normalization failure fails closed when raw output cannot become a bounded `PROPOSAL_ARTIFACT`.

Expected behavior:

- raw response retained
- failure reason retained
- governance receives no executable proposal
- operator receives governed rejection evidence

### Authority Escalation Attempt

Authority escalation fails closed when output claims execution authority, authorization authority, governance authority, replay bypass, hidden continuation, orchestration, memory, agents, shell, network, mutation, or unsupported capability access.

Expected behavior:

- escalation recorded
- attachment rejected
- no execution request created
- no continuation

## Non-Recovery Rule

The real LLM attachment model does not permit autonomous retry, self-repair, semantic guessing, hidden fallback, or automatic continuation after failure.
