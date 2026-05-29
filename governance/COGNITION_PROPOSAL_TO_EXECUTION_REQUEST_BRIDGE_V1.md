# Cognition Proposal To Execution Request Bridge V1

Status: permanent invariant hardening milestone.

This artifact clarifies the constitutional bridge between bounded cognition output and governed execution request creation. It introduces no new runtime capability, no autonomous execution, no agent runtime, no orchestration runtime, and no cognition authority.

## Primary Invariant

AiGOL permanently preserves:

- LLM / cognition proposes only.
- AiGOL governs, validates, authorizes, rejects, records, and enforces constitutional constraints.
- Worker / deterministic execution runtime executes only bounded authorized tasks.
- Replay records lineage, authorization evidence, execution evidence, rejection evidence, and governed return evidence.

There must never be:

```text
LLM -> executes
```

There must only be:

```text
LLM -> proposes
AiGOL -> validates / authorizes / rejects
Worker -> executes bounded authorized task
AiGOL -> records replay / lineage / evidence
```

## Canonical Flow

```text
Human prompt
-> LLM cognition proposal
-> AiGOL proposal normalization
-> AiGOL constitutional validation
-> AiGOL Layer 0-4 governance checks
-> AiGOL authorization or rejection
-> governed execution request
-> worker / deterministic execution runtime
-> replay-visible result
-> governed return
```

## Proposal Semantics

An LLM output is an untrusted proposal input.

It is not:

- execution authority
- authorization authority
- governance authority
- worker authority
- orchestration authority
- planning authority

The proposal may describe a requested bounded action, but it cannot perform, authorize, escalate, route, retry, continue, or mutate that action.

## Execution Request Semantics

A governed execution request may exist only after AiGOL completes:

- deterministic proposal normalization
- constitutional validation
- authority boundary validation
- capability boundary validation
- replay lineage validation
- explicit authorization or rejection

If any step is ambiguous, missing, malformed, unsupported, unauthorized, or boundary-violating, the bridge must fail closed.

## Worker Semantics

The worker or deterministic execution runtime executes only an already authorized governed execution request.

The worker must not:

- self-authorize
- expand capability scope
- infer governance approval
- bypass replay
- mutate constitutional authority
- continue after failure
- create hidden state

## Architectural Status

This milestone hardens terminology and invariants only.

It does not introduce:

- LLM execution
- autonomous execution
- agent runtime
- direct cognition-to-execution authority
- cognition authority
- worker autonomy
- orchestration runtime
- capability expansion

Success is permanent constitutional clarification:

```text
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```
