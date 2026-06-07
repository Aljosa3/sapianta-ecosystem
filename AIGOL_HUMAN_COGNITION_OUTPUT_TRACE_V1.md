# AIGOL_HUMAN_COGNITION_OUTPUT_TRACE_V1

## Status

Review-only output trace.

No runtime code was changed. No provider behavior was changed. No workflow behavior was changed.

## Executive Finding

The OpenAI cognition response is not lost.

It is stored in the multi-provider cognition result bundle as `provider_response_artifact.response_text`, normalized into `LLM_COGNITION_ARTIFACT_V1`, persisted in replay, and referenced by the end-to-end artifact.

The operator does not see the cognition content because conversational OCS dispatch renders:

```text
render_ocs_llm_cognition_end_to_end_summary(...)
```

That renderer intentionally emits a technical completion summary rather than the normalized cognition fields.

## Complete Trace

```text
Human Prompt
-> _run_conversational_ocs_llm_cognition(...)
-> run_ocs_llm_cognition_end_to_end(...)
-> run_multi_provider_cognition_runtime(...)
-> _invoke_provider_request(...)
-> OpenAI transport
-> LLM_COGNITION_PROVIDER_RESPONSE_ARTIFACT_V1
-> run_cognition_artifact_runtime(...)
-> LLM_COGNITION_ARTIFACT_V1
-> single-provider comparison compatibility artifact
-> OCS_LLM_COGNITION_END_TO_END_ARTIFACT_V1
-> render_ocs_llm_cognition_end_to_end_summary(...)
-> conversational CLI output
```

## OpenAI Response Location

The provider response is created in:

```text
aigol/runtime/llm_cognition_provider_runtime.py:322-350
```

The artifact stores:

```text
raw_response
raw_response_hash
response_text
response_text_hash
response_status: CAPTURED
untrusted_provider_output: true
non_authoritative: true
```

In the validated replay, the response is embedded in:

```text
/tmp/aigol_single_provider_ocs_e2e_validation/interactive_runtime/SESSION-SINGLE-PROVIDER-OCS-E2E-VALIDATION-000001/TURN-000001/ocs_llm_cognition_end_to_end/stages/multi_provider_cognition/001_multi_provider_cognition_result_bundle.json
```

Path inside artifact:

```text
artifact.provider_results[0].provider_response_artifact.response_text
```

Validated response text contained:

```text
findings
assumptions
alternatives
risks
uncertainties
confidence
```

## Cognition Artifact Location

The cognition artifact is created by:

```text
aigol/runtime/cognition_artifact_runtime.py:78-104
aigol/runtime/cognition_artifact_runtime.py:133-199
```

It persists as:

```text
/tmp/aigol_single_provider_ocs_e2e_validation/interactive_runtime/SESSION-SINGLE-PROVIDER-OCS-E2E-VALIDATION-000001/TURN-000001/ocs_llm_cognition_end_to_end/stages/multi_provider_cognition/providers/openai/cognition_artifact/000_llm_cognition_artifact.json
```

The normalized artifact contains:

```text
findings:
- Sapianta should validate the first product through governed cognition before execution.
- The prompt requests product opportunity analysis, not autonomous mutation.

assumptions:
- The operator wants replay-visible strategic cognition.

alternatives:
- AI Decision Validator
- Managed governance review
- Platform licensing

risks:
- Provider output remains non-authoritative and requires governance framing.

uncertainties:
- Market entry sequencing requires additional operator input.

confidence:
- MEDIUM
```

## Result Assembly

The end-to-end artifact is assembled in:

```text
aigol/runtime/ocs_llm_cognition_end_to_end_runtime.py:313-359
```

It stores hashes and replay references for the provider response and cognition artifact:

```text
provider_response_artifact_hashes
cognition_artifact_hashes
stage_replay_references
lineage_refs.source_cognition_artifact_hashes
```

Its `human_facing_cognition_result` is built by:

```text
aigol/runtime/ocs_llm_cognition_end_to_end_runtime.py:392-409
```

That human-facing result currently contains:

```text
summary
comparison_confidence
comparison_findings
comparison_performed
single_provider_primary_mode
clarification_required
clarification_candidates
allowed_next_step
```

It does not include the normalized provider `findings`, `assumptions`, `alternatives`, `risks`, or `uncertainties`.

## CLI Renderer

The conversational CLI output path is:

```text
aigol/cli/aigol_cli.py:2794-2801
```

It renders:

```text
render_ocs_llm_cognition_end_to_end_summary(ocs_cognition_capture)
REAL_LLM_PROVIDER_USED_BY_OCS = true
```

The renderer is:

```text
aigol/runtime/ocs_llm_cognition_end_to_end_runtime.py:279-296
```

It outputs only:

```text
AIGOL OCS LLM COGNITION END-TO-END
status
classification
end_to_end_id
provider_count
successful_provider_count
comparison_confidence
clarification_required
replay_reference
fail_closed
failure_reason
```

Therefore the cognition content is hidden by renderer selection, not lost or discarded.

## Replay Reconstruction

The cognition content can already be reconstructed from replay:

1. Read the end-to-end replay artifact.
2. Follow `stage_replay_references.multi_provider_cognition`.
3. Open `001_multi_provider_cognition_result_bundle.json`.
4. Read `artifact.provider_results[0].provider_response_artifact.response_text` for the raw bounded response text.
5. Follow `artifact.provider_results[0].cognition_replay_reference`.
6. Open `000_llm_cognition_artifact.json` for normalized findings, assumptions, alternatives, risks, uncertainties, and confidence.

## Root Cause

The OCS conversational path completes cognition but renders the technical end-to-end summary instead of an operator-facing cognition view.

The renderer is completion-oriented, not cognition-content-oriented.

## Minimal Safe Fix

Add a non-authoritative operator cognition renderer, for example:

```text
render_ocs_llm_cognition_operator_result(...)
```

It should render from normalized cognition artifacts or replay-equivalent stage capture fields:

```text
Findings
Assumptions
Alternatives
Risks
Uncertainties
Confidence
Recommended next milestone / allowed next step
Clarification candidates
```

The renderer must preserve:

- provider non-authority;
- human review requirement;
- replay references;
- fail-closed behavior;
- existing technical summary fields;
- no worker invocation;
- no approval creation;
- no execution request.

The safest first implementation is to append the operator cognition view before or after the existing technical summary, leaving the existing summary intact for replay/debug continuity.

## Final Outputs

```text
OPENAI_RESPONSE_EXISTS = TRUE
OPENAI_RESPONSE_LOCATION = multi_provider_cognition result bundle: artifact.provider_results[0].provider_response_artifact.response_text
COGNITION_ARTIFACT_EXISTS = TRUE
COGNITION_ARTIFACT_LOCATION = stages/multi_provider_cognition/providers/openai/cognition_artifact/000_llm_cognition_artifact.json
CLI_RENDERER = aigol/runtime/ocs_llm_cognition_end_to_end_runtime.py::render_ocs_llm_cognition_end_to_end_summary
RESPONSE_HIDDEN_OR_LOST = HIDDEN_BY_SUMMARY_RENDERING
ROOT_CAUSE = conversational OCS renders a technical completion summary and does not render normalized cognition content
MINIMAL_SAFE_FIX = add a non-authoritative operator cognition renderer sourced from normalized cognition artifacts, preserving the existing technical summary and replay references
OPERATOR_VISIBLE_COGNITION_SUPPORTED = NOT_CURRENTLY_IN_CLI_OUTPUT_BUT_RECONSTRUCTABLE_FROM_REPLAY
```
