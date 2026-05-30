# Intent Classifier Memory Relationship V1

Status: relationship between Intent Classifier and Constitutional Memory.

## Can Classifier Consult Constitutional Memory?

Classification: `PARTIALLY_SUPPORTED`

## Constraints

The classifier may use Constitutional Memory context only when:

- retrieval was explicitly requested or governance-scoped
- retrieval used the Constitutional Memory access path
- citations are present
- replay evidence is present
- memory remains `REFERENCE_ONLY`
- memory context is input evidence, not authority

## Forbidden Memory Use

The classifier must not:

- perform hidden memory retrieval
- use uncited memory
- treat memory as governance decision
- treat memory as authorization
- mutate memory
- use memory to execute or invoke providers/workers

## Provider Relationship

Can classifier invoke a provider?

Classification: `FORBIDDEN`

The classifier may classify into `PROVIDER_PROPOSAL`, but provider invocation belongs to the provider attachment path.

## Worker Relationship

Can classifier invoke a worker?

Classification: `FORBIDDEN`

The classifier may classify into `EXECUTION_REQUEST`, but worker invocation requires validation and authorization.

