# Intent Classifier Input Model V1

Status: input boundary model for Intent Classifier.

## Allowed Inputs

### Human Prompt

Classification: `ALLOWED`

Reason: classifier exists to classify Human Prompt intent.

### Normalized Request

Classification: `ALLOWED`

Reason: normalized request evidence reduces ambiguity and preserves replay lineage.

## Conditional Inputs

### Constitutional Memory Context

Classification: `CONDITIONAL`

Allowed only when:

- memory context is returned through Constitutional Memory access
- citations are present
- retrieval is replay-visible
- memory remains reference-only
- classifier does not treat memory as authority

### Provider Output

Classification: `CONDITIONAL`

Allowed only as prior replay-visible evidence, not as authority.

Provider output must not cause automatic provider invocation.

### Worker Output

Classification: `CONDITIONAL`

Allowed only as replay-visible historical evidence, not as authority.

Worker output must not cause automatic worker invocation.

## Forbidden Inputs

The classifier must not receive hidden memory, hidden provider context, hidden worker state, or non-replay-visible context.

## Input Boundary

Every classifier input must be:

- explicit
- replay-visible
- bounded
- non-authoritative

