# G11-03 ACLI Next Persistent Conversational Session Implementation V1

Status: ACLI Next persistent conversational session implemented.

Final verdict: ACLI_NEXT_PERSISTENT_CONVERSATIONAL_SESSION_IMPLEMENTED

## 1. Executive Summary

G11-02 implemented `aigol next` as a natural conversational entrypoint.

Practical use revealed an operational UX gap:

```text
aigol next
-> single conversational turn
-> exit to operating system shell
```

This caused follow-up user input to be interpreted by the shell instead of remaining inside the governed development conversation.

G11-03 implements a persistent conversational REPL for interactive `aigol next` usage:

```text
aigol next
-> persistent conversational session
-> multiple governed conversational turns
-> explicit exit only
```

The implementation is a UX evolution only. It does not redesign Platform Core, Governance, Replay, Worker Platform, Architectural Health, or ACLI Next ownership.

## 2. Mandatory Capability Audit

Before implementation, required capabilities were reviewed.

| Required Capability | Existing Capability | Reuse Decision |
| --- | --- | --- |
| Conversational runtime | `aigol/acli_next/conversational.py` single-turn adapter | Reused as the per-turn unit. |
| Session runtime | ACLI Next session and interactive runtimes | Reused through execution-plan composition. |
| Session persistence | Deterministic session root and run directories | Reused and extended with persistent completion artifact. |
| Turn persistence | Existing conversational run artifacts under `RUN-000001`, `RUN-000002`, etc. | Reused for each REPL turn. |
| Execution-plan runtime | `run_acli_next_interactive_with_execution_plan(...)` | Reused. |
| Dashboard runtime | `run_acli_next_daily_dashboard(...)` | Reused. |
| Replay | Existing replay-visible artifacts | Reused through per-turn and completion artifacts. |
| Governance | Existing Governance status presentation | Reused; no approval or authorization created. |
| Platform Core workflow state | Platform Core daily operational exposure | Reused through dashboard refresh after each turn. |
| Architectural Health integration | Existing advisory status presentation | Reused; advisory-only. |

Audit result:

```text
persistent session behavior was the missing UX behavior; runtime foundations already existed
```

## 3. Responsibility Verification

No responsibility movement was required.

| Component | Certified Responsibility | G11-03 Result |
| --- | --- | --- |
| ACLI Next | Human interaction, presentation, guidance, delegation | Extended only to keep the prompt open. |
| Platform Core | Workflow orchestration and operational state | Preserved through existing execution-plan and dashboard paths. |
| Governance | Approval and authorization | Preserved; no Governance decisions are created. |
| Replay | Evidence and reconstruction | Preserved; ACLI Next writes presentation artifacts only. |
| Worker Platform | Bounded authorized execution | Preserved; no Worker is invoked directly. |
| Architectural Health | Deterministic advisory findings | Preserved; advisory status is displayed only. |

Implementation proceeded because no architectural review blocker or ownership migration was detected.

## 4. Implementation Summary

Updated files:

| File | Change |
| --- | --- |
| `aigol/acli_next/conversational.py` | Added persistent conversational REPL wrapper and persistent session completion artifact. |
| `aigol/acli_next/__init__.py` | Exported persistent session runtime and renderer. |
| `aigol/cli/aigol_cli.py` | Routed interactive bare `aigol next` to persistent REPL while preserving scripted one-shot behavior. |
| `tests/test_g11_acli_next_conversational_session.py` | Added persistent session loop coverage. |

The persistent REPL reuses the existing single-turn conversational adapter for every human input.

It does not create a new workflow engine.

## 5. Persistent Session Lifecycle

### 5.1 Session Start

When the human runs:

```text
aigol next
```

in an interactive terminal, ACLI Next:

1. establishes a deterministic persistent session id;
2. displays a session start message;
3. presents the `AiGOL>` prompt;
4. waits for user input.

### 5.2 Turn Loop

For each non-empty prompt:

1. ACLI Next captures the human input.
2. ACLI Next calls the existing single-turn conversational adapter.
3. The single-turn adapter delegates to existing execution-plan and dashboard runtimes.
4. The dashboard refreshes Platform Core operational state presentation.
5. The turn is recorded under the next deterministic run directory.
6. ACLI Next renders the turn summary.
7. The prompt remains active.

### 5.3 Turn Persistence

Each turn remains deterministic:

```text
<runtime-root>/<session-id>/RUN-000001
<runtime-root>/<session-id>/RUN-000002
...
```

The existing run numbering mechanism is reused.

### 5.4 Graceful Termination

The session terminates only when the human enters:

```text
exit
quit
close session
```

