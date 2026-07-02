# G12-02B ACLI Next Message Composer Operational Bugfix V1

Status: ACLI Next message composer operational bug fixed.

Final verdict: ACLI_NEXT_MESSAGE_COMPOSER_OPERATIONAL_BUG_FIXED

## 1. Executive Summary

G12-02 implemented the ACLI Next Message Composer and G12-02A confirmed its architecture.

First operational validation identified an implementation defect:

```text
visible /send input could fail to complete the governed conversational flow
```

The architecture remained valid. The defect was localized to command recognition in the ACLI Next UX layer.

G12-02B repairs command parsing so composer commands remain deterministic when pasted command lines contain invisible Unicode format characters. The submitted message content remains unchanged.

No Platform Core, Governance, Replay, Worker Platform, Platform Digital Twin, or Architectural Health responsibility moved.

## 2. Capability Discovery

Observed behavior:

- `aigol next` started correctly;
- message composition started correctly;
- `/clear` behaved correctly;
- visible `/send` did not complete the expected conversational flow in operational use;
- no conversational response, execution plan, dashboard, or Replay-visible run appeared for that submitted message;
- the REPL remained in compose mode.

Capability discovery focused on the narrow operational path:

```text
input line
-> composer command parsing
-> buffer lifecycle
-> /send branch
-> conversational adapter
-> execution-plan runtime
-> dashboard runtime
-> Replay-visible run
-> rendered response
```

## 3. Existing Capability Audit

| Capability | Audit Finding |
| --- | --- |
| Message Composer | Local buffer and command loop existed. |
| Persistent conversational REPL | Session remained active and delegated submitted prompts. |
| Conversational adapter | `run_acli_next_conversational_session(...)` completed correctly when called. |
| Execution-plan runtime | Existing runtime completed correctly after adapter delegation. |
| Dashboard runtime | Existing runtime completed correctly after adapter delegation. |
| Replay runtime | Existing per-run artifacts were created after adapter delegation. |
| Command parser | Composer command detection was exact-string based after ordinary `.strip().lower()`. |
| REPL loop | Correctly stayed active after each turn. |
| Message buffer lifecycle | Correctly cleared after successful recognized `/send`. |

Audit determination:

```text
the pipeline did not stop in Platform Core, execution-plan generation, dashboard generation, or Replay
```

The defect originated before delegation, in composer command recognition.

## 4. Reproduction Evidence

Plain PTY reproduction with exact `/send` completed successfully:

```text
one composed message
-> /preview
-> /send
-> one conversational turn
-> one execution-plan reference
-> one dashboard reference
-> one Replay-visible run
-> prompt returned to AiGOL>
```

Targeted regression reproduced the objectively supported failure class:

```text
visible command line: /send
actual command line: /send + invisible Unicode format character
```

Before repair, command recognition was too strict for this class of pasted terminal input. A visible `/send` line containing an invisible format character was treated as message content rather than a command, leaving the REPL in compose mode.

This diagnosis does not require changes to Platform Core or any certified authority boundary.

## 5. Root Cause Analysis

Root cause:

```text
composer command parsing used exact matching against stripped lowercase text
```

This was sufficient for typed ASCII commands, but brittle for pasted input from formatted sources where invisible Unicode format characters can appear in a command line.

Affected commands:

- `/send`;
- `/preview`;
- `/clear`;
- `/cancel`;
- `/help`;
- `/exit`;
- `/quit`.

Unaffected layers:

- Platform Core;
- Governance;
- Replay;
- Worker Platform;
- Platform Digital Twin;
- Architectural Health;
- execution-plan runtime;
- dashboard runtime;
- conversational adapter.

## 6. Repair Summary

Updated implementation:

| File | Repair |
| --- | --- |
| `aigol/acli_next/conversational.py` | Added deterministic composer command normalization for command detection only. |
| `tests/test_g11_acli_next_conversational_session.py` | Added regression coverage for pasted format-character commands and the real `main()` interactive CLI path. |
| `docs/governance/G12_02B_ACLI_NEXT_MESSAGE_COMPOSER_OPERATIONAL_BUGFIX_V1.md` | Added root-cause and validation evidence. |

The repair removes Unicode format characters during command detection:

```text
normalized command detection only
```

The repair does not alter the buffered message content.

## 7. Validation Scenario Coverage

Validated scenario:

1. Start `aigol next` through the persistent interactive path.
2. Compose a multi-line message.
3. Execute `/preview`.
4. Execute `/send`.
5. Verify exactly one conversational turn.
6. Verify exactly one execution-plan path.
7. Verify exactly one dashboard path.
8. Verify exactly one Replay-visible run.
9. Verify response rendering.
10. Verify the REPL returns to ready state.

Additional validation:

- `/clear` creates no turn;
- `/cancel` creates no turn;
- empty message handling creates no turn;
- repeated submissions create one run per submitted message;
- multiple consecutive conversations remain supported;
- pasted `/send` and `/preview` with invisible format characters are recognized.

## 8. Responsibility Verification

| Component | Responsibility | Repair Effect |
| --- | --- | --- |
| ACLI Next | UX, presentation, message composition, delegation | Narrow command normalization added. |
| Platform Core | Orchestration and workflow progression | Unchanged. |
| Governance | Authorization and approval | Unchanged. |
| Replay | Evidence and reconstruction | Unchanged. |
| Worker Platform | Execution | Unchanged. |
| Platform Digital Twin | Canonical architectural evidence source | Unchanged. |
| Architectural Health | Deterministic advisory findings | Unchanged. |

No responsibility migrated between certified components.

## 9. Architectural Health Assessment

Advisory checks:

| Check | Result |
| --- | --- |
| Ownership stability | Stable. |
| Authority stability | Stable. |
| Deterministic submission | Improved. |
| Replay integrity | Preserved. |
| Conversational integrity | Improved. |
| Duplicated orchestration | None detected. |
| Worker execution before `/send` | None detected. |

Advisory finding:

```text
NO_RESPONSIBILITY_LEAKAGE_DETECTED
```

## 10. Implementation Notes

The repair intentionally avoids:

- adding new composer authority;
- creating a new command subsystem;
- changing Platform Core orchestration;
- changing Governance authorization;
- changing Replay ownership;
- changing Worker Platform execution;
- changing dashboard or execution-plan semantics.

The Message Composer remains a thin ACLI Next UX buffer over the certified conversational runtime.

## 11. Validation Evidence

Validation performed:

```text
git diff --check
python -m py_compile aigol/acli_next/conversational.py aigol/acli_next/__init__.py aigol/cli/aigol_cli.py tests/test_g11_acli_next_conversational_session.py
python -m pytest tests/test_g11_acli_next_conversational_session.py tests/test_g10_acli_next_daily_operational_exposure.py tests/test_g8_acli_next_execution_plan.py
```

Validation result:

```text
clean; py_compile passed; targeted pytest passed
```

Final verdict: ACLI_NEXT_MESSAGE_COMPOSER_OPERATIONAL_BUG_FIXED
