# AIGOL_PROVIDER_ECOSYSTEM_FOUNDATION_V1

## Status

Provider ecosystem foundation.

## Final Classification

```text
AIGOL_PROVIDER_ECOSYSTEM_FOUNDATION_STATUS = CERTIFIED
```

## Purpose

This milestone defines the constitutional foundation for a multi-provider AiGOL ecosystem.

The provider ecosystem allows AiGOL to represent, compare, select, attach, and retire provider proposal sources without making any provider authoritative.

## Scope

Foundation only.

This milestone does not implement:

- provider adapters;
- API integration;
- credentials;
- provider invocation;
- streaming;
- tools;
- execution;
- dispatch;
- governance mutation;
- replay mutation.

## Provider Definition

A provider is an external or local proposal source boundary.

A provider may produce bounded proposal evidence.

A provider is not:

- a governor;
- an authorizer;
- an executor;
- a worker;
- a dispatcher;
- a replay authority;
- a governance mutation source;
- an autonomous continuation authority.

## Initial Provider Classes

Initial provider classes:

```text
OPENAI
ANTHROPIC
CODEX
CLAUDE_CODE
```

These are ecosystem identities and capability candidates.

They are not certified live integrations by this milestone.

## Provider Lifecycle

Provider lifecycle states:

```text
REGISTERED
APPROVED
ATTACHED
AVAILABLE
DEGRADED
UNAVAILABLE
SUSPENDED
RETIRED
```

Lifecycle meaning:

- `REGISTERED`: provider identity is known and replay-visible;
- `APPROVED`: provider is constitutionally allowed for bounded proposal use;
- `ATTACHED`: provider has an adapter boundary or operator attachment path;
- `AVAILABLE`: provider is available for approved proposal workflows;
- `DEGRADED`: provider is usable only under restricted policy;
- `UNAVAILABLE`: provider cannot be invoked;
- `SUSPENDED`: provider is blocked pending review;
- `RETIRED`: provider is no longer selectable.

## Registration

Provider registration records:

- provider id;
- provider family;
- provider product;
- provider version;
- adapter version when present;
- status;
- capabilities;
- trust level;
- cost model;
- failure policy;
- replay requirements;
- authority denials.

Registration is metadata-only.

Registration does not attach, approve, invoke, or authorize a provider.

## Attachment

Provider attachment means AiGOL can create a bounded request packet and capture provider response evidence through an approved boundary.

Attachment must record:

- provider id;
- provider version;
- adapter or attachment path;
- request hash;
- response hash;
- canonical chain id;
- replay references.

Attachment does not grant execution, dispatch, governance, or replay authority.

## Approval

Provider approval is a governance decision that permits proposal-only use under a defined policy.

Approval must specify:

- approved capabilities;
- approved domains;
- approved workflows;
- maximum trust level;
- cost limits;
- high-risk constraints;
- failure handling;
- retirement conditions.

Approval is separate from availability.

An approved provider may still be unavailable.

## Versioning

Provider versioning must distinguish:

- provider family;
- provider product;
- model or service version;
- adapter version;
- capability schema version;
- selection policy version.

Version changes must be replay-visible.

Provider output must preserve the exact provider identity and version observed for that request.

## Retirement

A provider may be retired when:

- provider product is deprecated;
- adapter is unsafe or obsolete;
- trust level changes below allowed threshold;
- repeated failures exceed policy;
- cost policy is violated;
- provider behavior becomes incompatible with proposal-only boundaries;
- governance review suspends or retires the provider.

Retirement must not rewrite historical replay.

Historical replay remains reconstructable with the provider identity recorded at the time of use.

## Provider Independence

AiGOL remains provider-independent because:

- provider output is untrusted input;
- provider identity is replay-visible;
- provider selection is policy-mediated;
- provider capability is metadata, not authority;
- provider failures fail closed;
- proposal validation remains AiGOL-owned;
- human approval remains final where required;
- workers are never invoked by providers.

## Constitutional Invariant

The ecosystem preserves:

```text
LLM proposes.
AiGOL governs.
Human authorizes.
Worker executes.
Replay records.
```

## Certification Judgment

The provider ecosystem foundation is certified as architecture.

Runtime implementation of additional providers remains future work.

