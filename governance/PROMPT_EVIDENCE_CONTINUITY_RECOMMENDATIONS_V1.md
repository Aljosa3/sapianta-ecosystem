# PROMPT_EVIDENCE_CONTINUITY_RECOMMENDATIONS_V1

## Recommendation 1: Preserve Original Provider Request Evidence Beside Adapter Payload

Priority:

```text
HIGHEST
```

Evidence:

```text
29 failures require structured human_prompt evidence.
```

Recommended next work:

Ensure provider proposal envelopes or adjacent replay evidence preserve the
original provider-assisted request fields alongside the adapter-specific OpenAI
payload.

Required fields:

```text
semantic_task
human_prompt
human_request_reference
allowed_destinations
context_capsule
```

Constraint:

Do not persist or expose API keys. Do not grant provider authority. Preserve
provider output as proposal evidence only.

## Recommendation 2: Keep Adapter Payload Evidence

Priority:

```text
HIGH
```

The OpenAI adapter payload is useful transport evidence and should remain
replay-visible, with `api_key_captured = false`.

The fix should add continuity, not remove transport evidence.

## Recommendation 3: Prefer Structured Replay Evidence Over Parsing Payload Text

Priority:

```text
HIGH
```

Although `payload.input` contains the prompt text, parsing it is less robust
than preserving `human_prompt` as structured replay evidence.

Recommended principle:

```text
structured prompt evidence first; payload parsing only as fallback analysis
```

## Recommendation 4: Validate Prompt Continuity With A Fifth Epoch

Priority:

```text
HIGH
```

After preserving structured request evidence across the adapter boundary, rerun
the same 50-prompt set to measure whether the 29 classification-normalization
failures convert into valid conversational responses.

## Recommendation 5: Keep Non-Prompt Failures Separate

Priority:

```text
MEDIUM
```

Do not conflate prompt continuity with:

- provider unavailability;
- authority text validation;
- non-conversation routing.

Those are separate bottlenecks and should remain separately measured.
