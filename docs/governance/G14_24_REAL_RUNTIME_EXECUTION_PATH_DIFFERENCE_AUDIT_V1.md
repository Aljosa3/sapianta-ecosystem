# G14-24 Real Runtime Execution Path Difference Audit V1

Status: real runtime execution path partially equivalent with state and prompt-class divergence identified.

Final verdict: REAL_RUNTIME_EXECUTION_PATH_PARTIALLY_EQUIVALENT

## 1. Executive Summary

G14-24 audited why two real interactive `aicli` / native-development executions appeared to produce different outcomes:

Observation A:

```text
FAILED_CLOSED:
native development task intake failed closed:
milestone id cannot be identified
```

Observation B:

```text
requested_milestone_id: AIGOL_GENERIC_DEVELOPMENT_TASK_V1
```

The audit found no evidence that `aicli` uses a different Platform Core, different runtime binding, different Provider Platform, or different Worker Platform.

The difference is explained by runtime input/state:

- Observation B was a first-turn plain native-development request: `Implement a governance documentation validator.`
- current Native Development Intake deterministically accepts that prompt and assigns `AIGOL_GENERIC_DEVELOPMENT_TASK_V1`;
- the located Observation A artifact came from a restored continuation turn with a 12-character single-line prompt, not from the same first-turn natural-language request;
- the Observation A path entered Native Development Intake through `post_context_continuation/conversation_ppp_routing/conversation_native_development/...`, not through the same first-turn context integration path as Observation B;
- Native Development Intake still has a legacy fail-closed branch for prompts that are not explicit milestone prompts and are not accepted by `is_plain_native_development_prompt(...)`.

Conclusion:

The runtime remains deterministic for the same prompt, same code revision, and same runtime state. The observed difference is not proven to be nondeterministic behavior. It is a partially equivalent runtime path because restored continuation state can route a short continuation prompt into Native Development Intake, where the legacy milestone fallback may fail closed.

Final verdict: REAL_RUNTIME_EXECUTION_PATH_PARTIALLY_EQUIVALENT

## 2. Audit Scope

The audit reviewed:

- `aicli` reference UHI entrypoint;
- AiGOL Next runtime binding;
- Native Development Intake;
- Native Development Context Integration;
- restored post-entry continuation;
- PPP routing continuation;
- current G14-23 runtime evidence;
- historical failed runtime evidence found under `/tmp`;
- regression tests for intent resolution, Platform Core project services, and reference UHI.

No architecture redesign was performed.

No implementation changes were made.

## 3. Shared Runtime Path

For the normal approved `aicli` path, the runtime is:

```text
aicli
-> Platform Core Development Intent Resolution
-> /approve
-> run_interactive_conversation(...)
-> conversational routing
-> Native Development Context Integration
-> Native Development Intake
-> Development Context Assembly
-> Post-Entry Continuation Gate
-> PPP Routing
-> Provider Platform
```

Implementation evidence:

| Stage | File / function |
| --- | --- |
| Reference UHI | `aigol/cli/aicli.py::run_reference_uhi_session` |
| Runtime delegation | `aigol/cli/aicli.py::_run_certified_runtime` |
| Certified conversation runtime | `aigol/cli/aigol_cli.py::run_interactive_conversation` |
| Native context integration | `aigol/runtime/conversation_native_development_context_integration.py::run_conversation_native_development_context_integration` |
| Native intake | `aigol/runtime/native_development_task_intake_runtime.py::run_native_development_task_intake` |
| Prompt analysis | `aigol/runtime/native_development_task_intake_runtime.py::_analyze_prompt` |
| PPP continuation | `aigol/runtime/context_assembled_to_ppp_routing_continuation.py::continue_context_assembled_to_ppp_routing` |

No alternate Platform Core was found.

No alternate Provider Platform was found.

No alternate Worker Platform was found.

## 4. Observation B Trace

Runtime command:

```text
./aicli --session-id G14-23-CONTEXT-AUDIT --runtime-root /tmp/aigol_g14_23_context_audit --workspace /home/pisarna/work/sapianta --created-at 2026-07-04T00:00:00Z
```

Prompt:

```text
Implement a governance documentation validator.
```

Evidence root:

```text
/tmp/aigol_g14_23_context_audit/G14-23-CONTEXT-AUDIT/TURN-000001
```

Native Intake evidence:

