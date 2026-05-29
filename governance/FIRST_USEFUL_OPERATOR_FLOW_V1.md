# First Useful Operator Flow V1

Status: first practical AiGOL interaction model.

## First Useful Flow

The first useful operator flow is:

```text
operator submits one request
-> AiGOL runs frozen governed read-only flow
-> AiGOL returns concise governed result summary
-> replay evidence remains available for verification
```

## What Makes It Useful

This flow is useful because it gives a human:

- a clear invocation boundary
- accepted or rejected result
- capability used
- replay evidence location
- replay verification status
- short result or rejection reason
- explicit authority boundary reminder

## What It Does Not Do

It does not:

- write files
- run shell commands
- access network
- invoke APIs
- route autonomously
- orchestrate workers
- persist memory
- create agents

## First Useful Scope

The first useful scope is intentionally small:

- runtime metadata inspection
- allowlisted filesystem read-only inspection
- governed result summary
- replay visibility
- fail-closed rejection

This is enough to prove practical operator usage without expanding authority.
