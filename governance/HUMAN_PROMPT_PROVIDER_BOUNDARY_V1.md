# HUMAN_PROMPT_PROVIDER_BOUNDARY_V1

## Provider Boundary

Human Prompt does not require a provider by default.

Provider use is conditional.

## Provider Required

A provider is required when:

- the prompt needs proposal generation;
- the prompt requires open-ended synthesis;
- deterministic AiGOL state cannot produce the candidate proposal;
- the operator asks for drafting or transformation beyond existing replay and Constitutional Memory.

## Provider Unnecessary

A provider is unnecessary when:

- the operator asks for replay verification;
- the operator asks for replay reporting;
- the operator asks for replay-backed explanation;
- the operator asks for Constitutional Memory citation lookup;
- the operator provides explicit bounded operation parameters.

## Boundary Guarantees

Provider remains:

```text
proposal source only
```

Provider cannot:

- authorize;
- govern;
- execute;
- dispatch;
- mutate replay;
- mutate memory;
- command a worker.

## Provider Output

Provider output must become a proposal envelope.

It must remain replay-visible and non-authoritative.

## Adapter Locality

Provider-specific prompt formatting should remain adapter-local.

Human Prompt should not require provider-specific constitutional adaptation.
