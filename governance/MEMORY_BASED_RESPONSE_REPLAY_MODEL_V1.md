# Memory Based Response Replay Model V1

Status: replay model for future Memory-Based Response implementation.

## Replay Requirement

Response generation replay is `MANDATORY`.

## Mandatory Records

A future response artifact must record:

- citation bundle used: `MANDATORY`
- consultation record reference: `MANDATORY`
- artifact references used: `MANDATORY`
- response record: `MANDATORY`
- response reconstruction metadata: `MANDATORY`
- response status: `MANDATORY`
- replay hash: `MANDATORY`

## Reconstruction Requirements

Replay observer must reconstruct:

- why the response was generated
- which consultation record was used
- which citations were used
- which artifacts were referenced
- what summary was returned
- whether generation failed closed

Classification: `REQUIRED`

## Replay Status

`MEMORY_BASED_RESPONSE_REPLAY_STATUS`: `READY_WITH_GAPS`

The consultation replay already exists. The remaining gap is a dedicated response replay artifact that links the response to the consultation record.
