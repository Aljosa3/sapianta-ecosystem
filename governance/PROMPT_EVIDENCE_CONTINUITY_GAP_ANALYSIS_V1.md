# PROMPT_EVIDENCE_CONTINUITY_GAP_ANALYSIS_V1

## Gap 1: Structured Prompt Evidence Is Not Preserved In OpenAI Provider Envelopes

Count:

```text
29 / 34 failed or non-conversation outcomes
```

Observed failure:

```text
provider-assisted conversation failed closed: human_prompt is required
```

Root cause:

The OpenAI adapter records an adapter-level request in the provider proposal
envelope. That request includes the OpenAI `payload.input` but not the original
provider-assisted request's structured `human_prompt`.

Category:

```text
provider request construction / adapter request transformation
```

Not caused by:

- replay serialization;
- replay reconstruction;
- routing;
- provider response generation;
- worker execution;
- governance mutation.

## Gap 2: Classification Normalization Reads Only Structured Request Evidence

The fourth-epoch refinement requires:

```text
provider_proposal_envelope.request.human_prompt
```

It does not reconstruct the prompt from:

- `000_human_prompt_artifact.json`;
- conversation start artifact;
- `request.payload.input`.

This is fail-closed and replay-visible, but it blocks use of already-recorded
prompt evidence.

## Gap 3: Provider Availability Remains Separate

Count:

```text
3 / 34
```

These failures are not prompt continuity failures. Prompt evidence exists, but
the provider did not return a response.

## Gap 4: Authority Validation Is Separate

Count:

```text
1 / 34
```

Prompt evidence exists. The failure was caused by authority-bearing text
validation, not prompt evidence continuity.

## Gap 5: Non-Conversation Routing Is Separate

Count:

```text
1 / 34
```

The prompt was stored in the human prompt artifact, but the operation routed to
`CONSTITUTIONAL_MEMORY_CONSULTATION` and did not create a conversation response.

## Loss-Point Taxonomy

| Loss or failure category | Count | Cause |
| --- | ---: | --- |
| OpenAI adapter request envelope lost structured `human_prompt` | 29 | Provider request construction / adapter transformation |
| Provider unavailable before response | 3 | Provider availability |
| No prompt loss; authority validation | 1 | Conversation response validation |
| No prompt loss; non-conversation route | 1 | Routing destination outside conversation |

## Reconstructability

The missing prompt can be deterministically reconstructed in every analyzed
case from existing replay evidence.

No constitutional authority transfer is required to restore continuity.
