# Constitutional Memory Access Replay Model V1

Status: replay model for the first Constitutional Memory access path.

## Replay Requirement

Every retrieval attempt must produce replay-visible evidence.

Replay visibility is mandatory for both successful and failed retrievals.

## Replay Sequence

The minimal replay chain is:

```text
000_retrieval_request.json
001_citation_bundle.json
002_retrieval_result.json
```

Successful lifecycle:

```text
REQUESTED
-> RETRIEVED
-> RETURNED
```

Failed lifecycle:

```text
REQUESTED
-> FAILED
-> FAILED
```

or, when the request itself is invalid:

```text
FAILED
-> FAILED
-> FAILED
```

## Replay Contents

Replay records include:

- retrieval request
- retrieval scope
- returned citations
- returned artifact identities
- retrieval status
- failure reason when failed closed
- artifact hashes
- replay wrapper hashes

## Append-Only Semantics

Replay artifacts are written immutably.

Existing replay files are not overwritten. A write collision fails closed.

## Reconstruction

Replay reconstruction validates:

- replay ordering
- replay step identity
- artifact hash integrity
- replay wrapper hash integrity
- lifecycle state ordering

Invalid replay fails closed.

