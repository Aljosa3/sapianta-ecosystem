# END_TO_END_EXECUTION_CHAIN_RECOMMENDATIONS_V1

## Purpose

Recommend the safest next steps for extending the execution governance chain after worker assignment.

## Recommendation 1: Implement Dispatch Runtime Next

Implement `DISPATCH_RUNTIME_V1` before invocation.

Scope should be limited to:

```text
WORKER_ASSIGNMENT_ARTIFACT_V1
  -> DISPATCH_ARTIFACT_V1
```

Do not implement invocation, execution, completion, or result persistence inside Dispatch Runtime.

Required guarantees:

- assignment status must be `ASSIGNED`;
- assignment replay must reconstruct;
- worker identity must match assignment;
- readiness lineage must match assignment;
- duplicate dispatch must fail closed;
- provider authority must remain false;
- worker self-dispatch must remain false;
- execution must remain false.

## Recommendation 2: Preserve Append-Only State Evidence

Future runtimes should continue recording new artifacts instead of mutating upstream artifacts.

The current chain is easiest to audit because each boundary records an append-only artifact with references and hashes.

## Recommendation 3: Define Canonical Chain Linkage Before Full Execution Certification

Before claiming full human prompt to worker execution certification, define a canonical chain linkage artifact or reconstruction report that binds:

- human prompt reference;
- source router selection;
- proposal artifact;
- approval artifact;
- execution request artifact;
- readiness artifact;
- worker artifact;
- worker assignment artifact;
- future dispatch artifact;
- future invocation artifact;
- future execution/result artifacts.

This can be read-only and replay-derived.

## Recommendation 4: Keep Dispatch, Invocation, Execution, And Completion Separate

Do not collapse these into one runtime.

The governance value of the current architecture comes from separate fail-closed boundaries:

```text
ASSIGNED
  -> DISPATCHED
  -> INVOKED
  -> EXECUTING
  -> COMPLETED or FAILED
```

Each boundary should have its own artifact, replay events, reconstruction logic, and tests.

## Recommendation 5: Treat Cancellation And Expiry As Explicit Runtime Work

Do not rely on foundation terminology alone.

If cancellation or expiry is needed downstream, define and test the corresponding runtime transitions with replay evidence.

## Recommendation 6: Add Capability Compatibility Evidence Before Broad Worker Use

Worker Runtime currently carries capability data locally.

Before supporting multiple worker types or dispatch decisions, add stronger replay-visible compatibility evidence so dispatch and invocation do not depend on informal capability matching.

## Recommendation 7: Continue Authority-Leak Tests At Every Layer

Every new runtime should include tests asserting absence of:

- provider authority;
- worker self-authority;
- automatic authorization;
- dispatch inside assignment;
- invocation inside dispatch;
- execution inside invocation;
- completion inside execution start unless explicitly defined.

## Recommendation 8: Add End-To-End Replay Validation After Invocation Runtime

The best time to add a unified chain reconstruction command is after dispatch and invocation runtime are certified.

At that point the chain will have enough boundaries to justify a read-only audit report from human prompt through worker invocation.

## Recommended Next Runtime Order

```text
1. DISPATCH_RUNTIME_V1
2. WORKER_INVOCATION_RUNTIME_V1
3. WORKER_EXECUTION_START_RUNTIME_FOUNDATION_V1
4. WORKER_RESULT_RUNTIME_FOUNDATION_V1
5. EXECUTION_COMPLETION_RUNTIME_FOUNDATION_V1
6. END_TO_END_EXECUTION_CHAIN_REPLAY_V1
```

## Recommendation Classification

Proceed to Dispatch Runtime with gaps known and bounded.

```text
END_TO_END_EXECUTION_CHAIN_STATUS = READY_WITH_GAPS
```
