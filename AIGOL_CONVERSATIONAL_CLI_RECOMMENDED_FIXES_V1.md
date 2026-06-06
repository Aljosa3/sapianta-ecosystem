# AIGOL_CONVERSATIONAL_CLI_RECOMMENDED_FIXES_V1

Recommendations only. No code changes were made; this document describes the
remediation shape and trade-offs for each finding in
[AIGOL_CONVERSATIONAL_CLI_ROOT_CAUSE_ANALYSIS_V1.md](AIGOL_CONVERSATIONAL_CLI_ROOT_CAUSE_ANALYSIS_V1.md).

## R-1 — Make multi-line prompt input first-class

Targets: **F-1**.

Two complementary mechanisms:

1. **Heredoc-style terminator inside the loop.** Treat a sentinel such as
   `"."` on its own line (operator-configurable, e.g. `--multiline-end`)
   as "end of prompt". Read lines into a buffer and submit the buffer as
   a single turn. Keep the current single-line behavior when the operator
   types one line followed by Enter.
2. **`--prompt-file PATH` and `-` (stdin)** for `aigol conversation`.
   Allow operators to pipe a multi-line block: `aigol conversation - < prompt.txt`
   which reads all of stdin as one prompt. This is also how the existing
   `aigol conversational route --prompt …` subcommand should be invoked
   from scripts.
3. Document the chosen mechanism in the prompt banner shown above each
   `AiGOL > ` (e.g., `Multi-line: end with a single '.'`).

Trade-off: the heredoc sentinel changes the operator UX; the file/stdin
mode is purely additive and preserves existing tests.

## R-2 — Replace the predicate cascade with a single deterministic classifier

Targets: **F-2**, **F-9**.

Build a unified `classify_conversational_intent(human_prompt) -> Intent`
that returns:

- `intent_id`
- `confidence` (e.g., `HIGH` / `MEDIUM` / `LOW`)
- `matched_terms`
- `competing_intents` (other intents that also matched)
- `routing_destination`

The CLI then dispatches off `intent_id` rather than a sequence of `elif`
predicates. The classifier should:

- Tie-break by explicit priority list, not source-order accident.
- Emit a replay-visible `intent_classification_artifact` for every turn
  so operators can audit *why* a prompt routed where it did.
- Provide a low-confidence "ambiguous" terminal state that routes to
  a single, deterministic clarification path (see R-7) instead of
  failing closed.

