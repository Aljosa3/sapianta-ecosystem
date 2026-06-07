# AIGOL_NESTED_COGNITION_JSON_NORMALIZATION_FIX_V1

## Status

Implemented minimal normalization fix.

## Goal

Recover structured cognition when a provider returns a valid cognition JSON document serialized inside `findings[0]`.

## Root Cause

The real pipeline trace identified this shape:

```json
{
  "findings": [
    "{\"findings\":[...],\"assumptions\":[...],\"risks\":[...],\"uncertainties\":[...]}"
  ]
}
```

The top-level provider JSON was parsed, but `_normalize_string_list(...)` preserved the nested JSON document as a plain finding string.

## Fix

The cognition artifact normalizer now performs a bounded nested-cognition expansion step before canonical field normalization.

Implemented in:

```text
aigol/runtime/cognition_artifact_runtime.py
```

The fix:

- detects JSON-looking strings inside `findings`;
- parses them only when they are valid JSON objects containing recognized cognition fields;
- merges nested `findings`, `assumptions`, `risks`, `uncertainties`, `clarification_questions`, and `recommended_next_milestone`;
- preserves invalid JSON strings as ordinary findings;
- preserves normal findings lists unchanged;
- preserves mixed plain and nested findings.

## Canonical Fields

Recovered nested values are merged into:

- `findings`
- `assumptions`
- `risks`
- `uncertainties`
- `clarification_questions`
- `recommended_next_milestone`

`clarification_questions` and `recommended_next_milestone` are also projected into the human-facing OCS cognition result for operator rendering.

## Preservation

Preserved:

- replay visibility;
- governance boundaries;
- provider non-authority;
- existing core cognition artifact fields;
- existing technical summary;
- invalid JSON handling;
- normal and mixed finding behavior.

The existing core `cognition_hash` input remains compatible with prior core fields.

## Regression Coverage

Regression cases:

- Case A: nested cognition JSON in `findings[0]`;
- Case B: normal findings list;
- Case C: mixed plain findings plus nested cognition JSON;
- Case D: invalid JSON string.

End-to-end OCS rendering also proves recovered nested fields render cleanly and no serialized `{"findings":` blob appears in operator output.

