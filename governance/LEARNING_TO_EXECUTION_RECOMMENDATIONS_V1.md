# LEARNING_TO_EXECUTION_RECOMMENDATIONS_V1

## Purpose

Record recommendations for future learning-to-execution work.

## Recommendation 1: Implement The Bridge As A Separate Runtime

Future work should implement:

```text
IMPROVEMENT_IMPLEMENTATION_PLAN_ARTIFACT_V1
-> EXECUTION_REQUEST_ARTIFACT_V1
```

as a distinct runtime, not as a mutation of the implementation plan runtime.

## Recommendation 2: Add Explicit Human Execution Authorization

The bridge should require a human authorization artifact or certified authorization field that explicitly permits execution request creation from an implementation plan.

Do not infer that authorization from plan text, review recommendations, provider output, worker output, or replay reconstruction.

## Recommendation 3: Preserve No-Automatic-Loop Semantics

Future bridge runtime should prevent accidental learning-to-execution loops through:

- duplicate request rejection;
- chain ancestry checks;
- recurrence limits;
- explicit reauthorization for repeated execution;
- replay-visible loop detection evidence.

## Recommendation 4: Define Domain Capability Policy Before Deployment

Before domain deployment, define:

- allowed request types;
- allowed worker classes;
- forbidden mutation classes;
- request payload bounds;
- validation requirements;
- replay evidence requirements;
- emergency cancellation or expiry semantics.

## Recommendation 5: Keep Implementation Plans Non-Executing

Implementation plans should continue to describe future steps only.

They must not:

- create execution requests;
- mutate execution state;
- dispatch workers;
- invoke workers;
- execute commands;
- mutate code;
- mutate governance;
- mutate replay;
- self-apply improvements.

## Recommendation 6: Build A Unified Replay Proof

Future certification should include a single replay reconstruction report spanning:

```text
Execution
-> Result
-> Evaluation
-> Proposal
-> Review
-> Approval
-> Implementation Plan
-> Execution Request
```

This will make domain deployment review more inspectable.

## Final Recommendation

Proceed with bounded bridge runtime design only after preserving explicit human authorization, no automatic execution loops, replay reconstruction, and domain capability policy.
