# Second Read-Only Capability Attachment V1

Status: second bounded read-only capability milestone.

This artifact documents the first filesystem read-only inspection capability attached to the existing execution runtime. It does not introduce filesystem write, filesystem mutation, shell execution, network execution, API execution, orchestration runtime, or agent runtime.

## Capability

Capability identifier:

```text
FILESYSTEM_READ_ONLY_INSPECTION
```

Capability class:

```text
READ_ONLY / INSPECTION
```

Risk:

```text
LOW
```

## Scope

The capability may inspect only explicitly allowed paths.

It may:

- inspect file metadata
- inspect directory metadata
- list one directory level for an allowed directory
- read a bounded UTF-8 preview from an allowed file

It must not:

- write
- delete
- move
- modify
- execute
- access network
- invoke shell

## Execution Flow

The capability follows:

```text
REQUESTED -> VALIDATED -> AUTHORIZED -> EXECUTED -> TERMINATED
```

or fails closed as `FAILED`.

## Fail-Closed Conditions

The capability fails closed on:

- unauthorized execution
- boundary violation
- invalid capability classification
- forbidden path access
- path ambiguity
- replay discontinuity
- lifecycle corruption

