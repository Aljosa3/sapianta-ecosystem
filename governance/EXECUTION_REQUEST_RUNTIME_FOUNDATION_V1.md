# Execution Request Runtime Foundation V1

Status: foundation review.

Final classification:

```text
EXECUTION_REQUEST_RUNTIME_FOUNDATION_STATUS = READY_WITH_GAPS
```

## Scope

This artifact defines the minimal execution request runtime boundary between an approved proposal and future worker execution.

It does not implement runtime code, workers, execution, dispatch, provider behavior, approval changes, governance mutation, deployment behavior, or automatic authorization.

## Context

AiGOL now has:

- Conversational Runtime;
- Resolution Strategy Runtime;
- Proposal Runtime;
- Proposal Approval Runtime.

Approved proposals exist as replay-visible approval dispositions.

The next missing runtime boundary is:

```text
APPROVED Proposal
-> Execution Request
-> Future Worker Execution
```

## 1. What Is An Execution Request?

An Execution Request is a governed runtime artifact derived by AiGOL from an approved proposal.

It is not execution.

It is not dispatch.

It is not a worker task.

It is not provider authority.

It is a replay-visible bridge artifact that says:

```text
An approved proposal has been converted into a bounded future execution candidate.
```

## 2. When Can It Be Created?

An Execution Request can be created only when all of the following evidence exists:

- valid proposal runtime artifact;
- proposal status eligible for execution request derivation;
- replay-visible approval evidence;
- approval disposition is `APPROVED`;
- proposal hash matches approval evidence;
- request payload is bounded to the approved proposal scope;
- AiGOL creates the execution request;
- no provider, worker, or automatic path claims creation authority.

If any prerequisite is missing or corrupt, creation must fail closed.

## 3. Proposal States That May Create It

The only proposal state that may create an Execution Request is:

```text
APPROVED
```

If a future lifecycle introduces an explicit inspection state before approval, execution request derivation should prefer:

```text
INSPECTED -> APPROVED -> EXECUTION_REQUEST.CREATED
```

## 4. Proposal States That May Never Create It

These proposal states may never create an Execution Request:

```text
CREATED
INSPECTED
REJECTED
EXPIRED
EXECUTED
REPLAY_RECONSTRUCTED
```

`REPLAY_RECONSTRUCTED` is read-only evidence reconstruction and never creates runtime authority.

## 5. Replay Evidence Required

Before an Execution Request can be created, replay must contain:

- proposal creation event;
- proposal artifact hash;
- proposal source evidence;
- approval artifact;
- approval event showing `APPROVED`;
- approval artifact hash;
- proposal reference matching approval evidence;
- human authorization evidence from approval runtime;
- absence of rejection or expiry after approval;
- absence of prior execution request for the same approved proposal unless duplicate derivation is explicitly certified later.

## 6. Mandatory Fields

The minimal runtime artifact is:

```text
EXECUTION_REQUEST_ARTIFACT_V1
```

Mandatory fields:

```text
execution_request_id
proposal_reference
proposal_hash
approval_reference
approval_hash
requested_by
created_at
request_type
request_payload
status
replay_reference
artifact_hash
```

Required boundary flags:

```text
provider_authority = false
worker_dispatched = false
execution_performed = false
approval_created = false
automatic_authorization = false
replay_visible = true
```

## 7. Reconstruction

Replay reconstructs Execution Request history by reading append-only evidence in deterministic order:

```text
PROPOSAL_RUNTIME_CREATED
PROPOSAL_APPROVED
EXECUTION_REQUEST_CREATED
EXECUTION_REQUEST_RETURNED
```

Reconstruction must verify:

- proposal reference;
- proposal hash;
- approval reference;
- approval hash;
- request id;
- request status;
- request payload hash;
- replay wrapper hash;
- artifact hash;
- non-execution and non-dispatch flags.

Replay may prove that an execution request exists.

Replay may not dispatch a worker, create execution, repair missing approval, or mutate proposal state.

## 8. Constitutional Preservation

Execution Request Runtime preserves:

```text
LLM proposes
AiGOL governs
Worker executes
Replay records
```

Mapping:

| Role | Execution request meaning |
| --- | --- |
| LLM proposes | Provider evidence remains upstream proposal evidence only |
| AiGOL governs | AiGOL derives a bounded request from approved proposal evidence |
| Worker executes | Worker execution is future-only and not implemented by this foundation |
| Replay records | Replay records derivation evidence and reconstruction metadata |

## 9. Transitions

Minimal execution request states:

```text
CREATED
READY_FOR_DISPATCH
CANCELLED
```

This foundation defines states only. It does not implement transitions.

## 10. Future Worker Integration

Future Worker Runtime may consume only a replay-valid request in:

```text
READY_FOR_DISPATCH
```

Worker Runtime must independently verify:

- execution request artifact hash;
- approval lineage;
- request type support;
- request payload bounds;
- worker authorization;
- replay write path;
- no provider authority.

## Gaps

The foundation is ready with gaps because:

- no execution request runtime implementation exists;
- no schema enforcement exists;
- no tests exist;
- no dispatch runtime exists;
- no worker authorization integration exists;
- duplicate derivation policy is not implemented;
- current Proposal Approval Runtime approves from `CREATED`, while earlier foundation documents prefer inspection before approval.

```text
EXECUTION_REQUEST_RUNTIME_FOUNDATION_STATUS = READY_WITH_GAPS
```
