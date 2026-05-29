# External Worker Boundary Guarantees V1

Status: boundary guarantees for the first external Worker attachment.

## Boundary Principle

The external Worker is execution-only.

It receives an AiGOL-authorized request and returns bounded inspection evidence. It cannot create, modify, or reinterpret authorization.

## Required Boundary Conditions

The Worker boundary requires:

- explicit worker identity
- explicit authorized execution request
- target capability limited to `READ_ONLY_RUNTIME_INSPECTION`
- read-only inspection classification
- no mutation authority
- no direct provider-to-worker path
- no direct human-to-worker path
- no replay bypass
- deterministic termination

## Authority Separation

The Worker must never obtain:

- proposal authority
- authorization authority
- governance authority
- replay authority
- capability expansion authority
- orchestration authority

AiGOL remains the governance authority. Provider output remains proposal input. Replay remains the evidence record.

## Prohibited Surfaces

The external Worker does not enable:

- filesystem write, delete, move, or modification
- shell execution
- network execution
- API execution
- worker self-authorization
- worker autonomy
- hidden continuation

## Boundary Failure

Boundary ambiguity fails closed before Worker inspection.

Failures are replay-visible and terminal. There are no retries, silent recovery paths, or continuation after failure.

