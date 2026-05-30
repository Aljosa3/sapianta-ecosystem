# Constitutional Memory Consultation Trigger Model V1

Status: trigger model for Constitutional Memory Consultation activation.

## Human

Classification: `ALLOWED`

Evidence:

- Constitutional Memory access permits `HUMAN` and `OPERATOR` requesters.
- Human questions may request constitutional reference evidence.

## Intent Routing

Classification: `ALLOWED`

Evidence:

- Intent routing attachment emits replay-visible destination evidence.
- `CONSTITUTIONAL_MEMORY_CONSULTATION` is a supported destination.
- Routing attachment does not invoke memory directly.

## Provider

Classification: `FORBIDDEN`

Evidence:

- Memory access boundary forbids provider requesters.
- Providers remain proposal sources only.

## Worker

Classification: `FORBIDDEN`

Evidence:

- Memory access boundary forbids worker requesters.
- Workers execute only authorized requests and cannot retrieve memory directly.

## Runtime

Classification: `CONDITIONAL`

Allowed only when runtime activation has explicit governance context, replay-visible routing evidence, and no hidden continuation.

## Trigger Rule

Activation must be caused by human/operator/governance-scoped routing evidence, not provider or worker pressure.

