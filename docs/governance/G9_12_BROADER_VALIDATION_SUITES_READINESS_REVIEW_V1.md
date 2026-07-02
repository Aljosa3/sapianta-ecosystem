# G9-12 Broader Validation Suites Readiness Review V1

Status: broader validation suites ready for minimal extension.

Final verdict: BROADER_VALIDATION_READY_FOR_MINIMAL_EXTENSION

## 1. Executive Summary

This review determines whether broader governed validation suites can be implemented by composing existing certified validation capabilities with minimal Platform Core extension.

Conclusion:

```text
BROADER_VALIDATION_READY_FOR_MINIMAL_EXTENSION
```

The certified Platform Core already contains the required foundations:

- one allowlisted governed validation command execution;
- validation command allowlist;
- validation candidate construction;
- hash-bound human approval;
- Governance authorization;
- Worker Platform command execution;
- Replay-visible validation evidence;
- validation result normalization;
- mutation runtimes that already produce validation evidence;
- rollback and multi-file mutation runtimes that expose validation integration points;
- Architectural Health advisory projection.

Broader validation suites should not become a new subsystem or authority layer. They should be implemented as a deterministic validation-suite envelope over existing certified single-command validation execution.

Minimal extension is required for:

- ordered validation-suite candidate construction;
- exact command-set authorization;
- per-command Worker authorization;
- suite-level Replay evidence;
- result aggregation;
- fail-closed suite behavior;
- mutation and transaction evidence binding;
- Architectural Health advisory review of validation coverage.

## 2. Review Basis

Reviewed certified capabilities:

| Capability | Current State | Reuse Finding |
| --- | --- | --- |
| Governed validation execution | Certified for one allowlisted non-shell command. | Reuse as per-command primitive. |
| Single-file mutation | Certified with validation evidence and rollback metadata. | Reuse validation prerequisites and post-mutation evidence. |
| Patch mutation | Certified with complete-artifact validation interaction. | Reuse artifact-bound validation model. |
| Multi-file mutation | Implemented and architecture-confirmed with pre/post transaction validation. | Reuse transaction evidence as suite input. |
| Rollback | Implemented and architecture-confirmed with pre/post rollback validation. | Reuse rollback validation evidence model. |
| Replay | Certified evidence and reconstruction boundary. | Extend to suite-level evidence and per-command references. |
| Governance | Certified authorization authority. | Extend to exact validation command-set authorization. |
| Worker Platform | Certified execution boundary. | Reuse validation command Worker per command. |
| Architectural Health | Certified advisory projection. | Reuse to detect validation coverage and authority drift. |

## 3. Existing Validation Capability

The existing governed validation capability supports:

- exactly one allowlisted validation command;
- non-shell execution;
- bounded timeout;
- bounded output capture;
- static command allowlist;
- hash-bound human approval;
- Governance authorization;
- Worker Platform execution;
- Replay evidence;
- validation result normalization.

Existing validation architecture is split across:

```text
aigol/runtime/governed_validation_runtime.py
aigol/runtime/platform_core_validation_allowlist.py
aigol/runtime/platform_core_validation_candidate.py
aigol/runtime/platform_core_validation_governance.py
aigol/runtime/platform_core_validation_replay.py
aigol/runtime/platform_core_validation_result.py
aigol/workers/validation_command_worker.py
```

The certified single-command runtime is therefore already the correct primitive for broader validation suites.

## 4. Readiness Determination

Broader validation suites are ready for minimal extension because the remaining gap is deterministic composition, not architectural preparation.

The current architecture already establishes:

- OCS-shaped candidate ownership for validation requests;
- Governance-owned approval and authorization;
- Worker Platform-owned command execution;
- Replay-owned evidence and reconstruction;
- Platform Core-owned workflow coordination;
- result evidence separated from certification authority;
- fail-closed behavior on missing approval, missing authorization, unsupported command, timeout, and replay issues.

The required suite capability is an ordered envelope around multiple already certified validation command executions.

## 5. Reuse Analysis

### 5.1 Validation Command Allowlist

The existing command allowlist should be reused unchanged for first broader-suite implementation.

Suite expansion should not introduce arbitrary shell execution or dynamic command construction. Each command must remain a known allowlisted command with:

- command id;
- argv;
- working directory;
- timeout;
- output limit;
- expected exit code.

Allowlist expansion remains governance-significant and should require separate certification.

### 5.2 Validation Candidate Construction

Existing single-command validation candidates can be composed into a suite candidate.

