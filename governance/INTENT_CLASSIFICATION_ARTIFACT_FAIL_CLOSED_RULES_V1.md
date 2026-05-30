# Intent Classification Artifact Fail-Closed Rules V1

Status: fail-closed requirements for Intent Classification Artifact.

## Required Behavior

All listed failure modes must `FAIL_CLOSED`.

## Failure Modes

Unknown destination: `FAIL_CLOSED`

Ambiguous destination: `FAIL_CLOSED`

Multiple destinations: `FAIL_CLOSED`

Invalid destination: `FAIL_CLOSED`

Missing destination: `FAIL_CLOSED`

Missing replay reference: `FAIL_CLOSED`

Corrupt artifact: `FAIL_CLOSED`

Missing human request reference: `FAIL_CLOSED`

Missing classification version: `FAIL_CLOSED`

Authority-bearing output: `FAIL_CLOSED`

Execution-bearing output: `FAIL_CLOSED`

## No Silent Defaults

The artifact must not default ambiguous or invalid classifications to `CONVERSATION`.

It must not guess.

It must not emit multiple successful destinations.

## Failure Artifact

Failed classification must remain replay-visible and include:

- artifact id
- failure status
- failure reason
- replay reference when available
- non-authority guarantees

