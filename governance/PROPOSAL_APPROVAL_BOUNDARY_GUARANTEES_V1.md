# Proposal Approval Boundary Guarantees V1

Status: boundary guarantees.

## Certified Guarantees

Proposal approval preserves the boundary between proposal creation and future execution.

## Human Approval Boundary

Only a human operator may approve a proposal.

Human approval is valid only after AiGOL inspection.

Human approval does not by itself create execution authority.

## AiGOL Boundary

AiGOL may:

- inspect proposals;
- open pending approval;
- record human approval evidence;
- record human rejection evidence;
- expire pending approvals deterministically;
- transition lifecycle state from valid approval evidence.

AiGOL may not treat missing human approval as approval.

## Provider Boundary

Provider may not:

- approve;
- reject;
- expire;
- inspect;
- authorize;
- execute;
- dispatch workers;
- mutate replay.

Provider output remains proposal evidence only.

## Worker Boundary

Worker may not:

- approve proposals;
- reject proposals;
- infer approval;
- inspect proposals;
- expand proposal scope;
- self-authorize execution.

Worker execution remains future work and requires governed execution request authorization.

## Replay Boundary

Replay records and reconstructs approval decisions.

Replay may not:

- create approval;
- infer approval;
- repair missing approval;
- mutate proposal state;
- dispatch execution.

## Execution Boundary

Approval does not:

- execute work;
- create worker task;
- create execution request by itself;
- authorize provider execution;
- bypass future governed execution request validation.

## Required Non-Execution Flags

Approval evidence must preserve:

```text
execution_performed = false
worker_dispatched = false
provider_dispatched = false
execution_request_created = false
autonomous_continuation_performed = false
governance_mutation_performed = false
```

## Fail-Closed Boundary

Approval must fail closed on:

- missing inspection evidence;
- missing human decision;
- provider decision;
- worker decision;
- replay-inferred decision;
- proposal hash mismatch;
- inspection hash mismatch;
- expired proposal;
- rejected proposal;
- execution already performed;
- approval artifact missing non-execution flags.

## Constitutional Invariant

Approval preserves:

```text
LLM proposes
AiGOL governs
Worker executes
Replay records
```

Mapping:

```text
LLM proposes = provider evidence remains non-authoritative
AiGOL governs = AiGOL verifies inspection, records human decision, and preserves boundaries
Worker executes = no worker execution occurs during approval
Replay records = replay records and reconstructs approval evidence
```

## Boundary Result

```text
PROPOSAL_APPROVAL_BOUNDARY_STATUS = PRESERVED
```
