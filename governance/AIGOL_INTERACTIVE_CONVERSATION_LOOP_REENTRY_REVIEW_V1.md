# AIGOL_INTERACTIVE_CONVERSATION_LOOP_REENTRY_REVIEW_V1

## Status

Review-only loop reentry trace.

No runtime was changed. No CLI behavior was changed. No provider behavior was changed. No OCS cognition behavior was changed.

## Executive Finding

After `AIGOL OCS LLM COGNITION END-TO-END` returns `status: COMPLETED`, the interactive `aigol conversation` command re-enters the prompt loop by design.

The owning runtime is:

```text
aigol/cli/aigol_cli.py::run_interactive_conversation
```

There is no explicit `TURN_COMPLETED` or `RESULT_DELIVERED` transition that terminates the command or pauses reentry after a successful turn. A completed turn is implicit in:

- appending the turn summary to `turns`;
- emitting `Result Assembly`;
- emitting `Replay` with completed progress status;
- returning to the top of the `while True` loop.

Therefore repeated `AiGOL >` prompts after a successful cognition result are expected REPL behavior unless the operator enters `exit`, `quit`, or sends EOF.

## Root Cause

The immediate reentry is caused by the interactive loop structure:

```text
while True:
    raw_prompt = input_reader("AiGOL > ")
    ...
```

After each turn, including a successful OCS cognition turn, control reaches the end of the `try` block and naturally loops back to `input_reader("AiGOL > ")`.

The repeated fail-closed cycles are caused by subsequent non-empty input lines being processed as new turns. If those lines do not match explicit conversational routes, they fall into the legacy default path:

```text
submit_prompt_to_conversation(...)
-> provider-unavailable clarification fallback
-> prompt is not clarification-eligible
```

## Conversation Loop Trace

### Successful Turn

| Step | Function | Input | Output | Decision |
| --- | --- | --- | --- | --- |
| 1 | `run_interactive_conversation` | `I want to create the first real AiGOL product.` | `TURN-000001` | Process turn |
| 2 | source router | human prompt | source router artifacts | Source selected |
| 3 | OCS cognition branch | broad cognition prompt | `OCS_LLM_COGNITION_END_TO_END` capture | Completed |
| 4 | result rendering | cognition capture | human-facing end-to-end summary | Delivered to output buffer |
| 5 | progress runtime | turn state | `[7/8] Result Assembly`, `[8/8] Replay` | Completed visibility |
| 6 | output assembly | progress + result buffer | terminal output | Printed |
| 7 | loop tail | no explicit break | returns to `while True` | Reentry |

### Reentry

| Step | Function | Input | Output | Decision |
| --- | --- | --- | --- | --- |
| 1 | `input_reader("AiGOL > ")` | blank line | no turn | `continue` |
| 2 | `input_reader("AiGOL > ")` | blank line | no turn | `continue` |
| 3 | `input_reader("AiGOL > ")` | non-empty unmatched line | `TURN-000002` | Process new turn |
| 4 | default branch | unmatched prompt | provider-assisted conversation failure | fail closed |
| 5 | fallback branch | failed capture | fallback artifact | not clarification-eligible |

## Turn Lifecycle Trace

The implemented lifecycle is:

```text
PROMPT_READ
-> PROMPT_NORMALIZED
-> TURN_ALLOCATED
-> ROUTED
-> BRANCH_EXECUTED
-> RESULT_ASSEMBLED
-> REPLAY_PROGRESS_RECORDED
-> LOOP_REENTRY
```

The lifecycle does not contain explicit persisted states named:

- `TURN_COMPLETED`;
- `RESULT_DELIVERED`.

The closest current substitute is the conversational progress `Replay` snapshot with completed status.

## Result Delivery Trace

For successful OCS cognition:

- the OCS branch calls `render_ocs_llm_cognition_end_to_end_summary(...)`;
- the rendered text is appended to `turn_output_buffer`;
- after branch execution, the CLI appends result assembly and replay progress lines;
- the terminal writer prints progress lines plus non-failure output once;
- the loop then reads the next prompt.

