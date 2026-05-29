# Worker Position Gaps V1

Status: genuine gap record.

## Classification

`WORKER_POSITION_STATUS`: `MOSTLY_COMPLETE`

The Worker position is mostly complete constitutionally, but not fully complete operationally.

## Already Defined

Already defined:

- Worker is execution-only.
- Worker receives only authorized execution requests.
- Worker cannot self-authorize.
- Worker cannot govern.
- Worker cannot mutate replay.
- Worker cannot expand capabilities.
- Worker identity is invocation-scoped.
- Worker replay mapping is specified.
- Worker fail-closed behavior is specified.
- First Worker capability binding is read-only.

## Genuine Gaps

### Worker Registration

No canonical worker registration or registry process is currently defined.

### Worker Discovery

No canonical worker discovery mechanism is currently defined.

### Worker Replaceability

The ability to swap interchangeable workers is not yet canonicalized.

### Worker Specialization

Capability-specific and domain-specific worker taxonomy remains undefined.

### Implemented External Worker Lifecycle

The current artifacts define worker attachment semantics but do not implement a real external worker lifecycle.

### Worker Sandbox Runtime

Worker isolation is specified as a boundary guarantee, but no dedicated Worker sandbox runtime is defined in the Worker artifacts.

## Non-Gaps

These are not gaps:

- Worker authority
- Worker relationship to LLM
- Worker relationship to AiGOL governance
- Worker relationship to authorization
- Worker relationship to replay
- Worker fail-closed expectations

These are already defined sufficiently for the current constitutional baseline.
