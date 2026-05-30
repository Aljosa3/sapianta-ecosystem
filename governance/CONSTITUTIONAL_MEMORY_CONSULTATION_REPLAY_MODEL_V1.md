# Constitutional Memory Consultation Replay Model V1

Status: implementation replay model for `CONSTITUTIONAL_MEMORY_CONSULTATION_ACTIVATION_V1`.

## Replay Requirement

Replay is mandatory.

## Mandatory Records

Activation records:

- `000_constitutional_memory_consultation_record.json`
- `001_constitutional_memory_consultation_replay.json`

The activation also preserves nested Constitutional Memory access replay:

- `000_retrieval_request.json`
- `001_citation_bundle.json`
- `002_retrieval_result.json`

## Mandatory Evidence

The consultation replay must include:

- routing reference
- consultation record
- retrieval scope
- citation bundle
- reconstruction metadata
- consultation status
- consultation version
- replay hash

## Reconstruction Requirements

Replay observer must reconstruct:

- which routing record selected consultation
- which retrieval scope was used
- which artifacts were consulted
- which citations were returned
- whether consultation failed closed
- that reconstruction did not perform retrieval again

Classification: `REQUIRED`

## Replay Status

`CONSTITUTIONAL_MEMORY_CONSULTATION_REPLAY_STATUS`: `READY`

The activation now links routing evidence to citation evidence through replay-visible artifacts.
