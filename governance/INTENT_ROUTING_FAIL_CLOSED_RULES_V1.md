# Intent Routing Fail-Closed Rules V1

Status: fail-closed rules for canonical intent routing.

## Required Fail-Closed Conditions

Routing must fail closed on:

- unknown intent
- ambiguous intent
- multiple valid destinations
- conflicting destinations
- missing destination
- invalid destination
- missing prompt reference
- invalid replay parent
- authority-bearing route output
- execution-bearing route output
- provider command output
- worker command output

## Multiple Valid Destinations

If a prompt could validly route to more than one destination and no deterministic disambiguation rule exists, routing must fail closed.

It must not guess.

## Ambiguity Handling

Ambiguity produces:

- `FAILED_CLOSED`
- replay-visible ambiguity reason
- no destination execution
- no provider invocation
- no memory retrieval
- no authorization

## No Silent Fallback

Routing must not silently fall back from:

- execution to conversation
- provider proposal to memory consultation
- memory consultation to provider proposal
- ambiguous route to default route

## Continuation Rule

After routing failure, AiGOL must not continue into a destination unless a separately governed correction process exists.

No correction loop is introduced by this model.

