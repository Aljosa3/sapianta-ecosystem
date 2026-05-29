# Proposal Normalization Model V1

Status: model-only proposal normalization definition.

## Purpose

Proposal normalization converts raw LLM output into a bounded `PROPOSAL_ARTIFACT`.

Normalization does not grant authority. It only prepares untrusted proposal input for AiGOL governance.

## Normalization Target

The normalized proposal artifact must be compatible with the existing proposal bridge and must represent:

- proposal id
- provider identity reference
- raw response evidence hash
- human prompt reference
- target capability
- bounded intent
- arguments
- created timestamp
- non-authority flags

## Required Non-Authority Flags

Each normalized proposal must preserve:

- `llm_proposes_only`: true
- `llm_execution_authority`: false
- `llm_authorization_authority`: false
- `llm_governance_authority`: false
- `worker_self_authorization`: false
- `replay_bypass_requested`: false

## Normalization Rules

Normalization must be:

- deterministic
- replay-linked to raw response evidence
- fail-closed on malformed structure
- fail-closed on ambiguity
- fail-closed on unsupported capability
- fail-closed on authority escalation
- free of semantic rewriting beyond bounded structure normalization

## Accepted Output Boundary

The only artifact that may cross from the LLM attachment boundary into AiGOL governance is the normalized `PROPOSAL_ARTIFACT`.

Raw provider text remains evidence at the adapter boundary.

## Failure Handling

When normalization fails:

- no proposal artifact is emitted
- raw response evidence remains replay-visible
- failure reason is deterministic
- AiGOL does not infer intent
- AiGOL does not retry autonomously
- AiGOL does not continue execution