```text
native_development_task_intake/000_native_development_task_intake_recorded.json
```

Observed values:

```text
intake_status: NATIVE_DEVELOPMENT_TASK_INTAKE_ACCEPTED
requested_milestone_id: AIGOL_GENERIC_DEVELOPMENT_TASK_V1
requested_domain: AIGOL
requested_worker_family: CLAUDE_EXTERNAL
task_kind: WORKER
failure_reason: null
```

Context evidence:

```text
native_development_context_integration/000_conversation_native_development_context_integrated.json
development_context_assembly/004_development_context_assembly_returned.json
```

Observed values:

```text
integration_status: CONVERSATION_NATIVE_DEVELOPMENT_CONTEXT_INTEGRATED
context_status: CONTEXT_ASSEMBLED
missing_context: []
ambiguous_context: []
provider_necessity_classification: PROVIDER_REQUIRED_FOR_PROPOSAL
```

PPP continuation evidence:

```text
post_context_continuation/000_post_context_continuation_recorded.json
```

Observed values:

```text
continuation_status: FAILED_CLOSED
failure_reason: OpenAI provider unavailable
operational_failure_classification: PROVIDER_AVAILABILITY
```

Finding:

Observation B did not fail milestone resolution. It reached provider proposal production and failed closed on provider availability in the restricted runtime environment.

## 5. Observation A Trace

Historical failed evidence located:

```text
/tmp/tmp35h_od6z/interactive_runtime/SESSION-NATIVE-CONTEXT-CLI-RESTORE-CONTINUE-000001/TURN-000002/post_context_continuation/conversation_ppp_routing/conversation_native_development/native_development_task_intake/000_native_development_task_intake_recorded.json
```

Observed values:

```text
intake_status: FAILED_CLOSED
requested_milestone_id: null
requested_domain: null
requested_worker_family: null
failure_reason: native development task intake failed closed: milestone id cannot be identified
```

Neighboring prompt-capture evidence:

```text
/tmp/tmp35h_od6z/interactive_runtime/SESSION-NATIVE-CONTEXT-CLI-RESTORE-CONTINUE-000001/TURN-000002/multiline_prompt_capture/000_multiline_prompt_captured.json
```

Observed values:

```text
input_mode: SINGLE_LINE
line_count: 1
character_count: 12
session_id: SESSION-NATIVE-CONTEXT-CLI-RESTORE-CONTINUE-000001
turn_id: TURN-000002
```

Path evidence:

```text
TURN-000002/pending_post_entry_continuation_restore/
TURN-000002/post_context_continuation/
TURN-000002/post_context_continuation/conversation_ppp_routing/conversation_native_development/
```

Finding:

The located Observation A evidence is a restored continuation turn, not the same first-turn natural-language implementation request used in Observation B.

## 6. First Point of Divergence

| Stage | Observation A | Observation B |
| --- | --- | --- |
| Session shape | Restored continuation session, `TURN-000002` | New reference UHI session, `TURN-000001` |
| Prompt evidence | Single-line, 12 characters | `Implement a governance documentation validator.` |
| Runtime subpath | `post_context_continuation/conversation_ppp_routing/conversation_native_development/...` | `native_development_context_integration/...` then `post_context_continuation/...` |
| Native Intake decision | `FAILED_CLOSED` | `NATIVE_DEVELOPMENT_TASK_INTAKE_ACCEPTED` |
| Milestone result | `None` | `AIGOL_GENERIC_DEVELOPMENT_TASK_V1` |
| Failure cause | prompt not accepted by milestone or plain-native branches | provider availability after context assembly |

First proven divergence:

```text
runtime state and prompt form before Native Development Intake
```

No evidence proves that the same prompt in the same state produced different Native Development Intake decisions.

## 7. Deterministic Decision Comparison

Direct Native Intake probe:

```text
Implement a governance documentation validator.
-> NATIVE_DEVELOPMENT_TASK_INTAKE_ACCEPTED
-> AIGOL_GENERIC_DEVELOPMENT_TASK_V1
```

Control probes:

```text
Prepare governance documentation validator.
-> FAILED_CLOSED
-> milestone id cannot be identified

Implement the project.
-> FAILED_CLOSED
-> milestone id cannot be identified
```

Interpretation:

The decision is deterministic based on:

- whether a milestone id is present;
- whether `is_plain_native_development_prompt(...)` accepts the prompt;
- whether the prompt contains forbidden authority terms;
- whether the prompt reaches Native Intake as an original implementation request or as a continuation/control phrase.