Required minimal extension:

- deterministic suite id;
- ordered command list;
- per-command candidate hash;
- mutation or transaction evidence reference;
- validation purpose for each command;
- expected result policy;
- stop-on-failure policy.

OCS remains the owner of candidate and plan formation.

### 5.3 Governance Authorization

Governance can reuse the existing authorization record pattern.

Required minimal extension:

- one hash-bound human approval for the exact validation-suite candidate;
- per-command Worker authorization records generated from the approved suite;
- exact command-set binding;
- exact ordering binding;
- no authorization for shell, Git, deployment, provider invocation, dependency installation, or mutation.

Governance remains authorization-only.

### 5.4 Worker Platform Execution

The existing validation command Worker should be reused per command.

The broader suite must not introduce a suite Worker with planning authority.

Worker Platform should continue to:

- execute one authorized allowlisted command;
- capture bounded output;
- record Worker-local evidence;
- return deterministic result evidence.

Worker Platform must not:

- select commands;
- reorder commands;
- authorize execution;
- interpret results as certification;
- execute shell commands outside the allowlist.

### 5.5 Replay Evidence

Replay can be extended with a suite-level envelope.

Required suite evidence:

- suite candidate;
- human approval;
- Governance authorization;
- per-command Worker request references;
- per-command Worker result references;
- per-command normalized result;
- suite aggregate result;
- completion or fail-closed artifact.

Replay remains append-only and owns reconstruction.

### 5.6 Result Normalization

Existing result normalization should be reused per command.

Required minimal extension:

- aggregate command statuses;
- aggregate pass/fail state;
- record first failing command;
- record timeout or blocked command;
- preserve per-command stdout/stderr bounds;
- distinguish validation failure from architecture certification failure.

Validation results remain evidence, not certification.

## 6. Relationship To Mutation Capabilities

### 6.1 Single-File Mutation

Single-file creation, existing-file replacement, and patch mutation already produce mutation evidence that validation suites can reference.

Broader validation should bind to:

- mutation execution id;
- mutation completion hash;
- affected file path;
- post-mutation artifact hash;
- rollback metadata reference.

### 6.2 Multi-File Mutation

Multi-file mutation increases the need for broader validation because a real transaction can affect runtime code, tests, fixtures, and governance documents together.

Broader validation should bind to:

- transaction candidate hash;
- transaction completion hash;
- exact file set;
- operation count;
- transaction replay hash;
- rollback metadata hash.

Validation suite selection must remain OCS/Governance-owned and must not be inferred locally by ACLI Next or Worker Platform.

### 6.3 Rollback

Rollback execution already includes pre/post rollback validation. Broader suites can extend this by running additional allowlisted checks after rollback completion.

Rollback validation suites must remain separately authorized and must not imply automatic rollback approval.

## 7. Architectural Health Relationship

Architectural Health is ready to advise on validation-suite coverage.

Possible advisory findings:

- validation suite omits required evidence for touched file classes;
- validation command appears outside allowlist;
- validation selection is being made by ACLI Next or Worker Platform;
- validation result is being treated as certification;
- missing Replay evidence;
- missing Governance evidence;
- validation scope is inconsistent with mutation file set;
- command ordering is nondeterministic.

Architectural Health remains advisory only and must not approve, reject, repair, or select validation suites.

## 8. Platform Digital Twin Relationship

The Platform Digital Twin can project validation suites from existing evidence:

- mutation evidence;
- validation-suite candidate;
- Governance authorization;
- Worker command results;
- Replay reconstruction;
- result aggregation;
- Architectural Health advisory findings.

No new Platform Digital Twin subsystem is required.

## 9. Ownership Boundary Review

| Owner | Broader Validation Suite Responsibility |
| --- | --- |
| ACLI Next | Capture intent and render validation proposal/result only. |
| Platform Core | Coordinate suite lifecycle. |
| OCS | Construct deterministic suite candidate and command ordering. |
| Governance | Authorize exact suite command set. |
| Replay | Record and reconstruct suite evidence. |
| Worker Platform | Execute one authorized command at a time. |
| Architectural Health | Produce advisory findings from evidence only. |
| Human | Remain final decision authority. |

No ownership boundary needs to change.

## 10. Required Minimal Extensions

Broader validation requires:

