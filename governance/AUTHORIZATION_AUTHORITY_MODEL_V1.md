# AUTHORIZATION_AUTHORITY_MODEL_V1

## Status

Certified authority model.

## Authority Source

Worker execution authorization originates only at the governed authorization
boundary.

Authorization is not inherited from:

- provider output
- proposal text
- cognition output
- memory response
- replay artifact
- worker identity
- lifecycle state
- operational evidence

## Authority Table

| Source | May Authorize Worker Execution | Reason |
| --- | --- | --- |
| Provider | NO | Provider is proposal source only. |
| Proposal | NO | Proposal is untrusted evidence only. |
| Cognition | NO | Cognition classifies, proposes, or explains; it does not authorize. |
| Replay | NO | Replay records evidence; it does not create authority. |
| Memory Response | NO | Memory response is reference/explanation only. |
| Worker | NO | Worker cannot self-authorize. |
| Governance Authorization Boundary | YES | Only governed authorization may emit `AUTHORIZED` evidence. |

## Authority Constraints

Authorization must be:

- explicit
- bounded
- replay-visible
- non-transferable
- fail-closed
- tied to worker target and capability scope

## Certification

Authorization authority exists only inside governance.