## 8. State Analysis

| Factor | Effect observed |
| --- | --- |
| Different CLI entrypoint | Not proven. Current `aicli` delegates to `run_interactive_conversation(...)`. |
| Different runtime configuration | Partially relevant: restored continuation state changes the turn path. |
| Different environment | Relevant after context assembly: restricted environment produced provider availability failure. |
| Different replay state | Relevant: Observation A was from pending post-entry continuation restore. |
| Different workspace state | Not proven as the cause. Current Native Intake does not directly consume workspace state. |
| Different provider configuration | Relevant only after intake; not relevant to milestone failure. |
| Different prompt normalization | Relevant: prompt class determines plain-native acceptance. |
| Different routing path | Proven: Observation A used restored continuation / nested conversation-native-development path. |
| Different deterministic decision | Proven and expected for different prompt classes. |
| Different code revision | Possible historically, but not required to explain the located evidence. |
| Different executable | Not proven. |
| Different startup parameters | Partially relevant if they create restored continuation state. |

## 9. Runtime Equivalence Assessment

The runtime is equivalent for:

```text
same prompt
same code revision
same runtime state
same startup parameters
same provider availability
```

The runtime is not equivalent across:

```text
first-turn implementation request
vs.
restored post-entry continuation turn
```

That difference is expected because restored continuation uses the pending context and a short operator confirmation phrase, while first-turn native development uses the original implementation request.

## 10. Determinism Assessment

The observed difference represents:

```text
expected deterministic behavior under different runtime state and prompt class
```

It is not currently classified as:

- nondeterministic runtime behavior;
- Provider Platform defect;
- Worker Platform defect;
- Unified Human Interface defect;
- proven implementation defect in `aicli`.

Residual concern:

The restored continuation subpath can pass a short continuation/control phrase into Native Development Intake through a nested conversation-native-development path. That is a compatibility-path sharp edge, but this audit does not prove it occurred for the same original prompt as Observation B.

## 11. Architecture Verification

Both observed paths preserve:

- Unified Human Interface thin adapter principles;
- Platform Core ownership of runtime progression;
- Development Intent Resolution ownership;
- Governance ownership;
- Provider Platform ownership;
- Worker Platform ownership;
- Replay ownership.

No authority moved into `aicli`.

No provider execution bypass was found.

No worker execution bypass was found.

Replay evidence was preserved in both accepted and failed paths.

## 12. Minimal Correction Analysis

No implementation change is recommended from this audit alone.

If Generation 14 continues hardening this path, the smallest correction to evaluate is:

```text
Ensure restored post-entry continuation never re-runs Native Development Intake on the short continuation phrase when the original native context has already been restored and verified.
```

The correction, if later implemented, should:

- remain in Platform Core / runtime continuation code;
- reuse the restored native context capture;
- avoid duplicating intent classification;
- avoid adding UHI-specific logic;
- preserve fail-closed behavior when restored context is missing or invalid.

## 13. Validation Evidence

Runtime probes:

```text
./aicli --session-id G14-23-CONTEXT-AUDIT --runtime-root /tmp/aigol_g14_23_context_audit --workspace /home/pisarna/work/sapianta --created-at 2026-07-04T00:00:00Z
```

Direct prompt probes:

```text
Implement a governance documentation validator.
-> NATIVE_DEVELOPMENT_TASK_INTAKE_ACCEPTED

Prepare governance documentation validator.
-> FAILED_CLOSED

Implement the project.
-> FAILED_CLOSED
```

Regression validation:

```text
python -m pytest tests/test_native_development_task_intake_and_session_resume_v1.py tests/test_g14_19_development_intent_resolution_unification_v1.py tests/test_g14_22_reference_unified_human_interface_v1.py -q
```

Result:

```text
17 passed
```

Whitespace validation:

```text
git diff --check
```

Result:

```text
clean
```

## 14. Final Determination

The real runtime execution path is partially equivalent.

The current `aicli` first-turn implementation path and the historical restored-continuation failure path share Platform Core components, but they are not identical runtime states and do not pass the same prompt form into Native Development Intake.

The runtime remains operationally deterministic for equivalent inputs and state.

Final verdict: REAL_RUNTIME_EXECUTION_PATH_PARTIALLY_EQUIVALENT
