# G3-02 Implementation Phase 4 Proposal Approval Bridge V1

Status: implementation certification artifact.

Scope: proposal object creation and approval-request evidence for conversational ACLI
development sessions.

This phase does not implement authorization, worker execution, provider execution,
repository mutation, Product 1 runtime, deployment, or execution activation.

## 1. Objective

Implement the governed bridge between conversational ACLI confirmations and the existing
proposal / approval workflow.

The bridge creates deterministic, replay-visible proposal artifacts and approval-request
evidence while preserving the Generation 2 authority model. Proposals remain
non-authoritative until a later approved workflow explicitly consumes them.

## 2. Runtime Implementation

Implemented runtime:

- `aigol/runtime/acli_proposal_approval_bridge.py`

Implemented public functions:

- `create_conversational_development_proposal(...)`;
- `revise_conversational_development_proposal(...)`;
- `generate_conversational_approval_request(...)`;
- `record_conversational_approval_decision(...)`;
- `reconstruct_acli_proposal_approval_bridge_replay(...)`.

The runtime consumes Phase 2 conversational ACLI artifacts and reuses the existing
immutable approval request contract from `aigol.runtime.approval.approval_request`.

## 3. Proposal Lifecycle Implemented

Implemented proposal states:

| State | Meaning |
| --- | --- |
| `PROPOSAL_DRAFTED` | Proposal object created from a conversational turn |
| `PROPOSAL_REVISED` | A new proposal version was recorded |
| `APPROVAL_REQUESTED` | Approval-request evidence was generated |
| `APPROVAL_RECORDED` | Approval state was recorded as evidence only |
| `PROPOSAL_REJECTED` | Rejection handling path was recorded |
| `CLARIFICATION_RETURNED` | Clarification return path was recorded |
| `FAILED_CLOSED` | Reserved terminal failure state |

Every proposal records:

- proposal id;
- originating session id;
- originating conversation id;
- originating turn id and turn hash;
- CSA reference/hash;
- proposal version;
- proposal status;
- approval status;
- rollback reference;
- replay lineage;
- immutable artifact hash.

## 4. Proposal Versioning

Proposal revisions are append-only.

Every version records:

- version number;
- deterministic summary hash;
- rollback reference;
- previous version hash;
- version hash;
- non-authority flags.

Replay reconstruction validates version ordering and hash lineage.

## 5. Approval Bridge Implemented

The bridge generates approval-request evidence using the existing immutable
`ApprovalRequest` shape.

Approval-request evidence records:

- approval request id;
- proposal id;
- proposal version;
- proposal hash;
- CSA reference/hash;
- approval-required flag;
- request hash.

The bridge records approval state transitions, but does not grant approval authority,
authorization authority, execution authority, worker authority, provider authority, or
repository mutation authority.

## 6. Rejection And Clarification Handling

Rejection handling records:

- rejection status;
- rejection reference;
- approval decision hash;
- replay-visible proposal lineage.

Clarification return handling records:

- clarification status;
- clarification return reference;
- approval decision hash;
- replay-visible proposal lineage.

Both paths preserve rollback references and leave execution disabled.

## 7. Replay Evidence

Replay evidence is written as immutable wrappers:

- `NNN_acli_proposal_created.json`;
- `NNN_acli_proposal_revised.json`;
- `NNN_acli_approval_request_generated.json`;
- `NNN_acli_approval_decision_recorded.json`.

Replay reconstruction validates:

- wrapper hashes;
- artifact hashes;
- event ordering;
- event lineage;
- proposal version lineage;
- non-authority flags.

## 8. Non-Authority Guarantees

The runtime explicitly denies:

- provider invocation;
- worker invocation;
- approval creation;
- authorization creation;
- execution request;
- repository mutation;
- deployment request;
- Product 1 workflow start.

Approval requests are evidence only. Approval creation, authorization, execution, and
repository mutation remain deferred to later governed workstreams.

## 9. Regression Coverage

Added regression tests:

- proposal creation from a conversational turn with required fields;
- proposal versioning and lineage preservation;
- approval-request generation without approval or authorization;
- rejection handling;
- clarification return path;
- decision-before-request fail-closed behavior;
- replay tamper detection;
- non-authority surface assertions.

Targeted test file:

- `tests/test_acli_proposal_approval_bridge_v1.py`

## 10. Rollback Impact

Rollback impact is low.

The runtime is additive and non-authoritative:

- no existing ACLI routing behavior changes;
- no existing approval engine behavior changes;
- no provider or worker path is activated;
- no Product 1 runtime starts;
- no deployment path is added;
- no repository mutation, authorization, or execution path is introduced.

Removing this runtime and its tests restores Phase 3 behavior without changing existing
execution semantics.

## 11. Certification Impact

This phase certifies that conversational ACLI sessions can now produce deterministic
proposal and approval-request evidence.

G3-02 remains incomplete after this phase. Remaining phases must add authorization
handoff, governed validation, release handoff, and operational recovery flows before ACLI
can function as the full primary development interface.

## 12. Validation Scope

Required validation:

```text
git diff --check
python -m py_compile ...
targeted proposal/approval bridge tests
python -m pytest -q
```

Generated `.runtime` artifacts from validation must be cleaned before completion.

## 13. Final Verdict

```text
G3_02_IMPLEMENTATION_PHASE_4_READY
```
