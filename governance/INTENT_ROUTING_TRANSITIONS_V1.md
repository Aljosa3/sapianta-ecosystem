# Intent Routing Transitions V1

Status: transition analysis for Human Prompt routing.

## Transition Rule

Routing transitions select a destination.

They do not perform the destination action.

## Human Prompt To Conversation

Transition:

```text
Human Prompt
-> CONVERSATION
```

Classification: `CONDITIONAL`

Conditions:

- prompt can be answered without provider proposal
- prompt does not request execution
- prompt does not require Constitutional Memory citation
- future conversation destination boundary exists
- route is replay-visible

Reason: conversation is partial, not invalid.

## Human Prompt To Constitutional Memory Consultation

Transition:

```text
Human Prompt
-> CONSTITUTIONAL_MEMORY_CONSULTATION
```

Classification: `ALLOWED`

Conditions:

- prompt requests constitutional reference, evidence, governance position, or cited memory
- routing artifact identifies retrieval scope without executing retrieval itself
- memory access path performs citation-bound retrieval
- route is replay-visible

Reason: Constitutional Memory access is reference-only and defined.

## Human Prompt To Provider Proposal

Transition:

```text
Human Prompt
-> PROVIDER_PROPOSAL
```

Classification: `ALLOWED`

Conditions:

- prompt requires external LLM proposal source
- provider remains proposal-only
- provider attachment captures raw response before normalization
- route is replay-visible

Reason: provider proposal path exists and preserves authority separation.

## Human Prompt To Execution Request

Transition:

```text
Human Prompt
-> EXECUTION_REQUEST
```

Classification: `CONDITIONAL`

Conditions:

- prompt is interpreted as a bounded execution request
- execution request remains untrusted until normalized and validated
- authorization remains mandatory
- worker execution occurs only after authorization
- route is replay-visible

Reason: execution destination exists, but routing must not bypass validation or authorization.

## Forbidden Transitions

The following transitions are forbidden:

- Human Prompt directly to Worker
- Human Prompt directly to provider command
- Human Prompt directly to execution without authorization
- Provider directly to Worker
- Provider directly to Constitutional Memory access
- Worker directly to Constitutional Memory access
- Routing artifact directly to governance decision
- Routing artifact directly to authorization

## Invalid Transition Handling

Invalid transitions must fail closed and create replay-visible rejection evidence.

