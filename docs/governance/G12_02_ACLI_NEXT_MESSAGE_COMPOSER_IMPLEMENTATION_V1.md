# G12-02 ACLI Next Message Composer Implementation V1

Status: ACLI Next message composer implemented.

Final verdict: ACLI_NEXT_MESSAGE_COMPOSER_IMPLEMENTED

## 1. Executive Summary

G12-01 specified a message composition layer for `aigol next`.

The operational gap was:

```text
one logical multi-line human message
-> many independent conversational turns
```

G12-02 implements a bounded ACLI Next message composer so the human can compose multiple lines and submit the complete message with:

```text
/send
```

Only the submitted complete message enters the existing governed conversational pipeline.

The implementation is a UX layer only. It does not redesign Platform Core, Governance, Replay, Worker Platform, Platform Digital Twin, Architectural Health, or the certified conversational adapter.

## 2. Mandatory Capability Audit

Before implementation, the required capabilities were reviewed.

| Required Capability | Existing Certified Capability | Reuse Decision |
| --- | --- | --- |
| ACLI Next conversational runtime | `run_acli_next_conversational_session(...)` | Reused as the only submit path. |
| Persistent conversational session | `run_acli_next_persistent_conversational_session(...)` | Extended with a local in-memory composer buffer. |
| Conversational adapter | Existing single-turn adapter | Reused without duplicating turn execution logic. |
| Execution-plan runtime | `run_acli_next_interactive_with_execution_plan(...)` | Reused after `/send`. |
| Dashboard runtime | `run_acli_next_daily_dashboard(...)` | Reused after `/send`. |
| Replay runtime | Existing replay-visible per-run artifacts | Reused; no per-line Replay writes are introduced. |
| Platform Core orchestration | Existing Platform Core-facing execution-plan and dashboard flow | Preserved. |
| Governance | Existing approval and authorization presentation | Preserved; no composer approval logic added. |
| Worker Platform | Certified Worker execution boundary | Preserved; no Worker execution before `/send`. |
| Platform Digital Twin | Canonical architectural evidence source | Preserved. |
| Architectural Health | Deterministic advisory-only presentation | Preserved. |

Audit finding:

```text
the missing capability was only local pre-turn message buffering
```

## 3. Implementation Summary

Updated files:

| File | Change |
| --- | --- |
| `aigol/acli_next/conversational.py` | Added G12 message composer constants, in-memory composition buffer, `/send`, `/preview`, `/clear`, `/cancel`, `/help`, and composer completion metadata. |
| `aigol/acli_next/__init__.py` | Exported `ACLI_NEXT_MESSAGE_COMPOSER_VERSION`. |
| `tests/test_g11_acli_next_conversational_session.py` | Updated persistent REPL coverage and added message composer tests. |

Created artifact:

| File | Purpose |
| --- | --- |
| `docs/governance/G12_02_ACLI_NEXT_MESSAGE_COMPOSER_IMPLEMENTATION_V1.md` | Implementation evidence and certification record. |

## 4. Composer Behavior

The persistent REPL now starts with:

```text
AiGOL conversational session started. Compose a message, then type /send.
```

The composer supports:

| Command | Behavior |
| --- | --- |
| `/send` | Submits the current non-empty buffer as one governed conversational turn and clears the buffer after successful submission. |
| `/preview` | Displays the current buffer without creating a turn or executing anything. |
| `/clear` | Empties the current buffer and preserves the session. |
| `/cancel` | Discards the current message and preserves the session. |
| `/help` | Displays composer command guidance. |

Blank lines are preserved inside an active buffer.

Exit commands close the session only when the buffer is empty. If the buffer is non-empty, ACLI Next asks the human to use `/send`, `/clear`, or `/cancel` before exiting.

## 5. Replay Behavior

The implemented behavior is:

```text
multiple composed lines
-> /send
-> one complete prompt string
-> one conversational turn
-> one execution plan
-> one dashboard update
-> one Replay-visible run
```

No governed conversational turn is created while the message is being composed.

No run directory is created for `/preview`, `/clear`, `/cancel`, empty `/send`, or ordinary buffered lines.

The persistent session completion artifact records composer summary metadata:

```text
message_composer_enabled: true
submitted_message_count
preview_count
clear_count
cancel_count
empty_send_count
composer_creates_turn_before_send: false
composer_creates_replay_before_send: false
one_submitted_message_per_turn: true
```

This metadata is ACLI Next presentation evidence only. It is not Governance approval, execution evidence, architectural certification, or Replay ownership.

## 6. Platform Core Interaction

Platform Core continues to receive exactly one completed conversational request per `/send`.

The composer does not:

- inspect Platform Core workflow state;
- modify Platform Core workflow state;
- decide workflow progression;
- execute Platform Core operations;
- create a new orchestration engine.

The existing conversational adapter remains the delegation boundary.

## 7. Governance, Worker Platform and Replay Boundaries

Governance remains responsible only for:

- approvals;
- authorization;
- governance decisions.

Worker Platform remains responsible only for:

- bounded authorized execution.

Replay remains responsible only for:

- evidence;
- reconstruction;
- execution history.

The composer does not move any of these responsibilities into ACLI Next.

## 8. Architectural Health Review

Architectural Health advisory review was performed against the implementation scope.

Advisory inputs:

- message composition is local to ACLI Next;
- `/send` delegates to the certified conversational adapter;
- `/preview`, `/clear`, and `/cancel` do not create conversational turns;
- no Governance logic was added;
- no Worker execution path was added;
- no Platform Core orchestration was duplicated;
- Replay-visible run creation remains after submission only.

Advisory finding:

```text
NO_RESPONSIBILITY_LEAKAGE_DETECTED
```

Mandatory advisory note:

```text
future composer commands must remain presentation-only unless separately specified and certified
```

## 9. Responsibility Verification

| Component | Certified Responsibility | G12-02 Result |
| --- | --- | --- |
| ACLI Next | Human interaction, presentation, guidance, delegation | Adds only local message buffering and composer commands. |
| Platform Core | Workflow orchestration and operational state | Preserved; receives submitted complete messages only. |
| Governance | Authorization and approval | Preserved; no composer authority added. |
| Replay | Evidence and reconstruction | Preserved; composer does not own Replay. |
| Worker Platform | Execution | Preserved; no Worker execution before `/send`. |
| Platform Digital Twin | Canonical architectural evidence source | Preserved. |
| Architectural Health | Advisory-only findings | Preserved. |

Responsibility finding:

```text
no responsibility migration occurred
```

## 10. Targeted Tests

Targeted test coverage verifies:

- existing single-turn conversational composition still works;
- persistent REPL submits only after `/send`;
- multi-line composition creates one turn and one run;
- `/preview` creates no turn;
- `/clear` creates no turn;
- `/cancel` creates no turn;
- composer metadata is recorded in the persistent session completion artifact.

## 11. Validation Evidence

Validation performed:

```text
git diff --check
python -m py_compile aigol/acli_next/conversational.py aigol/acli_next/__init__.py tests/test_g11_acli_next_conversational_session.py
python -m pytest tests/test_g11_acli_next_conversational_session.py
```

Validation result:

```text
clean; py_compile passed; targeted pytest passed
```

Final verdict: ACLI_NEXT_MESSAGE_COMPOSER_IMPLEMENTED
