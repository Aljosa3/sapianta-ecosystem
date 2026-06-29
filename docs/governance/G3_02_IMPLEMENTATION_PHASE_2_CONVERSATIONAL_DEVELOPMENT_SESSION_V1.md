# G3-02 Implementation Phase 2 Conversational Development Session V1

Status: implementation certification artifact.

Scope: conversational development turns inside governed ACLI development sessions.

This phase does not implement provider execution, worker execution, Product 1 runtime,
deployment, repository mutation, approval creation, or authorization creation.

## 1. Objective

Implement conversational development sessions that preserve the existing governance model
while allowing iterative natural-language interaction inside the governed ACLI session
lifecycle established by G3-02 Phase 1.

## 2. Runtime Implementation

Implemented runtime:

- `aigol/runtime/acli_conversational_development_session.py`

Implemented public functions:

- `start_conversational_development_session(...)`;
- `record_conversational_development_turn(...)`;
- `reconstruct_acli_conversational_development_session_replay(...)`.

The runtime consumes a Phase 1 ACLI session lifecycle artifact and creates a deterministic
conversation artifact with append-only turn lineage.

## 3. Conversational Session Features Implemented

Implemented features:

- conversational session context;
- association with a governed ACLI session artifact;
- conversation history;
- parent-turn linkage;
- CSA continuity across turns;
- clarification status recording;
- proposal lifecycle status recording;
- confirmation status recording;
- continuation status recording;
- replay-visible turn lineage;
- tamper-detecting replay reconstruction.

Every turn records:

- `turn_id`;
- `session_id`;
- `conversation_id`;
- `parent_turn_id`;
- `turn_index`;
- prompt hash;
- CSA reference and hash;
- previous turn hash;
- previous CSA hash;
- replay lineage;
- clarification status;
- proposal status;
- confirmation status;
- continuation status.

## 4. Replay Evidence

Replay evidence is written as immutable wrappers:

- `000_acli_conversational_development_session_started.json`;
- `NNN_acli_conversational_development_turn_recorded.json`.

Replay reconstruction validates:

- wrapper hash;
- artifact hash;
- event ordering;
- event hash chain;
- turn ordering;
- parent-turn references;
- previous-turn hash continuity;
- CSA continuity;
- non-authority flags.

## 5. Non-Authority Guarantees

The runtime records conversational state only.

It explicitly denies:

- provider invocation;
- worker invocation;
- approval creation;
- authorization creation;
- execution request;
- repository mutation;
- deployment request;
- Product 1 workflow start.

Proposal and confirmation statuses are lifecycle evidence only. They do not create
approval, authorization, execution, or mutation.

## 6. Clarification, Proposal, Confirmation, And Continuation Statuses

Clarification statuses:

- `CLARIFICATION_NOT_REQUIRED`;
- `CLARIFICATION_REQUESTED`;
- `CLARIFICATION_OPEN`;
- `CLARIFICATION_RESOLVED`;
- `FAILED_CLOSED`.

Proposal statuses:

- `PROPOSAL_NOT_CREATED`;
- `PROPOSAL_CANDIDATE_RECORDED`;
- `PROPOSAL_CONFIRMATION_REQUIRED`;
- `FAILED_CLOSED`.

Confirmation statuses:

- `CONFIRMATION_NOT_REQUIRED`;
- `CONFIRMATION_REQUIRED`;
- `CONFIRMATION_RECORDED`;
- `FAILED_CLOSED`.

Continuation statuses:

- `NEW_CONVERSATION`;
- `CONTINUATION_FROM_PARENT_TURN`;
- `CONTINUATION_BLOCKED_NO_PARENT`;
- `FAILED_CLOSED`.

Continuation from a parent turn fails closed when the parent turn is absent.

## 7. Deferred Workstreams

Deferred to later Generation 3 work:

- provider activation;
- worker execution;
- Product 1 runtime workflows;
- deployment readiness;
- repository mutation;
- approval and authorization bridges;
- release candidate creation.

Later workstreams must consume the session and turn evidence produced here rather than
bypassing it.

## 8. Regression Coverage

Added regression tests:

- conversation start from Phase 1 session lifecycle artifact;
- first turn recording with CSA and replay lineage;
- parented continuation turn recording;
- CSA continuity across turns;
- clarification, proposal, confirmation, and continuation status visibility;
- fail-closed missing parent turn for continuation;
- replay tamper detection;
- non-authority surface assertions.

Targeted test file:

- `tests/test_acli_conversational_development_session_v1.py`

## 9. Rollback Impact

Rollback impact is low.

The runtime is additive and non-authoritative:

- no existing ACLI routing behavior changes;
- no provider or worker path is activated;
- no Product 1 flow starts;
- no deployment path is added;
- no repository mutation, approval, or authorization path is introduced.

Removing this runtime and its tests restores the repository to Phase 1 behavior without
changing existing execution semantics.

## 10. Certification Impact

This phase certifies that governed ACLI sessions can now contain deterministic
conversation history and replay-visible turn lineage.

G3-02 remains incomplete after this phase. Remaining phases must add operator-visible
rendering, proposal/approval/authorization bridges, validation evidence, release handoff,
and recovery UI.

## 11. Validation Scope

Required validation:

```text
git diff --check
python -m py_compile ...
targeted conversational session tests
python -m pytest -q
```

Generated `.runtime` artifacts from validation must be cleaned before completion.

## 12. Final Verdict

```text
G3_02_IMPLEMENTATION_PHASE_2_READY
```
