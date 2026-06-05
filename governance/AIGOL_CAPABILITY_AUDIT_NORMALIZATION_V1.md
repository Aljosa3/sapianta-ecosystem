# AIGOL_CAPABILITY_AUDIT_NORMALIZATION_V1

## Status

Runtime implementation certification.

```text
AIGOL_CAPABILITY_AUDIT_NORMALIZATION_STATUS = CERTIFIED
```

## Purpose

Create stable capability identities across audit generations.

This milestone introduces:

```text
CAPABILITY_ID
```

The `CAPABILITY_ID` is the stable identity used to compare capabilities across audits despite name, version, alias, or formatting drift.

## Runtime Scope

Runtime file:

```text
aigol/runtime/capability_normalization_runtime.py
```

Rules artifact:

```text
governance/AIGOL_CAPABILITY_NORMALIZATION_RULES_V1.json
```

Generated normalized matrix:

```text
governance/AIGOL_CAPABILITY_NORMALIZED_MATRIX_V1.json
```

The audit runtime now emits `capability_id`, `canonical_capability_key`, and `normalization` for every raw V2 matrix entry.

## Normalization Semantics

Normalization applies:

- lowercasing;
- `AIGOL_` prefix removal;
- non-alphanumeric formatting collapse;
- repeated underscore collapse;
- version suffix collapse;
- terminal classification suffix collapse;
- explicit alias mapping;
- stable `CAPABILITY::<CANONICAL_KEY>` id generation.

## Detection Semantics

The runtime detects:

- duplicate capability names;
- renamed capabilities;
- version-only changes;
- alias collapses;
- formatting differences;
- suffix-only capability splits.

## Generated Normalization Summary

Source matrix:

```text
governance/AIGOL_CAPABILITY_MATRIX_V2.json
```

Generated result:

| Metric | Count |
| --- | ---: |
| Source capabilities | 1821 |
| Normalized capabilities | 1622 |
| Collapsed capabilities | 199 |
| Duplicate groups | 157 |
| Renamed capabilities | 157 |
| Version-only changes | 78 |

Generated normalized status counts:

| Status | Count |
| --- | ---: |
| `CERTIFIED` | 366 |
| `IMPLEMENTED` | 8 |
| `PARTIAL` | 1244 |
| `NOT_STARTED` | 4 |

## Authority Boundaries

This runtime is identity normalization only.

It does not:

- certify capabilities by itself;
- authorize implementation;
- authorize execution;
- invoke providers;
- invoke workers;
- mutate governance semantics;
- hide duplicate evidence;
- delete raw audit evidence.

The raw audit matrix remains inspectable. The normalized matrix is the stable planning surface.

## Validation Coverage

Test file:

```text
tests/test_capability_normalization_runtime_v1.py
```

Certified validation:

- alias detection;
- rename detection;
- duplicate collapse;
- version collapse;
- normalized matrix generation;
- stable `CAPABILITY_ID` generation.

Audit runtime integration test:

```text
tests/test_capability_audit_runtime_v1.py
```

Certified integration:

- raw audit matrix entries include `capability_id`;
- raw audit matrix entries include `canonical_capability_key`;
- raw audit matrix entries include normalization metadata.

## Success Criteria

Capability identity remains stable across audit generations because future audits can compare:

```text
CAPABILITY_ID
```

instead of raw names, raw filenames, raw versions, or parser-dependent capability keys.
