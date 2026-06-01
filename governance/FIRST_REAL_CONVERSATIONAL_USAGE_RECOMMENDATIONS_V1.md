# FIRST_REAL_CONVERSATIONAL_USAGE_RECOMMENDATIONS_V1

## Recommendation

Prioritize connecting the existing provider-assisted conversation runtime to
the Human Prompt CLI surface.

## Recommended Next Step

Implement a bounded prompt response mode:

```text
aigol prompt submit
↓
provider-assisted intent classification
↓
conversation runtime when destination is CONVERSATION
↓
response artifact
↓
replay-backed operator output
```

This should be an extension of the existing prompt surface, not a new CLI
framework.

## Required Properties

The next implementation should preserve:

- self-resolution first;
- provider assistance only when necessary;
- provider response as proposal evidence only;
- AiGOL response validation;
- replay-visible prompt, intent, provider, validation, and response artifacts;
- fail-closed behavior.

## Secondary Improvements

After response activation, improve:

- top-level failure reason propagation;
- prompt replay summaries;
- explanation for unsupported prompts;
- clarification handling for incomplete prompts;
- classifier coverage for replay and capability questions.

## Do Not Prioritize Yet

The usage epoch does not support prioritizing:

- new workers;
- new providers;
- orchestration;
- planning;
- autonomous dispatch;
- broad semantic memory.

## Final Recommendation

The next bottleneck for AiGOL evolution is:

```text
Prompt-to-response activation
```

not provider expansion, worker expansion, or governance redesign.
