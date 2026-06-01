# PROMPT_EVIDENCE_CONTINUITY_ADR_V1

## Status

Accepted.

## Context

`FOURTH_REAL_CONVERSATIONAL_USAGE_EPOCH_V1` improved conversational success to:

```text
16 / 50 = 32%
```

The main remaining failure category was:

```text
29 failures: human_prompt is required
```

## Decision

Certify prompt evidence continuity analysis as:

```text
PROMPT_EVIDENCE_CONTINUITY_STATUS = READY_WITH_GAPS
```

The analysis may claim:

- original prompts are replay-visible;
- provider payloads contain prompt text for the 29 dominant failures;
- structured `human_prompt` evidence is absent from the OpenAI provider
  proposal envelope request consumed by classification normalization;
- the prompt can be deterministically reconstructed from existing replay
  evidence;
- continuity can be restored without changing constitutional authority
  boundaries.

The analysis may not claim:

- the runtime is fixed;
- provider-assisted classification continuity is complete;
- providers gain routing, governance, worker, replay, or execution authority.

## Consequences

The next implementation target should be request evidence continuity across the
OpenAI adapter boundary, not provider replacement or governance redesign.
