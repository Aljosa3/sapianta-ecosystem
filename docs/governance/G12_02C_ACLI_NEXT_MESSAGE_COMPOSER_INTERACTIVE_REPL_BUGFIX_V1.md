# G12-02C ACLI Next Message Composer Interactive REPL Bugfix V1

Status: ACLI Next interactive message composer behavior restored.

Final verdict: ACLI_NEXT_INTERACTIVE_MESSAGE_COMPOSER_OPERATIONAL_BEHAVIOR_RESTORED

## 1. Executive Summary

G12-02B repaired a Message Composer command-recognition defect.

Further real interactive validation identified remaining REPL defects:

- prompt rendering was noisy during multi-line composition;
- copied transcript prompt prefixes could prevent command recognition;
- interactive behavior was not yet validated through a real PTY path.

G12-02C repairs the remaining REPL defects while preserving the certified Message Composer architecture.

The repair is operational only. It does not redesign Platform Core, ACLI Next architecture, Governance, Replay, Worker Platform, Platform Digital Twin, or Architectural Health.

## 2. Capability Discovery

The investigated path was:

```text
real interactive terminal
-> persistent ACLI Next REPL
-> Message Composer buffer
-> command recognition
-> /preview, /clear, /cancel, /send
-> conversational adapter delegation
-> execution-plan runtime
-> dashboard runtime
-> Replay-visible run
-> rendered response
```

Capability discovery found that the existing downstream governed path remained functional. The defects were localized to interactive REPL behavior before delegation.

## 3. Existing Capability Audit

| Capability | Audit Finding |
| --- | --- |
| Interactive REPL loop | Functional, but continuation prompt rendering was visually noisy during pasted multi-line composition. |
| Message Composer | Functional, but command detection needed to tolerate copied prompt prefixes. |
| Command parser | Already handled invisible Unicode format characters after G12-02B; still needed transcript-prefix normalization. |
| Compose buffer lifecycle | Correct after `/send`, `/clear`, and `/cancel`; preserved. |
| Prompt rendering | Needed repair to avoid repeated `AiGOL compose>` injection during active composition. |
| Terminal input handling | Needed PTY regression validation. |
| Conversational adapter | Functional and reused. |
| Execution-plan runtime | Functional and reused. |
| Dashboard runtime | Functional and reused. |
| Replay runtime | Functional and reused. |

Audit determination:

```text
the divergence occurred in the ACLI Next interactive REPL layer, not in Platform Core or downstream governed runtimes
```

## 4. Root-Cause Analysis

Two operational root causes were identified.

### 4.1 Prompt Rendering Noise

The composer previously rendered:

```text
AiGOL compose>
```

for every input line after the buffer became active.

During multi-line paste or rapid typing, this made the terminal transcript appear as if the prompt was injected into the composed message. The prompt was not part of stored message content, but the visual behavior was inconsistent with daily operator use.

Repair:

```text
show AiGOL> only when the buffer is empty; suppress repeated continuation prompts while composing
```

### 4.2 Transcript-Prefixed Command Recognition

Real operator workflows may copy commands from visible transcripts, producing inputs such as:

```text
AiGOL compose> /send
AiGOL> /preview
```

The command parser did not normalize these prompt prefixes.

Repair:

```text
normalize known ACLI Next prompt prefixes during command detection only
```

Buffered message content remains unchanged.

## 5. Repair Summary

Updated implementation:

| File | Repair |
| --- | --- |
| `aigol/acli_next/conversational.py` | Suppressed repeated compose prompts during active buffering and normalized copied ACLI prompt prefixes for command detection. |
| `tests/test_g11_acli_next_conversational_session.py` | Added regression tests for prompt-prefixed commands and a real PTY interactive flow. |
| `docs/governance/G12_02C_ACLI_NEXT_MESSAGE_COMPOSER_INTERACTIVE_REPL_BUGFIX_V1.md` | Recorded investigation, repair, and validation evidence. |

The repair remains scoped to ACLI Next UX.

## 6. PTY Validation Evidence

A real PTY validation session was performed with:

```text
python -m aigol.cli.aigol_cli next
```

Scenario validated:

