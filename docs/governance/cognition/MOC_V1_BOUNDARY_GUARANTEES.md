# MOC_V1_BOUNDARY_GUARANTEES

Status: boundary specification.

## Core Boundary

Cognition does not equal authority.

MOC V1 is a bounded operational cognition protocol. It may produce advisory semantic contracts and proposals, but it cannot execute, dispatch, mutate, activate providers, or issue authority.

## Positive Guarantees

MOC V1 preserves:

- read-only governance interpretation until explicit downstream authorization
- replay-visible semantic contract formation
- advisory-only proposal semantics
- explicit human approval boundary
- explicit worker task boundary
- governed return interpretation boundary
- deterministic constraint visibility

## Negative Guarantees

MOC V1 does not introduce:

- execution authority
- orchestration
- autonomous cognition
- autonomous continuation
- hidden continuation
- worker dispatch
- provider activation
- runtime mutation
- governance mutation
- semantic repair
- hidden inference
- semantic truth certification

## Approval Boundary

Human approval is required before any worker task can be considered. Human approval does not itself execute a task, dispatch a worker, or activate a provider.

## Worker Boundary

Worker task proposals are bounded proposals only. MOC V1 may prepare a task proposal, but it must not dispatch it.

## Return Boundary

MOC V1 may interpret governed returns as evidence summaries. Return interpretation does not certify semantic truth, correctness, compliance, or execution success beyond explicit governed return evidence.

## Replay Boundary

MOC V1 artifacts must remain replay-safe. Missing evidence must remain explicit and must not be inferred, repaired, or silently completed.
