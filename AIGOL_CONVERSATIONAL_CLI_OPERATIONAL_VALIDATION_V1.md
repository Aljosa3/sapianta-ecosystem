# AIGOL_CONVERSATIONAL_CLI_OPERATIONAL_VALIDATION_V1

Operational validation review of the AiGOL conversational CLI (`aigol conversation`) against
the operator-observed behaviors described in
`AIGOL_CONVERSATIONAL_CLI_OPERATIONAL_VALIDATION_V1` request.

This is a **review-only audit**. No code was modified.

## Scope

Validate whether the `aigol conversation` interactive turn lifecycle:

1. Accepts multi-line operator input as a single conversational turn.
2. Routes prompts deterministically to the certified workflow.
3. Emits accurate provider visibility.
4. Reports a wall-clock-accurate `elapsed` value.
5. Emits `TURN COMPLETED` only after the operator-facing result is actually delivered.
6. Surfaces lifecycle progress that reflects real execution, not deterministic
   placeholders.
7. Can be considered operationally reliable for normal human usage.

## Inputs reviewed

- [aigol/cli/aigol_cli.py](aigol/cli/aigol_cli.py) — `run_interactive_conversation` (entry loop, routing chain, completion record).
- [aigol/runtime/conversational_cli_runtime.py](aigol/runtime/conversational_cli_runtime.py) — workflow classification (`_classify_workflow`, `_is_ocs_llm_cognition_prompt`).
- [aigol/runtime/conversational_progress_binding_runtime.py](aigol/runtime/conversational_progress_binding_runtime.py) — stage model, deterministic `_duration_history`.
- [aigol/runtime/conversational_turn_completion_runtime.py](aigol/runtime/conversational_turn_completion_runtime.py) — `TURN COMPLETED` rendering, providers/elapsed fields.
- [aigol/runtime/conversation_provider_unavailable_clarification_fallback.py](aigol/runtime/conversation_provider_unavailable_clarification_fallback.py) — fallback eligibility (`_classify_ambiguity`).
- [aigol/runtime/prompt_to_conversation_integration.py](aigol/runtime/prompt_to_conversation_integration.py) — default conversation path.
- [aigol/runtime/conversation_native_development_intent_routing.py](aigol/runtime/conversation_native_development_intent_routing.py) — `_classify_intent` catalog.
- [aigol/runtime/unknown_domain_clarification_runtime.py](aigol/runtime/unknown_domain_clarification_runtime.py) — `_analyze_prompt`.
- [aigol/runtime/runtime_progress_visibility.py](aigol/runtime/runtime_progress_visibility.py) — snapshot `elapsed_seconds` computation.

## Validation matrix

