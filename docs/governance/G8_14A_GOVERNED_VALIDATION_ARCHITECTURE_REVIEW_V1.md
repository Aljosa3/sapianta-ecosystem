# G8-14A Governed Validation Architecture Review V1

Status: governed validation architecture reviewed.

Final verdict: GOVERNED_VALIDATION_ARCHITECTURE_CONFIRMED

## 1. Executive Summary

G8-14A reviews the governed validation execution implementation introduced by G8-14.

The review confirms that governed validation execution preserves the certified Platform Core ownership boundaries:

- ACLI Next remains a thin human interface.
- Platform Core coordinates validation execution.
- OCS-shaped candidate handling owns validation candidate artifacts.
- Governance owns human approval validation and authorization.
- Worker Platform owns command execution.
- Replay owns evidence persistence and reconstruction.
- validation result handling normalizes Worker output without becoming Governance.

No new authority layer, orchestration engine, Replay replacement, Governance replacement, shell execution surface, Git path, commit path, deployment path, package installation path, provider invocation path, or ACLI Next execution authority was identified.

The architecture is acceptable for the smallest governed validation capability: execution of exactly one allowlisted, non-shell validation command with timeout-bound execution, bounded output capture, Governance authorization, Worker Platform execution, and Replay-visible evidence.

## 2. Review Scope

Reviewed implementation surfaces:

| Surface | File | Review Focus |
| --- | --- | --- |
| Governed validation coordinator | `aigol/runtime/governed_validation_runtime.py` | Platform Core coordination boundary. |
| Validation command allowlist | `aigol/runtime/platform_core_validation_allowlist.py` | Capability lookup and command constraint boundary. |
| Validation candidate helper | `aigol/runtime/platform_core_validation_candidate.py` | OCS-shaped candidate ownership. |
| Validation Governance helper | `aigol/runtime/platform_core_validation_governance.py` | Human approval and authorization ownership. |
| Validation Replay helper | `aigol/runtime/platform_core_validation_replay.py` | Replay persistence and reconstruction ownership. |
| Validation result helper | `aigol/runtime/platform_core_validation_result.py` | Result normalization boundary. |
| Validation command Worker | `aigol/workers/validation_command_worker.py` | Worker Platform execution boundary. |
| Targeted tests | `tests/test_g8_governed_validation_runtime.py` | Boundary and fail-closed coverage. |
| Implementation record | `docs/governance/G8_14_GOVERNED_VALIDATION_EXECUTION_IMPLEMENTATION_V1.md` | Certified implementation intent. |
| Specification baseline | `docs/governance/G8_13_GOVERNED_VALIDATION_EXECUTION_SPECIFICATION_V1.md` | Required architectural constraints. |

## 3. Ownership Matrix

| Responsibility | Canonical Owner | Current Implementation | Review Result |
| --- | --- | --- | --- |
| Human request and approval presentation | ACLI Next / human interface | No new ACLI execution authority was introduced. | Confirmed thin entrypoint. |
| Validation candidate construction | OCS-shaped Platform Core helper | `platform_core_validation_candidate.py` | Correctly separated from Worker and Governance. |
| Validation command capability lookup | Canonical validation allowlist | `platform_core_validation_allowlist.py` | Correctly isolated as allowlist lookup and normalization. |
| Human approval artifact | Governance | `platform_core_validation_governance.py` | Correctly bound to candidate id and candidate hash. |
| Authorization record creation | Governance / existing authorization record model | `platform_core_validation_governance.py` delegates to existing authorization record helpers. | Confirmed. |
| Overall validation workflow coordination | Platform Core coordinator | `governed_validation_runtime.py` | Acceptable coordination layer. |
| Command execution | Worker Platform | `validation_command_worker.py` | Confirmed Worker-only execution. |
| Replay persistence | Replay | `platform_core_validation_replay.py`; Worker-side replay inside Worker execution boundary. | Confirmed for G8-14 scope. |
| Replay reconstruction | Replay | `platform_core_validation_replay.py` and Worker replay reconstruction. | Confirmed. |
| Validation result normalization | Platform Core validation result helper | `platform_core_validation_result.py` | Confirmed; does not authorize or execute. |
| Governance interpretation of validation outcome | Governance / later certification process | Not implemented as automatic certification. | Confirmed. |
| Git, commit, deployment, provider invocation | Prohibited | Guard fields and tests assert absence. | Confirmed absent. |

