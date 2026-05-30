# Intent Routing Attachment Replay Model V1

Status: replay model for Intent Routing Attachment V1.

## Replay Visibility

`INTENT_ROUTING_ATTACHMENT_REPLAY_STATUS`: `READY`

Replay is mandatory for every routing attachment attempt.

## Replay Files

The implemented replay chain is:

```text
000_intent_routing_attachment_record.json
001_intent_routing_attachment_replay.json
```

## Replay Contents

Replay records include:

- routing record reference
- source artifact reference
- destination evidence
- routing status
- routing version
- routing record hash
- replay reference
- destination invoked flag

## Reconstruction

Runtime reconstruction validates:

- replay ordering
- replay step identity
- wrapper hash integrity
- record hash integrity
- replay-to-record linkage
- routing status and destination semantics
- destination invocation absence

## Replay Boundary

Replay proves:

```text
Intent Artifact
-> Routing Attachment
-> Destination Evidence
```

It does not invoke the destination.

