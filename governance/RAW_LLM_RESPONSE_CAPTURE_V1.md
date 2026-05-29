# Raw LLM Response Capture V1

Status: model-only raw response capture definition.

## Purpose

Raw LLM response capture makes external LLM output replay-visible before normalization.

Raw capture prevents hidden transformation, preserves failure evidence, and allows malformed or rejected provider output to remain inspectable without granting authority.

## Capture Requirements

Raw response capture must record:

- provider identity envelope
- raw response text or deterministic absence marker
- raw response hash
- response capture timestamp
- invocation id
- response id
- capture status
- normalization status
- normalization reason when rejected

## Replay Requirements

Raw response evidence must be:

- replay-visible
- deterministic
- hash-linked
- immutable after capture
- preserved even when normalization fails

## No Hidden Transformation

Raw LLM output must not be silently rewritten before raw capture.

Any transformation after capture must occur through deterministic proposal normalization and must be replay-linked to the raw response hash.

## Non-Authority Rule

Raw response evidence is not:

- execution authority
- authorization evidence
- worker instruction authority
- governance authority
- replay replacement

It is provider boundary evidence.

## Fail-Closed Capture Conditions

Raw response capture must fail closed when:

- raw response hash does not match raw response text
- raw response evidence mutates
- provider identity is absent
- response id is absent
- replay lineage cannot link identity to response
- capture ordering is ambiguous
- raw response absence is not explicitly represented
