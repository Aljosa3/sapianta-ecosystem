# AIGOL_GENERIC_DOMAIN_FACTORY_GAP_ANALYSIS_V1

## Status

Review-only gap analysis.

## Gap Summary

AiGOL has a governed executable bundle lifecycle, but not a generic domain
factory. The runtime creates one exact Marketing bundle and does not select,
parameterize, or validate domain-specific bundle definitions for arbitrary
domains.

## Gap 1: Domain Bundle Registry

Current gap:

- no executable bundle registry maps domain ids to exact artifact sets;
- no generic bundle entry schema exists;
- no per-domain content hash manifest exists outside Marketing constants.

Required capability:

- define a registry of certified domain bundle definitions;
- include domain id, bundle id, artifact paths, artifact types, content hashes,
  runtime symbol expectations, and test expectations;
- fail closed when no certified bundle entry exists.

## Gap 2: Parameterized Bundle Authorization

Current gap:

- authorization creation is bound to `MARKETING_EXECUTABLE_DOMAIN_BUNDLE_V1`;
- `_require_bundle_id` accepts only the Marketing executable bundle id;
- `_require_validated_outputs` compares only against Marketing paths.

Required capability:

- create authorization from a selected registry entry;
- preserve exact ordered artifact lists and content hashes;
- reject ambiguous or unsupported domain bundle requests.

## Gap 3: Generic Artifact Content Contract

Current gap:

- foundation, model, certification, runtime, and test content are fixed
  Marketing literals;
- runtime function and test imports are Marketing-specific.

Required capability:

- deterministic content templates or pre-certified static content per domain;
- explicit content hash validation before write;
- no provider-generated free-form code in the factory path.

## Gap 4: CLI Domain Bundle Selection

Current gap:

- CLI executable bundle binding invokes the bundle runtime only when the
  Marketing foundation path appears in validated outputs;
- non-Marketing domain prompts do not reach an executable bundle definition.

Required capability:

- bind validated outputs to a certified bundle registry entry;
- pass selected bundle identity into generic bundle authorization and creation;
- preserve terminal fail-closed behavior when no entry exists.

## Gap 5: Domain Prompt Coverage

Current gap:

- `Create a server management domain.` can be routed as domain intent but has
  no executable bundle.
- `Create a trading domain.` has governance/domain registry context but no
  executable bundle runtime contract.
- `Create a healthcare domain.` has future-domain registry context but no
  executable bundle.

Required capability:

- add certified executable bundle entries domain by domain;
- define domain-specific non-goals and regulatory limits;
- preserve explicit known-gap visibility.

## Gap 6: Factory Certification

Current gap:

- certification covers the exact Marketing executable bundle runtime;
- no certification proves generic domain selection, registry validation,
  unsupported-domain fail-closed behavior, or multi-domain replay continuity.

Required capability:

- certify one generic factory runtime;
- test at least one supported non-Marketing domain;
- test unsupported-domain fail-closed behavior;
- test collision and replay consistency for all supported bundle classes.

## Final Gap Classification

Generic domain factory readiness remains blocked by the absence of a certified
domain bundle registry and parameterized factory runtime.
