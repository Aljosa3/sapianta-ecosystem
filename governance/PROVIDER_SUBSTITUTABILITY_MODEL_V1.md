# Provider Substitutability Model V1

Status: provider substitutability model.

## Substitutable Providers

The following provider classes can be substituted without constitutional modification if they preserve the proposal-only boundary:

- OpenAI
- Claude
- Codex
- Gemini
- Local LLM
- Future Provider

## Required Compatibility

Substitution must not modify:

- governance model
- replay model
- authorization model
- execution model
- worker model
- Constitutional Memory model

## Adapter-Specific Scope

Provider substitution may require adapter-specific implementation for:

- SDK request shape
- credential handling
- timeout mapping
- response extraction
- provider version reporting
- provider error mapping

These are implementation details, not constitutional authority changes.

## Status

Provider substitutability is ready at the constitutional boundary.

Provider ecosystem routing and provider selection remain out of scope.
