# AIGOL_DOMAIN_BUNDLE_REGISTRY_RUNTIME_V1

## Status

Certified runtime milestone.

`AIGOL_DOMAIN_BUNDLE_REGISTRY_RUNTIME_STATUS = CERTIFIED`

## Root Cause

The certified executable domain bundle runtime preserved deterministic
`CREATE_ONLY` semantics, but domain identity resolution remained embedded in
Marketing-specific runtime constants.

That meant AiGOL could validate and create the current Marketing executable
bundle, but it could not deterministically resolve domain bundle identity for
`SERVER_MANAGEMENT`, `TRADING`, or `HEALTHCARE` before a future factory
implementation.

## Runtime Model

`AIGOL_DOMAIN_BUNDLE_REGISTRY_RUNTIME_V1` introduces a replay-visible
`DOMAIN_BUNDLE_REGISTRY`.

The runtime provides:

- canonical default registry construction;
- deterministic registry hash;
- deterministic registry entry hash;
- domain bundle lookup;
- optional executable requirement gating;
- fail-closed behavior for unknown, duplicate, hash-mismatched, or
  non-executable entries;
- replay persistence;
- replay reconstruction.

## Registry Domains

The registry resolves:

| Domain | Resolution status |
| --- | --- |
| `MARKETING` | `RESOLVABLE_EXECUTABLE` |
| `SERVER_MANAGEMENT` | `RESOLVABLE_NOT_EXECUTABLE` |
| `TRADING` | `RESOLVABLE_NOT_EXECUTABLE` |
| `HEALTHCARE` | `RESOLVABLE_NOT_EXECUTABLE` |

Only Marketing is executable in this milestone. Non-Marketing domains are
registry-resolvable but must fail closed when executable creation is required.

## Replay Model

Replay persists:

1. `domain_bundle_resolution_recorded`;
2. `domain_bundle_resolution_returned`.

Replay reconstruction verifies:

- replay order;
- wrapper hashes;
- resolution artifact hash;
- returned artifact hash;
- resolution reference continuity;
- resolution hash continuity.

## Executable Bundle Compatibility

The current Marketing executable bundle runtime continues to work. Bundle id
validation now consults the domain bundle registry for Marketing executable
identity, while artifact creation remains the existing certified Marketing
runtime path.

## Non-Goals

This runtime does not implement:

- generic domain factory artifact creation;
- non-Marketing executable bundle creation;
- provider-generated executable code;
- runtime or test template rendering;
- deployment, broker/API, or domain execution authority.

## Replay Impact

Domain bundle resolution is now replay-visible before future factory creation
work. Registry hash and entry hash continuity are explicit, and unsupported
domains fail closed deterministically without mutating filesystem artifacts.

## Final Classification

AIGOL_DOMAIN_BUNDLE_REGISTRY_RUNTIME_STATUS = CERTIFIED