or when EOF is received.

On termination, ACLI Next records a replay-visible persistent session completion artifact.

### 5.5 Session Cleanup

No destructive cleanup is performed.

Replay-visible artifacts remain available for review and reconstruction.

## 6. CLI Behavior

Interactive behavior:

```text
aigol next
```

starts the persistent REPL when:

- no subcommand is provided;
- no `--prompt` is provided;
- stdin is a TTY;
- JSON output is not requested.

Scripted behavior remains one-shot:

```text
aigol next --prompt "Prepare a governed review."
```

Existing subcommands remain unchanged:

- `aigol next session`;
- `aigol next interactive`;
- `aigol next readonly-worker`;
- `aigol next execution-plan`;
- `aigol next dashboard`.

This preserves testability, automation, and backward compatibility.

## 7. Platform Core Interaction

Platform Core continues to own:

- workflow progression;
- execution-plan semantics;
- operational state;
- capability coordination.

The persistent REPL only coordinates user interaction by repeatedly delegating to the existing single-turn adapter.

It does not decide workflow authority.

## 8. Hybrid Behavior

If a request requires external operation, such as Git remote workflow, dependency management, deployment, or exceptional environment work:

- the dashboard marks the operation as hybrid-required;
- ACLI Next displays the reason and return condition;
- the persistent session remains active;
- the human can return to the same session after the external operation;
- no new session is required.

The persistent REPL does not perform the external operation.

## 9. Architectural Health Review

Architectural Health advisory review was performed against the G11-03 implementation scope.

Advisory inputs:

- persistent loop invokes existing single-turn adapter;
- no Platform Core orchestration is duplicated;
- no Governance authorization is created;
- no Worker Platform execution is introduced;
- no Replay ownership is moved;
- hybrid operations remain guidance-only;
- session completion artifact is presentation evidence only.

Advisory finding:

```text
NO_RESPONSIBILITY_LEAKAGE_DETECTED
```

Mandatory advisory notes:

- Architecture review should verify the persistent loop remains a UX loop only.
- Architecture review should verify future REPL commands do not become hidden execution commands.
- Architecture review should verify session completion remains presentation evidence, not Governance certification.

No implementation compensation was required.

## 10. Boundary Preservation Evidence

Persistent session completion artifacts include:

```text
persistent_repl: True
show_guide_delegate_only: True
minimal_ux_extension_only: True
platform_core_coordinates: True
governance_authority_preserved: True
replay_authority_preserved: True
worker_execution_authority_preserved: True
architectural_health_advisory_only: True
platform_digital_twin_evidence_source_preserved: True
acli_next_authorizes: False
acli_next_executes: False
acli_next_records_replay_evidence: False
acli_next_repairs_architecture: False
acli_next_certifies: False
external_operation_performed: False
repository_mutated: False
deployment_performed: False
dependency_operation_performed: False
git_remote_operation_performed: False
```

These fields preserve the certified ownership boundaries.

## 11. Targeted Tests

Updated test coverage:

```text
tests/test_g11_acli_next_conversational_session.py
```

New test verifies:

- persistent session accepts multiple prompts;
- each prompt creates a deterministic run;
- hybrid-required guidance remains visible;
- session exits only after explicit `exit`;
- ACLI Next remains non-authoritative.

Existing G8 and G10 ACLI Next tests remain passing.

## 12. Known Limitations

This implementation does not add:

- governed Git remote execution;
- dependency management;
- deployment;
- external operation execution;
- provider invocation;
- autonomous planning;
- Governance authority in ACLI Next;
- Replay ownership in ACLI Next;
- Worker execution in ACLI Next.

Those remain separate Generation 11 operational expansion items.

## 13. Final Determination

The ACLI Next persistent conversational session is implemented.

The implementation transforms interactive `aigol next` from a one-turn UX into a persistent governed conversational session while preserving the certified Platform Core architecture.

Final verdict: ACLI_NEXT_PERSISTENT_CONVERSATIONAL_SESSION_IMPLEMENTED

## 14. Validation Evidence

Validation performed:

```text
git diff --check
python -m py_compile aigol/acli_next/conversational.py aigol/acli_next/__init__.py aigol/cli/aigol_cli.py
python -m pytest tests/test_g11_acli_next_conversational_session.py tests/test_g8_acli_next_interactive_session.py tests/test_g8_acli_next_execution_plan.py tests/test_g10_acli_next_daily_operational_exposure.py
```

Validation result: clean; targeted tests passed.

Final verdict: ACLI_NEXT_PERSISTENT_CONVERSATIONAL_SESSION_IMPLEMENTED
