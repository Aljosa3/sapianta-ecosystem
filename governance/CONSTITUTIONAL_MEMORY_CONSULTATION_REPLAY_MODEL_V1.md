# Constitutional Memory Consultation Replay Model V1

Status: replay model for consultation activation.

## Replay Requirement

Replay is mandatory.

## Mandatory Records

Activation must record:

- retrieval request: `MANDATORY`
- retrieval scope: `MANDATORY`
- retrieval result: `MANDATORY`
- citation bundle: `MANDATORY`
- reconstruction metadata: `MANDATORY`
- routing evidence reference: `MANDATORY`

## Reconstruction Requirements

Replay observer must reconstruct:

- why retrieval occurred
- which routing record selected consultation
- which retrieval scope was used
- which artifacts were consulted
- which citations were returned
- whether consultation failed closed

Classification: `REQUIRED`

## Replay Status

`CONSTITUTIONAL_MEMORY_CONSULTATION_REPLAY_STATUS`: `READY_WITH_GAPS`

The underlying memory access path already records retrieval replay. The remaining gap is activation-level linkage from routing evidence to retrieval request.

