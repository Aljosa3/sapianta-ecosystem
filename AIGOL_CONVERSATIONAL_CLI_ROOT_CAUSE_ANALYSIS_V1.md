# AIGOL_CONVERSATIONAL_CLI_ROOT_CAUSE_ANALYSIS_V1

Findings indexed against the operator request's "REQUIRED DELIVERABLES /
SUCCESS CRITERIA" section. Each finding lists exact file, function, branch,
and root cause. Review-only; no code modified.

## F-1 — Multi-line prompts are fragmented into separate turns

- **Classification:** IMPLEMENTATION_BUG
- **File:** [aigol/cli/aigol_cli.py](aigol/cli/aigol_cli.py)
- **Function:** `run_interactive_conversation`
- **Branch:** main `while True` loop body, `input_reader("AiGOL > ")` call.
- **Lines:** [1177-1188](aigol/cli/aigol_cli.py#L1177-L1188)
- **Root cause:** The CLI uses a single `input()` per turn. There is no
  bracketed-paste handling, no continuation character, no blank-line/EOF
  sentinel, no `--prompt-file`/`-` stdin redirect, and no operator command
  to mark the end of a multi-line block. Blank lines are explicitly
  discarded by the loop. Multi-line input is structurally impossible on the
  current entry point.
- **Operational impact:** Every newline in a paste creates an independent
  turn; routing, OCS cognition, providers, and clarification fallback are
  applied per fragment, producing the Case B output the operator observed.

## F-2 — Routing is a manually ordered cascade of fragile string predicates

- **Classification:** ROUTING_BUG
- **File:** [aigol/cli/aigol_cli.py](aigol/cli/aigol_cli.py), [aigol/runtime/conversational_cli_runtime.py](aigol/runtime/conversational_cli_runtime.py)
- **Function:** `run_interactive_conversation` dispatch chain →
  `is_ocs_llm_cognition_prompt`, `_is_operator_decision_support_prompt`,
  `_is_domain_adaptation_reference_prompt`, `is_native_development_prompt`,
  `is_unknown_domain_clarification_eligible`,
  `_is_conversational_cli_readonly_candidate`.
- **Branch:** [aigol/cli/aigol_cli.py:1234-2250](aigol/cli/aigol_cli.py#L1234-L2250) — successive `elif`
  chain.
- **Root cause:** No unified intent classifier. Each predicate is a separate
  case-insensitive substring search with its own marker set:
  - `_is_ocs_llm_cognition_prompt` ([aigol/runtime/conversational_cli_runtime.py:282-308](aigol/runtime/conversational_cli_runtime.py#L282-L308))
    looks for `"first real aigol product"`, `"commercialization"`,
    `"should sapianta"`, etc.
  - `_is_operator_decision_support_prompt` ([aigol/runtime/conversational_cli_runtime.py:256-269](aigol/runtime/conversational_cli_runtime.py#L256-L269))
    requires `"first real"` + (`"product domain"` or `"aigol product domain"`).
  - `is_conversation_native_development_intent` ([aigol/runtime/conversation_native_development_intent_routing.py:214-242](aigol/runtime/conversation_native_development_intent_routing.py#L214-L242))
    needs ALL of a catalog's required terms.
  - `is_unknown_domain_clarification_eligible` ([aigol/runtime/unknown_domain_clarification_runtime.py:204-226](aigol/runtime/unknown_domain_clarification_runtime.py#L204-L226))
    fires only on `"compliance"`/`"regulatory"` + `"domain"`.

  Routing is therefore deterministic but extremely phrasing-sensitive:
  swapping "Sapianta" for "AiGOL", changing "product" to "product domain", or
  dropping a trigger word silently redirects the prompt to an entirely
  different runtime. There is no ambiguity score, no tie-breaker, and no
  evidence trail beyond the per-branch replay artifacts.
- **Operational impact:** Variations within a single operator session
  produce inconsistent routing without any operator-visible explanation,
  which is the underlying mechanism behind the "providers: NONE vs alpha+beta"
  divergence the operator reported.

## F-3 — `providers: NONE` is a turn-summary projection gap

- **Classification:** VISIBILITY_BUG
- **File:** [aigol/cli/aigol_cli.py](aigol/cli/aigol_cli.py)
- **Function:** `_interactive_turn_providers` ([aigol/cli/aigol_cli.py:631-640](aigol/cli/aigol_cli.py#L631-L640)),
  every `_interactive_*_turn_summary` builder except
  `_interactive_ocs_llm_cognition_turn_summary` ([aigol/cli/aigol_cli.py:2797-2878](aigol/cli/aigol_cli.py#L2797-L2878)).
- **Branch:** Turn-summary construction at routing-branch end (e.g.
  [aigol/cli/aigol_cli.py:1691-1700](aigol/cli/aigol_cli.py#L1691-L1700), [2289-2298](aigol/cli/aigol_cli.py#L2289-L2298)).
- **Root cause:** Only the OCS cognition turn summary populates
  `provider_ids`. Every other branch returns a summary without that key, so
  `_interactive_turn_providers` falls through to `[]`, which
  `render_conversational_turn_completion_summary` ([aigol/runtime/conversational_turn_completion_runtime.py:212-232](aigol/runtime/conversational_turn_completion_runtime.py#L212-L232))
  renders as `providers: NONE`.
- **Operational impact:** `providers: NONE` does not mean "no providers
  bound to this branch" — it means "the turn summary forgot to project the
  provider identifiers". For the default conversation branch in particular,
  the OpenAI provider IS invoked (and failing) yet the completion artifact
  asserts no provider involvement.

## F-4 — `elapsed_seconds` is a hardcoded stage count

- **Classification:** VISIBILITY_BUG
- **File:** [aigol/cli/aigol_cli.py](aigol/cli/aigol_cli.py), [aigol/runtime/conversational_progress_binding_runtime.py](aigol/runtime/conversational_progress_binding_runtime.py)
- **Function:** `_interactive_turn_elapsed_seconds` ([aigol/cli/aigol_cli.py:624-628](aigol/cli/aigol_cli.py#L624-L628))
  and `_duration_history` ([aigol/runtime/conversational_progress_binding_runtime.py:204-216](aigol/runtime/conversational_progress_binding_runtime.py#L204-L216)).
- **Branch:** Called unconditionally inside `_record_interactive_turn_completion`
  ([aigol/cli/aigol_cli.py:597-609](aigol/cli/aigol_cli.py#L597-L609)).
- **Root cause:**

  ```python
  def _interactive_turn_elapsed_seconds(progress_binding_capture):
      artifact = progress_binding_capture.get("conversational_progress_binding_artifact")
      if isinstance(artifact, dict) and isinstance(artifact.get("stage_count"), int):
          return artifact["stage_count"]
      return 0
  ```

  `stage_count == len(CONVERSATIONAL_PROGRESS_STAGE_MODEL) == 8`. The value
  has no relationship to real time. No `time.monotonic()` is captured at
  start; no wall-clock delta is computed at completion. The same
  `created_at` constant is passed as both `started_at` and `snapshot_at` to
  every checkpoint, so the underlying progress runtime's
  `elapsed_seconds = int((snapshot - started).total_seconds())` always
  resolves to `0`.
- **Operational impact:** `elapsed: 8s` is constant regardless of actual
  duration, so operators cannot diagnose slow turns from CLI output. The
  replay-visible `TURN_COMPLETED_ARTIFACT_V1.elapsed_seconds` is also a
  constant placeholder, undermining replay-based latency analysis.

## F-5 — `TURN COMPLETED` is recorded before result delivery

- **Classification:** VISIBILITY_BUG
- **File:** [aigol/cli/aigol_cli.py](aigol/cli/aigol_cli.py)
- **Function:** `_record_interactive_turn_completion` ([aigol/cli/aigol_cli.py:586-621](aigol/cli/aigol_cli.py#L586-L621))
  and the surrounding turn-completion block ([aigol/cli/aigol_cli.py:2314-2335](aigol/cli/aigol_cli.py#L2314-L2335)).
- **Branch:** Normal-output flush at end of each turn.
- **Root cause:**

  ```python
  completion_capture = _record_interactive_turn_completion(...)
  normal_output.append(completion_capture["operator_completion_summary"])
  rendered_normal_output = "\n".join(turn_progress_buffer + normal_output)
  terminal_output_writer(rendered_normal_output)
  ```

  `record_conversational_result_delivered` is invoked **inside**
  `_record_interactive_turn_completion`, which stamps the artifact with
  `delivered_at=created_at` and `result_delivered=True` before any of the
  buffered output is actually written to the terminal. The
  `delivered_output_line_count` argument counts the buffer contents at the
  moment of the call (line 2326-2328) but does not include the completion
  summary itself, so even the line count is internally inconsistent with
  what is ultimately printed.
- **Operational impact:** `result_delivered: TRUE` is a lifecycle assertion,
  not a delivery attestation. If the process is killed between the
  artifact write and the terminal flush, replay claims the result was
  delivered when it was not. Operators waiting for results have no
  reliable signal that the turn truly completed.

## F-6 — Progress checkpoints are deterministic placeholders

- **Classification:** VISIBILITY_BUG
- **File:** [aigol/cli/aigol_cli.py](aigol/cli/aigol_cli.py), [aigol/runtime/conversational_progress_binding_runtime.py](aigol/runtime/conversational_progress_binding_runtime.py),
  [aigol/runtime/runtime_progress_visibility.py](aigol/runtime/runtime_progress_visibility.py)
- **Function:** `_emit_interactive_conversation_progress` ([aigol/cli/aigol_cli.py:543-561](aigol/cli/aigol_cli.py#L543-L561)),
  `_emit_interactive_conversation_cognition_progress` ([aigol/cli/aigol_cli.py:563-583](aigol/cli/aigol_cli.py#L563-L583)),
  `record_runtime_progress_snapshot` ([aigol/runtime/runtime_progress_visibility.py:90-145](aigol/runtime/runtime_progress_visibility.py#L90-L145)).
- **Branch:** Called at routing entry, cognition entry, result assembly,
  replay close.
- **Root cause:** Every checkpoint is emitted with `snapshot_at=created_at`
  (a CLI argument with default `2026-06-01T00:00:00Z`), so the snapshot
  timestamps are identical to the start timestamp and to each other. The
  fan-out of five "cognition" checkpoints at
  [aigol/cli/aigol_cli.py:570-583](aigol/cli/aigol_cli.py#L570-L583) is emitted
  unconditionally before any of those stages actually runs — they will
  fire even on a branch (e.g. read-only audit review) where Provider
  Invocation, Comparison, Continuity, and Clarification do not happen.
- **Operational impact:** Progress visibility tracks lifecycle checkpoints,
  not real execution. The "8 stages" rendered to the operator are a
  guaranteed pattern regardless of whether the corresponding work occurred.

## F-7 — Provider-unavailable clarification fallback is a hard-coded phrase list

- **Classification:** USABILITY_BUG (with USAGE_RELIABILITY impact)
- **File:** [aigol/runtime/conversation_provider_unavailable_clarification_fallback.py](aigol/runtime/conversation_provider_unavailable_clarification_fallback.py)
- **Function:** `_classify_ambiguity` ([aigol/runtime/conversation_provider_unavailable_clarification_fallback.py:165-231](aigol/runtime/conversation_provider_unavailable_clarification_fallback.py#L165-L231))
- **Branch:** Raised exception at line 229-231.
- **Root cause:** The fallback understands exactly four prompt families:
  `"workstation" + (create|open|build|add)`, `"improve trading"`,
  `"add analysis"`, `"create reporting"` (with optional trailing period).
  Anything else triggers
  `FailClosedRuntimeError("conversation provider clarification fallback failed closed: prompt is not clarification-eligible")`.
  The default conversation branch ([aigol/cli/aigol_cli.py:2263-2286](aigol/cli/aigol_cli.py#L2263-L2286))
  then prints `FAILED_CLOSED: prompt is not clarification-eligible`.
- **Operational impact:** Whenever the OpenAI provider is unavailable
  (no API key, network blocked, rate limited) the operator sees a generic
  "not clarification-eligible" error for almost every prompt. There is no
  graceful "I can't reach the provider" response and no actionable hint
  about what the operator could do instead.

## F-8 — Default conversation path requires a live OpenAI provider

- **Classification:** IMPLEMENTATION_BUG (with operational reliability impact)
- **File:** [aigol/runtime/prompt_to_conversation_integration.py](aigol/runtime/prompt_to_conversation_integration.py)
- **Function:** `submit_prompt_to_conversation` ([aigol/runtime/prompt_to_conversation_integration.py:35-102](aigol/runtime/prompt_to_conversation_integration.py#L35-L102)),
  `_provider_dependencies` ([aigol/runtime/prompt_to_conversation_integration.py:222-232](aigol/runtime/prompt_to_conversation_integration.py#L222-L232)).
- **Branch:** Hard default `provider_id=OPENAI_PROVIDER_ID` and
  `OpenAIProviderAdapter()` with no offline fallback transport.
- **Root cause:** The else-branch of the CLI cascade routes to a runtime
  that always picks the OpenAI live provider. The OCS-cognition branch
  uses an in-process transport ([aigol/cli/aigol_cli.py:439-494](aigol/cli/aigol_cli.py#L439-L494)),
  but the default conversation branch does not. There is no opt-in
  deterministic transport for the legacy conversation path, so the CLI is
  not usable offline.
- **Operational impact:** Most operator prompts fall into the legacy
  conversation branch (because the OCS markers are narrow), so unless
  `AIGOL_OPENAI_API_KEY` is configured and the network is reachable, the
  CLI looks broken: every fragment fails closed with
  `prompt is not clarification-eligible`.

## F-9 — Operator decision-support keyword soup can collide with OCS markers

- **Classification:** ROUTING_BUG (latent)
- **File:** [aigol/runtime/conversational_cli_runtime.py](aigol/runtime/conversational_cli_runtime.py)
- **Function:** `_is_operator_decision_support_prompt` ([aigol/runtime/conversational_cli_runtime.py:256-269](aigol/runtime/conversational_cli_runtime.py#L256-L269))
  and `_is_ocs_llm_cognition_prompt` ([aigol/runtime/conversational_cli_runtime.py:282-308](aigol/runtime/conversational_cli_runtime.py#L282-L308)).
- **Branch:** Two adjacent predicates evaluated in series at
  [aigol/cli/aigol_cli.py:1735, 2216](aigol/cli/aigol_cli.py#L1735).
- **Root cause:** `_is_operator_decision_support_prompt` matches
  `"prioritize"`, `"priority"`, `"roadmap"`, `"sequencing"`, `"which capability"`,
  `"which provider"`, etc. `_is_ocs_llm_cognition_prompt` matches
  `"first real aigol product"`, `"commercialization"`, `"continue "`,
  `"help me decide"`, `"what should"`. A genuine business question like
  *"How should we prioritize commercialization?"* matches BOTH predicates
  and is routed to decision-support purely because that predicate is
  earlier in the `elif` chain. Operators have no visibility into which
  predicate "won" or why.
- **Operational impact:** Subtle routing ambiguity that produces different
  artifact types for nearly identical prompts; cannot be diagnosed from
  the CLI alone.

## F-10 — Per-turn `created_at` is a CLI argument, not a real timestamp

- **Classification:** VISIBILITY_BUG
- **File:** [aigol/cli/aigol_cli.py](aigol/cli/aigol_cli.py)
- **Function:** `run_interactive_conversation` ([aigol/cli/aigol_cli.py:1164](aigol/cli/aigol_cli.py#L1164))
- **Branch:** `created_at = _require_cli_string(args.created_at, "created_at")`,
  reused for every replay artifact in the session.
- **Root cause:** The conversation subcommand exposes `--created-at` with
  default `"2026-06-01T00:00:00Z"` ([aigol/cli/aigol_cli.py:956](aigol/cli/aigol_cli.py#L956)).
  The CLI never derives a real timestamp from the system clock and never
  updates it between turns. Every artifact, every progress checkpoint,
  every `delivered_at` carries the same constant value.
- **Operational impact:** Forensic correlation between an operator's
  wall-clock observation and the replay artifact is impossible. Turn 136 and
  turn 149 in Case B share the same `created_at`, so replay cannot
  reconstruct ordering or latency.

## Determinism vs accuracy summary

The CLI satisfies deterministic-replay invariants by replacing real
measurements with constants:

| Claim | Constant source | Actual value |
|---|---|---|
| `elapsed: 8s` | `stage_count` | Wall-clock unknown |
| `started_at = snapshot_at` | `args.created_at` | Real moments not captured |
| `result_delivered: TRUE` | Recorded before terminal flush | Delivery not attested |
| Cognition checkpoints | Always 5 emitted | Branch may never run that work |

Determinism is preserved, **operational truth is not**. This is the
single largest cause of operator confusion in the trace.

## Operational reliability verdict

The current `aigol conversation` CLI is **not operationally reliable for
unconstrained human use**:

- Multi-line input is structurally unsupported.
- Routing is brittle, phrasing-sensitive, and silently undiagnosable.
- The completion summary (`providers`, `elapsed`, `result_delivered`) is
  decorative for every branch except OCS cognition.
- The fallback path covers four phrases and otherwise fails closed.
- Without an OpenAI key, the default conversation branch is unusable.

The CLI is reliable for **bounded test scenarios** matching the existing
test corpus (single-line, marker-matching prompts in
[tests/](tests/)). It is not reliable for the open-ended human prompts the
operator described.
