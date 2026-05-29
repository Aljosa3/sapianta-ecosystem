# Operator Replay View Model V1

Status: deterministic replay view model.

## View Contract

The operator replay view presents existing replay evidence using stable fields:

| Field | Meaning |
| --- | --- |
| Replay ID | operator-provided replay identifier or replay directory name |
| Status | governed result status |
| Capability | capability used by the governed flow |
| Authorization Status | authorization outcome reconstructed from bridge replay |
| Verification Status | replay verification result |
| Result Summary | governed result reason |
| Timestamp / Ordering Information | creation timestamp and lifecycle ordering |

## Verification

The replay view must verify:

- operator replay artifact hashes
- replay wrapper hashes
- replay ordering
- bridge replay reconstruction
- governed result summary hash

## Non-Authority

The replay view must not:

- authorize execution
- execute work
- repair replay
- infer missing replay
- create memory
- route requests
- create orchestration

## Operator Use

The operator may use this command to understand a replay outcome before deciding whether to retain evidence, retry with a bounded request, or stop.
