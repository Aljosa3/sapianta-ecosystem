# AIGOL_DOMAIN_BUNDLE_RESOLUTION_MODEL_V1

## Status

Review-only resolution model.

## Purpose

`DOMAIN_BUNDLE_RESOLUTION_MODEL` defines how a future generic executable domain
factory selects a domain bundle entry without hardcoded filenames.

## Resolution Inputs

Resolution consumes:

- requested domain id;
- requested bundle id, if present;
- target milestone id;
- worker result validation artifact;
- allowed outputs;
- produced outputs;
- domain bundle registry;
- registry hash.

## Resolution Steps

1. Normalize requested domain id.
2. Find exactly one registry entry for the domain id.
3. Verify registry entry hash.
4. Verify requested bundle id if provided.
5. Verify the entry supports `DOMAIN_FOUNDATION` bundle creation.
6. Verify entry factory resolution status.
7. Compare validation outputs to registry artifact paths.
8. Produce a resolution artifact.

## Resolution Artifact

The resolution artifact must include:

- `artifact_type = DOMAIN_BUNDLE_RESOLUTION_ARTIFACT_V1`;
- `resolution_id`;
- `resolution_status`;
- `domain_id`;
- `bundle_id`;
- `registry_version`;
- `registry_hash`;
- `registry_entry_hash`;
- `artifact_paths`;
- `artifact_roles`;
- `template_hashes`;
- `factory_capability`;
- `failure_reason`.

## Domain Resolution Table

| Domain | Resolution status | Factory behavior |
| --- | --- | --- |
| `MARKETING` | `RESOLVABLE_EXECUTABLE` | May proceed through generic factory once implemented because the current Marketing executable placeholder is certified. |
| `SERVER_MANAGEMENT` | `RESOLVABLE_NOT_EXECUTABLE` | Must fail closed until a Server Management bundle entry is certified executable. |
| `TRADING` | `RESOLVABLE_NOT_EXECUTABLE` | Must fail closed pending explicit human-approved Trading bundle certification and non-broker execution constraints. |
| `HEALTHCARE` | `RESOLVABLE_NOT_EXECUTABLE` | Must fail closed pending Healthcare-specific regulatory constraints and no compliance guarantee claims. |

## Handoff Integration

`conversation_to_ppp_handoff_execution.py` currently emits generic governance
output targets from the target milestone. The future model must replace this
with registry resolution when the intent class is `CREATE_DOMAIN`.

`implementation_handoff_visibility.py` currently extends runtime and test
artifacts only for `MARKETING_DOMAIN_FOUNDATION_V1`. The future model must use
the resolved registry entry artifact roles instead.

## Bundle Runtime Integration

`executable_domain_bundle_runtime.py` and
`multi_artifact_domain_bundle_runtime.py` currently validate only Marketing
bundle constants. The future model must pass the selected resolution artifact
into authorization and creation so the runtime consumes registry paths and
template hashes instead of module constants.

## Fail-Closed Requirements

Resolution must fail closed when:

- no registry entry exists;
- more than one registry entry matches;
- the entry status is not executable for the requested lifecycle;
- requested outputs do not equal registry artifact paths;
- registry entry path constraints fail;
- registry hash or entry hash cannot be verified.
