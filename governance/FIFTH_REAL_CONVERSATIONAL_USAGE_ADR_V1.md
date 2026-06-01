# FIFTH_REAL_CONVERSATIONAL_USAGE_ADR_V1

## Status

Accepted.

## Context

The second and third conversational usage epochs produced 6 successful
responses out of 50 prompts. The fourth epoch increased coverage to 16 out of
50 after provider response acceptance contract refinement.

`PROMPT_EVIDENCE_CONTINUITY_RESTORATION_V1` restored structured prompt
continuity across provider proposal envelopes.

The fifth epoch re-ran the same 50-prompt corpus through the normal AiGOL CLI
path to measure actual impact.

## Decision

AiGOL records:

```text
FIFTH_REAL_CONVERSATIONAL_USAGE_STATUS = READY_WITH_GAPS
```

This status is justified because the fifth epoch produced:

```text
responses_created = 41
prompts_submitted = 50
success_rate = 82%
```

The observed improvement is material compared to the 32% fourth-epoch baseline.

## Evidence

Execution path:

```text
python -m aigol.cli.aigol_cli prompt submit
```

Runtime root:

```text
/tmp/aigol_fifth_conversation_epoch/
```

Comparison:

```text
Second epoch = 6 / 50 = 12%
Third epoch = 6 / 50 = 12%
Fourth epoch = 16 / 50 = 32%
Fifth epoch = 41 / 50 = 82%
```

The prior `human_prompt is required` failure did not recur.

## Consequences

AiGOL may claim that, for the observed fifth-epoch prompt corpus, prompt
evidence continuity restoration materially improved conversational coverage.

AiGOL may not claim full conversational readiness. Remaining gaps include:

- ambiguous provider-assisted classification;
- authority text validation edge cases;
- provider availability variability;
- non-conversation intent response coverage;
- evidence-limited answers for state/history questions.

## Boundaries

This ADR does not change:

- provider authority;
- routing authority;
- worker authority;
- authorization semantics;
- replay architecture;
- governance architecture.

The provider remains proposal evidence only. AiGOL remains the validating
authority for final artifacts.
