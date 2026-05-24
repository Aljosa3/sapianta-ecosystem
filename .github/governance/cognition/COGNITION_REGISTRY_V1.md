# COGNITION_REGISTRY_V1

Status: governance-safe cognition primitive registry.

Scope: read-only primitive indexing and registry integrity validation.

## Purpose

`COGNITION_REGISTRY_V1` creates a canonical index over bounded cognition primitives already present in AiGOL / SAPIANTA.

The registry answers:

- what cognition primitives exist
- what each primitive does
- what authority each primitive has
- what replay role each primitive has
- what lifecycle role each primitive has
- what governance boundaries constrain each primitive

## Non-Goals

This milestone does not create:

- execution authority
- orchestration
- autonomous cognition
- autonomous continuation
- semantic reasoning
- provider routing
- dynamic plugin loading
- mutation authority
- runtime activation
- self-registration
- hidden ingestion

## Registry Model

The registry consumes the existing `COGNITION_PRIMITIVES_INDEX.json` as explicit evidence and emits a canonical `COGNITION_REGISTRY_V1` artifact.

The registry includes:

- primitive list
- primitive count
- cognition category topology
- authority classification topology
- replay relevance topology
- lifecycle role topology
- source file presence diagnostics
- governance boundary guarantees
- registry hash
- validation summary

## Validation Model

`COGNITION_REGISTRY_VALIDATION_V1` checks:

- required primitive fields
- duplicate primitive IDs
- source file list presence
- source file existence
- forbidden authority terms
- summary count consistency
- registry hash integrity
- no-authority governance boundary integrity

Validation is deterministic and read-only. It does not discover hidden primitives, self-register modules, load plugins, or activate runtime behavior.

## Governance Guarantees

The registry hard-codes:

- `execution_authority = false`
- `orchestration_authority = false`
- `autonomous_cognition = false`
- `autonomous_continuation = false`
- `semantic_reasoning_authority = false`
- `provider_routing_authority = false`
- `dynamic_plugin_loading = false`
- `mutation_authority = false`
- `runtime_activation = false`
- `self_registration = false`
- `hidden_ingestion = false`

The registry is discoverability only. It grants no cognition agency.

## CLI Observability

The CLI command is:

```bash
aigol cognition registry
```

Optional flags:

- `--input <registry_index_json>`
- `--json`
- `--output <path>`

Writing output is explicit only. The command does not execute, dispatch, orchestrate, mutate, route providers, or ingest hidden context.
