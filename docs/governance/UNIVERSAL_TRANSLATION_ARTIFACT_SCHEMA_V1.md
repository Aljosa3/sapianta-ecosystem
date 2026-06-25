# UNIVERSAL_TRANSLATION_ARTIFACT_SCHEMA_V1

Status: Implemented

Target verdict:

```text
UNIVERSAL_TRANSLATION_ARTIFACT_SCHEMA_READY
```

## 1. Purpose

This artifact records the canonical runtime-safe schema used by the Universal Bidirectional Translation Runtime.

The schema supports both translation directions:

```text
Human -> Governance
Governance -> Human
```

Runtime implementation:

```text
aigol/runtime/universal_translation_artifact_schema.py
```

## 2. Canonical Artifact Fields

Every universal translation artifact contains:

```text
artifact_type
schema_version
translation_id
translation_request
source_direction
source_payload
normalized_intent
translated_governance_payload
human_readable_payload
ambiguity_flags
confidence
provider_metadata
deterministic_fallback_status
replay_reference
authority_flags
created_at
artifact_hash
```

## 3. Direction Rules

Allowed directions:

```text
HUMAN_TO_GOVERNANCE
GOVERNANCE_TO_HUMAN
```

`HUMAN_TO_GOVERNANCE` requires:

```text
translated_governance_payload
```

`GOVERNANCE_TO_HUMAN` requires:

```text
human_readable_payload
```

## 4. Authority Rules

Translation artifacts are evidence only.

They never grant:

- translation authority;
- governance authority;
- approval authority;
- execution authority;
- mutation authority;
- replay mutation authority;
- provider authority;
- worker authority.

Any authority flag set to true fails closed.

## 5. Replay Requirements

Translation artifacts must be:

- JSON serializable;
- deterministic-hash bound;
- replay-reference linked;
- strict about missing or extra fields;
- fail-closed on malformed structure.

The artifact hash excludes only the `artifact_hash` field itself.

## 6. Validation Helpers

Runtime helpers:

```text
create_universal_translation_artifact(...)
validate_universal_translation_artifact(...)
translation_artifact_hash(...)
authority_flags_for_translation()
```

## 7. Certification Coverage

Focused tests verify:

- Human -> Governance artifact creation;
- Governance -> Human artifact creation;
- stable hash verification;
- authority flag rejection;
- hash mismatch rejection;
- direction-specific payload requirements;
- provider comparison metadata;
- malformed artifact rejection;
- non-serializable payload rejection.

Test file:

```text
tests/test_universal_translation_artifact_schema_v1.py
```

## 8. Final Verdict

```text
UNIVERSAL_TRANSLATION_ARTIFACT_SCHEMA_READY
```
