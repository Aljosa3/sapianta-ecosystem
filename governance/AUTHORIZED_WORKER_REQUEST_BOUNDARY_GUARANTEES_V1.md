# AUTHORIZED_WORKER_REQUEST_BOUNDARY_GUARANTEES_V1

## Status

Certified boundary guarantees.

## Authorized Worker Request May

- reference an authorization artifact
- identify a worker target
- bind an authorized scope
- bind a capability
- provide replay-visible lineage
- serve as the legal worker handoff object

## Authorized Worker Request May Not

- execute work
- dispatch work
- invoke worker
- exceed authorization scope
- carry raw provider output
- carry raw proposal text as authority
- carry raw authorization artifact as authority
- create governance authority
- create replay authority
- create worker self-authorization

## Worker Receive Rule

Worker may receive:

```text
AUTHORIZED_WORKER_REQUEST
```

Worker may not receive:

- raw provider output
- raw proposal
- raw authorization artifact
- replay artifact as authority
- cognition artifact as authority

## Authority Status

Provider authority = none.

Proposal authority = none.

Authorization authority = bounded.

Authorized request authority = bounded.

Worker authority = execution only and only after worker boundary validation.
