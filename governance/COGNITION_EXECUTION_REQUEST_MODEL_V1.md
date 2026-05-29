# Cognition Execution Request Model V1

Status: bridge request model.

## Request Input

Cognition output must be a JSON object with:

- contribution identifier
- human prompt
- target capability
- intent
- creation timestamp
- arguments

The input is untrusted and must be normalized before validation.

## Supported Capability Targets

Only the following targets are supported:

- `READ_ONLY_RUNTIME_INSPECTION`
- `FILESYSTEM_READ_ONLY_INSPECTION`

No new capability class is introduced.

## Normalization

Normalization must:

- require all expected fields
- reject unexpected fields
- normalize capability identifiers
- normalize intent text
- preserve read-only arguments
- reject hidden continuation language
- reject forbidden mutation intent

## Validation

Validation must prove:

- supported capability
- boundedness
- replay centrality
- authority separation
- execution boundary enforcement
- constitutional freeze compatibility