## 4. Governed Validation Coordinator Review

The governed validation coordinator in `aigol/runtime/governed_validation_runtime.py` acts as a thin Platform Core coordination layer.

It delegates:

- candidate validation to `platform_core_validation_candidate.py`;
- human approval validation and authorization creation to `platform_core_validation_governance.py`;
- pre-execution and result artifacts to `platform_core_validation_result.py`;
- replay persistence and reconstruction to `platform_core_validation_replay.py`;
- executable command dispatch to `aigol/workers/validation_command_worker.py`.

The coordinator retains only the minimum workflow assembly responsibilities required to run the governed validation sequence and produce a completion capture. It does not directly run subprocesses, select arbitrary commands, create a new policy engine, evaluate Governance policy outside the Governance helper, reconstruct replay independently, or introduce an ACLI-facing authority path.

Review result: compliant.

## 5. Validation Command Worker Review

The validation command Worker in `aigol/workers/validation_command_worker.py` owns execution only.

The Worker:

- validates an authorized validation request;
- rejects forbidden request fields;
- verifies the command against the static allowlist;
- resolves the bounded working directory;
- executes the allowlisted argument vector with `shell=False`;
- enforces timeout behavior;
- captures bounded stdout and stderr excerpts;
- records hashes for stdout and stderr;
- reports `VALIDATION_PASSED`, `VALIDATION_FAILED`, `VALIDATION_TIMED_OUT`, or `VALIDATION_BLOCKED`;
- records Worker-side replay evidence.

The Worker does not:

- choose a validation command autonomously;
- approve a validation command;
- create Governance authorization;
- interpret validation success as certification;
- execute Git;
- create commits;
- deploy;
- install packages;
- invoke providers;
- perform arbitrary shell execution.

The presence of `subprocess.run` is appropriate in this module because Worker Platform execution is the certified execution boundary. The implementation uses an argument vector and explicitly sets `shell=False`, preserving the G8-13 prohibition against raw shell execution.

Review result: compliant.

## 6. OCS Validation Candidate Handling

The OCS-shaped candidate helper in `aigol/runtime/platform_core_validation_candidate.py` owns validation candidate artifact creation and verification.

The candidate artifact records:

- candidate id;
- command id;
- validation purpose;
- allowlisted command metadata;
- command hash and spec hash;
- Worker id, authorized scope, and operation;
- explicit false flags for shell, Git, repository mutation, deployment, and provider invocation;
- human approval, Governance authorization, and Replay requirements.

This helper does not execute commands, approve execution, persist Replay evidence, or normalize Worker output.

Review result: compliant.

## 7. Governance Authorization Review

The Governance helper in `aigol/runtime/platform_core_validation_governance.py` owns approval and authorization evidence.

It requires hash-bound human approval using:

```text
confirm validation <candidate_id> <candidate_hash>
```

It also creates authorization through the existing authorization record implementation for:

- `worker_id`: `GOVERNED_VALIDATION_COMMAND_WORKER`
- `authorization_scope`: `RUN_ALLOWLISTED_VALIDATION_COMMAND`

Human approval alone does not execute validation. Authorization remains a Governance-owned artifact that the Worker must validate before execution.

Review result: compliant.

## 8. Replay Evidence Review

Replay evidence for the Platform Core validation workflow is owned by `aigol/runtime/platform_core_validation_replay.py`.

The Replay model records the ordered sequence:

| Step | Evidence |
| --- | --- |
| 0 | Validation candidate recorded. |
| 1 | Human approval recorded. |
| 2 | Governance authorization recorded. |
| 3 | Worker request recorded. |
| 4 | Pre-execution state recorded. |
| 5 | Worker result recorded. |
| 6 | Validation result recorded. |
| 7 | Completion recorded. |

Replay reconstruction verifies ordering, artifact hashes, candidate-to-approval binding, authorization-to-candidate binding, Worker request authorization binding, command hash continuity, result hash continuity, and completion linkage.

Worker-side replay exists inside the Worker execution boundary and records the Worker request and result. This is acceptable because it remains evidence for Worker execution rather than a replacement for Platform Core Replay reconstruction.

Review result: compliant.

## 9. Validation Result Handling Review

The validation result helper in `aigol/runtime/platform_core_validation_result.py` normalizes Worker output into Platform Core validation evidence.

