# Attachment Implementation Sequence V1

Status: planning-only attachment sequence.

## Minimal Safe Sequence

### 1. REAL_LLM_ATTACHMENT_V1

Implement one provider-agnostic supplied-response attachment.

Required behavior:

- accept explicit provider identity envelope
- capture raw response evidence
- verify deterministic response hash
- normalize into existing proposal artifact
- reject malformed or authority-escalating output
- emit replay-visible lineage
- never authorize or execute

### 2. LLM Attachment Pressure Validation

Validate the attachment before worker attachment.

Required pressure cases:

- malformed provider identity
- raw response hash mismatch
- malformed proposal
- ambiguous proposal
- unsupported capability
- execution-authority claim
- hidden continuation language
- replay ordering mismatch

### 3. REAL_WORKER_ATTACHMENT_V1

Implement one runtime-inspection-only worker attachment.

Required behavior:

- accept only AiGOL-authorized execution requests
- record worker identity envelope
- bind only `READ_ONLY_RUNTIME_INSPECTION`
- emit worker result evidence
- emit worker termination evidence
- fail closed on missing authorization, identity mismatch, replay corruption, or capability mismatch

## Deferred Until After Sequence

Do not include in first sequence:

- live OpenAI API calls
- ChatGPT browser/session bridge
- Claude API calls
- Codex worker execution
- filesystem read-only worker
- CLI worker
- API query worker
- orchestration
- retries
- streaming
- memory

## Sequence Rationale

The LLM attachment is non-executing and can prove proposal-only behavior first.

The worker attachment touches execution and should only follow once external proposal input is proven to remain governed, replay-visible, and non-authoritative.
