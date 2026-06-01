# PROVIDER_NORMALIZATION_LAYER_RECOMMENDATIONS_V1

## Recommendation

Proceed with provider substitution using the existing provider proposal
envelope and provider response contract alignment boundary.

Do not redesign governance, replay, provider runtime, or conversation runtime.

## Recommended Provider Adapter Contract

Each provider adapter should emit one of:

```text
response_text
```

or:

```text
suggested_response_text
response_reasoning
confidence
```

inside:

```text
ProviderProposalEnvelope.response
```

## Recommended Real Provider Onboarding Checks

For each real provider:

- raw vendor response can be extracted into bounded text;
- provider proposal envelope validates;
- response is replay visible;
- authority-bearing fields are rejected;
- malformed response fails closed;
- conversation runtime accepts the normalized envelope;
- replay reconstruction succeeds.

## Recommended Next Provider Proof

Attach one additional simulated-to-real provider path, preferably:

```text
LOCAL_PROVIDER_ATTACHMENT_V1
```

or:

```text
SECOND_REAL_PROVIDER_ATTACHMENT_V1
```

The purpose should be to prove adapter-level extraction, not to change the
normalization layer.

## Not Recommended

Do not add:

- provider-specific branches in conversation runtime;
- governance changes for each provider;
- replay schema changes for provider identity;
- provider ranking;
- provider orchestration;
- autonomous provider selection.

## Final Recommendation

Treat `PROVIDER_RESPONSE_CONTRACT_ALIGNMENT_V1` as the canonical provider
normalization layer for conversation responses.

Provider substitution can proceed under existing constitutional boundaries.
