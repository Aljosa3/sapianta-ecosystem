# Intent Routing Destinations V1

Status: destination analysis for the canonical intent routing model.

## Destination A: Conversation

Purpose:

- respond conversationally without provider proposal, memory consultation, or execution
- preserve operator-facing interaction where no action or external proposal is required

Authority:

- no execution authority
- no authorization authority
- no governance authority
- no replay mutation authority

Boundaries:

- must not silently become provider proposal
- must not silently become memory consultation
- must not silently become execution request
- requires a future conversation-only lifecycle before implementation

Replay requirements:

- routing into conversation must be replay-visible
- conversational output should be traceable to the prompt and route artifact

Classification: `PARTIAL`

Reason: operator-facing presentation exists, but a conversation-only constitutional destination is not fully defined.

## Destination B: Constitutional Memory Consultation

Purpose:

- retrieve citation-bound reference evidence from Constitutional Memory

Authority:

- `REFERENCE_ONLY`
- no authorization, governance, execution, provider, worker, or proposal authority

Citation requirements:

- artifact identity
- artifact classification
- artifact path
- retrieval timestamp
- citation reference

Replay requirements:

- retrieval request, citation bundle, and result must be replay-visible

Classification: `VALID`

Reason: memory consultation is explicitly modeled and minimally implemented as reference-only access.

## Destination C: Provider Proposal

Purpose:

- obtain untrusted proposal output from a provider
- normalize provider output into proposal evidence

Provider role:

- proposal source only
- non-authoritative
- non-executing

Proposal role:

- untrusted proposal input for AiGOL governance
- never execution, authorization, or governance

Replay requirements:

- provider identity
- raw provider response
- provider attachment record
- normalized proposal
- governed result

Classification: `VALID`

Reason: provider attachment and proposal normalization are already defined.

## Destination D: Execution Request

Purpose:

- represent a bounded request for execution through governed authorization and worker execution

Authorization requirements:

- validation before authorization
- explicit authorization before execution
- fail-closed ambiguity and boundary violation handling

Worker boundaries:

- worker executes only authorized request
- worker cannot self-authorize
- worker cannot mutate governance or replay

Replay requirements:

- execution request
- validation evidence
- authorization evidence
- worker evidence
- governed result

Classification: `VALID`

Reason: execution request semantics, authorization, and read-only worker boundaries already exist.

