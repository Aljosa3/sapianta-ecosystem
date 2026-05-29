# OpenAI Provider Fail-Closed Rules V1

Status: OpenAI adapter failure model.

## Fail-Closed Conditions

The OpenAI provider adapter fails closed on:

- empty human request
- missing adapter id
- missing timestamp
- missing API key
- invalid API key value
- invalid timeout
- provider client failure
- malformed provider response
- empty provider response
- oversized provider response
- authority escalation attempt
- downstream proposal normalization failure
- replay corruption
- append-only violation
- invalid provider attachment capture

## Failure Artifact

Every failure returns a deterministic governed failure artifact with:

- `final_status = FAILED`
- replay recording preserved
- OpenAI authority denied
- worker execution disabled
- automatic retries disabled
- streaming disabled
- memory disabled
- tool use disabled

## No Recovery Rule

The adapter does not:

- retry automatically
- stream partial results
- repair replay
- reinterpret ambiguous responses
- continue after failure

Failure is explicit, bounded, and replay-visible.

## Authority Escalation Rule

If OpenAI output attempts to authorize itself, execute directly, request mutation, create hidden continuation, or bypass governance, downstream attachment validation fails closed.

## Credential Rule

Credentials are used only by the provider client boundary.

Replay records credential source only and never records secret material.

