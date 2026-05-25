# MOC_V1_SEQUENCE_FLOW

Status: canonical sequence flow.

## Required Linear Flow

MOC V1 uses a single explicit sequence:

```text
Human Intent
-> Intent Normalization
-> Governance Retrieval
-> Semantic Contract
-> Advisory Proposal
-> Human Approval
-> Worker Task
-> Governed Return
-> Return Interpretation
```

No hidden branches are allowed.

## Stage Semantics

### Human Intent

The human provides explicit intent. MOC V1 must not infer hidden intent.

### Intent Normalization

The intent is normalized into bounded, replay-visible semantic form. Normalization does not certify truth or authority.

### Governance Retrieval

Governance anchors are retrieved from explicit governance artifacts. Missing anchors remain explicit gaps.

### Semantic Contract

The semantic contract records intent, scope, risk, mutation classification, governance anchors, allowed actions, forbidden actions, required approvals, expected outputs, and deterministic constraints.

### Advisory Proposal

The proposal is advisory only. It cannot execute, dispatch, mutate, or activate providers.

### Human Approval

Human approval is required before any worker task may be considered. Approval does not equal execution.

### Worker Task

The worker task is a bounded proposal or governed task boundary. MOC V1 does not self-dispatch the worker.

### Governed Return

The governed return is replay-visible evidence from a governed process.

### Return Interpretation

Return interpretation summarizes evidence. It does not repair semantics, certify truth, or create authority.

## Forbidden Branches

The sequence forbids:

- hidden continuation
- recursive orchestration
- self-dispatch
- provider activation
- silent governance mutation
- hidden context ingestion
- semantic repair
