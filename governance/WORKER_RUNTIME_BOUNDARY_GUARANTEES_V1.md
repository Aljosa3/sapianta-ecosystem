# Worker Runtime Boundary Guarantees V1

Status: boundary guarantee foundation.

## Boundary Summary

Worker Runtime is execution-only.

It is downstream of:

```text
Proposal Runtime
Proposal Approval Runtime
Execution Request Runtime
Future Dispatch Readiness
```

A Worker cannot create authority. A Worker can only execute assigned bounded work.

## Execution Request Boundary

Workers may receive only:

```text
EXECUTION_REQUEST_ARTIFACT_V1
status = READY_FOR_DISPATCH
```

Current Execution Request Runtime produces only:

```text
status = CREATED
```

Therefore current execution requests are not worker-eligible.

## Provider Boundary

Providers may not:

- assign workers;
- command workers;
- approve worker execution;
- expand worker scope;
- dispatch workers;
- receive worker results as authority;
- bypass AiGOL.

Required invariant:

```text
provider_authority = false
```

## Worker Authority Boundary

Workers may not:

- approve proposals;
- approve execution requests;
- derive execution requests;
- dispatch themselves;
- choose new work;
- expand payload scope;
- mutate governance;
- mutate replay;
- invoke providers for authority;
- create hidden follow-up actions.

Required invariant:

```text
worker_self_assigned = false
self_authorization = false
scope_expansion = false
```

## AiGOL Boundary

AiGOL remains responsible for:

- governance validation;
- execution request lineage validation;
- dispatch-readiness validation;
- worker identity validation;
- capability binding validation;
- assignment recording;
- replay continuity.

AiGOL does not become the worker. Worker execution remains separate from governance validation.

## Human Boundary

Human approval occurs upstream.

Human may not directly dispatch a worker unless a future governed operator dispatch surface is explicitly certified.

Human instructions do not bypass AiGOL validation or replay requirements.

## Replay Boundary

Replay records:

- worker identity;
- capability binding;
- assignment;
- execution start;
- result;
- failure;
- termination.

Replay may not:

- assign workers;
- execute work;
- infer missing identity;
- repair missing result evidence;
- mutate worker state.

## Fail-Closed Guarantees

Worker Runtime must fail closed on:

- missing dispatch-ready execution request;
- corrupt execution request replay;
- missing approval lineage;
- missing worker identity;
- missing capability binding;
- unsupported request type;
- provider command;
- worker self-assignment;
- scope expansion;
- missing result evidence;
- missing termination evidence;
- replay corruption;
- duplicate terminal results;
- hidden continuation.

## Constitutional Invariant

Worker Runtime preserves:

```text
LLM proposes
AiGOL governs
Worker executes
Replay records
```

Meaning:

- LLM/provider output remains upstream proposal evidence only;
- AiGOL governs dispatch eligibility and assignment;
- Worker executes only assigned bounded work;
- Replay records every worker boundary transition.
