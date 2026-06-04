# AIGOL_DOMAIN_BUNDLE_REGISTRY_AND_FACTORY_CONTRACT_V1

## Status

Certified review-only factory contract.

No runtime mutation, executable domain creation, or implementation change is
authorized by this artifact.

## Purpose

This contract replaces Marketing-specific executable bundle assumptions with a
registry-driven model for future executable domain factory implementation.

The contract defines:

- `DOMAIN_BUNDLE_REGISTRY`;
- `DOMAIN_FACTORY_CONTRACT`;
- `DOMAIN_ARTIFACT_TEMPLATE_MODEL`;
- `DOMAIN_RUNTIME_TEMPLATE_MODEL`;
- `DOMAIN_TEST_TEMPLATE_MODEL`;
- `DOMAIN_BUNDLE_RESOLUTION_MODEL`.

## Reviewed Runtime Surfaces

The contract was designed after reviewing:

- `aigol/runtime/executable_domain_bundle_runtime.py`;
- `aigol/runtime/multi_artifact_domain_bundle_runtime.py`;
- `aigol/runtime/implementation_handoff_visibility.py`;
- `aigol/runtime/conversation_to_ppp_handoff_execution.py`.

## Required Runtime Direction

A future generic executable bundle runtime must resolve these domain ids through
the registry rather than hardcoded filenames:

- `MARKETING`;
- `SERVER_MANAGEMENT`;
- `TRADING`;
- `HEALTHCARE`.

Resolution does not mean all domains are executable today. Resolution means the
runtime can deterministically find a registry entry, determine whether the entry
is executable, and either continue with exact authorized artifacts or fail
closed with a domain-specific reason.

## Runtime Realization Note

`AIGOL_GENERIC_DOMAIN_FACTORY_RUNTIME_V1` realizes the first runtime
implementation of this contract for executable placeholder bundles while
preserving the contract boundaries below.

## Contract Boundaries

The future factory runtime must preserve:

- `CREATE_ONLY`;
- exact artifact paths;
- exact artifact types;
- exact deterministic content hashes;
- target absence preflight before first write;
- create-only file writes;
- per-artifact verification;
- replay-visible failure;
- post-execution replay review before termination;
- no overwrite, delete, rename, move, recursive creation, implicit creation, or
  directory creation authority.

## Non-Goals

This contract does not authorize:

- provider-generated executable code;
- hidden domain expansion;
- runtime mutation in this milestone;
- broker/API execution;
- Healthcare compliance claims;
- trading execution authority;
- unrestricted autonomous factory behavior.

## Final Classification

AIGOL_DOMAIN_BUNDLE_REGISTRY_AND_FACTORY_CONTRACT_STATUS = CERTIFIED_REVIEW_ONLY