| Extension | Owner | Requirement |
| --- | --- | --- |
| Suite candidate | OCS | Ordered list of allowlisted command candidates. |
| Suite approval | Governance | Hash-bound human approval for exact suite candidate. |
| Per-command authorization | Governance | Worker authorization for each command in order. |
| Suite coordinator | Platform Core | Deterministically sequence existing validation Worker calls. |
| Suite Replay | Replay | Suite-level wrapper with per-command evidence references. |
| Result aggregation | Platform Core result helper | Aggregate per-command result evidence without certifying. |
| Fail-closed model | Platform Core and Replay | Stop or record according to approved policy. |
| Advisory projection | Architectural Health | Detect coverage and authority drift indicators. |

These are deterministic composition extensions, not new subsystem responsibilities.

## 11. Recommended Suite Model

Recommended initial workflow:

```text
Mutation or rollback evidence
-> OCS validation-suite candidate
-> UHCL-compatible proposal rendering
-> Human hash-bound approval
-> Governance suite authorization
-> Replay suite start
-> ordered per-command Worker execution
-> per-command result normalization
-> suite aggregate result
-> Replay suite completion
-> Platform Digital Twin projection
-> Architectural Health advisory findings
-> Human review
```

Recommended first supported suite behavior:

- ordered commands only;
- stop on first failed or blocked command;
- no shell;
- no arbitrary command input;
- no dependency installation;
- no Git command execution unless separately certified;
- no deployment;
- no provider invocation;
- bounded stdout and stderr per command;
- deterministic aggregate status.

## 12. Fail-Closed Requirements

Broader validation suites must fail closed when:

- suite candidate is missing;
- command is not allowlisted;
- command ordering is missing or nondeterministic;
- human approval is absent or not hash-bound;
- Governance authorization is missing;
- Worker request authorization fails;
- Worker Replay evidence is missing;
- suite Replay evidence is missing;
- command output exceeds bounds;
- timeout policy is missing;
- mutation evidence reference is stale, missing, partial, or conflicting.

A command failure or non-zero exit code should be recorded as a validation result. It should block completion claims only when the suite candidate or Governance policy requires pass-before-completion.

## 13. Risk Assessment

| Risk | Mitigation |
| --- | --- |
| Validation suite becomes local authority | Keep candidate construction in OCS and authorization in Governance. |
| Worker becomes command selector | Worker accepts only one authorized command request. |
| Validation success becomes certification | Result artifact remains evidence only. |
| Arbitrary terminal execution sneaks in | Reuse allowlist and non-shell Worker execution. |
| Replay becomes partial | Require suite-level Replay and per-command references. |
| ACLI Next chooses commands | ACLI Next remains capture/render only. |
| Architectural Health becomes gatekeeper | Architectural Health remains advisory only. |

No risk requires architectural preparation before specification.

## 14. Implementation Readiness Assessment

| Area | Readiness | Finding |
| --- | --- | --- |
| Single-command validation Worker | Ready | Existing Worker executes one allowlisted command. |
| Validation allowlist | Ready | Reuse unchanged for first suite. |
| Governance authorization | Ready for extension | Needs exact suite and per-command binding. |
| Replay evidence | Ready for extension | Needs suite-level wrapper. |
| Result normalization | Ready for extension | Needs aggregate result model. |
| Mutation evidence integration | Ready | Single-file and multi-file mutation produce replay-visible evidence. |
| Rollback evidence integration | Ready | Rollback produces replay-visible validation and completion evidence. |
| Architectural Health | Ready | Advisory checks can consume suite evidence. |

Overall readiness: ready for minimal extension.

## 15. Recommended Next Milestone

The next milestone should be:

```text
G9_13_GOVERNED_VALIDATION_SUITE_SPECIFICATION_V1
```

Recommended scope:

- deterministic validation-suite candidate;
- exact command-set approval;
- per-command Governance authorization;
- ordered execution over existing validation Worker;
- suite-level Replay;
- aggregate validation result;
- fail-closed behavior;
- mutation and rollback evidence binding;
- Architectural Health advisory integration.

Do not implement:

- arbitrary shell execution;
- autonomous validation selection;
- dependency installation;
- Git remote operations;
- deployment;
- provider invocation;
- certification automation.

## 16. Final Determination

Broader governed validation suites can be implemented by deterministic composition of the existing certified validation command capability.

No new validation subsystem is required.

No authority boundary needs to change.

Final verdict: BROADER_VALIDATION_READY_FOR_MINIMAL_EXTENSION

## 17. Validation Evidence

Validation performed:

```text
git diff --check
```

Validation result: clean.

Final verdict: BROADER_VALIDATION_READY_FOR_MINIMAL_EXTENSION
