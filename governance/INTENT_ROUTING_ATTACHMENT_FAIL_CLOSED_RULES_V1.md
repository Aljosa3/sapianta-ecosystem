# Intent Routing Attachment Fail-Closed Rules V1

Status: fail-closed rules for Intent Routing Attachment V1.

## Fail-Closed Conditions

The attachment fails closed on:

- unknown destination
- invalid destination
- missing artifact
- corrupt artifact
- ambiguous artifact
- multiple destinations
- authority-bearing artifact
- replay corruption
- append-only violations
- replay ordering mismatch

## Failure Record

Failure emits an `INTENT_ROUTING_ATTACHMENT_RECORD` with:

- `routing_status`: `FAILED_CLOSED`
- `destination`: null
- failure reason
- source artifact reference when available
- routing version
- replay reference

## No Fallback

The attachment does not:

- retry
- guess destination
- fall back to conversation
- activate destination
- correct classification artifacts
- continue into provider, worker, execution, memory, or conversation handling

## Invalid Output Protection

Records containing authorization, governance, execution, provider command, worker command, memory retrieval, or conversation response fields are invalid.

