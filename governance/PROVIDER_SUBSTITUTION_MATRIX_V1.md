# PROVIDER_SUBSTITUTION_MATRIX_V1

## Status

Provider substitution matrix for `PROVIDER_SUBSTITUTION_PROOF_V1`.

## Matrix

| Provider | Adapter Contract | Proposal Envelope | Replay Visibility | Failure Model | Authority Restrictions | Governance Boundary | Runtime Interface | Substitution Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| OpenAI | SAME | SAME | SAME | SAME | SAME | SAME | SAME | CERTIFIED |
| Claude | SAME_REQUIRED | SAME_REQUIRED | SAME_REQUIRED | SAME_REQUIRED | SAME_REQUIRED | SAME_REQUIRED | SAME_REQUIRED | CERTIFIED_AT_BOUNDARY |
| Codex | SAME_REQUIRED | SAME_REQUIRED | SAME_REQUIRED | SAME_REQUIRED | SAME_REQUIRED | SAME_REQUIRED | SAME_REQUIRED | CERTIFIED_AT_BOUNDARY |
| Gemini | SAME_REQUIRED | SAME_REQUIRED | SAME_REQUIRED | SAME_REQUIRED | SAME_REQUIRED | SAME_REQUIRED | SAME_REQUIRED | CERTIFIED_AT_BOUNDARY |
| Local LLM | SAME_REQUIRED | SAME_REQUIRED | SAME_REQUIRED | SAME_REQUIRED | SAME_REQUIRED | SAME_REQUIRED | SAME_REQUIRED | CERTIFIED_AT_BOUNDARY |
| Future Provider | SAME_REQUIRED | SAME_REQUIRED | SAME_REQUIRED | SAME_REQUIRED | SAME_REQUIRED | SAME_REQUIRED | SAME_REQUIRED | CERTIFIED_AT_BOUNDARY |

## Replacement Paths

| Replacement | Result |
| --- | --- |
| OpenAI -> Claude | Allowed at adapter boundary. No governance, replay, authority, or execution model change required. |
| Claude -> Codex | Allowed at adapter boundary. No governance, replay, authority, or execution model change required. |
| Codex -> Gemini | Allowed at adapter boundary. No governance, replay, authority, or execution model change required. |
| Gemini -> Local LLM | Allowed at adapter boundary. No governance, replay, authority, or execution model change required. |
| Any reviewed provider -> Future Provider | Allowed if the future provider implements the same adapter contract and proposal envelope. |

## Required Invariant For Every Provider

Each provider must remain:

- proposal-only
- replay-visible
- fail-closed
- non-authoritative
- adapter-contract compatible

Each provider must not:

- execute
- authorize
- govern
- dispatch
- invoke workers
- mutate replay
- mutate memory
- change governance
- change execution model
