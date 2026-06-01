# PROVIDER_NORMALIZATION_LAYER_FINDINGS_V1

## Findings Summary

The provider normalization layer is provider-generic at the AiGOL conversation
runtime boundary.

It is not OpenAI-specific.

## Finding 1: Normalization Uses Envelope Shape

The conversation runtime reads:

```text
provider_proposal_envelope.response
```

It does not inspect OpenAI API fields such as:

```text
output_text
output
model
raw_response
```

Vendor-specific raw response extraction remains inside provider adapters.

## Finding 2: Two Response Forms Are Supported

Structured provider response:

```text
suggested_response_text
response_reasoning
confidence
```

Generic provider response:

```text
response_text
```

Both can produce the same AiGOL validation artifact.

## Finding 3: Simulated Provider Substitution Passed

Simulated providers:

| Provider | Result | Confidence |
| --- | --- | --- |
| OpenAI | `PROVIDER_ASSISTED_CONVERSATION_RESPONSE_CREATED` | `PROVIDER_TEXT_NORMALIZED` |
| Claude | `PROVIDER_ASSISTED_CONVERSATION_RESPONSE_CREATED` | `PROVIDER_TEXT_NORMALIZED` |
| Gemini | `PROVIDER_ASSISTED_CONVERSATION_RESPONSE_CREATED` | `PROVIDER_TEXT_NORMALIZED` |
| Local Provider | `PROVIDER_ASSISTED_CONVERSATION_RESPONSE_CREATED` | `PROVIDER_TEXT_NORMALIZED` |

## Finding 4: Governance Does Not Change

Provider response remains proposal evidence only.

No provider obtains:

- governance authority;
- authorization authority;
- execution authority;
- worker authority;
- dispatch authority.

## Finding 5: Conversation Runtime Does Not Need Provider-Specific Branches

The runtime requires a valid provider proposal envelope.

Provider identity is replay evidence, not a runtime behavior selector.

## Finding 6: Replay Remains Stable

Replay can reconstruct:

- provider identity;
- provider version;
- provider request;
- provider response;
- proposal hash;
- validation result;
- conversation response.

No replay schema change is required for substitution.

## Finding 7: Remaining Gap Is Adapter-Level

The generic normalization layer does not guarantee that every future provider
adapter can extract usable text from its own API response.

Each real adapter must still fail closed if its vendor response is missing,
malformed, ambiguous, too large, or authority-bearing.

## Final Finding

Provider substitution is certified at the provider proposal envelope and
conversation normalization boundary.

Real-provider onboarding still requires adapter-specific raw response
extraction tests.
