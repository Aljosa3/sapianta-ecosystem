# Capability Risk Model V1

Status: capability risk semantics only.

## LOW

Applies to capabilities that observe bounded information without mutation.

Classes:

- `READ_ONLY`
- `INSPECTION`

Requirements:

- explicit authorization
- replay-visible evidence
- bounded scope
- no mutation flags
- fail-closed ambiguity handling

## MEDIUM

Applies to capabilities that request information from a declared source and may involve external response handling.

Classes:

- `QUERY`

Requirements:

- explicit authorization
- source scope
- request and response replay capture
- no mutation methods
- fail-closed response ambiguity handling

## HIGH

Applies to capabilities that change state.

Classes:

- `MUTATION`

Requirements:

- denied under current baseline
- future constitutional gate required before implementation
- any current request fails closed

## CRITICAL

Applies to capabilities that destroy state, use privileged authority, bypass boundaries, or reach constitutional mutation surfaces.

Classes:

- `DESTRUCTIVE`
- `PRIVILEGED`

Requirements:

- denied under current baseline
- violation evidence must be replay-visible if attempted
- any current request fails closed

## Risk Rule

Risk classification does not grant capability.

Risk classification only determines the minimum governance, replay, authorization, boundary, and fail-closed requirements for future capability attachment.

