# FOURTH_REAL_CONVERSATIONAL_USAGE_RECOMMENDATIONS_V1

## Recommendation 1: Preserve Original Provider-Assisted Request Evidence Across Adapter Boundaries

Priority:

```text
HIGHEST
```

Evidence:

```text
29 failures = human_prompt is required
```

Recommended next work:

Review how provider attachment captures original structured request evidence
when the OpenAI adapter transforms it into an OpenAI payload. The classifier
normalization gate needs replay-visible access to the original `human_prompt`
or equivalent prompt evidence.

Constraint:

Do not expose API keys. Do not grant provider routing authority. AiGOL must
remain the validator of the normalized destination.

## Recommendation 2: Decide Whether Quoted Bad Authority Examples Should Be Allowed

Priority:

```text
MEDIUM
```

Evidence:

`Explain provider boundaries.` failed because the provider used direct
forbidden authority wording as an example.

Recommended next work:

Evaluate whether the validator should distinguish a quoted forbidden example
from an actual provider authority claim.

Constraint:

Direct claims such as `I authorize execution` must still fail closed when
presented as an operative instruction.

## Recommendation 3: Add A Fifth Epoch After Request Evidence Preservation

Priority:

```text
HIGH
```

Evidence:

The fourth epoch improved success from 12% to 32%, but 29 failures are now
clustered in one evidence-preservation gap.

Recommended next work:

After addressing that gap, rerun the same 50-prompt set to measure whether
classification normalization can convert the remaining relevant provider
responses into final conversation responses.

## Recommendation 4: Keep Provider Unavailability Fail-Closed

Priority:

```text
MEDIUM
```

Evidence:

Three prompts failed because the provider was unavailable.

Recommended next work:

Continue recording provider unavailability as replay-visible fail-closed
evidence.