1. Start `aigol next`.
2. Compose a multi-line message.
3. Run `/preview`.
4. Confirm preview displays the complete composed message.
5. Run `/clear`.
6. Confirm buffer clears.
7. Run empty `/send`.
8. Confirm no turn is created.
9. Compose and `/send` a second multi-line message.
10. Confirm one governed conversational turn and one run.
11. Compose and `/send` a third message.
12. Confirm a second governed conversational turn and second run.
13. Compose and `/cancel`.
14. Confirm no third run.
15. Exit.

Observed PTY result:

```text
RUN-000001 created after first non-empty /send
RUN-000002 created after second non-empty /send
RUN-000003 not created after /cancel
preview displayed complete buffer
clear emptied buffer
empty /send created no run
conversational summaries rendered
execution-plan references rendered
dashboard references rendered
Replay-visible run references rendered
session returned to AiGOL> after submissions
```

## 7. Regression Tests

Regression coverage now verifies:

- exact command input;
- pasted commands with invisible Unicode format characters;
- copied prompt-prefixed commands;
- `/preview` display;
- `/clear`;
- `/cancel`;
- empty message handling;
- repeated submissions;
- multiple consecutive conversations;
- real `main()` interactive path;
- real PTY interactive behavior;
- absence of repeated `AiGOL compose>` prompt corruption during active composition.

## 8. UX Verification

| UX Requirement | Verification |
| --- | --- |
| Prompts render correctly | `AiGOL>` appears at ready boundaries. |
| Compose mode is visually stable | Repeated `AiGOL compose>` continuation prompts are suppressed. |
| Prompt text is not inserted into user content | Buffered content remains the raw operator message. |
| `/preview` displays the buffer | Confirmed in unit and PTY regression. |
| `/send` completes flow | Confirmed in unit and PTY regression. |
| `/clear` empties buffer | Confirmed. |
| `/cancel` creates no run | Confirmed. |
| Daily use suitability | Restored. |

## 9. Responsibility Verification

| Component | Certified Responsibility | Repair Effect |
| --- | --- | --- |
| ACLI Next | UX, presentation, message composition, delegation | Prompt and command parsing repaired. |
| Platform Core | Orchestration and workflow progression | Unchanged. |
| Governance | Authorization and approval | Unchanged. |
| Replay | Evidence and reconstruction | Unchanged. |
| Worker Platform | Execution | Unchanged. |
| Platform Digital Twin | Canonical architectural evidence source | Unchanged. |
| Architectural Health | Deterministic advisory findings | Unchanged. |

No responsibility migrated between certified components.

## 10. Architectural Health Assessment

Advisory checks:

| Check | Result |
| --- | --- |
| Ownership stability | Stable. |
| Authority stability | Stable. |
| Deterministic submission | Restored. |
| Replay integrity | Preserved. |
| Conversational integrity | Restored. |
| Duplicated orchestration | None detected. |
| Worker execution before `/send` | None detected. |
| Prompt corruption | Repaired. |

Advisory finding:

```text
NO_RESPONSIBILITY_LEAKAGE_DETECTED
```

## 11. Implementation Notes

The repair intentionally avoids:

- changing Platform Core orchestration;
- changing Governance authorization;
- changing Replay ownership;
- changing Worker Platform execution;
- changing Platform Digital Twin projection semantics;
- changing Architectural Health authority;
- introducing a new command subsystem;
- introducing a new runtime authority.

The Message Composer remains a thin ACLI Next UX buffer over the certified conversational runtime.

## 12. Validation Evidence

Validation performed:

```text
real interactive PTY validation using python -m aigol.cli.aigol_cli next
git diff --check
python -m py_compile aigol/acli_next/conversational.py aigol/acli_next/__init__.py aigol/cli/aigol_cli.py tests/test_g11_acli_next_conversational_session.py
python -m pytest tests/test_g11_acli_next_conversational_session.py tests/test_g10_acli_next_daily_operational_exposure.py tests/test_g8_acli_next_execution_plan.py
```

Validation result:

```text
clean; py_compile passed; targeted pytest passed
```

Final verdict: ACLI_NEXT_INTERACTIVE_MESSAGE_COMPOSER_OPERATIONAL_BEHAVIOR_RESTORED
