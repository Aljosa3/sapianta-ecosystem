# AIGOL_CONVERSATIONAL_CLI_OPERATIONAL_TRACE_ANALYSIS_V1

End-to-end code-path traces for the operator-reported Case A and Case B
incidents. Review-only; no code modified.

## Case A — single-line prompt

Operator typed:

```
I want to create the first real commercial Sapianta product.
```

### 1. CLI loop reads the prompt

[aigol/cli/aigol_cli.py:1179](aigol/cli/aigol_cli.py#L1179):

```python
raw_prompt = input_reader("AiGOL > ")
```

`input_reader` defaults to Python's built-in `input()`, which reads exactly
one line. `human_prompt` = `"I want to create the first real commercial Sapianta product."`.

### 2. Routing cascade

The branches are evaluated in this order
([aigol/cli/aigol_cli.py:1234-2250](aigol/cli/aigol_cli.py#L1234-L2250)):

| # | Branch | Predicate | Match? |
|---|--------|-----------|--------|
| 1 | Human decision against pending approval | `pending_approval_required is not None` | No (fresh session) |
| 2 | Recommendation approval / followup | `_is_recommendation_decision_prompt` / `is_recommendation_followup_prompt` | No |
| 3 | Read-only conversational workflow | `_is_conversational_cli_readonly_candidate` ([aigol/cli/aigol_cli.py:3318-3324](aigol/cli/aigol_cli.py#L3318-L3324)) → requires "latest"+"chain", "review"+"audit", or "improve"+"provider"+"layer" | No |
| 4 | Domain reference adaptation | `is_domain_reference_adaptation_prompt` → requires "similar to"/"based on"/… AND a known domain word | No |
| 5 | Operator decision support | `is_operator_decision_support_prompt` → requires "first real" + ("product domain" or "aigol product domain") | No (prompt has "commercial Sapianta product", not "product domain") |
| 6 | Unknown-domain clarification | `is_unknown_domain_clarification_eligible` ([aigol/runtime/unknown_domain_clarification_runtime.py:204-226](aigol/runtime/unknown_domain_clarification_runtime.py#L204-L226)) → requires "domain" + create/new/add + compliance/regulatory | No |
| 7 | Native development intent | `is_conversation_native_development_intent` ([aigol/runtime/conversation_native_development_intent_routing.py:41-47](aigol/runtime/conversation_native_development_intent_routing.py#L41-L47)) → catalog of `(create, marketing, domain)` etc. | No |
| 8 | Native development task intake | `is_native_development_prompt` → requires `MILESTONE_PATTERN` like `FOO_BAR_V1` | No |
| 9 | OCS LLM cognition | `is_ocs_llm_cognition_prompt` ([aigol/runtime/conversational_cli_runtime.py:272-308](aigol/runtime/conversational_cli_runtime.py#L272-L308)) — marker set: `first real aigol product`, `commercialization`, `managed services`, `license the platform`, `sell domains`, `should sapianta`, `continue the aigol`, `continue `, `help me decide`, `what should`. Or `?`-terminated + `should/what should/how should/why should/can you analyze`. | **Edge case** — the literal prompt does not contain any marker; the marker set requires "first real aigol product" but the operator wrote "commercial Sapianta product". A genuine operator phrasing here does **not** match. |
| 10 | Default conversation | `submit_prompt_to_conversation` ([aigol/cli/aigol_cli.py:2251-2298](aigol/cli/aigol_cli.py#L2251-L2298)) | Catch-all |

The OCS-cognition output the operator observed in Case A could only have been
produced if the prompt happened to include one of the cognition markers
(e.g., the operator wrote `"should sapianta…"`, `"what should…"`, or
`"first real aigol product…"`). Any nearby paraphrase that omits these markers
silently degrades to the default conversation path. **Routing is deterministic
but extremely sensitive to surface phrasing.**

### 3. OCS LLM cognition branch (when it does fire)

[aigol/cli/aigol_cli.py:2216-2249](aigol/cli/aigol_cli.py#L2216-L2249):

- `route_conversational_cli_intent` records the `WORKFLOW_SELECTED` decision.
- `_run_conversational_ocs_llm_cognition` ([aigol/cli/aigol_cli.py:497-521](aigol/cli/aigol_cli.py#L497-L521))
  drives `run_ocs_llm_cognition_end_to_end` against the two in-process
  contracts `aigol-cognition-alpha` and `aigol-cognition-beta` with a
  hard-coded deterministic transport.
- `_interactive_ocs_llm_cognition_turn_summary` ([aigol/cli/aigol_cli.py:2797-2878](aigol/cli/aigol_cli.py#L2797-L2878))
  is the **only** turn summary that populates `provider_ids` (line 2860:
  `"provider_ids": request_bundle.get("deterministic_provider_order", [])`).

That is why Case A renders:

```
providers:
  aigol-cognition-alpha
  aigol-cognition-beta
```

while Case B turns rendered `providers: NONE`. The bound providers exist in
every branch the runtime calls into, but only this branch projects them into
the `TURN_COMPLETED` artifact.

## Case B — multi-line pasted prompt

Operator pasted ~24 lines beginning with
`"I want to create the first real commercial Sapianta product."` and
continuing through a numbered request list.

### 1. Stdin handling

The interactive loop's `input()` returns one line at a time. The terminal
delivers the pasted block as a sequence of newline-terminated stdin reads —
each newline ends a separate `input()` call. Python's `input()` does **not**
support bracketed paste accumulation; the CLI provides no `\` continuation,
no end-of-input sentinel, no heredoc, no `--prompt-file`, and the empty-line
guard at [aigol/cli/aigol_cli.py:1184-1186](aigol/cli/aigol_cli.py#L1184-L1186) silently
discards blank lines:

```python
human_prompt = raw_prompt.strip()
if not human_prompt:
    continue
```

so the surface symptom is that the first ~24 non-empty pasted lines become
~24 independent turns. This matches the operator's observation that turns
139, 140, 145 each "returned" a numbered list item.

### 2. Per-line routing in Case B

| Pasted line | Routes to | Reason |
|---|---|---|
| `I want to create the first real commercial Sapianta product.` | OCS LLM cognition only if it contains a marker. Otherwise default conversation. | See Case A. |
| `Use the current AiGOL architecture and repository state.` | Default conversation | No marker. |
| `Produce:` | Default conversation | No marker. |
| `1. Findings`, `2. Assumptions`, … `10. Recommended commercialization path` | "commercialization" matches `_is_ocs_llm_cognition_prompt`'s `cognition_markers` for line 10 only ([aigol/runtime/conversational_cli_runtime.py:287-297](aigol/runtime/conversational_cli_runtime.py#L287-L297)). Lines 1–9 do not match anything and fall to the default conversation. | Routing fragmentation. |
| `Explain your reasoning.` | Default conversation | No marker. |
| `Do not create or modify anything.` | `is_ocs_llm_cognition_prompt` short-circuits at [aigol/runtime/conversational_cli_runtime.py:285-286](aigol/runtime/conversational_cli_runtime.py#L285-L286) (`"domain" not in normalized`, so check passes) → still no marker → default conversation. | Not OCS. |
| `Provide cognition output only.` | Default conversation | No marker. |

### 3. Default conversation branch

[aigol/cli/aigol_cli.py:2251-2298](aigol/cli/aigol_cli.py#L2251-L2298):

```python
conversation_capture = submit_prompt_to_conversation(...)
...
if fail_closed:
    fallback_capture = run_conversation_provider_unavailable_clarification_fallback(...)
    if fallback_capture.get("response_status") == PROVIDER_UNAVAILABLE_HUMAN_CLARIFICATION_REQUIRED:
        conversation_capture = fallback_capture
        ...
    else:
        ...
        output_writer(f"FAILED_CLOSED: {failure_reason}")
```

`submit_prompt_to_conversation` ([aigol/runtime/prompt_to_conversation_integration.py:35-102](aigol/runtime/prompt_to_conversation_integration.py#L35-L102))
goes through `run_provider_assisted_conversation`, which on a fresh
deployment without the `AIGOL_OPENAI_API_KEY` returns
`failure_reason="provider-assisted conversation failed closed"`. That string
matches `PROVIDER_UNAVAILABLE_MARKERS`
([aigol/runtime/conversation_provider_unavailable_clarification_fallback.py:28-32](aigol/runtime/conversation_provider_unavailable_clarification_fallback.py#L28-L32)), so the
fallback is invoked. Inside the fallback,
`_classify_ambiguity` ([aigol/runtime/conversation_provider_unavailable_clarification_fallback.py:165-231](aigol/runtime/conversation_provider_unavailable_clarification_fallback.py#L165-L231))
recognizes only:

- Prompts containing `"workstation"` + create/open/build/add.
- The exact strings `"improve trading"`, `"improve trading."`,
  `"add analysis"`, `"add analysis."`, `"create reporting"`,
  `"create reporting."`.

Every other prompt raises:

```
conversation provider clarification fallback failed closed:
prompt is not clarification-eligible
```

which is exactly the error the operator observed. This is the canonical
trace for the "fallback failed closed: prompt is not clarification-eligible"
turns.

### 4. Per-line `TURN COMPLETED` semantics

For each fragment line:

- `_create_interactive_conversation_progress_binding` ([aigol/cli/aigol_cli.py:524-540](aigol/cli/aigol_cli.py#L524-L540))
  starts a fresh stage model.
- Eight checkpoints (`ROUTING`, `COGNITION`, `PROVIDER_INVOCATION`,
  `COMPARISON`, `CONTINUITY`, `CLARIFICATION`, `RESULT_ASSEMBLY`, `REPLAY`)
  are recorded with `snapshot_at=created_at`
  ([aigol/cli/aigol_cli.py:1213-1232](aigol/cli/aigol_cli.py#L1213-L1232), 2299-2313).
- `_record_interactive_turn_completion` ([aigol/cli/aigol_cli.py:586-621](aigol/cli/aigol_cli.py#L586-L621))
  passes:
    - `providers=_interactive_turn_providers(turn_summary)` — `[]` for every
      non-OCS branch → renders `providers: NONE`.
    - `elapsed_seconds=_interactive_turn_elapsed_seconds(progress_binding_capture)`
      — returns `stage_count` (constant `8`) regardless of wall clock.
    - `result_delivered=False` initially, then
      `record_conversational_result_delivered` flips it to `True` **before**
      `terminal_output_writer(rendered_normal_output)` flushes the response
      ([aigol/cli/aigol_cli.py:2329-2332](aigol/cli/aigol_cli.py#L2329-L2332)). The
      replay artifact therefore certifies "result_delivered=TRUE" before
      `print()` runs.

That produces the exact rendering operators saw:

```
TURN COMPLETED
turn_id: …
providers: NONE
status: COMPLETED
result_delivered: TRUE
elapsed: 8s
```

with `elapsed: 8s` invariant across short and long real-time waits.

## Stage progress checkpoints

[aigol/runtime/conversational_progress_binding_runtime.py:204-216](aigol/runtime/conversational_progress_binding_runtime.py#L204-L216):

```python
def _duration_history() -> dict[str, Any]:
    return {
        "history_source": "CONVERSATIONAL_PROGRESS_BINDING_V1",
        "runtime_duration_seconds": len(CONVERSATIONAL_PROGRESS_STAGE_MODEL),
        "stage_durations": {
            stage: {
                "average_duration_seconds": 1,
                "last_duration_seconds": 1,
                "sample_count": 1,
            }
            for stage in CONVERSATIONAL_PROGRESS_STAGE_MODEL
        },
    }
```

Every checkpoint carries deterministic, hardcoded durations. The downstream
snapshot also derives `elapsed_seconds = int((snapshot - started).total_seconds())`
from a single `created_at` value
([aigol/runtime/runtime_progress_visibility.py:113-119](aigol/runtime/runtime_progress_visibility.py#L113-L119)),
so `snapshot - started == 0`. The progress line `[N/8] Stage` therefore
advances purely as a function of how the lifecycle function chooses to call
`_emit_interactive_conversation_progress`, not how long real work took.

## Why Case A vs Case B diverged

| Symptom | Root cause |
|---|---|
| Single-line prompt completed cleanly with OCS providers | The line happened to contain an OCS marker, hitting the OCS-cognition branch which is the only branch that populates `provider_ids` and the only branch that exercises an in-process provider transport. |
| Multi-line paste fragmented across turns | `input()` reads one line; CLI lacks multi-line aggregation. |
| Some fragments showed `providers: NONE` | Non-OCS branches don't populate `provider_ids`. |
| Some fragments failed with `prompt is not clarification-eligible` | Default conversation needs a live provider; without one it escalates to a fallback whose `_classify_ambiguity` recognizes only four hard-coded phrases. |
| `elapsed: 8s` despite long wall time | `_interactive_turn_elapsed_seconds` returns the stage-count constant; `snapshot_at` is the static `created_at` value. |
| `TURN COMPLETED ... result_delivered: TRUE ... elapsed: 8s` precedes visible result | Completion artifact is recorded into the buffer **before** `terminal_output_writer` flushes. |
