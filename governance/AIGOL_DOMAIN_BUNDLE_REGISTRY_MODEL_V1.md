# AIGOL_DOMAIN_BUNDLE_REGISTRY_MODEL_V1

## Status

Review-only registry model.

## Registry Identity

`DOMAIN_BUNDLE_REGISTRY` is the canonical source of executable domain bundle
identity for the future generic factory runtime.

Registry version:

`AIGOL_DOMAIN_BUNDLE_REGISTRY_V1`

## Registry Entry Schema

Each registry entry must include:

- `domain_id`;
- `domain_display_name`;
- `domain_status`;
- `bundle_id`;
- `bundle_status`;
- `factory_capability`;
- `artifact_templates`;
- `runtime_template`;
- `test_template`;
- `regulatory_constraints`;
- `non_goals`;
- `known_gaps`;
- `factory_resolution_status`;
- `entry_hash`.

## Domain Status Values

Allowed `domain_status` values:

- `EXECUTABLE_PLACEHOLDER_CERTIFIED`;
- `REGISTERED_CONTRACT_ONLY`;
- `REGISTERED_REQUIRES_HUMAN_APPROVAL`;
- `REGISTERED_BLOCKED`.

Allowed `factory_resolution_status` values:

- `RESOLVABLE_EXECUTABLE`;
- `RESOLVABLE_NOT_EXECUTABLE`;
- `FAILED_CLOSED`.

## Required Domain Entries

The registry must contain entries for:

| Domain | Bundle id | Required status |
| --- | --- | --- |
| `MARKETING` | `MARKETING_EXECUTABLE_DOMAIN_BUNDLE_V1` | `EXECUTABLE_PLACEHOLDER_CERTIFIED` until replaced by a generic implementation |
| `SERVER_MANAGEMENT` | `SERVER_MANAGEMENT_EXECUTABLE_DOMAIN_BUNDLE_V1` | `REGISTERED_CONTRACT_ONLY` |
| `TRADING` | `TRADING_EXECUTABLE_DOMAIN_BUNDLE_V1` | `REGISTERED_REQUIRES_HUMAN_APPROVAL` |
| `HEALTHCARE` | `HEALTHCARE_EXECUTABLE_DOMAIN_BUNDLE_V1` | `REGISTERED_REQUIRES_HUMAN_APPROVAL` |

## Required Artifact Templates

Each entry must define these logical artifact roles:

- `DOMAIN_FOUNDATION`;
- `DOMAIN_MODEL`;
- `DOMAIN_CERTIFICATION`;
- `DOMAIN_RUNTIME`;
- `DOMAIN_RUNTIME_TEST`.

The registry entry, not the runtime module, owns the concrete path for each
role.

## Path Constraints

Allowed path roots:

- `governance/`;
- `aigol/runtime/`;
- `tests/`.

The future runtime must reject any registry entry with:

- absolute paths;
- parent-directory traversal;
- paths outside allowed roots;
- duplicate paths;
- missing role coverage;
- path names derived at execution time from unvalidated prompts.

## Content Hash Requirements

Every template must include:

- `template_id`;
- `template_version`;
- `rendering_mode`;
- `canonical_content_hash`;
- `artifact_type`;
- `permission = CREATE_ONLY`;
- `overwrite_permitted = false`.

The registry hash must be computed from normalized entries after removing any
derived `entry_hash` fields.

## Required Registry Semantics

The registry is read-only for the executable bundle runtime. A runtime may
consume a registry entry but must not modify the registry, add entries, infer
new domains, or rewrite template content.
