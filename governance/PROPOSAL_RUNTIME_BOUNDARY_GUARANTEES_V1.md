# Proposal Runtime Boundary Guarantees V1

Status: boundary guarantees.

## Certified Guarantees

The proposal runtime foundation preserves constitutional authority boundaries.

## Proposal Runtime Boundary

The proposal runtime artifact is a candidate record only.

It cannot:

- execute;
- authorize;
- dispatch;
- approve itself;
- mutate governance;
- mutate replay;
- invoke workers;
- invoke providers.

## Creation Boundary

AiGOL is the only actor that may create `PROPOSAL_RUNTIME_ARTIFACT_V1`.

Human prompts, provider outputs, resolution strategies, and replay evidence may contribute source evidence, but they do not create proposal authority.

## Provider Boundary

Provider output may be referenced as:

```text
source_provider_event_id
proposal_source = PROVIDER_EVIDENCE
```

Provider output may not:

- create proposal state;
- approve proposal state;
- inspect proposal state;
- execute proposal state;
- derive execution requests;
- dispatch workers;
- mutate replay.

## Conversational Runtime Boundary

Conversational Runtime may identify action candidates.

It may not:

- approve proposals;
- execute proposals;
- create worker tasks;
- bypass proposal lifecycle;
- bypass replay.

## Resolution Strategy Boundary

Resolution Strategy may determine:

```text
proposal_lifecycle_required = true
```

It may not:

- create approved proposal state;
- create execution requests;
- dispatch workers;
- treat provider output as authority.

## Worker Boundary

Worker execution is not implemented or authorized by this foundation.

Future workers may execute only after:

- proposal creation;
- proposal inspection;
- required human approval;
- governed execution request creation;
- authorization evidence;
- replay lineage continuity.

## Replay Boundary

Replay records proposal creation and state transition evidence.

Replay may not:

- create proposals;
- approve proposals;
- execute proposals;
- repair missing lineage;
- infer missing approval;
- mutate lifecycle truth.

## Fail-Closed Boundary

Proposal runtime must fail closed on:

- missing source prompt lineage;
- missing replay reference;
- unsupported proposal type;
- unsupported proposal source;
- non-AiGOL creator;
- invalid status;
- illegal transition;
- provider authority language;
- execution authority language;
- artifact hash mismatch.

## Constitutional Invariant

The proposal runtime foundation preserves:

```text
LLM proposes
AiGOL governs
Worker executes
Replay records
```

Runtime mapping:

```text
LLM proposes = provider output may contribute evidence only
AiGOL governs = AiGOL creates and validates proposal artifacts
Worker executes = absent until future authorized execution request
Replay records = replay records proposal creation and transitions
```

## Boundary Result

```text
PROPOSAL_RUNTIME_BOUNDARY_STATUS = PRESERVED
```
