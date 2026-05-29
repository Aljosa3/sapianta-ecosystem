# Operational Epoch Guarantees V1

Status: frozen operational epoch guarantee set.

## Guarantee 1: LLM Proposal-Only

LLM / cognition output remains proposal-only.

It cannot:

- execute directly
- authorize execution
- self-route to a worker
- create hidden continuation
- mutate governance authority

## Guarantee 2: AiGOL Governance Authority

AiGOL remains the governance authority for:

- proposal normalization
- validation
- authorization
- rejection
- replay recording
- governed return creation

No worker or LLM may bypass AiGOL governance.

## Guarantee 3: Worker Execution-Only

Worker / deterministic runtime execution remains execution-only.

Workers execute only bounded authorized tasks. Workers cannot self-authorize, infer missing authorization, expand capability scope, or continue after fail-closed rejection.

## Guarantee 4: Replay Mandatory

Replay remains mandatory for:

- operator prompt evidence
- proposal evidence
- validation evidence
- authorization evidence
- worker execution evidence
- governed result evidence
- failure evidence

Replay artifacts remain append-only and hash-verifiable.

## Guarantee 5: Authorization Mandatory

Execution cannot occur before validation and authorization. Unauthorized, malformed, unsupported, ambiguous, or boundary-violating flows must fail closed.

## Guarantee 6: Read-Only Boundaries Intact

The frozen epoch permits only existing read-only capabilities:

- `READ_ONLY_RUNTIME_INSPECTION`
- `FILESYSTEM_READ_ONLY_INSPECTION`

Filesystem read-only inspection remains allowlisted and non-mutating.

## Guarantee 7: No Hidden Authority Escalation

The frozen epoch grants no hidden authority to:

- LLM
- worker
- bridge
- capability
- replay artifact
- governed result

Any authority ambiguity must fail closed.