| # | Operator-observed claim | Behavior verified in code | Verdict |
|---|---|---|---|
| 1 | Multi-line pasted prompt is split into separate turns | [aigol/cli/aigol_cli.py:1179](aigol/cli/aigol_cli.py#L1179) `raw_prompt = input_reader("AiGOL > ")` is a single `input()` call. No multi-line aggregation, no terminator, no EOF/sentinel. Blank lines are silently dropped at [aigol/cli/aigol_cli.py:1184-1186](aigol/cli/aigol_cli.py#L1184-L1186). | **CONFIRMED** — each line submitted as its own turn. |
| 2 | Provider visibility differs across turns (`providers: NONE` vs the two cognition providers) | `_interactive_turn_providers` ([aigol/cli/aigol_cli.py:631-640](aigol/cli/aigol_cli.py#L631-L640)) returns providers only if the turn summary populates `provider_ids`. Only the OCS LLM cognition branch sets this ([aigol/cli/aigol_cli.py:2860](aigol/cli/aigol_cli.py#L2860)). Every other branch (read-only, recommendation, default conversation, native-development) returns `[]`, which `render_conversational_turn_completion_summary` renders as `NONE` ([aigol/runtime/conversational_turn_completion_runtime.py:218](aigol/runtime/conversational_turn_completion_runtime.py#L218)). | **CONFIRMED** — `providers: NONE` is not "no providers used", it is "this branch never wired its provider list into the completion artifact". |
| 3 | Some prompts run OCS cognition, others land in clarification fallback failure | Routing is an ordered cascade of independent string predicates at [aigol/cli/aigol_cli.py:1234-2250](aigol/cli/aigol_cli.py#L1234-L2250). The OCS branch fires only when `is_ocs_llm_cognition_prompt` matches the narrow marker set in [aigol/runtime/conversational_cli_runtime.py:282-308](aigol/runtime/conversational_cli_runtime.py#L282-L308). All other unmatched prompts fall to the default `submit_prompt_to_conversation` branch ([aigol/cli/aigol_cli.py:2250-2298](aigol/cli/aigol_cli.py#L2250-L2298)), which requires a live provider and on failure escalates to `run_conversation_provider_unavailable_clarification_fallback` whose `_classify_ambiguity` only recognizes the literal phrases "workstation"/"improve trading"/"add analysis"/"create reporting" ([aigol/runtime/conversation_provider_unavailable_clarification_fallback.py:165-231](aigol/runtime/conversation_provider_unavailable_clarification_fallback.py#L165-L231)). | **CONFIRMED** — routing is deterministic but fragile, and the fallback path is intentionally narrow. |
| 4 | `elapsed: 8s` is shown even when wall clock was much longer | `_interactive_turn_elapsed_seconds` ([aigol/cli/aigol_cli.py:624-628](aigol/cli/aigol_cli.py#L624-L628)) returns `progress_binding_artifact["stage_count"]` (a constant `len(CONVERSATIONAL_PROGRESS_STAGE_MODEL) == 8` per [aigol/runtime/conversational_progress_binding_runtime.py:35-44](aigol/runtime/conversational_progress_binding_runtime.py#L35-L44)). No wall-clock difference is ever measured. | **CONFIRMED** — `elapsed` is a hardcoded stage count, not real elapsed time. |
| 5 | `TURN COMPLETED` is supposed to follow operator-visible result delivery | `_record_interactive_turn_completion` ([aigol/cli/aigol_cli.py:586-621](aigol/cli/aigol_cli.py#L586-L621)) records `turn_completed` then `result_delivered` BEFORE the operator-facing text is flushed (the appended `operator_completion_summary` is added to the buffer at line 2330, then printed at line 2332). The `result_delivered_artifact` therefore claims delivery while delivery is still pending. The line counter passes the progress + normal output but does not include the completion summary itself. | **CONFIRMED** — `result_delivered: TRUE` is a lifecycle assertion, not an attestation of delivery. |
| 6 | Conversational progress visibility represents real execution | All progress checkpoints are emitted with `snapshot_at=created_at` (a CLI-supplied constant, default `2026-06-01T00:00:00Z`), and `_duration_history` returns a per-stage `last_duration_seconds=1` regardless of work ([aigol/runtime/conversational_progress_binding_runtime.py:204-216](aigol/runtime/conversational_progress_binding_runtime.py#L204-L216)). `record_runtime_progress_snapshot` consequently computes `elapsed_seconds = int((snapshot - started).total_seconds()) == 0`. | **CONFIRMED** — progress checkpoints are deterministic placeholders, not execution telemetry. |
| 7 | CLI is operationally reliable for normal human usage | Multi-line input is broken; routing depends on string markers without ambiguity scoring; provider visibility, elapsed time, and turn-completion semantics are decorative; clarification fallback covers ~four hard-coded phrases. | **NOT OPERATIONALLY RELIABLE** for unconstrained human usage. |

## Summary

Six of the seven validation claims surface a defect:

- One **IMPLEMENTATION_BUG** in stdin handling (no multi-line aggregation).
- Two **VISIBILITY_BUG**s (elapsed time and progress checkpoint timestamps are
  hardcoded; the completion artifact reports `result_delivered=TRUE` before the
  result text is flushed).
- One **ROUTING_BUG** (multi-class predicates evaluated in a hand-rolled order
  without ambiguity scoring; failure path narrows to a hard-coded phrase list).
- One **USABILITY_BUG** (`providers: NONE` is the default for almost every
  branch because the turn summary does not project provider identity into the
  completion artifact).
- One **USABILITY_BUG** (clarification fallback only handles four literal
  phrases).

No FALSE_POSITIVE was identified — every operator-observed symptom maps to a
concrete code-path defect.

Detailed traces are in [AIGOL_CONVERSATIONAL_CLI_OPERATIONAL_TRACE_ANALYSIS_V1.md](AIGOL_CONVERSATIONAL_CLI_OPERATIONAL_TRACE_ANALYSIS_V1.md);
root-cause analysis in [AIGOL_CONVERSATIONAL_CLI_ROOT_CAUSE_ANALYSIS_V1.md](AIGOL_CONVERSATIONAL_CLI_ROOT_CAUSE_ANALYSIS_V1.md);
recommended fix shape in [AIGOL_CONVERSATIONAL_CLI_RECOMMENDED_FIXES_V1.md](AIGOL_CONVERSATIONAL_CLI_RECOMMENDED_FIXES_V1.md);
machine-readable record in [AIGOL_CONVERSATIONAL_CLI_OPERATIONAL_VALIDATION_CERTIFICATION.json](AIGOL_CONVERSATIONAL_CLI_OPERATIONAL_VALIDATION_CERTIFICATION.json).
