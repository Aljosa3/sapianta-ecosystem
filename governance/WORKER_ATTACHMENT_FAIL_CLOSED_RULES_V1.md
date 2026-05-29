# Worker Attachment Fail-Closed Rules V1

Status: model-only fail-closed worker attachment rules.

## Fail-Closed Principle

Any real worker attachment ambiguity must fail closed.

Failure must preserve replay evidence and must not continue execution.

## Failure Modes

### Worker Unavailable

If the worker cannot be reached, cannot be identified, or cannot accept the bounded request, the attachment fails closed.

Expected behavior:

- worker unavailable state recorded
- no retry by default
- no hidden fallback worker
- no partial execution

### Worker Timeout

If the worker does not return deterministically within the governed boundary, the attachment fails closed.

Expected behavior:

- timeout recorded
- worker invocation terminated
- no hidden continuation
- no autonomous retry

### Worker Corruption

If worker output is malformed, unverifiable, authority-escalating, or inconsistent with the request, the attachment fails closed.

Expected behavior:

- malformed result recorded
- governed return rejects the worker result
- replay lineage preserved
- no result accepted silently

### Replay Corruption

If worker replay lineage, ordering, hashes, or references cannot be verified, the attachment fails closed.

Expected behavior:

- replay violation recorded
- no governed success emitted
- no replay repair attempted

### Capability Mismatch

If the worker receives a capability outside the authorized binding, the attachment fails closed.

Expected behavior:

- capability mismatch recorded
- no execution
- no capability substitution
- no automatic downgrade

### Identity Mismatch

If worker identity does not match the authorized worker envelope or changes during invocation, the attachment fails closed.

Expected behavior:

- identity mismatch recorded
- execution terminated
- no cross-worker continuation

### Self-Authorization Attempt

If the worker claims authorization authority or attempts to authorize itself, the attachment fails closed.

Expected behavior:

- authority violation recorded
- no execution request accepted
- no worker result trusted

## Non-Recovery Rule

The worker attachment model does not permit hidden retry, self-healing execution, worker substitution, automatic continuation, or replay repair.