The result is not returned more than once in the reviewed code path.

## Terminal Output Trace

Controlled local trace used this input sequence:

```text
I want to create the first real AiGOL product.


nonsense followup
exit
```

Observed trace:

```text
prompts_displayed: 5
turn_count: 2
failed_turns: 1
turn 1: COMPLETED, OCS_LLM_COGNITION_END_TO_END
turn 2: FAILED_CLOSED, DETERMINISTIC_CLARIFICATION_FALLBACK
```

Interpretation:

- the first prompt completed OCS cognition;
- the two blank lines displayed two extra `AiGOL > ` prompts but did not create turns;
- the non-empty `nonsense followup` was processed as a second turn and failed through the legacy fallback path.

## Review Question Answers

1. After `status: COMPLETED`, the turn is appended, result output is assembled, progress replay is recorded, and the loop returns to `input_reader("AiGOL > ")`.

2. The conversation loop re-enters routing because `run_interactive_conversation` is a REPL loop and has no break after a successful turn.

3. `AiGOL > AiGOL >` appears repeatedly when the loop reads blank lines or buffered input and immediately prompts again. Blank lines are stripped and skipped without output.

4. Empty prompts are not processed. They hit `if not human_prompt: continue` before `turn_count` increments.

5. Stdin buffering can be involved. Pasted trailing newlines, terminal sends, or scripted input can produce repeated prompts. Buffered non-empty lines after success become new turns.

6. The result is not returned more than once by the reviewed code path. A valid cognition result may appear once for each successful cognition prompt.

7. The loop is not failing to terminate a completed turn; it has no design intent to terminate the interactive session after a turn. It terminates only on `exit`, `quit`, or EOF.

8. Valid cognition output can appear after several fail-closed cycles if a valid broad cognition prompt appears later in the input stream after earlier non-empty lines failed. It can also appear visually delayed if terminal IO interleaves prompts and buffered output.

9. `aigol/cli/aigol_cli.py::run_interactive_conversation` owns turn completion. The OCS cognition runtime owns only the end-to-end cognition capture for that branch.

10. There is no explicit `TURN_COMPLETED` transition. Completion is implicit in the turn summary and completed progress snapshot.

11. There is no explicit `RESULT_DELIVERED` transition. Delivery is implicit in `terminal_output_writer(...)`.

12. The bug or gap is located in the interactive conversation loop and output lifecycle semantics in `aigol_cli.py`, not in the OCS cognition runtime and not in the clarification fallback path. The fallback path is only the downstream symptom for later non-empty unmatched turns.

## Affected File And Function

Exact file:

```text
aigol/cli/aigol_cli.py
```

Exact function:

```text
run_interactive_conversation(...)
```

Relevant code regions:

- lines 1106-1117: prompt read, blank prompt skip, exit handling;
- lines 2148-2178: OCS cognition branch completion;
- lines 2179-2217: legacy default branch and fallback;
- lines 2228-2248: result assembly, replay progress, output writing;
- lines 2280-2312: final command result after loop termination.

## Minimal Fix Scope

No cognition runtime fix is indicated.

Minimal future fix scope:

1. Add explicit turn lifecycle states:
   - `TURN_COMPLETED`;
   - `RESULT_DELIVERED`.
2. Persist a turn-completion artifact or extend the progress binding with result-delivery state.
3. Add an operator-visible separator before re-prompting after completed results.
4. Optionally add a one-shot conversational mode that exits after one completed turn.
5. Keep the REPL behavior for interactive mode, but make reentry visibly intentional.
6. Keep empty prompts ignored and non-empty prompts processed as new turns.

## Classification

`AIGOL_INTERACTIVE_CONVERSATION_LOOP_REENTRY_REVIEW_V1`

## Conclusion

The OCS cognition result completes successfully. The repeated prompt display is caused by normal interactive loop reentry. Empty prompts are not processed, but buffered non-empty input after a successful result is processed as additional turns and may fail through the legacy fallback path.

The missing architecture is not another cognition binding. It is an explicit result-delivery and turn-completion boundary in the interactive conversation loop.
