# AIGOL_MULTI_PROVIDER_LIVE_COGNITION_CERTIFICATION_V1

Status: prepared and executable.

## Goal

Certify live multi-provider cognition support.

The question under test is:

```text
Can AiGOL govern multiple cognition providers using the same approval,
authorization, replay, and audit model?
```

## Governing Evidence

- `CERT-000009`
- Provider Governance Runtime
- Provider Credential Vault
- Provider Vault ACLI Integration
- Product 1 End-To-End Certification

## Providers

The certification covers:

- `openai`
- `claude`
- `gemini`
- `mistral`

Required credential references:

- `vault://provider/openai`
- `vault://provider/claude`
- `vault://provider/gemini`
- `vault://provider/mistral`

## Certification Scope

The runtime verifies:

- provider onboarding lifecycle visibility;
- credential reference resolution;
- provider selection;
- provider failover behavior;
- replay-visible provider participation;
- provider governance metrics for usage, failures, participation, and cost hooks;
- live-provider evidence for multi-provider cognition.

## Runtime

Run:

```bash
python -m aigol.runtime.multi_provider_live_cognition_certification_v1
```

Artifacts are written under:

```text
runtime/multi_provider_live_cognition_certification_v1/CERT-XXXXXX/
```

## Evidence Outputs

- coverage report;
- evidence package;
- replay package;
- certification report.

## Pass Criteria

The verdict is `MULTI_PROVIDER_LIVE_COGNITION_CERTIFIED` only if:

- Product 1 end-to-end certification is present;
- OpenAI live cognition certification is present;
- all required provider vault references are defined;
- all required provider credentials are present and enabled;
- multi-provider runtime selects all providers;
- provider failure isolation is replay-visible;
- usage, failure, participation, and cost-hook metrics are replay-visible;
- at least one non-OpenAI provider has live cognition certification evidence;
- all representative certification scenarios pass;
- replay reconstruction succeeds.

Otherwise the verdict is:

```text
MULTI_PROVIDER_LIVE_COGNITION_GAPS_FOUND
```

## Expected Current Risk

At the time this artifact is introduced, OpenAI has live cognition evidence via
`CERT-000009`. Claude, Gemini, and Mistral have canonical provider ids and
credential references, but may not yet have live provider executors,
credentials, or one-provider live certifications.

If that remains true at execution time, the certification must report gaps
rather than claiming multi-provider live cognition readiness.
