# AIGOL_GENERIC_DOMAIN_FACTORY_REUSE_PLAN_V1

## Status

Review-only reuse plan.

## Objective

Define the safest path from the current Marketing-specific executable bundle
runtime to a generic governed domain factory without weakening replay,
authorization, or mutation boundaries.

## Reuse Strategy

Reuse the existing lifecycle mechanics, not the Marketing constants.

The future factory should preserve:

- worker result validation as the upstream authority;
- exact `CREATE_ONLY` bundle authorization;
- target absence preflight;
- create-only file writes;
- per-artifact verification;
- terminal failure replay consistency;
- post-execution replay review;
- governed termination.

## Proposed Milestones

### Milestone 1: Domain Bundle Registry Contract

Create `AIGOL_DOMAIN_BUNDLE_REGISTRY_AND_FACTORY_CONTRACT_V1`.

Required outputs:

- bundle registry schema;
- one Marketing registry entry equivalent to the current certified bundle;
- unsupported-domain fail-closed rules;
- exact artifact manifest format;
- registry hash model.

No filesystem mutation should be added in this milestone.

### Milestone 2: Generic Bundle Authorization Runtime

Create authorization from a selected registry entry instead of hardcoded
Marketing constants.

Required behavior:

- one selected bundle entry per authorization;
- exact ordered artifacts;
- exact content hashes;
- exact domain id and bundle id;
- fail closed on unsupported or ambiguous domain.

### Milestone 3: Generic Bundle Creation Runtime

Refactor bundle creation to consume the selected authorization artifact and
registry-derived content map.

Required behavior:

- preserve current `CREATE_ONLY` semantics;
- preserve preflight-before-write behavior;
- preserve failure replay consistency;
- preserve successful four-step replay.

### Milestone 4: Non-Marketing Pilot Bundle

Add one non-Marketing bundle entry as the first factory proof.

Recommended pilot:

`SERVER_MANAGEMENT_DOMAIN_FOUNDATION_V1`

Reason:

- server management is already present in conversation routing and the domain
  registry;
- it can remain governance-only or placeholder-executable without broker/API
  execution risk;
- it is less regulated than Healthcare and less product-critical than Trading.

### Milestone 5: Multi-Domain Certification

Certify:

- Marketing still works through the generic factory;
- Server Management works through the same factory;
- Trading and Healthcare fail closed until explicit bundle entries are
  certified;
- collision replay remains single-failure and replay-valid.

## Explicit Non-Goals

The reuse path must not introduce:

- arbitrary code generation;
- provider-authored executable code without bounded validation;
- overwrite/update/delete behavior;
- hidden domain creation;
- broker/API execution;
- Healthcare compliance claims;
- unrestricted autonomous domain expansion.

## Recommended Next Milestone

`AIGOL_DOMAIN_BUNDLE_REGISTRY_AND_FACTORY_CONTRACT_V1`
