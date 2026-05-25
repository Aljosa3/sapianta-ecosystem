# MOC_V1_GOVERNED_PROPOSAL_CORRECTION_LOOP_FOUNDATION

Status: bounded proposal-correction workflow foundation.

## Purpose

`MOC_V1_GOVERNED_PROPOSAL_CORRECTION_LOOP_FOUNDATION` creates deterministic correction feedback for invalid MOC V1 advisory proposals.

AiGOL governs convergence.

LLM performs advisory correction externally.

Proposal does not equal execution.

## Flow

```text
Human intent
-> LLM proposal
-> AiGOL proposal validation
-> if rejected: AiGOL emits correction feedback artifact
-> LLM prepares revised proposal
-> AiGOL validates again
-> if valid: proposal becomes eligible for approval gate
-> NOT execution
```

No hidden branches are allowed.

## Correction Feedback

The feedback artifact includes:

- correction status
- bounded attempt information
- linked proposal id
- linked validation result hash
- rejection reason
- explicit validation violations
- required corrections
- forbidden next steps
- LLM-safe instruction payload
- replay references
- lineage references
- governance guarantees
- deterministic correction feedback hash

## Status Classes

Correction feedback may return:

- `CORRECTION_REQUIRED`
- `CORRECTION_LIMIT_REACHED`
- `PROPOSAL_VALID`
- `FAIL_CLOSED`

The maximum attempt count is enforced deterministically.

## AiGOL Boundary

AiGOL does not repair proposals.

AiGOL does not call the LLM.

AiGOL emits rejection evidence only.

AiGOL does not generate corrected proposals.

## LLM Boundary

The LLM may prepare a corrected advisory proposal externally using the correction feedback. The correction feedback is safe to send to an LLM because it contains only:

- rejection summary
- explicit violations
- required corrections
- forbidden actions
- reminders that output must remain `advisory_only=true` and `replay_safe=true`
- reminder that proposal does not equal execution

## Human Approval Boundary

Human approval remains required before any worker execution may be considered. A valid advisory proposal is only eligible for an approval gate. It is not execution, dispatch, provider activation, or authority issuance.

## Governance Guarantees

This milestone does not:

- execute proposals
- dispatch workers
- activate providers
- self-authorize
- bypass human approval
- mutate governance
- create autonomous execution
- create hidden continuation
- run indefinitely
- infer hidden meaning
- repair proposals inside AiGOL
- call an LLM

The correction loop is bounded, replay-visible, deterministic, and advisory only.
