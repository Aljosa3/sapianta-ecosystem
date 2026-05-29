# Provider Duplication Risks V1

Status: provider duplication and lock-in risk review.

## Primary Risk

The main provider risk is not hidden OpenAI authority.

The main provider risk is duplicated provider concepts across:

- external LLM attachment
- real provider attachment
- provider-agnostic raw response capture
- governed provider activation
- live OpenAI connector
- provider registry and gate

These concepts currently align, but they should not drift into parallel provider models.

## OpenAI Naming Gravity

Risk: `MEDIUM`

OpenAI-specific runtime files and tests exist. This can create naming gravity where OpenAI appears to be the default provider.

Evidence:

- `aigol/runtime/providers/openai_provider.py`
- `aigol/runtime/live_openai_runtime_connector.py`
- `aigol/runtime/real_openai_api_invocation.py`
- OpenAI-specific tests and governance evidence

Mitigation:

- Preserve generic provider boundary vocabulary in constitutional artifacts.
- Keep OpenAI-specific code adapter-local.
- Avoid describing OpenAI as canonical provider.

## Provider Identity Duplication

Risk: `MEDIUM`

Provider identity appears as `provider_identity`, `provider_id`, `provider_name`, `model_identity`, `model_name`, and provider envelope fields.

These fields are compatible, but not fully canonicalized into one provider identity vocabulary.

Mitigation:

- Treat this as a future canonicalization target if multi-provider work begins.
- Do not introduce a new identity layer unless current fields conflict.

## Provider Replay Duplication

Risk: `LOW`

Provider replay, external response replay, raw response replay, and activation replay are layered but compatible.

Mitigation:

- Preserve replay centrality.
- Ensure all provider replay layers remain append-only and reconstructable.
- Avoid parallel replay authority.

## Provider Ecosystem Inflation

Risk: `MEDIUM`

Provider registry, discovery, routing, marketplace, optimization, and fallback are attractive but not required for first real provider integration.

Mitigation:

- Keep provider selection explicit.
- Do not add routing, discovery, failover, or optimization until a genuine operational need is proven.

## Authority Duplication

Risk: `LOW`

Authority semantics are consistent: provider authority is absent.

No reviewed artifact grants OpenAI or any other provider governance, authorization, execution, replay, or worker authority.

## Review Finding

Provider substitutability is present at the boundary, but provider vocabulary and implementation surfaces should be watched for OpenAI naming gravity and identity-field duplication.

