# Capability Class Model V1

Status: capability class definitions only.

## READ_ONLY

Purpose: observe bounded information without mutation.

Replay requirements:

- request, validation, authorization, execution evidence, and termination must be replay-visible
- output must include deterministic evidence hash

Authorization requirements:

- explicit authorization required
- capability scope must be bounded

Boundary requirements:

- no write
- no delete
- no move
- no network mutation
- no shell mutation
- no API mutation

Fail-closed requirements:

- ambiguity, missing authorization, mutation signal, or replay discontinuity fails closed

## INSPECTION

Purpose: inspect bounded metadata or runtime-visible state without mutation.

Replay requirements:

- inspected fields must be declared
- blocked fields must remain visible
- evidence hash required

Authorization requirements:

- explicit authorization required
- inspected scope must be defined

Boundary requirements:

- no secret exposure
- no process control
- no environment dumping
- no persistent monitoring

Fail-closed requirements:

- unsafe field ambiguity or inspection scope ambiguity fails closed

## QUERY

Purpose: request bounded information from a declared source.

Replay requirements:

- query request and response must be captured
- endpoint or source scope must be replay-visible

Authorization requirements:

- explicit authorization required
- source, method, and response handling must be bounded

Boundary requirements:

- no create
- no update
- no delete
- no hidden continuation

Fail-closed requirements:

- ambiguous source, missing response capture, or mutation pressure fails closed

## MUTATION

Purpose: change state.

Constitutional treatment: denied by default.

Replay requirements:

- future mutation would require pre-change and post-change evidence
- not enabled by this taxonomy

Authorization requirements:

- future constitutional gate required

Boundary requirements:

- currently denied

Fail-closed requirements:

- any mutation request under current baseline fails closed

## DESTRUCTIVE

Purpose: remove, delete, destroy, revoke, overwrite, or irreversibly change state.

Constitutional treatment: denied.

Replay requirements:

- not enabled by this taxonomy

Authorization requirements:

- not authorized by current baseline

Boundary requirements:

- denied

Fail-closed requirements:

- destructive request fails closed

## PRIVILEGED

Purpose: access elevated authority, privileged process control, protected resources, or constitutional mutation surfaces.

Constitutional treatment: denied.

Replay requirements:

- privileged request must be recorded as violation evidence if attempted

Authorization requirements:

- not authorized by current baseline

Boundary requirements:

- denied

Fail-closed requirements:

- privileged request fails closed

