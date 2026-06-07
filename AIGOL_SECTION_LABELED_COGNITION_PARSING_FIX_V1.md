# AIGOL_SECTION_LABELED_COGNITION_PARSING_FIX_V1

## Status

Implemented.

## Goal

Recover structured cognition when a provider returns known cognition sections as labeled text instead of strict JSON.

## Root Cause

Real operator acceptance showed that provider output can arrive as a single normalized finding containing section labels:

```text
Findings ...
Assumptions ...
Risks ...
Uncertainties ...
Clarification Questions ...
Recommended Next Milestone ...
```

The existing normalizer handled valid JSON cognition documents and nested JSON inside `findings[]`, but it did not parse section-labeled plain text. The whole provider response was therefore preserved as one Findings item, leaving canonical Assumptions, Risks, and Uncertainties empty.

## Fix

Implemented bounded section-labeled cognition parsing in:

```text
aigol/runtime/cognition_artifact_runtime.py
```

The normalizer now:

- detects known cognition labels inside finding text;
- supports multiline `Label:` sections;
- supports flattened `label: ... label: ...` sections;
- supports provider-observed `Label - ...` sections;
- parses bullet and numbered items;
- merges parsed values into canonical cognition fields;
- preserves plain findings when no multi-section cognition document is detected;
- preserves existing nested JSON handling.

## Canonical Fields Populated

- `findings`
- `assumptions`
- `risks`
- `uncertainties`
- `clarification_questions`
- `recommended_next_milestone`

`alternatives` are also supported when present because they are part of the existing canonical cognition field set.

## Preservation

Preserved:

- replay compatibility;
- governance compatibility;
- provider non-authority;
- authority boundary checks;
- existing nested JSON expansion;
- invalid JSON preservation;
- technical summary rendering;
- ordinary plain-text fallback behavior.

## Real Operator Validation

Fresh real OpenAI-backed validation:

```text
session_id: AIGOL-SECTION-LABELED-COGNITION-000003
turn_id: TURN-000001
runtime_root: /tmp/aigol_section_labeled_cognition_runtime_3
workflow: OCS_LLM_COGNITION
provider: openai
status: COMPLETED
successful_provider_count: 1
```

Operator output rendered all required sections without `(none recorded)` for populated fields:

- Findings
- Assumptions
- Risks
- Uncertainties
- Clarification Questions
- Recommended Next Milestone

Technical summary remained available after the operator cognition section.

## Validation

Focused cognition and OCS tests:

```text
python -m pytest tests/test_cognition_artifact_runtime_v1.py tests/test_ocs_llm_cognition_end_to_end_runtime_v1.py
31 passed
```

Routing and conversational alignment tests:

```text
python -m pytest tests/test_conversational_ocs_cognition_binding_v1.py tests/test_conversational_dispatch_authority_unification_v1.py tests/test_conversational_cli_runtime_v1.py tests/test_conversational_routing_visibility_runtime_v1.py
33 passed
```

## Known Limitation

One non-concise real provider run returned a truncated JSON-looking payload. That is a separate malformed/truncated provider-output shape, not the section-labeled cognition shape fixed here.

## Final Outputs

```text
SECTION_LABELED_COGNITION_DETECTED = TRUE
SECTIONS_PARSED = TRUE
ASSUMPTIONS_RECOVERED = TRUE
RISKS_RECOVERED = TRUE
UNCERTAINTIES_RECOVERED = TRUE
CLARIFICATION_QUESTIONS_RECOVERED = TRUE
NEXT_MILESTONE_RECOVERED = TRUE

OPERATOR_OUTPUT_STATUS = STRUCTURED_SECTION_LABELED_COGNITION_RENDERED
```
