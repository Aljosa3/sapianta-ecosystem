# AIGOL_IMPLEMENTATION_APPROVAL_RESUME_V1

## Status

CERTIFIED

## Purpose

Allow a high-risk conversation chain that stopped at `HUMAN_APPROVAL_REQUIRED` to resume after explicit human approval and produce `IMPLEMENTATION_HANDOFF_CREATED`.

Approval resume continues an existing approved chain only. It does not execute workers, dispatch workers, authorize unrelated work, or mutate governance.

## Problem

AiGOL could correctly stop high-risk prompts such as:

```text
Improve trading strategy.
```

at:

```text
HUMAN_APPROVAL_REQUIRED
```

but had no governed mechanism to resume the same canonical chain after the human approved it.

## Target Flow

```text
Human Prompt
-> Conversation
-> PPP
-> Proposal Validation
-> HUMAN_APPROVAL_REQUIRED
-> Human Approval
-> Approval Resume
-> IMPLEMENTATION_HANDOFF_CREATED
```

## Approval Model

The human approval artifact contains:

- chain id;
- approval id;
- approval scope;
- approval request reference;
- approval request hash;
- proposal reference;
- proposal hash;
- approval timestamp;
- approval expiration;
- approving actor;
- approval hash.

The approval scope is bound to the original high-risk chain. Example:

```text
TRADING:IMPROVE_EXISTING_CAPABILITY:TRADING_STRATEGY_IMPROVEMENT_CAPABILITY_V1
```

## Resume Verification

Approval resume verifies:

- approval request lineage;
- approval decision lineage;
- chain continuity;
- approval scope continuity;
- proposal lineage;
- replay continuity;
- approval validity;
- approval expiration;
- resumed handoff lineage.

## Replay Model

The approval-required stop now carries a replay-visible resume packet containing:

- context assembly artifact;
- registry resolution artifact;
- provider necessity policy artifact;
- proposal production artifact;
- proposal artifact;
- proposal validation artifact;
- approval request artifact;
- hashes for all resume inputs.

Approval resume persists:

- approval request;
- approval decision;
- approval resume artifact;
- resumed handoff artifact.

Replay reconstruction verifies wrapper ordering, wrapper hashes, artifact hashes, approval request lineage, approval decision lineage, chain continuity, and resumed handoff lineage.

## CLI Before And After

Before:

```text
Improve trading strategy.
-> HUMAN_APPROVAL_REQUIRED
```

After:

```text
Improve trading strategy.
-> HUMAN_APPROVAL_REQUIRED

Approve.
-> IMPLEMENTATION_APPROVAL_RESUMED
-> IMPLEMENTATION_HANDOFF_CREATED
```

## Authority Boundaries

Approval Resume may:

- continue an existing approved chain.

Approval Resume may not:

- create approvals autonomously;
- modify approvals;
- authorize unrelated work;
- execute workers;
- dispatch workers;
- mutate governance.

The CLI `Approve.` command records an explicit human approval artifact for the pending approval request, then passes that artifact into the resume runtime.

## Fail-Closed Conditions

Approval resume fails closed when:

- approval is missing;
- approval is expired;
- chain id mismatches;
- approval scope mismatches;
- proposal lineage mismatches;
- approval request lineage breaks;
- replay corruption is detected;
- handoff creation fails.

## Remaining Blockers Before Governed Implementation Execution

- Implementation execution remains separate and must require additional governed execution authority.
- Approval resume creates a handoff candidate, not executed artifacts.
- Expiration policy is deterministic but not yet connected to an enterprise approval dashboard.

## Final Classification

AIGOL_IMPLEMENTATION_APPROVAL_RESUME_STATUS = CERTIFIED
