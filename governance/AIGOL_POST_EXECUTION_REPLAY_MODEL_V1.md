# AIGOL_POST_EXECUTION_REPLAY_MODEL_V1

## Status

Certified constitutional replay model.

## Purpose

Define the replay evidence and reconstruction rules required after governed
Worker execution.

## Replay Principle

Replay is the append-only constitutional record of execution lifecycle evidence.

Replay does not:

- authorize execution;
- invoke Workers;
- repair missing authority;
- infer missing evidence;
- accept results;
- retry execution;
- mutate governance;
- create hidden continuation.

## Canonical Replay Chain

```text
intent_lineage
-> proposal_lineage
-> approval_lineage
-> implementation_handoff
-> execution_candidate
-> execution_packet
-> execution_validation
-> execution_ready_status
-> execution_authorization
-> worker_invocation_request
-> worker_assignment
-> dispatch
-> worker_invocation
-> worker_execution_evidence
-> worker_result
-> result_validation
-> post_execution_replay_review
-> termination
```

Rejected, revoked, expired, cancelled, failed, and partial paths must remain
reconstructable.

## Required Replay Evidence

Post-execution replay must preserve:

- stable chain id;
- ordered replay indices and timestamps;
- all artifact references and hashes;
- authorization scope and revocation state;
- Worker identity, role, capability, assignment, and dispatch evidence;
- invocation parameters and parameter hash;
- execution evidence;
- outputs and output hashes;
- result disposition;
- result validation evidence;
- termination status;
- explicit evidence of policy violations or failure.

## Post-Execution Replay Review

`POST_EXECUTION_REPLAY_REVIEW_ARTIFACT_V1` must answer:

- Was execution authorized?
- Was authorization active at invocation?
- Was the correct Worker invoked?
- Did execution remain within scope?
- Were forbidden operations absent?
- Are outputs and results hash-verifiable?
- Did result validation complete?
- Is termination explicit?
- Can the full chain be reconstructed without inference?
- Did replay remain non-authoritative and append-only?

## Replay Reconstruction

Reconstruction must verify:

- expected artifact presence;
- canonical ordering;
- timestamp ordering;
- chain continuity;
- reference continuity;
- authorization continuity;
- invocation continuity;
- result continuity;
- wrapper and inner artifact hash integrity;
- valid terminal state;
- absence of duplicate invocation or hidden continuation.

## Replay Review Outcomes

Replay review recognizes:

- `REPLAY_REVIEW_PASSED`;
- `REPLAY_REVIEW_FAILED_CLOSED`;
- `REPLAY_REVIEW_REQUIRES_HUMAN_REVIEW`.

A failed or incomplete replay review prevents result promotion and future
continuation under the same execution authority.

## Retention And Immutability

Execution replay must be retained as historical evidence.

Revocation, rejection, validation failure, or later policy changes must not
rewrite prior replay. Corrections require new append-only evidence linked to the
original chain.

## Constitutional Rule

```text
Worker executes.
Replay records.
Replay never becomes authority.
```