It records:

- validation status;
- validation pass/fail boolean;
- exit code;
- timeout state;
- stdout and stderr hashes;
- bounded output excerpts;
- Worker replay hash;
- explicit false flags for Git, repository mutation, deployment, and provider invocation.

This result artifact is evidence, not Governance certification. A non-zero exit code or timeout is represented as a validation result, not as automatic architectural failure unless required evidence is missing.

Review result: compliant.

## 10. ACLI Next Interaction Review

No evidence was found that ACLI Next has absorbed validation execution responsibilities.

Under the current architecture, ACLI Next may capture a human request, present a validation proposal, capture explicit approval, render a result, and present Replay references. It must continue not to:

- select validation commands autonomously;
- construct local validation plans;
- execute commands;
- authorize validation;
- persist or reconstruct Replay evidence;
- interpret validation output as certification.

The G8-14 implementation did not add a new ACLI Next command execution authority.

Review result: compliant.

## 11. Authority And Prohibited Surface Review

The implementation preserves the prohibited-operation boundaries from G8-13.

| Prohibited Surface | Review Finding |
| --- | --- |
| Git | No Git execution path identified; false flags and tests cover absence. |
| Commits | No commit creation path identified. |
| Deployment | No deployment path identified; false flags and forbidden field guards are present. |
| Package installation | No package installation capability introduced. |
| Provider invocation | No provider invocation path identified. |
| Arbitrary shell execution | Worker uses allowlisted argv and `shell=False`; shell executables are rejected by allowlist validation. |
| Raw command strings | No raw shell command string interface identified. |
| New authority layer | No new Governance, Replay, OCS, Worker Platform, or ACLI authority layer identified. |

Review result: compliant.

## 12. Test Coverage Review

Targeted tests in `tests/test_g8_governed_validation_runtime.py` cover:

- successful allowlisted validation execution;
- replay reconstruction;
- non-zero validation exit code as validation failure;
- timeout recording;
- missing approval fail-closed behavior;
- unbound human confirmation rejection;
- unallowlisted command rejection;
- absence of shell, Git, provider, and deployment surfaces.

The tests are aligned with the intended architecture. They validate both happy-path execution and core boundary failures.

## 13. Architectural Risks

No current responsibility leakage was detected.

Future risks:

| Risk | Boundary Concern | Guardrail |
| --- | --- | --- |
| Allowlist expansion becomes policy logic | Validation allowlist could become a hidden Governance or OCS substitute. | Add commands only through governed review and keep policy decisions in Governance / OCS. |
| Validation result becomes certification | A passing command could be treated as architectural approval. | Keep certification decisions separate from validation result evidence. |
| Worker grows command selection logic | Worker could become an orchestrator. | Worker must continue receiving a fully authorized request and must not select commands. |
| Replay logic spreads into interfaces | ACLI Next or future Web/REST/Mobile/Voice adapters could reconstruct evidence locally. | All interfaces must present Replay references and delegate reconstruction to Replay. |
| Test-only commands are normalized as production commands | Static failure/timeout commands are useful for tests but should not become broad execution precedent. | Keep test commands explicitly bounded or replace with certified production validation commands in later milestones. |

## 14. Recommendations

No refactoring is required before the next governed validation milestone.

Recommended guardrails:

1. Treat validation command allowlist changes as governance-significant.
2. Require a separate review for each new validation command class.
3. Keep Worker request schemas free of raw shell command fields.
4. Keep validation result artifacts descriptive and avoid certification language.
5. Preserve ACLI Next as request, approval, rendering, and Replay-reference presentation only.
6. Keep Replay reconstruction centralized in Replay-owned helpers.
7. Continue targeted tests for forbidden surfaces whenever validation capability expands.

## 15. Final Determination

The governed validation implementation preserves the certified Platform Core architecture.

Worker Platform owns execution only. Platform Core coordinates. Governance remains the authority. Replay remains the evidence system. ACLI Next remains a thin entrypoint. No new authority layer was introduced.

Final verdict: GOVERNED_VALIDATION_ARCHITECTURE_CONFIRMED

## 16. Validation Evidence

Validation performed:

```text
git diff --check
```

Validation result: clean.

Final verdict: GOVERNED_VALIDATION_ARCHITECTURE_CONFIRMED
