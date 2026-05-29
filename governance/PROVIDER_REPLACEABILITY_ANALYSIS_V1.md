# Provider Replaceability Analysis V1

Status: provider replacement and substitutability review.

## Replaceability Classification

`PROVIDER_REPLACEABILITY`: `PARTIAL`

Provider substitution is constitutionally supported, but a complete provider ecosystem is not defined.

## Provider-Agnostic Evidence

Evidence supporting substitutability:

- Provider identity is generic.
- Provider output is treated as untrusted proposal input.
- Raw provider response capture records `provider_name` and `model_name` without provider-specific authority.
- External attachment accepts externally supplied LLM responses without SDK binding.
- Provider replay records identity and raw response before proposal normalization.
- OpenAI and Claude readiness are both classified as `READY_WITH_CONSTRAINTS`.

## Provider Examples

### OpenAI

Status: substitutable provider candidate.

OpenAI has implemented adapter-local surfaces, but it is not constitutionally privileged.

### Claude

Status: substitutable provider candidate.

Claude requires adapter-local transport, response extraction, and credential handling, but no constitutional modification.

### Gemini

Status: substitutable future provider candidate.

No Gemini adapter exists in the reviewed evidence. It can be represented through generic provider identity and raw response capture if it preserves proposal-only semantics.

### Local LLM

Status: substitutable future provider candidate.

Local models can be represented as provider identities and proposal sources if they remain non-authoritative and replay-visible.

### Future Provider

Status: substitutable future provider candidate.

Future providers require adapter-local boundary work, not constitutional authority changes.

## Replay Compatibility

Classification: `COMPLETE`

Replay already supports:

```text
Provider A
-> raw provider response
-> normalized proposal
-> governed result
```

and:

```text
Provider B
-> raw provider response
-> normalized proposal
-> governed result
```

without changing constitutional semantics.

## Provider Selection

Classification: `UNDEFINED`

Provider selection is not currently a canonical multi-provider decision system.

Evidence:

- Existing registry validation reports `dynamic_selection_present: False`.
- Existing registry validation reports `routing_present: False`.
- OpenAI or Claude adapter choice remains implementation or operator policy, not an AiGOL routing subsystem.

## Replacement Boundary

Provider replacement should require:

- provider identity capture
- raw response replay before normalization
- proposal-only boundary preservation
- deterministic failure mapping
- no provider authority
- no bypass of AiGOL governance

It should not require constitutional modification.