This makes routing diagnosable from the CLI itself ("matched OCS_LLM_COGNITION
because 'commercialization'; competing: OPERATOR_DECISION_SUPPORT
because 'prioritize'"). It also collapses ~5 marker functions into one
audited module.

## R-3 — Project provider identity into every turn summary

Targets: **F-3**.

Inside each `_interactive_*_turn_summary` builder, set:

- `provider_ids`: list of providers the runtime actually invoked
  (read from the underlying capture; for the default conversation branch
  that is `[OPENAI_PROVIDER_ID]`; for the read-only audit/improve branches
  it is `[]` *and* the rendering should say so explicitly, e.g.
  `providers: NONE_REQUIRED` to distinguish from "forgot to wire it").
- `provider_invoked`: true/false matching reality.

Adjust `render_conversational_turn_completion_summary` to render `NONE`
only when the branch is genuinely provider-less and `NONE_REQUIRED` or
`UNAVAILABLE` otherwise, so operators can distinguish "no providers" from
"providers attempted but failed".

## R-4 — Measure real elapsed time

Targets: **F-4**, **F-10**.

- Capture `t0 = time.monotonic()` at the top of the per-turn `try:` block.
- Capture `t1 = time.monotonic()` immediately before
  `_record_interactive_turn_completion` and pass
  `elapsed_seconds = int(round(t1 - t0))`.
- Replace `_interactive_turn_elapsed_seconds`'s fallback to `stage_count`
  with the measured value. Preserve `stage_count` as a separate
  `stage_count` field if the artifact consumers need it.
- Stop using `args.created_at` as the per-snapshot timestamp. Generate
  per-turn ISO timestamps via `datetime.now(timezone.utc).isoformat()` and
  thread them through `started_at` / `snapshot_at` / `delivered_at`.

Replay invariance can be preserved by allowing tests to inject a
`clock_func` parameter (defaulting to `time.monotonic` and
`datetime.now`), matching the existing `input_func` / `output_func`
hooks.

## R-5 — Record `result_delivered` after the terminal flush

Targets: **F-5**.

Re-order the completion block ([aigol/cli/aigol_cli.py:2314-2335](aigol/cli/aigol_cli.py#L2314-L2335)) so that:

1. The buffered text is flushed to `terminal_output_writer` first.
2. Only after the flush returns is `record_conversational_result_delivered`
   called with the actually-delivered line count (recomputed including the
   completion summary).
3. The completion summary itself is written to the terminal after the
   delivered artifact is persisted, with the artifact ID/hash visible to
   the operator.

If a hard atomic guarantee is required, write the `result_delivered`
artifact only after `terminal_output_writer` succeeds (catching exceptions
from `print()`), and record a `FAILED_CLOSED` delivery if the flush
raised.

## R-6 — Replace placeholder progress stages with real telemetry

Targets: **F-6**.

- Emit checkpoints **only when the corresponding stage actually runs**.
  Move the cognition/provider/comparison/continuity/clarification
  checkpoints inside the OCS branch instead of the unconditional
  `_emit_interactive_conversation_cognition_progress` helper.
- Compute `snapshot_at` per-emit using the real clock (R-4).
- Drop the constant `_duration_history` and either omit duration history
  or read it from the runtime's actual prior runs.

The stage model can remain canonical for replay determinism, but the
recorded data must reflect what really happened.

## R-7 — Broaden (or simplify) the provider-unavailable fallback

Targets: **F-7**, **F-8**.

Two paths, pick one:

1. **Deterministic offline fallback.** When `AIGOL_OPENAI_API_KEY` is
   unset, route the default-conversation branch through the same
   in-process transport the OCS branch uses (or an explicit "offline
   self-resolution" provider) and return a clearly-labeled
   `OFFLINE_DETERMINISTIC_RESPONSE` rather than fail closed. The CLI
   then degrades gracefully without network access.
2. **Generic clarification fallback.** Replace `_classify_ambiguity`'s
   hard-coded phrase table with a single canonical clarification that
   always asks the operator to choose between:
   - Refine intent (re-route through a specific subcommand).
   - Provide more context.
   - Abort.

Either approach removes the "prompt is not clarification-eligible"
dead-end the operator hit.

## R-8 — Surface routing decisions to the operator

Targets: **F-2**, **F-9**.

Add a one-line operator-visible routing summary at the start of each turn:

```
ROUTED → OCS_LLM_COGNITION (confidence=MEDIUM)
  matched: "commercialization", "what should"
  competing: OPERATOR_DECISION_SUPPORT (matched: "prioritize")
```

This makes the deterministic-but-fragile routing immediately diagnosable
without reading replay artifacts. It also lets operators self-correct
("oh, it routed to OCS; I'll rephrase to hit decision-support").

## R-9 — Add CLI-level smoke tests against the Case B input

Targets: regression prevention.

Add a test that feeds the exact Case B paste (as a single multi-line
string, with R-1's heredoc terminator) and asserts:

- Exactly one turn is created.
- `providers` is populated (not `NONE`).
- `elapsed_seconds` is `> 0` when the test clock is advanced.
- `result_delivered` becomes `TRUE` only after the simulated
  `terminal_output_writer` is observed to have been called.

This would have caught all six VISIBILITY_BUG/IMPLEMENTATION_BUG findings
in this audit.

## R-10 — Document operator expectations explicitly

Targets: human reliability.

Update [AIGOL_CLI_FOUNDATION_V1.md](AIGOL_CLI_FOUNDATION_V1.md) (or add a
companion `AIGOL_CLI_OPERATOR_GUIDE_V1.md`) describing:

- Supported prompt families (with examples that match each predicate).
- Multi-line input mechanism (R-1).
- What `providers: NONE` vs `NONE_REQUIRED` means (R-3).
- That `elapsed` reflects wall-clock and `created_at` reflects real time
  (R-4).
- That the CLI requires a configured `AIGOL_OPENAI_API_KEY` unless the
  offline fallback is enabled (R-7).

Operators using the CLI today have no documented contract for any of
these behaviors.

## Priority order

| Priority | Recommendations | Rationale |
|---|---|---|
| P0 | R-1, R-7, R-8 | Restores basic operator usability; the CLI is unusable for typical pasted prompts and silently fails closed without an API key. |
| P1 | R-4, R-5 | The most-confusing artifact fields are misleading; replay-based diagnosis is impossible until these are real. |
| P1 | R-3 | Provider visibility is a one-line projection fix per branch. |
| P2 | R-2, R-6, R-9 | Architectural cleanup; requires refactor but unlocks reliable evolution. |
| P3 | R-10 | Documentation; cheap once behavior is correct. |

## What this audit deliberately does NOT recommend

- Removing the OCS-cognition deterministic transport
  ([aigol/cli/aigol_cli.py:439-494](aigol/cli/aigol_cli.py#L439-L494)).
  It is the only branch that demonstrably works end-to-end today and
  should be preserved as the canonical happy path while the other
  branches are stabilized.
- Changing the `TURN_COMPLETED_ARTIFACT_V1` schema. Adding measured
  values into the existing schema fields is sufficient; no new artifact
  type is required.
- Removing the `args.created_at` argument. Tests rely on it for
  deterministic replay. Recommend defaulting to a real timestamp when
  the user does not pass `--created-at` and preserving the explicit
  override for tests.
