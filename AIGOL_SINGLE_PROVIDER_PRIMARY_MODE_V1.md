# AIGOL_SINGLE_PROVIDER_PRIMARY_MODE_V1

## Status

Runtime stabilization implemented and certified.

Conversational OCS now uses a single default provider as the primary cognition execution path. Multi-provider cognition and comparison remain supported by the generic OCS end-to-end runtime, but they are no longer required for successful conversational OCS execution.

## Default Provider

```text
DEFAULT_PROVIDER = OPENAI
```

The conversational OCS binding now creates exactly one provider contract by default:

```text
openai
```

The previous default conversational pair:

```text
openai
openai-comparison
```

is no longer used by the conversational OCS default path.

## Current Conversational OCS Execution Path

Previous default:

```text
Human
-> OCS
-> OpenAI
-> OpenAI-comparison
-> two cognition artifacts
-> comparison runtime
-> continuity
-> clarification
-> replay
```

New default:

```text
Human
-> OCS
-> DEFAULT_PROVIDER: OPENAI
-> one LLM_COGNITION_ARTIFACT_V1
-> single-provider primary summary artifact
-> continuity
-> clarification
-> replay
-> done
```

The summary artifact is persisted in the existing cognition comparison replay slot for compatibility, but it records:

```text
single_provider_primary_mode: True
comparison_performed: False
comparison_required: False
```

## Current Comparison Dependencies

The explicit minimum cognition artifact count is enforced in:

```text
aigol/runtime/cognition_comparison_runtime.py::create_cognition_comparison_artifact
```

The invariant is:

```text
if len(artifacts) < 2:
    fail closed
```

Tests certifying this behavior remain in:

```text
tests/test_cognition_comparison_runtime_v1.py
tests/test_ocs_llm_cognition_end_to_end_runtime_v1.py
```

Continuity and clarification currently consume a completed comparison-shaped artifact. The minimal safe implementation therefore preserves that replay shape while making comparison optional in single-provider primary mode.

## Required Code Changes

Implemented:

1. Added `DEFAULT_PROVIDER = "OPENAI"` in the conversational CLI.
2. Changed conversational OCS provider contracts to include only `openai`.
3. Changed conversational OCS transport registry to expose only `openai`.
4. Added `single_provider_primary_mode=True` to conversational OCS end-to-end invocation.
5. Added a single-provider primary path in `run_ocs_llm_cognition_end_to_end(...)`.
6. Added replay-visible fields:

```text
single_provider_primary_mode
comparison_required
comparison_performed
```

7. Preserved the generic multi-provider comparison path by leaving the default end-to-end runtime mode unchanged.

## Replay Impact

Replay remains compatible:

- Existing end-to-end artifact type is preserved.
- Existing multi-provider result bundle type is preserved.
- Existing continuity and clarification replay types are preserved.
- Existing cognition comparison replay slot is preserved.
- The single-provider primary path records that comparison was not performed.

The completed conversational replay now records:

```text
provider_count: 1
successful_provider_count: 1
cognition_artifact_count: 1
comparison_required: False
comparison_performed: False
```

## Governance Impact

Governance boundaries are preserved:

- Provider output remains non-authoritative.
- Human review remains required.
- No approval is created.
- No worker is invoked.
- No execution is requested.
- No dispatch authority is granted to the provider.
- No governance or replay mutation path is introduced.

## Compatibility Impact

Conversational OCS default behavior changes from two provider slots to one provider slot.

Generic multi-provider OCS remains supported:

```text
run_ocs_llm_cognition_end_to_end(..., single_provider_primary_mode=False)
```

Comparison still requires at least two successful cognition artifacts in advanced mode.

## Risks

- The single-provider summary artifact uses the existing comparison replay slot for continuity compatibility. This is intentional but should eventually be replaced by a first-class single-provider cognition summary artifact type.
- Operator-facing progress still includes a comparison stage label even when comparison is not performed.
- Provider replacement is not implemented in this milestone.
- Single-provider mode reduces operational complexity but also removes provider-disagreement evidence from the default path.

## Future Provider Switching

Future human-controlled provider switching should be explicit, replay-visible, and non-authoritative.

Examples:

```text
Use Claude for this conversation.
Use Gemini for this task.
Set default provider to Claude.
```

Future provider switching should create a replay-visible provider selection artifact with:

- requested provider;
- normalized provider id;
- provider availability;
- provider approval status;
- selection scope;
- human instruction reference;
- no provider authority;
- no dispatch authority;
- no governance mutation.

This milestone documents that direction but does not implement provider switching.

## Minimal Safe Implementation

The smallest safe implementation is:

```text
Conversational OCS default:
  one provider contract
  one transport binding
  single_provider_primary_mode=True
  comparison_required=False

Generic OCS advanced path:
  unchanged multi-provider runtime
  comparison still requires >= 2 cognition artifacts
```

## Validation

```bash
python -m pytest tests/test_interactive_conversation_cli_v1.py tests/test_multiline_prompt_support_runtime_v1.py tests/test_conversational_ocs_cognition_binding_v1.py tests/test_ocs_llm_cognition_end_to_end_runtime_v1.py tests/test_cognition_comparison_runtime_v1.py
```

Result:

```text
28 passed
```

## Final Outputs

```text
DEFAULT_PROVIDER = OPENAI
SINGLE_PROVIDER_PRIMARY_MODE_SUPPORTED = TRUE
COMPARISON_OPTIONAL = TRUE
MULTI_PROVIDER_STILL_SUPPORTED = TRUE
REPLAY_COMPATIBLE = TRUE
GOVERNANCE_COMPATIBLE = TRUE
MINIMAL_SAFE_FIX = conversational OCS defaults to one OPENAI provider with single_provider_primary_mode=True; advanced multi-provider comparison remains intact
```
